//! Safe layer over TA-Lib's abstract API (`ta_lib::abstract_api`, the official Rust port): a
//! `Function` is TA-Lib's own description of one TA function (inputs, parameters, outputs), and
//! `call` runs it on plain `f64` columns. Nothing here knows any function by name, except the
//! three whose integer output is a position in the input.

use std::collections::HashMap;
use std::fmt;
use std::sync::{LazyLock, OnceLock};

use serde::Deserialize;
use ta_lib::abstract_api::{
    self, FuncId, FuncInfo, Group, InputFlags, InputInfo, InputType, OptInputInfo, OptInputType, OutputInfo,
    OutputType, ParamHolder,
};
use ta_lib::{Core, OutRange, RetCode};

#[derive(Debug, Clone)]
pub struct Error(pub String);

impl Error {
    /// A failed TA-Lib call as text: what was called, then the code and its meaning
    /// ("SMA: timeperiod=0: BadParam (bad parameter)").
    fn code(what: &str, code: RetCode) -> Error {
        Error(format!("{what}: {code:?} ({code})"))
    }
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.0)
    }
}

/// The TA-Lib library this plugin is built on.
pub struct Library;

impl Library {
    /// The version of the `ta-lib` crate, read from its exact pin in `Cargo.toml`, so the
    /// version is written in one place only.
    pub fn version() -> &'static str {
        const PIN: &str = r#"ta-lib = "="#;
        include_str!("../Cargo.toml")
            .lines()
            .find_map(|line| line.strip_prefix(PIN))
            .and_then(|rest| rest.strip_suffix('"'))
            .expect(r#"Cargo.toml pins the ta-lib crate as ta-lib = "=x.y.z""#)
    }

    /// TA-Lib names the way ta-lib-python spells them: the Hungarian prefix goes and the rest
    /// is lower-cased (`optInFastPeriod` → `fastperiod`, `inReal0` → `real0`, `outMACD` →
    /// `macd`). Outputs also drop a leading `Real` when something follows it
    /// (`outRealUpperBand` → `upperband`, `outReal` → `real`). A name without the prefix is
    /// an error: it would collide with or misname a Python parameter.
    fn plain(raw: &str, prefix: &str) -> Result<String, Error> {
        let Some(name) = raw.strip_prefix(prefix) else {
            return Err(Error(format!("unexpected TA-Lib name {raw}, expected prefix {prefix}")));
        };
        let name = match (prefix, name.strip_prefix("Real")) {
            ("out", Some(rest)) if !rest.is_empty() => rest,
            _ => name,
        };
        Ok(name.to_ascii_lowercase())
    }

    /// The one `Core` all calls share: TA-Lib's default settings, immutable and `Sync`.
    fn core() -> &'static Core {
        static CORE: LazyLock<Core> = LazyLock::new(Core::new);
        &CORE
    }
}

