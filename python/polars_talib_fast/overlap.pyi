from polars import Expr
from polars._typing import IntoExpr

def accbands(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., timeperiod: int = 20) -> Expr:
    """Acceleration Bands (Overlap Studies), TA-Lib ACCBANDS.
    
    timeperiod: Time period (default 20)
    Output struct: upperband, middleband, lowerband"""

def alma(real: IntoExpr = ..., timeperiod: int = 9, sigma: float = 6.0, offset: float = 0.85) -> Expr:
    """Arnaud Legoux Moving Average (Overlap Studies), TA-Lib ALMA.
    
    timeperiod: Time period (default 9)
    sigma: Gaussian width divisor (default 6.0)
    offset: Position of the peak weight (default 0.85)
    Output: real"""

def bbands(real: IntoExpr = ..., timeperiod: int = 20, nbdevup: float = 2.0, nbdevdn: float = 2.0, matype: int = 0) -> Expr:
    """Bollinger Bands (Overlap Studies), TA-Lib BBANDS.
    
    timeperiod: Time period (default 20)
    nbdevup: Deviation multiplier for upper band (default 2.0)
    nbdevdn: Deviation multiplier for lower band (default 2.0)
    matype: Type of Moving Average (default 0)
    Output struct: upperband, middleband, lowerband"""

def cksp(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., timeperiod: int = 10, multiplier: float = 1.0, stopperiod: int = 9) -> Expr:
    """Chande Kroll Stop (Overlap Studies), TA-Lib CKSP.
    
    timeperiod: ATR and extreme window (default 10)
    multiplier: ATR multiplier (default 1.0)
    stopperiod: Stop window (default 9)
    Output struct: highstop, lowstop"""

def dema(real: IntoExpr = ..., timeperiod: int = 30) -> Expr:
    """Double Exponential Moving Average (Overlap Studies), TA-Lib DEMA.
    
    timeperiod: Time period (default 30)
    Output: real"""

def donchian(high: IntoExpr = ..., low: IntoExpr = ..., timeperiod: int = 20) -> Expr:
    """Donchian Channels (Overlap Studies), TA-Lib DONCHIAN.
    
    timeperiod: Time period (default 20)
    Output struct: upperband, middleband, lowerband"""

def ema(real: IntoExpr = ..., timeperiod: int = 30) -> Expr:
    """Exponential Moving Average (Overlap Studies), TA-Lib EMA.
    
    timeperiod: Time period (default 30)
    Output: real"""

def frama(high: IntoExpr = ..., low: IntoExpr = ..., timeperiod: int = 16) -> Expr:
    """Fractal Adaptive Moving Average (Overlap Studies), TA-Lib FRAMA.
    
    timeperiod: Number of bars, even; the window is split into two halves of optInTimePeriod/2 bars (default 16)
    Output: real"""

def hma(real: IntoExpr = ..., timeperiod: int = 20) -> Expr:
    """Hull Moving Average (Overlap Studies), TA-Lib HMA.
    
    timeperiod: Time period (default 20)
    Output: real"""

def ht_trendline(real: IntoExpr = ...) -> Expr:
    """Hilbert Transform - Instantaneous Trendline (Overlap Studies), TA-Lib HT_TRENDLINE.
    
    Output: real"""

def ichimoku(high: IntoExpr = ..., low: IntoExpr = ..., tenkanperiod: int = 9, kijunperiod: int = 26, senkoubperiod: int = 52) -> Expr:
    """Ichimoku Kinko Hyo (Overlap Studies), TA-Lib ICHIMOKU.
    
    tenkanperiod: Period of the conversion line (default 9)
    kijunperiod: Period of the base line, and the forward shift of the two spans (default 26)
    senkoubperiod: Period of the second leading span (default 52)
    Output struct: tenkansen, kijunsen, senkouspana, senkouspanb"""

