from polars import Expr
from polars._typing import IntoExpr

def beta(real0: IntoExpr = ..., real1: IntoExpr = ..., timeperiod: int = 5) -> Expr:
    """Beta (Statistic Functions), TA-Lib BETA.
    
    timeperiod: Time period (default 5)
    Output: real"""

def correl(real0: IntoExpr = ..., real1: IntoExpr = ..., timeperiod: int = 30) -> Expr:
    """Pearson's Correlation Coefficient (r) (Statistic Functions), TA-Lib CORREL.
    
    timeperiod: Time period (default 30)
    Output: real"""

def kurtosis(real: IntoExpr = ..., timeperiod: int = 30) -> Expr:
    """Rolling Excess Kurtosis (Statistic Functions), TA-Lib KURTOSIS.
    
    timeperiod: Time period (default 30)
    Output: real"""

def linearreg(real: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Linear Regression (Statistic Functions), TA-Lib LINEARREG.
    
    timeperiod: Time period (default 14)
    Output: real"""

def linearreg_angle(real: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Linear Regression Angle (Statistic Functions), TA-Lib LINEARREG_ANGLE.
    
    timeperiod: Time period (default 14)
    Output: real"""

def linearreg_intercept(real: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Linear Regression Intercept (Statistic Functions), TA-Lib LINEARREG_INTERCEPT.
    
    timeperiod: Time period (default 14)
    Output: real"""

def linearreg_slope(real: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Linear Regression Slope (Statistic Functions), TA-Lib LINEARREG_SLOPE.
    
    timeperiod: Time period (default 14)
    Output: real"""

def median(real: IntoExpr = ..., timeperiod: int = 30) -> Expr:
    """Rolling Median (Statistic Functions), TA-Lib MEDIAN.
    
    timeperiod: Number of bars in the window (default 30)
    Output: real"""

def percentile(real: IntoExpr = ..., timeperiod: int = 100, percentile: float = 50.0) -> Expr:
    """Percentile (nearest rank) (Statistic Functions), TA-Lib PERCENTILE.
    
    timeperiod: Number of bars in the window (default 100)
    percentile: Percentile to report (default 50.0)
    Output: real"""

def percentrank(real: IntoExpr = ..., timeperiod: int = 100) -> Expr:
    """Percent Rank (Statistic Functions), TA-Lib PERCENTRANK.
    
    timeperiod: Time period (default 100)
    Output: real"""

def stddev(real: IntoExpr = ..., timeperiod: int = 5, nbdev: float = 1.0) -> Expr:
    """Standard Deviation (Statistic Functions), TA-Lib STDDEV.
    
    timeperiod: Time period (default 5)
    nbdev: Nb of deviations (default 1.0)
    Output: real"""

def tsf(real: IntoExpr = ..., timeperiod: int = 14) -> Expr:
    """Time Series Forecast (Statistic Functions), TA-Lib TSF.
    
    timeperiod: Time period (default 14)
    Output: real"""

def var(real: IntoExpr = ..., timeperiod: int = 5, nbdev: float = 1.0) -> Expr:
    """Variance (Statistic Functions), TA-Lib VAR.
    
    timeperiod: Time period (default 5)
    nbdev: Nb of deviations (default 1.0)
    Output: real"""
