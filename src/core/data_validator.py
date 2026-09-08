import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    is_valid: bool = False
    exchange: str = "NSE"
    symbol: str = ""
    expiry: str = ""
    atm_strike: float = 0.0
    strike_range: Tuple[float, float] = (0, 0)
    num_strikes: int = 0
    missing_columns: List[str] = field(default_factory=list)
    duplicate_strikes: bool = False
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class DataValidator:
    """Validates Option Chain data quality and completeness"""
    
    REQUIRED_COLUMNS = ['STRIKE PRICE', 'OI_x', 'OI_y']
    
    def __init__(self):
        self.df = None
        self.file_name = None
        self.validation_result = ValidationResult()
    
    def validate(self, df: pd.DataFrame) -> ValidationResult:
        """Perform comprehensive validation"""
        self.df = df
        result = ValidationResult()
        
        # Extract symbol from file name
        if self.file_name:
            if 'NIFTY' in self.file_name.upper() and 'BANK' not in self.file_name.upper():
                result.symbol = 'NIFTY'
            elif 'BANKNIFTY' in self.file_name.upper():
                result.symbol = 'BANKNIFTY'
            elif 'SENSEX' in self.file_name.upper():
                result.symbol = 'SENSEX'
                result.exchange = 'BSE'
            else:
                result.symbol = 'UNKNOWN'
        
        # Check required columns
        result.missing_columns = self._check_required_columns(df)
        if result.missing_columns:
            result.errors.append(f"Missing columns: {result.missing_columns}")
        
        # Check duplicate strikes
        strikes = df['STRIKE PRICE']
        result.duplicate_strikes = strikes.duplicated().any()
        if result.duplicate_strikes:
            result.warnings.append("Duplicate strike prices found")
        
        # Get strike range
        result.strike_range = (strikes.min(), strikes.max())
        
        # Count strikes
        result.num_strikes = len(strikes)
        
        # Check for missing/invalid values
        result.warnings.extend(self._check_missing_values(df))
        
        # Identify ATM strike
        result.atm_strike = self._find_atm_strike(df)
        
        # Validate OI data
        if 'OI_x' in df.columns and 'OI_y' in df.columns:
            ce_oi = df['OI_x'].fillna(0)
            pe_oi = df['OI_y'].fillna(0)
            if ce_oi.sum() == 0 and pe_oi.sum() == 0:
                result.warnings.append("All OI values are zero")
        
        result.is_valid = len(result.errors) == 0
        self.validation_result = result
        return result
    
    def _check_required_columns(self, df: pd.DataFrame) -> List[str]:
        """Check if all required columns exist"""
        missing = []
        for col in self.REQUIRED_COLUMNS:
            if col not in df.columns:
                # Try to find alternative
                found = False
                for existing_col in df.columns:
                    if col.split('_')[0] in existing_col:
                        found = True
                        break
                if not found:
                    missing.append(col)
        return missing
    
    def _check_missing_values(self, df: pd.DataFrame) -> List[str]:
        """Check for high percentage of missing values"""
        warnings = []
        for col in ['OI_x', 'OI_y', 'VOLUME_x', 'VOLUME_y']:
            if col in df.columns:
                missing_pct = df[col].isna().mean() * 100
                if missing_pct > 50:
                    warnings.append(f"High missing values in {col}: {missing_pct:.1f}%")
        return warnings
    
    def _find_atm_strike(self, df: pd.DataFrame) -> float:
        """Find ATM strike using highest OI concentration"""
        try:
            ce_oi = df.get('OI_x', pd.Series([0]*len(df))).fillna(0)
            pe_oi = df.get('OI_y', pd.Series([0]*len(df))).fillna(0)
            total_oi = ce_oi + pe_oi
            max_oi_idx = total_oi.idxmax()
            return df.loc[max_oi_idx, 'STRIKE PRICE']
        except:
            return df['STRIKE PRICE'].iloc[len(df)//2] if len(df) > 0 else 0.0