import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Dict, List
import logging
import re

logger = logging.getLogger(__name__)


class DataLoader:
    """
    DataLoader for NSE Option Chain CSV files.
    
    CSV Structure:
    - Row 1: CALLS,,PUTS
    - Row 2: ,OI,CHNG IN OI,VOLUME,IV,LTP,CHNG,BID QTY,BID,ASK,ASK QTY,STRIKE,BID QTY,BID,ASK,ASK QTY,CHNG,LTP,IV,VOLUME,CHNG IN OI,OI,
    - Row 3+: Data rows with 21 columns
    
    Column Mapping (21 columns total):
    Index  | Column Name        | Side
    -------|-------------------|--------
    0      | (empty)           | CALLS
    1      | OI                | CALLS
    2      | CHNG IN OI        | CALLS
    3      | VOLUME            | CALLS
    4      | IV                | CALLS
    5      | LTP               | CALLS
    6      | CHNG              | CALLS
    7      | BID QTY           | CALLS
    8      | BID               | CALLS
    9      | ASK               | CALLS
    10     | ASK QTY           | CALLS
    11     | STRIKE            | COMMON
    12     | BID QTY           | PUTS
    13     | BID               | PUTS
    14     | ASK               | PUTS
    15     | ASK QTY           | PUTS
    16     | CHNG              | PUTS
    17     | LTP               | PUTS
    18     | IV                | PUTS
    19     | VOLUME            | PUTS
    20     | CHNG IN OI        | PUTS
    21     | OI                | PUTS
    """
    
    # Column mapping for CALLS side (indices 0-10)
    CALLS_COLUMNS = [
        'CALLS_EMPTY',      # 0: Empty column
        'OI_x',             # 1: OI
        'CHNG_IN_OI_x',     # 2: CHNG IN OI
        'VOLUME_x',         # 3: VOLUME
        'IV_x',             # 4: IV
        'LTP_x',            # 5: LTP
        'CHNG_x',           # 6: CHNG
        'BID_QTY_x',        # 7: BID QTY
        'BID_x',            # 8: BID
        'ASK_x',            # 9: ASK
        'ASK_QTY_x'         # 10: ASK QTY
    ]
    
    # PUTS side columns (indices 12-21)
    PUTS_COLUMNS = [
        'BID_QTY_y',        # 12: BID QTY
        'BID_y',            # 13: BID
        'ASK_y',            # 14: ASK
        'ASK_QTY_y',        # 15: ASK QTY
        'CHNG_y',           # 16: CHNG
        'LTP_y',            # 17: LTP
        'IV_y',             # 18: IV
        'VOLUME_y',         # 19: VOLUME
        'CHNG_IN_OI_y',     # 20: CHNG IN OI
        'OI_y'              # 21: OI
    ]
    
    def __init__(self):
        self.df = None
        self.file_name = None
        self.metadata = {}
    
    def load_csv(self, file_path: str) -> pd.DataFrame:
        """Load CSV file with proper parsing"""
        try:
            self.file_name = Path(file_path).name
            logger.info(f"Loading file: {self.file_name}")
            
            # Read CSV with proper parameters
            df = self._read_csv(file_path)
            
            # Parse and clean
            df = self._parse_and_clean(df)
            
            self.df = df
            logger.info(f"Loaded {len(df)} strikes successfully")
            return df
            
        except Exception as e:
            logger.error(f"Error loading file: {e}")
            raise
    
    def _read_csv(self, file_path: str) -> pd.DataFrame:
        """Read CSV with proper header detection"""
        
        # Try reading with skiprows=1 (skip first row: CALLS,,PUTS)
        try:
            df = pd.read_csv(
                file_path,
                encoding='utf-8-sig',
                skiprows=1,      # Skip first row (CALLS,,PUTS)
                header=0,        # Use second row as header
                thousands=',',   # Handle thousands separators
                dtype=str        # Read everything as string first
            )
            logger.info(f"Read {len(df)} rows, {len(df.columns)} columns")
            return df
        except Exception as e:
            logger.warning(f"First read attempt failed: {e}")
        
        # Try with skiprows=2 (skip first two rows)
        try:
            df = pd.read_csv(
                file_path,
                encoding='utf-8-sig',
                skiprows=2,
                header=None,
                thousands=',',
                dtype=str
            )
            logger.info(f"Read with skiprows=2: {len(df)} rows, {len(df.columns)} columns")
            return df
        except Exception as e:
            logger.warning(f"Second read attempt failed: {e}")
        
        # Try manual parsing
        try:
            df = self._manual_parse(file_path)
            return df
        except Exception as e:
            logger.error(f"All read attempts failed: {e}")
            raise
    
    def _manual_parse(self, file_path: str) -> pd.DataFrame:
        """Manual parsing of CSV"""
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
        
        # Find header line (contains STRIKE)
        header_idx = None
        for i, line in enumerate(lines):
            if 'STRIKE' in line.upper():
                header_idx = i
                break
        
        if header_idx is None:
            raise ValueError("Header row with STRIKE not found")
        
        # Parse header
        header = [h.strip() for h in lines[header_idx].strip().split(',')]
        
        # Parse data
        data = []
        for line in lines[header_idx + 1:]:
            if line.strip():
                row = line.strip().split(',')
                if len(row) >= len(header):
                    data.append(row[:len(header)])
        
        # Create DataFrame
        df = pd.DataFrame(data, columns=header)
        return df
    
    def _parse_and_clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse and clean dataframe with 21-column structure"""
        
        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Find strike column
        strike_col = None
        for col in df.columns:
            if 'STRIKE' in str(col).upper():
                strike_col = col
                break
        
        if strike_col is None:
            raise ValueError(f"Strike column not found. Columns: {list(df.columns)}")
        
        logger.info(f"Found strike column: '{strike_col}'")
        
        # Get column list
        col_list = list(df.columns)
        strike_idx = col_list.index(strike_col)
        
        logger.info(f"Strike at index: {strike_idx}, Total columns: {len(col_list)}")
        
        # Build new column mapping based on position
        rename_map = {}
        
        # CALLS side (before strike)
        call_cols = col_list[:strike_idx]
        for i, col in enumerate(call_cols):
            if i < len(self.CALLS_COLUMNS):
                if self.CALLS_COLUMNS[i] != 'CALLS_EMPTY':  # Skip empty column
                    rename_map[col] = self.CALLS_COLUMNS[i]
        
        # Rename strike column
        rename_map[strike_col] = 'STRIKE PRICE'
        
        # PUTS side (after strike)
        put_cols = col_list[strike_idx + 1:]
        for i, col in enumerate(put_cols):
            if i < len(self.PUTS_COLUMNS):
                rename_map[col] = self.PUTS_COLUMNS[i]
        
        # Apply renaming
        df = df.rename(columns=rename_map)
        
        # Remove empty column if it exists
        if 'CALLS_EMPTY' in df.columns:
            df = df.drop(columns=['CALLS_EMPTY'])
        
        # Clean data - replace invalid values
        df = df.replace('-', np.nan)
        df = df.replace('', np.nan)
        df = df.replace('--', np.nan)
        df = df.replace(' ', np.nan)
        
        # Remove commas from numeric strings and convert
        numeric_cols = [
            'OI_x', 'OI_y', 
            'CHNG_IN_OI_x', 'CHNG_IN_OI_y',
            'VOLUME_x', 'VOLUME_y', 
            'IV_x', 'IV_y', 
            'LTP_x', 'LTP_y',
            'CHNG_x', 'CHNG_y', 
            'BID_x', 'BID_y', 
            'ASK_x', 'ASK_y',
            'BID_QTY_x', 'BID_QTY_y', 
            'ASK_QTY_x', 'ASK_QTY_y'
        ]
        
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
        
        # Keep only relevant columns (remove any extra columns)
        keep_cols = ['STRIKE PRICE'] + [c for c in numeric_cols if c in df.columns]
        df = df[[c for c in keep_cols if c in df.columns]]
        
        # Sort by strike price
        df = df.sort_values('STRIKE PRICE').reset_index(drop=True)
        
        logger.info(f"Final columns: {list(df.columns)}")
        logger.info(f"Final rows: {len(df)}")
        
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
            return strikes.iloc[len(strikes)//2]
        
        max_oi_idx = total_oi.idxmax()
        return strikes.iloc[max_oi_idx]
    
    def get_data_summary(self) -> Dict:
        """Get summary of loaded data"""
        if self.df is None:
            return {}
        
        return {
            'file_name': self.file_name,
            'num_strikes': len(self.df),
            'strike_range': self.get_strike_range(),
            'atm_strike': self.get_atm_strike(),
            'columns': list(self.df.columns),
            'has_ce_oi': 'OI_x' in self.df.columns,
            'has_pe_oi': 'OI_y' in self.df.columns,
        }