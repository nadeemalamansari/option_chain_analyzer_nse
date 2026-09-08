"""
Tests for DataLoader
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from src.core.data_loader import DataLoader


class TestDataLoader:
    """Test DataLoader class"""
    
    def test_load_csv(self, sample_csv):
        """Test loading CSV file"""
        loader = DataLoader()
        df = loader.load_csv(sample_csv)
        
        assert df is not None
        assert len(df) > 0
        assert 'STRIKE PRICE' in df.columns
    
    def test_get_strike_range(self, sample_df):
        """Test getting strike range"""
        loader = DataLoader()
        loader.df = sample_df
        
        min_strike, max_strike = loader.get_strike_range()
        assert min_strike > 0
        assert max_strike > min_strike
    
    def test_get_atm_strike(self, sample_df):
        """Test getting ATM strike"""
        loader = DataLoader()
        loader.df = sample_df
        
        atm = loader.get_atm_strike()
        assert atm > 0
    
    @pytest.fixture
    def sample_csv(self, tmp_path):
        """Create sample CSV"""
        file_path = tmp_path / "sample.csv"
        df = pd.DataFrame({
            'STRIKE PRICE': [100, 110, 120],
            'OI_x': [1000, 2000, 1500],
            'OI_y': [800, 1200, 900]
        })
        df.to_csv(file_path, index=False)
        return str(file_path)
    
    @pytest.fixture
    def sample_df(self):
        """Create sample DataFrame"""
        return pd.DataFrame({
            'STRIKE PRICE': [100, 110, 120, 130, 140],
            'OI_x': [1000, 2000, 3000, 1500, 500],
            'OI_y': [800, 1200, 2500, 900, 300]
        })