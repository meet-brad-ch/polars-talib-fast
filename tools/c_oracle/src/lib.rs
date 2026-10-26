//! `c_oracle`: TA-Lib's C library through its abstract interface, as a Python module. It is the
//! code the plugin ran on before the port to the `ta-lib` crate (`talib.rs`, `ffi.rs`), kept to
//! write the golden data the plugin is tested against (`generate.py`). Not shipped.

mod ffi;
mod talib;

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyInt, PyList};

use talib::{Column, Function, Input, Number};

fn runtime_error(e: talib::Error) -> PyErr {
    PyRuntimeError::new_err(e.0)
}

#[pyfunction]
fn version() -> String {
    talib::version()
}

/// Every TA-Lib function as a dict: `name`, `group`, `hint`, `inputs` (name, price parts),
/// `params` (name, integer, default, hint) and `outputs` (name, integer).
#[pyfunction]
fn functions(py: Python<'_>) -> PyResult<Vec<Bound<'_, PyDict>>> {
    Function::table()
        .map_err(runtime_error)?
        .iter()
        .map(|f| {
            let d = PyDict::new(py);
            d.set_item("name", &f.name)?;
            d.set_item("group", &f.group)?;
            d.set_item("hint", &f.hint)?;
            let inputs: Vec<(&str, &[&str])> = f
                .inputs
                .iter()
                .map(|i| match i {
                    Input::Real(name) => (name.as_str(), &[][..]),
                    Input::Price(parts) => ("price", parts.as_slice()),
                })
                .collect();
            d.set_item("inputs", inputs)?;
            let params: Vec<(&str, bool, f64, &str)> =
                f.params.iter().map(|p| (p.name.as_str(), p.integer, p.default, p.hint.as_str())).collect();
            d.set_item("params", params)?;
            let outputs: Vec<(&str, bool)> = f.outputs.iter().map(|o| (o.name.as_str(), o.integer)).collect();
            d.set_item("outputs", outputs)?;
            Ok(d)
        })
        .collect()
}

/// Run function `name` on `columns` (declaration order, equal length) with `params` (declaration
/// order; a Python int stays an integer). `offset` rows were cut off the front by the caller, as
/// the plugin cuts leading NaN rows; see `Function::call`. One list per output.
#[pyfunction]
fn call<'py>(
    py: Python<'py>,
    name: &str,
    columns: Vec<Vec<f64>>,
    params: Vec<Bound<'py, PyAny>>,
    offset: usize,
) -> PyResult<Vec<Bound<'py, PyList>>> {
    let function = Function::get(name).map_err(runtime_error)?;
    let values = params.iter().map(number).collect::<PyResult<Vec<_>>>()?;
    let slices: Vec<&[f64]> = columns.iter().map(Vec::as_slice).collect();
    let outputs = function.call(&slices, &values, offset).map_err(runtime_error)?;
    outputs.into_iter().map(|out| list(py, out)).collect()
}

/// A Python parameter value: an int stays an integer.
fn number(p: &Bound<'_, PyAny>) -> PyResult<Number> {
    if p.is_instance_of::<PyInt>() {
        Ok(Number::Int(p.extract()?))
    } else {
        Ok(Number::Float(p.extract()?))
    }
}

fn list(py: Python<'_>, column: Column) -> PyResult<Bound<'_, PyList>> {
    match column {
        Column::Real(v) => PyList::new(py, v),
        Column::Integer(v) => PyList::new(py, v),
    }
}

#[pymodule]
fn c_oracle(m: &Bound<'_, PyModule>) -> PyResult<()> {
    talib::initialize().map_err(runtime_error)?;
    m.add_function(wrap_pyfunction!(version, m)?)?;
    m.add_function(wrap_pyfunction!(functions, m)?)?;
    m.add_function(wrap_pyfunction!(call, m)?)?;
    Ok(())
}
