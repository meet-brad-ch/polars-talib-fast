from polars import Expr
from polars._typing import IntoExpr

def avgdev(real: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Average Deviation (Price Transform), TA-Lib AVGDEV.
    
    timeperiod: Time period (default 14)
    Output: real"""

def avgprice(open: IntoExpr = ..., high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ...) -> Expr:
    """Average Price (Price Transform), TA-Lib AVGPRICE.
    
    Output: real"""

def ha(open: IntoExpr = ..., high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ...) -> Expr:
    """Heikin-Ashi Candles (Price Transform), TA-Lib HA.
    
    Output struct: haopen, hahigh, halow, haclose"""

def medprice(high: IntoExpr = ..., low: IntoExpr = ...) -> Expr:
    """Median Price (Price Transform), TA-Lib MEDPRICE.
    
    Output: real"""

def typprice(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ...) -> Expr:
    """Typical Price (Price Transform), TA-Lib TYPPRICE.
    
    Output: real"""

def wclprice(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ...) -> Expr:
    """Weighted Close Price (Price Transform), TA-Lib WCLPRICE.
    
    Output: real"""