def kama(real: IntoExpr = ..., timeperiod: int = 30) -> Expr:
    """Kaufman Adaptive Moving Average (Overlap Studies), TA-Lib KAMA.
    
    timeperiod: Time period (default 30)
    Output: real"""

def kc(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., timeperiod: int = 20, atrperiod: int = 10, nbdev: float = 2.0) -> Expr:
    """Keltner Channels (Overlap Studies), TA-Lib KC.
    
    timeperiod: Time period for the typical price moving average (default 20)
    atrperiod: Time period for the Average True Range (default 10)
    nbdev: Multiplier applied to the Average True Range (default 2.0)
    Output struct: upperband, middleband, lowerband"""

def ma(real: IntoExpr = ..., timeperiod: int = 30, matype: int = 0) -> Expr:
    """Moving average (Overlap Studies), TA-Lib MA.
    
    timeperiod: Time period (default 30)
    matype: Type of Moving Average (default 0)
    Output: real"""

def mama(real: IntoExpr = ..., fastlimit: float = 0.5, slowlimit: float = 0.05) -> Expr:
    """MESA Adaptive Moving Average (Overlap Studies), TA-Lib MAMA.
    
    fastlimit: Upper limit use in the adaptive algorithm (default 0.5)
    slowlimit: Lower limit use in the adaptive algorithm (default 0.05)
    Output struct: mama, fama"""

def mavp(real: IntoExpr = ..., periods: IntoExpr = ..., minperiod: int = 2, maxperiod: int = 30, matype: int = 0) -> Expr:
    """Moving average with variable period (Overlap Studies), TA-Lib MAVP.
    
    minperiod: Value less than minimum will be changed to Minimum period (default 2)
    maxperiod: Value higher than maximum will be changed to Maximum period (default 30)
    matype: Type of Moving Average (default 0)
    Output: real"""

