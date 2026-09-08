"""
Strike data models
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class OptionSide(Enum):
    """Option side enum"""
    CALL = "CALL"
    PUT = "PUT"


@dataclass
class StrikeData:
    """Strike data container"""
    strike: float
    side: OptionSide
    
    # OI Data
    oi: float = 0
    change_in_oi: float = 0
    volume: float = 0
    
    # Price Data
    ltp: float = 0
    change: float = 0
    iv: float = 0
    
    # Quote Data
    bid: float = 0
    ask: float = 0
    bid_qty: float = 0
    ask_qty: float = 0
    
    @property
    def is_call(self) -> bool:
        return self.side == OptionSide.CALL
    
    @property
    def is_put(self) -> bool:
        return self.side == OptionSide.PUT
    
    @property
    def spread(self) -> float:
        return self.ask - self.bid if self.ask > 0 and self.bid > 0 else 0
    
    @property
    def mid_price(self) -> float:
        return (self.bid + self.ask) / 2 if self.ask > 0 and self.bid > 0 else self.ltp


@dataclass
class StrikePair:
    """Call and Put data for a strike"""
    strike: float
    call: Optional[StrikeData] = None
    put: Optional[StrikeData] = None
    
    @property
    def total_oi(self) -> float:
        return (self.call.oi if self.call else 0) + (self.put.oi if self.put else 0)
    
    @property
    def total_volume(self) -> float:
        return (self.call.volume if self.call else 0) + (self.put.volume if self.put else 0)
    
    @property
    def oi_pcr(self) -> float:
        call_oi = self.call.oi if self.call else 0
        put_oi = self.put.oi if self.put else 0
        return put_oi / call_oi if call_oi > 0 else 0
    
    @property
    def volume_pcr(self) -> float:
        call_vol = self.call.volume if self.call else 0
        put_vol = self.put.volume if self.put else 0
        return put_vol / call_vol if call_vol > 0 else 0