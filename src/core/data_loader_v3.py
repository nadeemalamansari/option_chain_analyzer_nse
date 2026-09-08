import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Dict
import logging
import re

logger = logging.getLogger(__name__)


class DataLoader:
    """Fixed DataLoader for Option Chain CSV"""
    
    def __init__(self):
        self.df = None
        self.file_name = None
        self.metadata = {}
    
    def load_csv(self, file_path: str) -> pd.DataFrame:
        """Load CSV file with proper parsing"""
        try:
            self.file_name = Path(file_path).name
            logger.info(f"Loading file: {self.file_name}")
            
            # Read with proper parameters
            df = pd.read_csv(
                file_path,
                encoding='utf-8-sig',
                skiprows=1,  # Skip first row (CALLS,,PUTS)
                header=0,    # Use second row as header
                thousands=',',  # Handle thousands separators
                dtype=str    # Read everything as string first
            )
            
            logger.info(f"Initial load - rows: {len(df)}, columns: {len(df.columns)}")
            
            # Clean and parse
            df = self._parse_and_clean(df)
            
            self.df = df
            logger.info(f"Loaded {len(df)} strikes successfully")
            return df
            
        except Exception as e:
            logger.error(f"Error loading file: {e}")
            raise
    
    def _parse_and_clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse and clean dataframe"""
        
        # Clean column names - remove extra spaces
        df.columns = [str(col).strip() for col in df.columns]
        
        # Find strike column
        strike_col = None
        for col in df.columns:
            if 'STRIKE' in str(col).upper():
                strike_col = col
                break
        
        if strike_col is None:
            raise ValueError(f"Strike column not found. Columns: {list(df.columns)}")
        
        # Rename strike column
        df = df.rename(columns={strike_col: 'STRIKE PRICE'})
        
        # Identify call and put columns by position
        col_list = list(df.columns)
        strike_idx = col_list.index('STRIKE PRICE')
        
        # Columns before strike are Calls, after are Puts
        call_cols = col_list[:strike_idx]
        put_cols = col_list[strike_idx + 1:]
        
        # Map column names based on position
        call_names = ['OI_x', 'CHNG_IN_OI_x', 'VOLUME_x', 'IV_x', 'LTP_x', 'CHNG_x',
                      'BID_QTY_x', 'BID_x', 'ASK_x', 'ASK_QTY_x']
        put_names = ['OI_y', 'CHNG_IN_OI_y', 'VOLUME_y', 'IV_y', 'LTP_y', 'CHNG_y',
                     'BID_QTY_y', 'BID_y', 'ASK_y', 'ASK_QTY_y']
        
        # Rename call columns (first 10 columns before strike)
        rename_map = {}
        for i, col in enumerate(call_cols[:len(call_names)]):
            rename_map[col] = call_names[i]
        
        # Rename put columns (first 10 columns after strike)
        for i, col in enumerate(put_cols[:len(put_names)]):
            rename_map[col] = put_names[i]
        
        # Apply renaming
        df = df.rename(columns=rename_map)
        
        # Clean data - replace strings
        df = df.replace('-', np.nan)
        df = df.replace('', np.nan)
        df = df.replace('--', np.nan)
        
        # Remove commas from numeric strings and convert
        numeric_cols = ['OI_x', 'OI_y', 'CHNG_IN_OI_x', 'CHNG_IN_OI_y',
                       'VOLUME_x', 'VOLUME_y', 'IV_x', 'IV_y', 'LTP_x', 'LTP_y',
                       'CHNG_x', 'CHNG_y', 'BID_x', 'BID_y', 'ASK_x', 'ASK_y',
                       'BID_QTY_x', 'BID_QTY_y', 'ASK_QTY_x', 'ASK_QTY_y']
        
        for col in numeric_cols:
            if col in df.columns:
                # Remove commas and convert
                df[col] = df[col].astype(str).str.replace(',', '', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Convert strike price
        df['STRIKE PRICE'] = df['STRIKE PRICE'].astype(str).str.replace(',', '', regex=False)
        df['STRIKE PRICE'] = pd.to_numeric(df['STRIKE PRICE'], errors='coerce')
        
        # Drop invalid rows
        df = df.dropna(subset=['STRIKE PRICE'])
        
        # Keep only relevant columns
        keep_cols = ['STRIKE PRICE'] + [c for c in numeric_cols if c in df.columns]
        df = df[[c for c in keep_cols if c in df.columns]]
        
        # Sort by strike price
        df = df.sort_values('STRIKE PRICE').reset_index(drop=True)
        
        return df
    
    def get_strike_range(self) -> Tuple[float, float]:
        """Get min and max strike prices"""
        if self.df is None or len(self.df) == 0:
            return (0, 0)
        return (self.df['STRIKE PRICE'].min(), self.df['STRIKE PRICE'].max())
    
    def get_atm_strike(self, spot_price: Optional[float] = None) -> float:
        """Find the ATM strike"""
        if self.df is None or len(self.df) == 0:
            return 0
        
        strikes = self.df['STRIKE PRICE']
        
        if spot_price:
            return strikes.iloc[(strikes - spot_price).abs().argsort()[:1]].values[0]
        
        # Find strike with highest total OI
        ce_oi = self.df.get('OI_x', pd.Series([0]*len(self.df))).fillna(0)
        pe_oi = self.df.get('OI_y', pd.Series([0]*len(self.df))).fillna(0)
        total_oi = ce_oi + pe_oi
        
        if total_oi.sum() == 0:
            # If no OI, use middle strike
            return strikes.iloc[len(strikes)//2]
        
        max_oi_idx = total_oi.idxmax()
        return strikes.iloc[max_oi_idx]
