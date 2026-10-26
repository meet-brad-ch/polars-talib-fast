//! Compiles TA-Lib (the `ta-lib` git submodule next to this file) into a static library linked
//! into the oracle. The source directories are the ones TA-Lib's own CMakeLists.txt puts into
//! `ta-lib-static`, and the floating-point flag is the one it sets: no compiler contraction of
//! `a*b+c` into an FMA on GCC/Clang, so explicit `fma()` calls are the only fused arithmetic.
//!
//! `TA_FuncInfo` lost its `camelCaseName` field in TA-Lib 0.8; the `ta_camel_case` cfg tells
//! `ffi.rs` which layout the checked-out headers have.

use std::fs;
use std::path::Path;

const TA_LIB: &str = "ta-lib";
const SOURCE_DIRS: [&str; 5] = [
    "src/ta_common",
    "src/ta_abstract",
    "src/ta_abstract/tables",
    "src/ta_abstract/frames",
    "src/ta_func",
];

fn main() {
    let root = Path::new(TA_LIB);
    let version = fs::read_to_string(root.join("VERSION"))
        .unwrap_or_else(|e| panic!("{TA_LIB}/VERSION: {e} (run `git submodule update --init`)"));
    let mut parts = version.trim().split('.').map(|p| p.parse::<u32>().expect("numeric TA-Lib version"));
    let (major, minor) = (parts.next().unwrap(), parts.next().unwrap());
    println!("cargo::rustc-check-cfg=cfg(ta_camel_case)");
    if (major, minor) < (0, 8) {
        println!("cargo::rustc-cfg=ta_camel_case");
    }

    let mut build = cc::Build::new();
    for dir in SOURCE_DIRS {
        let dir = root.join(dir);
        let entries = fs::read_dir(&dir).unwrap_or_else(|e| panic!("{}: {e}", dir.display()));
        for entry in entries {
            let path = entry.unwrap().path();
            if path.extension().is_some_and(|ext| ext == "c") {
                build.file(path);
            }
        }
        build.include(&dir);
    }
    build.flag_if_supported("-ffp-contract=off");
    build.include(root.join("include")).warnings(false).compile("ta-lib");
    println!("cargo:rerun-if-changed={TA_LIB}/VERSION");
}
