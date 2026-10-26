from polars import Expr
from polars._typing import IntoExpr

def ac(high: IntoExpr = ..., low: IntoExpr = ..., fastperiod: int = 5, slowperiod: int = 34, signalperiod: int = 5) -> Expr:
    """Accelerator/Decelerator Oscillator (Momentum Indicators), TA-Lib AC.
    
    fastperiod: Period of the fast MA (default 5)
    slowperiod: Period of the slow MA (default 34)
    signalperiod: Smoothing for the signal line (period length) (default 5)
    Output: real"""

def adx(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Average Directional Movement Index (Momentum Indicators), TA-Lib ADX.
    
    timeperiod: Time period (default 14)
    Output: real"""

def adxr(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Average Directional Movement Index Rating (Momentum Indicators), TA-Lib ADXR.
    
    timeperiod: Time period (default 14)
    Output: real"""

def ao(high: IntoExpr = ..., low: IntoExpr = ..., fastperiod: int = 5, slowperiod: int = 34) -> Expr:
    """Awesome Oscillator (Momentum Indicators), TA-Lib AO.
    
    fastperiod: Period of the fast MA (default 5)
    slowperiod: Period of the slow MA (default 34)
    Output: real"""

def apo(real: IntoExpr = ..., fastperiod: int = 12, slowperiod: int = 26, matype: int = 1) -> Expr:
    """Absolute Price Oscillator (Momentum Indicators), TA-Lib APO.
    
    fastperiod: Period of the fast MA (default 12)
    slowperiod: Period of the slow MA (default 26)
    matype: Type of Moving Average (default 1)
    Output: real"""

def aroon(high: IntoExpr = ..., low: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Aroon (Momentum Indicators), TA-Lib AROON.
    
    timeperiod: Time period (default 14)
    Output struct: aroondown, aroonup"""

def aroonosc(high: IntoExpr = ..., low: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Aroon Oscillator (Momentum Indicators), TA-Lib AROONOSC.
    
    timeperiod: Time period (default 14)
    Output: real"""

def asi(open: IntoExpr = ..., high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., limitmove: float = 3.0) -> Expr:
    """Wilder Accumulative Swing Index (Momentum Indicators), TA-Lib ASI.
    
    limitmove: Largest one-bar price move the index is scaled against, in price units (default 3.0)
    Output: real"""

def bop(open: IntoExpr = ..., high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ...) -> Expr:
    """Balance Of Power (Momentum Indicators), TA-Lib BOP.
    
    Output: real"""

def cci(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Commodity Channel Index (Momentum Indicators), TA-Lib CCI.
    
    timeperiod: Time period (default 14)
    Output: real"""

def cg(real: IntoExpr = ..., timeperiod: int = 10) -> Expr:
    """Center of Gravity Oscillator (Momentum Indicators), TA-Lib CG.
    
    timeperiod: Number of bars in the window (default 10)
    Output: real"""

def chop(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Choppiness Index (Momentum Indicators), TA-Lib CHOP.
    
    timeperiod: Time period (default 14)
    Output: real"""

def choptr(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Choppiness Index (True Range Box) (Momentum Indicators), TA-Lib CHOPTR.
    
    timeperiod: Time period (default 14)
    Output: real"""

def cmo(real: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Chande Momentum Oscillator (Momentum Indicators), TA-Lib CMO.
    
    timeperiod: Time period (default 14)
    Output: real"""

def cmou(real: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Chande Momentum Oscillator (Unsmoothed) (Momentum Indicators), TA-Lib CMOU.
    
    timeperiod: Time period (default 14)
    Output: real"""

def coppock(real: IntoExpr = ..., wmaperiod: int = 10, roc1period: int = 11, roc2period: int = 14) -> Expr:
    """Coppock Curve (Momentum Indicators), TA-Lib COPPOCK.
    
    wmaperiod: Smoothing period for the ROC sum (default 10)
    roc1period: Short rate-of-change period (default 11)
    roc2period: Long rate-of-change period (default 14)
    Output: real"""

def crsi(real: IntoExpr = ..., timeperiod: int = 3, streakperiod: int = 2, rankperiod: int = 100) -> Expr:
    """Connors Relative Strength Index (Momentum Indicators), TA-Lib CRSI.
    
    timeperiod: Time period (default 3)
    streakperiod: Time period of the RSI of the up/down streak (default 2)
    rankperiod: Number of previous one-bar returns the current one is ranked against (default 100)
    Output: real"""

def cti(real: IntoExpr = ..., timeperiod: int = 20) -> Expr:
    """Correlation Trend Indicator (Momentum Indicators), TA-Lib CTI.
    
    timeperiod: Number of bars correlated against the ramp (default 20)
    Output: real"""

def dosc(real: IntoExpr = ..., timeperiod: int = 14, firstperiod: int = 5, secondperiod: int = 3, signalperiod: int = 9) -> Expr:
    """Derivative Oscillator (Momentum Indicators), TA-Lib DOSC.
    
    timeperiod: Period of the RSI (default 14)
    firstperiod: Period of the first smoothing, applied to the RSI (default 5)
    secondperiod: Period of the second smoothing, applied to the first (default 3)
    signalperiod: Period of the simple average subtracted from the smoothed line (default 9)
    Output: real"""

def dpo(real: IntoExpr = ..., timeperiod: int = 20) -> Expr:
    """Detrended Price Oscillator (Momentum Indicators), TA-Lib DPO.
    
    timeperiod: Time period (default 20)
    Output: real"""

def dx(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Directional Movement Index (Momentum Indicators), TA-Lib DX.
    
    timeperiod: Time period (default 14)
    Output: real"""

def er(real: IntoExpr = ..., timeperiod: int = 10) -> Expr:
    """Kaufman Efficiency Ratio (Momentum Indicators), TA-Lib ER.
    
    timeperiod: Number of one-bar changes in the path sum (default 10)
    Output: real"""

def eri(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., timeperiod: int = 13) -> Expr:
    """Elder Ray Index (Bull Power / Bear Power) (Momentum Indicators), TA-Lib ERI.
    
    timeperiod: Number of bars in the EMA of close (default 13)
    Output struct: bullpower, bearpower"""

def fisher(high: IntoExpr = ..., low: IntoExpr = ..., timeperiod: int = 10) -> Expr:
    """Fisher Transform (Momentum Indicators), TA-Lib FISHER.
    
    timeperiod: Time period (default 10)
    Output struct: fisher, trigger"""

def fosc(real: IntoExpr = ..., timeperiod: int = 5) -> Expr:
    """Forecast Oscillator (Momentum Indicators), TA-Lib FOSC.
    
    timeperiod: Time period (default 5)
    Output: real"""

def fractal(high: IntoExpr = ..., low: IntoExpr = ..., leftbars: int = 2, rightbars: int = 2) -> Expr:
    """Williams Fractal (Momentum Indicators), TA-Lib FRACTAL.
    
    leftbars: Number of bars required to be lower/higher before the pivot (default 2)
    rightbars: Number of bars required to be lower/higher after the pivot (default 2)
    Output struct: swinghigh, swinglow"""

def ibs(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ...) -> Expr:
    """Internal Bar Strength (Momentum Indicators), TA-Lib IBS.
    
    Output: real"""

def imi(open: IntoExpr = ..., close: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Intraday Momentum Index (Momentum Indicators), TA-Lib IMI.
    
    timeperiod: Time period (default 14)
    Output: real"""

def kdj(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., fastk_period: int = 9, slowk_period: int = 3, slowk_matype: int = 13, slowd_period: int = 3, slowd_matype: int = 13) -> Expr:
    """KDJ Stochastic (Momentum Indicators), TA-Lib KDJ.
    
    fastk_period: Time period for building the Fast-K line (default 9)
    slowk_period: Smoothing for making the Slow-K line. Usually set to 3 (default 3)
    slowk_matype: Type of Moving Average for Slow-K (default 13)
    slowd_period: Smoothing for making the Slow-D line (default 3)
    slowd_matype: Type of Moving Average for Slow-D (default 13)
    Output struct: k, d, j"""

def kst(real: IntoExpr = ..., roc1period: int = 10, roc2period: int = 15, roc3period: int = 20, roc4period: int = 30, sma1period: int = 10, sma2period: int = 10, sma3period: int = 10, sma4period: int = 15, signalperiod: int = 9) -> Expr:
    """Know Sure Thing (Pring) (Momentum Indicators), TA-Lib KST.
    
    roc1period: Rate-of-change period of leg 1 (default 10)
    roc2period: Rate-of-change period of leg 2 (default 15)
    roc3period: Rate-of-change period of leg 3 (default 20)
    roc4period: Rate-of-change period of leg 4 (default 30)
    sma1period: Smoothing period of leg 1 (default 10)
    sma2period: Smoothing period of leg 2 (default 10)
    sma3period: Smoothing period of leg 3 (default 10)
    sma4period: Smoothing period of leg 4 (default 15)
    signalperiod: Smoothing period of the signal line (default 9)
    Output struct: kst, kstsignal"""

def kstext(real: IntoExpr = ..., roc1period: int = 10, roc2period: int = 15, roc3period: int = 20, roc4period: int = 30, ma1period: int = 10, ma2period: int = 10, ma3period: int = 10, ma4period: int = 15, signalperiod: int = 9, rocmatype: int = 0, signalmatype: int = 0) -> Expr:
    """Know Sure Thing with controllable MA type (Momentum Indicators), TA-Lib KSTEXT.
    
    roc1period: Rate-of-change period of leg 1 (default 10)
    roc2period: Rate-of-change period of leg 2 (default 15)
    roc3period: Rate-of-change period of leg 3 (default 20)
    roc4period: Rate-of-change period of leg 4 (default 30)
    ma1period: Smoothing period of leg 1 (default 10)
    ma2period: Smoothing period of leg 2 (default 10)
    ma3period: Smoothing period of leg 3 (default 10)
    ma4period: Smoothing period of leg 4 (default 15)
    signalperiod: Smoothing period of the signal line (default 9)
    rocmatype: Type of Moving Average smoothing the four legs (default 0)
    signalmatype: Type of Moving Average for signal line (default 0)
    Output struct: kst, kstsignal"""

def macd(real: IntoExpr = ..., fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> Expr:
    """Moving Average Convergence/Divergence (Momentum Indicators), TA-Lib MACD.
    
    fastperiod: Period of the fast MA (default 12)
    slowperiod: Period of the slow MA (default 26)
    signalperiod: Smoothing for the signal line (period length) (default 9)
    Output struct: macd, macdsignal, macdhist"""

def macdext(real: IntoExpr = ..., fastperiod: int = 12, fastmatype: int = 0, slowperiod: int = 26, slowmatype: int = 0, signalperiod: int = 9, signalmatype: int = 0) -> Expr:
    """MACD with controllable MA type (Momentum Indicators), TA-Lib MACDEXT.
    
    fastperiod: Period of the fast MA (default 12)
    fastmatype: Type of Moving Average for fast MA (default 0)
    slowperiod: Period of the slow MA (default 26)
    slowmatype: Type of Moving Average for slow MA (default 0)
    signalperiod: Smoothing for the signal line (period length) (default 9)
    signalmatype: Type of Moving Average for signal line (default 0)
    Output struct: macd, macdsignal, macdhist"""

def macdfix(real: IntoExpr = ..., signalperiod: int = 9) -> Expr:
    """Moving Average Convergence/Divergence Fix 12/26 (Momentum Indicators), TA-Lib MACDFIX.
    
    signalperiod: Smoothing for the signal line (period length) (default 9)
    Output struct: macd, macdsignal, macdhist"""

def mfi(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., volume: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Money Flow Index (Momentum Indicators), TA-Lib MFI.
    
    timeperiod: Time period (default 14)
    Output: real"""

def minus_di(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Minus Directional Indicator (Momentum Indicators), TA-Lib MINUS_DI.
    
    timeperiod: Time period (default 14)
    Output: real"""

def minus_dm(high: IntoExpr = ..., low: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Minus Directional Movement (Momentum Indicators), TA-Lib MINUS_DM.
    
    timeperiod: Time period (default 14)
    Output: real"""

def mom(real: IntoExpr = ..., timeperiod: int = 10) -> Expr:
    """Momentum (Momentum Indicators), TA-Lib MOM.
    
    timeperiod: Time period (default 10)
    Output: real"""

def plus_di(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Plus Directional Indicator (Momentum Indicators), TA-Lib PLUS_DI.
    
    timeperiod: Time period (default 14)
    Output: real"""

def plus_dm(high: IntoExpr = ..., low: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Plus Directional Movement (Momentum Indicators), TA-Lib PLUS_DM.
    
    timeperiod: Time period (default 14)
    Output: real"""

def ppo(real: IntoExpr = ..., fastperiod: int = 12, slowperiod: int = 26, matype: int = 1) -> Expr:
    """Percentage Price Oscillator (Momentum Indicators), TA-Lib PPO.
    
    fastperiod: Period of the fast MA (default 12)
    slowperiod: Period of the slow MA (default 26)
    matype: Type of Moving Average (default 1)
    Output: real"""

def pso(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., fastk_period: int = 8, emaperiod: int = 5) -> Expr:
    """Premier Stochastic Oscillator (Momentum Indicators), TA-Lib PSO.
    
    fastk_period: Time period for building the Fast-K line (default 8)
    emaperiod: Period of each of the two smoothing passes (default 5)
    Output: real"""

def qstick(open: IntoExpr = ..., close: IntoExpr = ..., timeperiod: int = 10) -> Expr:
    """Qstick (Momentum Indicators), TA-Lib QSTICK.
    
    timeperiod: Time period (default 10)
    Output: real"""

def roc(real: IntoExpr = ..., timeperiod: int = 10) -> Expr:
    """Rate of change : ((price/prevPrice)-1)*100 (Momentum Indicators), TA-Lib ROC.
    
    timeperiod: Time period (default 10)
    Output: real"""

def rocp(real: IntoExpr = ..., timeperiod: int = 10) -> Expr:
    """Rate of change Percentage: (price-prevPrice)/prevPrice (Momentum Indicators), TA-Lib ROCP.
    
    timeperiod: Time period (default 10)
    Output: real"""

def rocr(real: IntoExpr = ..., timeperiod: int = 10) -> Expr:
    """Rate of change ratio: (price/prevPrice) (Momentum Indicators), TA-Lib ROCR.
    
    timeperiod: Time period (default 10)
    Output: real"""

def rocr100(real: IntoExpr = ..., timeperiod: int = 10) -> Expr:
    """Rate of change ratio 100 scale: (price/prevPrice)*100 (Momentum Indicators), TA-Lib ROCR100.
    
    timeperiod: Time period (default 10)
    Output: real"""

def rsi(real: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Relative Strength Index (Momentum Indicators), TA-Lib RSI.
    
    timeperiod: Time period (default 14)
    Output: real"""

def si(open: IntoExpr = ..., high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., limitmove: float = 3.0) -> Expr:
    """Wilder Swing Index (Momentum Indicators), TA-Lib SI.
    
    limitmove: Largest one-bar price move the index is scaled against, in price units (default 3.0)
    Output: real"""

def smi(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., timeperiod: int = 13, fastperiod: int = 2, slowperiod: int = 25, signalperiod: int = 9) -> Expr:
    """Stochastic Momentum Index (Momentum Indicators), TA-Lib SMI.
    
    timeperiod: Period of the high/low range (default 13)
    fastperiod: Period of the second smoothing, applied to the first (default 2)
    slowperiod: Period of the first smoothing, applied to the raw momentum (default 25)
    signalperiod: Smoothing for the signal line (period length) (default 9)
    Output struct: smi, smisignal"""

def sqzmom(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., bbperiod: int = 20, nbdev: float = 2.0, kcperiod: int = 20, factorwide: float = 2.0, factornormal: float = 1.5, factornarrow: float = 1.0) -> Expr:
    """Squeeze Momentum and Level (Momentum Indicators), TA-Lib SQZMOM.
    
    bbperiod: Period of the Bollinger Bands (default 20)
    nbdev: Deviation multiplier for both Bollinger Bands (default 2.0)
    kcperiod: Period of the Keltner Channel, and of the momentum regression (default 20)
    factorwide: Keltner width for the widest compression test (default 2.0)
    factornormal: Keltner width for the classic squeeze test (default 1.5)
    factornarrow: Keltner width for the tightest compression test (default 1.0)
    Output struct: momentum, squeeze"""

def stc(real: IntoExpr = ..., fastperiod: int = 23, slowperiod: int = 50, cycleperiod: int = 10) -> Expr:
    """Schaff Trend Cycle (Momentum Indicators), TA-Lib STC.
    
    fastperiod: Period of the fast EMA (default 23)
    slowperiod: Period of the slow EMA (default 50)
    cycleperiod: Window of both stochastic stages (default 10)
    Output: real"""

def stoch(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., fastk_period: int = 5, slowk_period: int = 3, slowk_matype: int = 0, slowd_period: int = 3, slowd_matype: int = 0) -> Expr:
    """Stochastic (Momentum Indicators), TA-Lib STOCH.
    
    fastk_period: Time period for building the Fast-K line (default 5)
    slowk_period: Smoothing for making the Slow-K line. Usually set to 3 (default 3)
    slowk_matype: Type of Moving Average for Slow-K (default 0)
    slowd_period: Smoothing for making the Slow-D line (default 3)
    slowd_matype: Type of Moving Average for Slow-D (default 0)
    Output struct: slowk, slowd"""

def stochf(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., fastk_period: int = 5, fastd_period: int = 3, fastd_matype: int = 0) -> Expr:
    """Stochastic Fast (Momentum Indicators), TA-Lib STOCHF.
    
    fastk_period: Time period for building the Fast-K line (default 5)
    fastd_period: Smoothing for making the Fast-D line. Usually set to 3 (default 3)
    fastd_matype: Type of Moving Average for Fast-D (default 0)
    Output struct: fastk, fastd"""

def stochrsi(real: IntoExpr = ..., timeperiod: int = 14, fastk_period: int = 5, fastd_period: int = 3, fastd_matype: int = 0) -> Expr:
    """Stochastic Relative Strength Index (Momentum Indicators), TA-Lib STOCHRSI.
    
    timeperiod: Time period (default 14)
    fastk_period: Time period for building the Fast-K line (default 5)
    fastd_period: Smoothing for making the Fast-D line. Usually set to 3 (default 3)
    fastd_matype: Type of Moving Average for Fast-D (default 0)
    Output struct: fastk, fastd"""

def trix(real: IntoExpr = ..., timeperiod: int = 30) -> Expr:
    """1-day Rate-Of-Change (ROC) of a Triple Smooth EMA (Momentum Indicators), TA-Lib TRIX.
    
    timeperiod: Time period (default 30)
    Output: real"""

def tsi(real: IntoExpr = ..., firstperiod: int = 25, secondperiod: int = 13) -> Expr:
    """True Strength Index (Momentum Indicators), TA-Lib TSI.
    
    firstperiod: Period of the first smoothing, applied to the raw momentum (default 25)
    secondperiod: Period of the second smoothing, applied to the first (default 13)
    Output: real"""

def ultosc(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., timeperiod1: int = 7, timeperiod2: int = 14, timeperiod3: int = 28) -> Expr:
    """Ultimate Oscillator (Momentum Indicators), TA-Lib ULTOSC.
    
    timeperiod1: Number of bars for 1st period. (default 7)
    timeperiod2: Number of bars fro 2nd period (default 14)
    timeperiod3: Number of bars for 3rd period (default 28)
    Output: real"""

def vhf(real: IntoExpr = ..., timeperiod: int = 28) -> Expr:
    """Vertical Horizontal Filter (Momentum Indicators), TA-Lib VHF.
    
    timeperiod: Time period (default 28)
    Output: real"""

def vortex(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Vortex Indicator (Momentum Indicators), TA-Lib VORTEX.
    
    timeperiod: Number of bars in the rolling sums (default 14)
    Output struct: plusvi, minusvi"""

def wad(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ...) -> Expr:
    """Williams' Accumulation/Distribution (Momentum Indicators), TA-Lib WAD.
    
    Output: real"""

def wavetrend(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., channelperiod: int = 10, averageperiod: int = 21, signalperiod: int = 4) -> Expr:
    """WaveTrend Oscillator (Momentum Indicators), TA-Lib WAVETREND.
    
    channelperiod: Period of the price channel, used by both the average and the deviation (default 10)
    averageperiod: Smoothing for the oscillator line (default 21)
    signalperiod: Simple average of the oscillator line, making the signal line (default 4)
    Output struct: wt1, wt2"""

def willr(high: IntoExpr = ..., low: IntoExpr = ..., close: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Williams' %R (Momentum Indicators), TA-Lib WILLR.
    
    timeperiod: Time period (default 14)
    Output: real"""