/// One declared input: a single real series, or a price bundle of the named components.
#[derive(Debug)]
pub enum Input {
    Real(String),
    Price(Vec<&'static str>),
}

impl Input {
    /// The price components of an `InputType::Price`, in the order `set_price_input` takes them.
    const PRICE_PARTS: [(InputFlags, &'static str); 6] = [
        (InputFlags::PRICE_OPEN, "open"),
        (InputFlags::PRICE_HIGH, "high"),
        (InputFlags::PRICE_LOW, "low"),
        (InputFlags::PRICE_CLOSE, "close"),
        (InputFlags::PRICE_VOLUME, "volume"),
        (InputFlags::PRICE_OPENINTEREST, "openinterest"),
    ];

    fn describe(function: &str, info: &InputInfo) -> Result<Input, Error> {
        match info.kind {
            InputType::Price => Ok(Input::Price(
                Self::PRICE_PARTS.iter().filter(|(flag, _)| info.flags.contains(*flag)).map(|(_, part)| *part).collect(),
            )),
            InputType::Real => Ok(Input::Real(Library::plain(info.param_name, "in")?)),
            InputType::Integer => Err(Error(format!("{function}: integer input {} is not supported", info.param_name))),
        }
    }

    /// How many series this input consumes from the plugin's argument list.
    pub fn width(&self) -> usize {
        match self {
            Input::Real(_) => 1,
            Input::Price(parts) => parts.len(),
        }
    }

    /// The name of each series this input consumes, in order.
    fn names(&self) -> Vec<&str> {
        match self {
            Input::Real(name) => vec![name.as_str()],
            Input::Price(parts) => parts.clone(),
        }
    }

    /// Bind `series` (this input's share of the columns) to input slot `slot`.
    fn bind<'a>(&self, holder: &mut ParamHolder<'a>, slot: usize, series: &[&'a [f64]]) -> Result<(), RetCode> {
        match self {
            Input::Real(_) => holder.set_input(slot, series[0]).map(|_| ()),
            Input::Price(parts) => {
                let mut by_part: [Option<&'a [f64]>; 6] = [None; 6];
                for (bound, (_, part)) in by_part.iter_mut().zip(Self::PRICE_PARTS.iter()) {
                    *bound = parts.iter().position(|p| p == part).map(|k| series[k]);
                }
                let [open, high, low, close, volume, open_interest] = by_part;
                holder.set_price_input(slot, open, high, low, close, volume, open_interest).map(|_| ())
            }
        }
    }
}

#[derive(Debug)]
pub struct Param {
    pub name: String,
    pub integer: bool,
    pub default: f64,
    pub hint: String,
}

impl Param {
    fn describe(info: &OptInputInfo) -> Result<Param, Error> {
        let (integer, default) = match info.kind {
            OptInputType::IntegerRange { default, .. } => (true, f64::from(default)),
            OptInputType::IntegerList { default, .. } => (true, default as f64),
            OptInputType::RealRange { default, .. } | OptInputType::RealList { default, .. } => (false, default),
        };
        Ok(Param { name: Library::plain(info.param_name, "optIn")?, integer, default, hint: info.hint.to_owned() })
    }

    /// `value` as this parameter's TA-Lib type. An integer parameter takes an integer that fits
    /// TA-Lib's 32 bits; a real parameter takes either.
    fn typed(&self, function: &str, value: Number) -> Result<ParamValue, Error> {
        match (self.integer, value) {
            (true, Number::Int(v)) => i32::try_from(v)
                .map(ParamValue::Integer)
                .map_err(|_| Error(format!("{function}: {} must fit a 32-bit integer, got {v}", self.name))),
            (true, Number::Float(v)) => Err(Error(format!("{function}: {} must be an integer, got {v:?}", self.name))),
            (false, Number::Int(v)) => Ok(ParamValue::Real(v as f64)),
            (false, Number::Float(v)) => Ok(ParamValue::Real(v)),
        }
    }

    /// Bind `value` to parameter slot `slot`.
    fn bind(&self, holder: &mut ParamHolder<'_>, function: &str, slot: usize, value: Number) -> Result<(), Error> {
        let bound = match self.typed(function, value)? {
            ParamValue::Integer(v) => holder.set_opt_input(slot, v).map(|_| ()),
            ParamValue::Real(v) => holder.set_opt_input(slot, v).map(|_| ()),
        };
        bound.map_err(|code| Error::code(&format!("{function}: {}", self.name), code))
    }
}

/// A parameter value in the type TA-Lib takes for its slot.
enum ParamValue {
    Integer(i32),
    Real(f64),
}

#[derive(Debug)]
pub struct Output {
    pub name: String,
    pub integer: bool,
}

impl Output {
    fn describe(info: &OutputInfo) -> Result<Output, Error> {
        Ok(Output { name: Library::plain(info.param_name, "out")?, integer: info.kind == OutputType::Integer })
    }
}

/// A parameter value as supplied by the caller; integers stay integers so an integer
/// parameter given a fraction is an error, not a silent truncation.
#[derive(Debug, Clone, Copy, Deserialize)]
#[serde(untagged)]
pub enum Number {
    Int(i64),
    Float(f64),
}

impl fmt::Display for Number {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Number::Int(v) => write!(f, "{v}"),
            Number::Float(v) => write!(f, "{v:?}"),
        }
    }
}

/// Result columns, one per declared output, each `offset` rows longer than the input.
pub enum Column {
    Real(Vec<f64>),
    Integer(Vec<i32>),
}

impl Column {
    /// `len` rows of the value a row without a result holds: NaN, or 0 for integers.
    fn empty(integer: bool, len: usize) -> Column {
        if integer {
            Column::Integer(vec![0; len])
        } else {
            Column::Real(vec![f64::NAN; len])
        }
    }

    /// Bind the rows from `first` on to output slot `slot`: TA-Lib writes its results there.
    fn bind<'a>(&'a mut self, holder: &mut ParamHolder<'a>, slot: usize, first: usize) -> Result<(), RetCode> {
        match self {
            Column::Real(v) => holder.set_output(slot, &mut v[first..]).map(|_| ()),
            Column::Integer(v) => holder.set_int_output(slot, &mut v[first..]).map(|_| ()),
        }
    }
}

