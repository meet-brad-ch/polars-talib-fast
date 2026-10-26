from polars import Expr
from polars._typing import IntoExpr

def adr(high: IntoExpr = ..., low: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Average Day Range (Volatility Indicators), TA-Lib ADR.
    
    timeperiod: Time period (default 14)
    Output: real"""

def atr(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Average True Range (Volatility Indicators), TA-Lib ATR.
    
    timeperiod: Time period (default 14)
    Output: real"""

def bbw(real: IntoExpr = ..., timeperiod: int = 20, nbdevup: float = 2.0, nbdevdn: float = 2.0, matype: int = 0) -> Expr:
    """Bollinger BandWidth (Volatility Indicators), TA-Lib BBW.
    
    timeperiod: Time period (default 20)
    nbdevup: Deviation multiplier for upper band (default 2.0)
    nbdevdn: Deviation multiplier for lower band (default 2.0)
    matype: Type of Moving Average (default 0)
    Output: real"""

def cvi(high: IntoExpr = ..., low: IntoExpr = ..., timeperiod: int = 10, rocperiod: int = 10) -> Expr:
    """Chaikin's Volatility (Volatility Indicators), TA-Lib CVI.
    
    timeperiod: Period of the EMA smoothing the high-low spread (default 10)
    rocperiod: Number of bars the rate of change reaches back (default 10)
    Output: real"""

def massi(high: IntoExpr = ..., low: IntoExpr = ..., fastperiod: int = 9, slowperiod: int = 25) -> Expr:
    """Mass Index (Volatility Indicators), TA-Lib MASSI.
    
    fastperiod: Period of both exponential averages of the high-low range (default 9)
    slowperiod: Number of bars the ratio is summed over (default 25)
    Output: real"""

def natr(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Normalized Average True Range (Volatility Indicators), TA-Lib NATR.
    
    timeperiod: Time period (default 14)
    Output: real"""

def percentb(real: IntoExpr = ..., timeperiod: int = 20, nbdevup: float = 2.0, nbdevdn: float = 2.0, matype: int = 0) -> Expr:
    """Bollinger Bands %B (Volatility Indicators), TA-Lib PERCENTB.
    
    timeperiod: Time period (default 20)
    nbdevup: Deviation multiplier for upper band (default 2.0)
    nbdevdn: Deviation multiplier for lower band (default 2.0)
    matype: Type of Moving Average (default 0)
    Output: real"""

def rogerssatchell(open: IntoExpr = ..., high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., timeperiod: int = 10, annualization: float = 252.0) -> Expr:
    """Rogers-Satchell Volatility (Volatility Indicators), TA-Lib ROGERSSATCHELL.
    
    timeperiod: Number of bars in the window (default 10)
    annualization: Periods per year; 1 leaves the per-bar figure (default 252.0)
    Output: real"""

def rvi(real: IntoExpr = ..., timeperiod: int = 14, stddevperiod: int = 10) -> Expr:
    """Relative Volatility Index (Volatility Indicators), TA-Lib RVI.
    
    timeperiod: Time period of the Wilder smoothing applied to both legs (default 14)
    stddevperiod: Time period of the standard deviation (default 10)
    Output: real"""

def rvir(high: IntoExpr = ..., low: IntoExpr = ..., timeperiod: int = 14, stddevperiod: int = 10) -> Expr:
    """Relative Volatility Index, refined high/low form (Volatility Indicators), TA-Lib RVIR.
    
    timeperiod: Time period of the Wilder smoothing applied to both indices (default 14)
    stddevperiod: Time period of the standard deviation (default 10)
    Output: real"""

def trange(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ...) -> Expr:
    """True Range (Volatility Indicators), TA-Lib TRANGE.
    
    Output: real"""
