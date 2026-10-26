from polars import Expr
from polars._typing import IntoExpr

def ad(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., volume: IntoExpr = ...) -> Expr:
    """Chaikin A/D Line (Volume Indicators), TA-Lib AD.
    
    Output: real"""

def adosc(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., volume: IntoExpr = ..., fastperiod: int = 3, slowperiod: int = 10) -> Expr:
    """Chaikin A/D Oscillator (Volume Indicators), TA-Lib ADOSC.
    
    fastperiod: Period of the fast MA (default 3)
    slowperiod: Period of the slow MA (default 10)
    Output: real"""

def cmf(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., volume: IntoExpr = ..., timeperiod: int = 20) -> Expr:
    """Chaikin Money Flow (Volume Indicators), TA-Lib CMF.
    
    timeperiod: Time period (default 20)
    Output: real"""

def efi(close: IntoExpr = ..., volume: IntoExpr = ..., timeperiod: int = 13) -> Expr:
    """Elder's Force Index (Volume Indicators), TA-Lib EFI.
    
    timeperiod: Time period (default 13)
    Output: real"""

def emv(high: IntoExpr = ..., low: IntoExpr = ..., volume: IntoExpr = ..., timeperiod: int = 14, volumedivisor: float = 10000.0) -> Expr:
    """Arms Ease of Movement (Volume Indicators), TA-Lib EMV.
    
    timeperiod: Bars in the SMA of the one-bar values (1 = unsmoothed) (default 14)
    volumedivisor: Volume is divided by this before forming the box ratio (default 10000.0)
    Output: real"""

def kvo(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., volume: IntoExpr = ..., fastperiod: int = 34, slowperiod: int = 55, signalperiod: int = 13) -> Expr:
    """Klinger Volume Oscillator (Volume Indicators), TA-Lib KVO.
    
    fastperiod: Period of the faster smoothing of the volume force (default 34)
    slowperiod: Period of the slower smoothing of the volume force (default 55)
    signalperiod: Smoothing for the trigger line (default 13)
    Output struct: kvo, kvosignal"""

def marketfi(high: IntoExpr = ..., low: IntoExpr = ..., volume: IntoExpr = ...) -> Expr:
    """Market Facilitation Index (Volume Indicators), TA-Lib MARKETFI.
    
    Output: real"""

def nvi(close: IntoExpr = ..., volume: IntoExpr = ...) -> Expr:
    """Negative Volume Index (Volume Indicators), TA-Lib NVI.
    
    Output: real"""

def obv(real: IntoExpr = ..., volume: IntoExpr = ...) -> Expr:
    """On Balance Volume (Volume Indicators), TA-Lib OBV.
    
    Output: real"""

def pvi(close: IntoExpr = ..., volume: IntoExpr = ...) -> Expr:
    """Positive Volume Index (Volume Indicators), TA-Lib PVI.
    
    Output: real"""

def pvo(volume: IntoExpr = ..., fastperiod: int = 12, slowperiod: int = 26, matype: int = 1) -> Expr:
    """Percentage Volume Oscillator (Volume Indicators), TA-Lib PVO.
    
    fastperiod: Period of the fast MA (default 12)
    slowperiod: Period of the slow MA (default 26)
    matype: Type of Moving Average (default 1)
    Output: real"""

def pvt(close: IntoExpr = ..., volume: IntoExpr = ...) -> Expr:
    """Price Volume Trend (Volume Indicators), TA-Lib PVT.
    
    Output: real"""

def rvol(volume: IntoExpr = ..., timeperiod: int = 20) -> Expr:
    """Relative Volume (Volume Indicators), TA-Lib RVOL.
    
    timeperiod: Time period (default 20)
    Output: real"""

def vwap(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., volume: IntoExpr = ...) -> Expr:
    """Volume Weighted Average Price (Volume Indicators), TA-Lib VWAP.
    
    Output: real"""