#[derive(Debug)]
pub struct Function {
    id: FuncId,
    pub name: String,
    pub group: String,
    pub hint: String,
    pub inputs: Vec<Input>,
    pub params: Vec<Param>,
    pub outputs: Vec<Output>,
    /// Integer outputs are positions in the input (see `call`'s `offset`).
    positional: bool,
}

/// Every function, described once: the first use reads TA-Lib's registry, every call after
/// that is a map lookup with no allocation. A failure to describe them is kept too.
struct Table {
    functions: Vec<Function>,
    index: HashMap<String, usize>,
}

impl Table {
    fn get() -> Result<&'static Table, Error> {
        static TABLE: OnceLock<Result<Table, Error>> = OnceLock::new();
        TABLE.get_or_init(Table::build).as_ref().map_err(Error::clone)
    }

    /// Every function TA-Lib knows, group by group in TA-Lib's group order, by name within
    /// a group (the order ta-lib-python lists them in).
    fn build() -> Result<Table, Error> {
        let mut functions = Vec::new();
        for group in Group::ALL {
            let mut infos: Vec<&FuncInfo> = abstract_api::FUNCS.iter().filter(|f| f.group == *group).collect();
            infos.sort_by_key(|f| f.name);
            for info in infos {
                functions.push(Function::describe(info)?);
            }
        }
        let index = functions.iter().enumerate().map(|(i, f)| (f.name.clone(), i)).collect();
        Ok(Table { functions, index })
    }
}

impl Function {
    /// The functions whose integer output is a position in the input.
    const POSITIONAL: [&'static str; 3] = ["MAXINDEX", "MININDEX", "MINMAXINDEX"];

    /// The description of one function, by TA-Lib's name.
    pub fn get(name: &str) -> Result<&'static Function, Error> {
        let table = Table::get()?;
        match table.index.get(name) {
            Some(&i) => Ok(&table.functions[i]),
            None => Err(Error(format!("unknown TA-Lib function {name}"))),
        }
    }