def mcgd(real: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """McGinley Dynamic (Overlap Studies), TA-Lib MCGD.
    
    timeperiod: Time period (default 14)
    Output: real"""

def midpoint(real: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """MidPoint over period (Overlap Studies), TA-Lib MIDPOINT.
    
    timeperiod: Time period (default 14)
    Output: real"""

def midprice(high: IntoExpr = ..., low: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Midpoint Price over period (Overlap Studies), TA-Lib MIDPRICE.
    
    timeperiod: Time period (default 14)
    Output: real"""

def rma(real: IntoExpr = ..., timeperiod: int = 30) -> Expr:
    """Wilder's Smoothed Moving Average (Overlap Studies), TA-Lib RMA.
    
    timeperiod: Time period (default 30)
    Output: real"""

def sar(high: IntoExpr = ..., low: IntoExpr = ..., acceleration: float = 0.02, maximum: float = 0.2) -> Expr:
    """Parabolic SAR (Overlap Studies), TA-Lib SAR.
    
    acceleration: Acceleration Factor used up to the Maximum value (default 0.02)
    maximum: Acceleration Factor Maximum value (default 0.2)
    Output: real"""

def sarext(high: IntoExpr = ..., low: IntoExpr = ..., startvalue: float = 0.0, offsetonreverse: float = 0.0, accelerationinitlong: float = 0.02, accelerationlong: float = 0.02, accelerationmaxlong: float = 0.2, accelerationinitshort: float = 0.02, accelerationshort: float = 0.02, accelerationmaxshort: float = 0.2) -> Expr:
    """Parabolic SAR - Extended (Overlap Studies), TA-Lib SAREXT.
    
    startvalue: Start value and direction. 0 for Auto, >0 for Long, <0 for Short (default 0.0)
    offsetonreverse: Percent offset added/removed to initial stop on short/long reversal (default 0.0)
    accelerationinitlong: Acceleration Factor initial value for the Long direction (default 0.02)
    accelerationlong: Acceleration Factor for the Long direction (default 0.02)
    accelerationmaxlong: Acceleration Factor maximum value for the Long direction (default 0.2)
    accelerationinitshort: Acceleration Factor initial value for the Short direction (default 0.02)
    accelerationshort: Acceleration Factor for the Short direction (default 0.02)
    accelerationmaxshort: Acceleration Factor maximum value for the Short direction (default 0.2)
    Output: real"""

def sma(real: IntoExpr = ..., timeperiod: int = 30) -> Expr:
    """Simple Moving Average (Overlap Studies), TA-Lib SMA.
    
    timeperiod: Time period (default 30)
    Output: real"""

def supertrend(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., timeperiod: int = 10, multiplier: float = 3.0) -> Expr:
    """SuperTrend (Overlap Studies), TA-Lib SUPERTREND.
    
    timeperiod: Time period for the Average True Range (default 10)
    multiplier: ATR multiplier for band width (default 3.0)
    Output struct: supertrend, trend"""

def swak_butter(real: IntoExpr = ..., timeperiod: int = 20) -> Expr:
    """Swiss Army Knife - Butterworth Filter (Overlap Studies), TA-Lib SWAK_BUTTER.
    
    timeperiod: Cutoff period (default 20)
    Output: real"""

def swak_gauss(real: IntoExpr = ..., timeperiod: int = 20) -> Expr:
    """Swiss Army Knife - Gaussian Filter (Overlap Studies), TA-Lib SWAK_GAUSS.
    
    timeperiod: Cutoff period (default 20)
    Output: real"""

def t3(real: IntoExpr = ..., timeperiod: int = 5, vfactor: float = 0.7) -> Expr:
    """Triple Exponential Moving Average (T3) (Overlap Studies), TA-Lib T3.
    
    timeperiod: Time period (default 5)
    vfactor: Volume Factor (default 0.7)
    Output: real"""

def tema(real: IntoExpr = ..., timeperiod: int = 30) -> Expr:
    """Triple Exponential Moving Average (Overlap Studies), TA-Lib TEMA.
    
    timeperiod: Time period (default 30)
    Output: real"""

def trima(real: IntoExpr = ..., timeperiod: int = 30) -> Expr:
    """Triangular Moving Average (Overlap Studies), TA-Lib TRIMA.
    
    timeperiod: Time period (default 30)
    Output: real"""

def vidya(real: IntoExpr = ..., timeperiod: int = 12, cmoperiod: int = 9) -> Expr:
    """Variable Index Dynamic Average (Overlap Studies), TA-Lib VIDYA.
    
    timeperiod: EMA-equivalent smoothing period, alpha = 2/(n+1) (default 12)
    cmoperiod: Period of the unsmoothed CMO that scales alpha (default 9)
    Output: real"""

def vwma(real: IntoExpr = ..., volume: IntoExpr = ..., timeperiod: int = 30) -> Expr:
    """Volume Weighted Moving Average (Overlap Studies), TA-Lib VWMA.
    
    timeperiod: Time period (default 30)
    Output: real"""

def wma(real: IntoExpr = ..., timeperiod: int = 30) -> Expr:
    """Weighted Moving Average (Overlap Studies), TA-Lib WMA.
    
    timeperiod: Time period (default 30)
    Output: real"""

def zigzag(high: IntoExpr = ..., low: IntoExpr = ..., sensitivity: float = 5.0, mintrendlength: int = 1) -> Expr:
    """Zig Zag (Overlap Studies), TA-Lib ZIGZAG.
    
    sensitivity: Minimum move away from the current extreme that reverses the leg, in percent (default 5.0)
    mintrendlength: Minimum number of bars between two pivots (default 1)
    Output struct: zigzag, trend, pivotidx"""

def zlema(real: IntoExpr = ..., timeperiod: int = 30) -> Expr:
    """Zero-Lag Exponential Moving Average (Overlap Studies), TA-Lib ZLEMA.
    
    timeperiod: Time period (default 30)
    Output: real"""
