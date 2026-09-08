"""
Option Chain data models
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime
import pandas as pd


@dataclass
class OptionData:
    """Individual option data"""
    oi: float = 0
    change_in_oi: float = 0
    volume: float = 0
    iv: float = 0
    ltp: float = 0
    change: float = 0
    bid: float = 0
    ask: float = 0
    bid_qty: float = 0
    ask_qty: float = 0


@dataclass
class Strike:
    """Strike price data"""
    strike_price: float
    ce: OptionData = field(default_factory=OptionData)
    pe: OptionData = field(default_factory=OptionData)
    
    @property
    def total_oi(self) -> float:
        return self.ce.oi + self.pe.oi
    
    @property
    def total_volume(self) -> float:
        return self.ce.volume + self.pe.volume
    
    @property
    def oi_pcr(self) -> float:
        if self.ce.oi == 0:
            return 0
        return self.pe.oi / self.ce.oi


@dataclass
class OptionChain:
    """Complete option chain data"""
    exchange: str = "NSE"
    symbol: str = ""
    expiry: str = ""
    atm_strike: float = 0
    strikes: List[Strike] = field(default_factory=list)
    spot_price: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert to DataFrame"""
        data = []
        for strike in self.strikes:
            data.append({
                'STRIKE': strike.strike_price,
                'CE_OI': strike.ce.oi,
                'CE_CHNG_OI': strike.ce.change_in_oi,
                'CE_VOLUME': strike.ce.volume,
                'CE_IV': strike.ce.iv,
                'CE_LTP': strike.ce.ltp,
                'CE_CHNG': strike.ce.change,
                'CE_BID': strike.ce.bid,
                'CE_ASK': strike.ce.ask,
                'PE_OI': strike.pe.oi,
                'PE_CHNG_OI': strike.pe.change_in_oi,
                'PE_VOLUME': strike.pe.volume,
                'PE_IV': strike.pe.iv,
                'PE_LTP': strike.pe.ltp,
                'PE_CHNG': strike.pe.change,
                'PE_BID': strike.pe.bid,
                'PE_ASK': strike.pe.ask,
            })
        return pd.DataFrame(data)
    
    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, **kwargs) -> 'OptionChain':
        """Create OptionChain from DataFrame"""
        chain = cls(**kwargs)
        
        for _, row in df.iterrows():
            strike = Strike(
                strike_price=float(row['STRIKE PRICE']),
                ce=OptionData(
                    oi=row.get('OI_x', 0),
                    change_in_oi=row.get('CHNG_IN_OI_x', 0),
                    volume=row.get('VOLUME_x', 0),
                    iv=row.get('IV_x', 0),
                    ltp=row.get('LTP_x', 0),
                    change=row.get('CHNG_x', 0),
                    bid=row.get('BID_x', 0),
                    ask=row.get('ASK_x', 0),
                    bid_qty=row.get('BID_QTY_x', 0),
                    ask_qty=row.get('ASK_QTY_x', 0)
                ),
                pe=OptionData(
                    oi=row.get('OI_y', 0),
                    change_in_oi=row.get('CHNG_IN_OI_y', 0),
                    volume=row.get('VOLUME_y', 0),
                    iv=row.get('IV_y', 0),
                    ltp=row.get('LTP_y', 0),
                    change=row.get('CHNG_y', 0),
                    bid=row.get('BID_y', 0),
                    ask=row.get('ASK_y', 0),
                    bid_qty=row.get('BID_QTY_y', 0),
                    ask_qty=row.get('ASK_QTY_y', 0)
                )
            )
            chain.strikes.append(strike)
        
        return chain