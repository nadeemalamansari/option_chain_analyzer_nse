"""
Tests for OptionChainAnalyzer
"""

import pytest
import pandas as pd
from src.core.analyzer import OptionChainAnalyzer, AnalysisResult


class TestAnalyzer:
    """Test OptionChainAnalyzer class"""
    
    def test_analyze_complete(self, sample_df, atm_strike):
        """Test complete analysis"""
        analyzer = OptionChainAnalyzer(sample_df, atm_strike)
        result = analyzer.analyze()
        
        assert result is not None
        assert isinstance(result, AnalysisResult)
        assert result.atm_strike == atm_strike
        assert result.oi_pcr >= 0
    
    def test_oi_analysis(self, sample_df, atm_strike):
        """Test OI analysis"""
        analyzer = OptionChainAnalyzer(sample_df, atm_strike)
        result = analyzer.analyze()
        
        assert result.total_ce_oi > 0
        assert result.total_pe_oi > 0
        assert result.oi_positioning_bias is not None
    
    def test_support_resistance(self, sample_df, atm_strike):
        """Test support/resistance analysis"""
        analyzer = OptionChainAnalyzer(sample_df, atm_strike)
        result = analyzer.analyze()
        
        assert result.supports is not None
        assert result.resistances is not None
    
    def test_verdict(self, sample_df, atm_strike):
        """Test verdict determination"""
        analyzer = OptionChainAnalyzer(sample_df, atm_strike)
        result = analyzer.analyze()
        
        assert result.final_verdict is not None
        assert result.confidence >= 0
    
    @pytest.fixture
    def sample_df(self):
        """Create sample DataFrame"""
        return pd.DataFrame({
            'STRIKE PRICE': [100, 110, 120, 130, 140, 150],
            'OI_x': [1000, 2000, 3000, 4000, 5000, 6000],
            'OI_y': [800, 1200, 2500, 3500, 4500, 5500],
            'CHNG_IN_OI_x': [100, 200, 300, 400, 500, 600],
            'CHNG_IN_OI_y': [80, 120, 250, 350, 450, 550],
            'VOLUME_x': [10000, 20000, 30000, 40000, 50000, 60000],
            'VOLUME_y': [8000, 12000, 25000, 35000, 45000, 55000],
            'LTP_x': [10, 9, 8, 7, 6, 5],
            'LTP_y': [5, 6, 7, 8, 9, 10],
            'BID_x': [9, 8, 7, 6, 5, 4],
            'ASK_x': [11, 10, 9, 8, 7, 6],
            'BID_y': [4, 5, 6, 7, 8, 9],
            'ASK_y': [6, 7, 8, 9, 10, 11]
        })
    
    @pytest.fixture
    def atm_strike(self):
        return 130