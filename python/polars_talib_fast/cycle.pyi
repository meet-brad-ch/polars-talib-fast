from polars import Expr
from polars._typing import IntoExpr

def ht_dcperiod(real: IntoExpr = ...) -> Expr:
    """Hilbert Transform - Dominant Cycle Period (Cycle Indicators), TA-Lib HT_DCPERIOD.
    
    Output: real"""

def ht_dcphase(real: IntoExpr = ...) -> Expr:
    """Hilbert Transform - Dominant Cycle Phase (Cycle Indicators), TA-Lib HT_DCPHASE.
    
    Output: real"""

def ht_phasor(real: IntoExpr = ...) -> Expr:
    """Hilbert Transform - Phasor Components (Cycle Indicators), TA-Lib HT_PHASOR.
    
    Output struct: inphase, quadrature"""

def ht_sine(real: IntoExpr = ...) -> Expr:
    """Hilbert Transform - SineWave (Cycle Indicators), TA-Lib HT_SINE.
    
    Output struct: sine, leadsine"""

def ht_trendmode(real: IntoExpr = ...) -> Expr:
    """Hilbert Transform - Trend vs Cycle Mode (Cycle Indicators), TA-Lib HT_TRENDMODE.
    
    Output: integer"""

def swak_2php(real: IntoExpr = ..., timeperiod: int = 20) -> Expr:
    """Swiss Army Knife - Two-Pole High-Pass Filter (Cycle Indicators), TA-Lib SWAK_2PHP.
    
    timeperiod: Cutoff period (default 20)
    Output: real"""

def swak_bp(real: IntoExpr = ..., timeperiod: int = 20, delta: float = 0.1) -> Expr:
    """Swiss Army Knife - Band-Pass Filter (Cycle Indicators), TA-Lib SWAK_BP.
    
    timeperiod: Center period (default 20)
    delta: Half-bandwidth as a fraction of the center period (default 0.1)
    Output: real"""

def swak_hp(real: IntoExpr = ..., timeperiod: int = 20) -> Expr:
    """Swiss Army Knife - High-Pass Filter (Cycle Indicators), TA-Lib SWAK_HP.
    
    timeperiod: Cutoff period (default 20)
    Output: real"""