    /// Every function TA-Lib knows, in TA-Lib's order.
    pub fn table() -> Result<&'static [Function], Error> {
        Ok(&Table::get()?.functions)
    }

    fn describe(info: &FuncInfo) -> Result<Function, Error> {
        Ok(Function {
            id: info.id,
            positional: Self::POSITIONAL.contains(&info.name),
            name: info.name.to_owned(),
            group: info.group.as_str().to_owned(),
            hint: info.hint.to_owned(),
            inputs: info.inputs.iter().map(|i| Input::describe(info.name, i)).collect::<Result<_, _>>()?,
            params: info.opt_inputs.iter().map(Param::describe).collect::<Result<_, _>>()?,
            outputs: info.outputs.iter().map(Output::describe).collect::<Result<_, _>>()?,
        })
    }

    /// The common length of the input series given by `lengths`, or why there is none:
    /// the wrong number of series, or series of different lengths. Allocates only for
    /// the error message.
    pub fn rows(&self, lengths: impl ExactSizeIterator<Item = usize> + Clone) -> Result<usize, Error> {
        let width: usize = self.inputs.iter().map(Input::width).sum();
        if lengths.len() != width {
            let names: Vec<&str> = self.inputs.iter().flat_map(Input::names).collect();
            return Err(Error(format!(
                "{}: expects {width} input series ({}), got {}",
                self.name,
                names.join(", "),
                lengths.len()
            )));
        }
        let mut rest = lengths.clone();
        let n = rest.next().unwrap_or(0);
        if rest.any(|len| len != n) {
            let names = self.inputs.iter().flat_map(Input::names);
            let each: Vec<String> = names.zip(lengths).map(|(name, len)| format!("{name}={len}")).collect();
            return Err(Error(format!("{}: input series differ in length: {}", self.name, each.join(", "))));
        }
        Ok(n)
    }

    /// The call as TA-Lib sees it, for error messages: "SMA: timeperiod=0".
    fn describe_call(&self, values: &[Number]) -> String {
        let given: Vec<String> = self.params.iter().zip(values).map(|(p, v)| format!("{}={v}", p.name)).collect();
        if given.is_empty() {
            self.name.clone()
        } else {
            format!("{}: {}", self.name, given.join(", "))
        }
    }

    /// Run the function. `columns` are the input series in declaration order, all of equal
    /// length; `values` are the parameters in declaration order. `offset` is the number of
    /// rows the caller cut off the front of its data: each output column is `offset` rows
    /// longer than the input, and those rows, like the rows before the function's lookback,
    /// hold NaN (real) or 0 (integer). Positions reported by the MAXINDEX family count from
    /// the caller's first row, as ta-lib-python's do. A window longer than the data is not
    /// an error: every row is then NaN / 0.
    pub fn call(&self, columns: &[&[f64]], values: &[Number], offset: usize) -> Result<Vec<Column>, Error> {
        let n = self.rows(columns.iter().map(|c| c.len()))?;
        let full = offset + n;
        let skipped = self.position_offset(offset, full)?;
        let mut holder = self.id.new_call(Library::core());
        let lookback = self.bind(&mut holder, columns, values)?;
        let mut outputs = self.empty_outputs(full);
        if lookback < n {
            let first = offset + lookback;
            self.compute(holder, &mut outputs, first, lookback, n, values)?;
            if self.positional {
                Self::shift_positions(&mut outputs, first, skipped);
            }
        }
        Ok(outputs)
    }

    /// Bind inputs and parameters; the function's lookback for those parameters. A rejected
    /// parameter shows here first; TA-Lib's call would report the same.
    fn bind<'a>(&self, holder: &mut ParamHolder<'a>, columns: &[&'a [f64]], values: &[Number]) -> Result<usize, Error> {
        self.bind_inputs(holder, columns)?;
        self.bind_params(holder, values)?;
        holder.lookback().map_err(|code| Error::code(&self.describe_call(values), code))
    }

    fn empty_outputs(&self, full: usize) -> Vec<Column> {
        self.outputs.iter().map(|o| Column::empty(o.integer, full)).collect()
    }

    /// Let TA-Lib write rows `first..` of `outputs`, then check it wrote exactly those.
    fn compute<'a>(
        &self,
        mut holder: ParamHolder<'a>,
        outputs: &'a mut [Column],
        first: usize,
        lookback: usize,
        n: usize,
        values: &[Number],
    ) -> Result<(), Error> {
        for (slot, out) in outputs.iter_mut().enumerate() {
            out.bind(&mut holder, slot, first).map_err(|code| Error::code(&format!("{}: output {slot}", self.name), code))?;
        }
        let range = holder.call(0, n - 1).map_err(|code| Error::code(&self.describe_call(values), code))?;
        self.check_range(range, lookback, n)
    }

    /// `offset` as the amount the MAXINDEX family's positions move by; TA-Lib reports positions
    /// as 32-bit integers, so the whole column must fit them.
    fn position_offset(&self, offset: usize, full: usize) -> Result<i32, Error> {
        i32::try_from(full)
            .map_err(|_| Error(format!("{}: {full} rows, TA-Lib handles at most {}", self.name, i32::MAX)))?;
        Ok(offset as i32) // fits: offset <= full
    }

    fn bind_inputs<'a>(&self, holder: &mut ParamHolder<'a>, columns: &[&'a [f64]]) -> Result<(), Error> {
        let mut next = 0;
        for (slot, input) in self.inputs.iter().enumerate() {
            let series = &columns[next..next + input.width()];
            next += input.width();
            input.bind(holder, slot, series).map_err(|code| Error::code(&format!("{}: input {slot}", self.name), code))?;
        }
        Ok(())
    }

    fn bind_params(&self, holder: &mut ParamHolder<'_>, values: &[Number]) -> Result<(), Error> {
        if values.len() != self.params.len() {
            return Err(Error(format!("{} takes {} parameters, {} given", self.name, self.params.len(), values.len())));
        }
        for (slot, (param, value)) in self.params.iter().zip(values).enumerate() {
            param.bind(holder, &self.name, slot, *value)?;
        }
        Ok(())
    }

    /// TA-Lib must report exactly the rows from the lookback to the end, or the output rows
    /// before `first` and after its values would be misread.
    fn check_range(&self, range: OutRange, lookback: usize, n: usize) -> Result<(), Error> {
        if range.beg_idx == lookback && range.count == n - lookback {
            return Ok(());
        }
        Err(Error(format!(
            "{}: TA-Lib produced rows {}..{}, expected {lookback}..{n}",
            self.name,
            range.beg_idx,
            range.beg_idx + range.count
        )))
    }

    fn shift_positions(outputs: &mut [Column], first: usize, skipped: i32) {
        for out in outputs.iter_mut() {
            if let Column::Integer(v) = out {
                v[first..].iter_mut().for_each(|i| *i += skipped);
            }
        }
    }
}
