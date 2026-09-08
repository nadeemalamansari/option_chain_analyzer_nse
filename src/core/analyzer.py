import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from loguru import logger

from .oi_analyzer import OIAnalyzer
from .pcr_analyzer import PCRAnalyzer
from .volume_analyzer import VolumeAnalyzer
from .change_oi_analyzer import ChangeOIAnalyzer
from .support_resistance import SupportResistanceAnalyzer
from .max_pain import MaxPainCalculator
from .liquidity_analyzer import LiquidityAnalyzer


@dataclass
class AnalysisResult:
    """Complete analysis result container"""
    # OI Analysis
    total_ce_oi: float = 0
    total_pe_oi: float = 0
    oi_pcr: float = 0
    highest_ce_oi_strike: float = 0
    highest_pe_oi_strike: float = 0
    ce_oi_concentration: list = field(default_factory=list)
    pe_oi_concentration: list = field(default_factory=list)
    oi_positioning_bias: str = "NEUTRAL"
    
    # Change in OI
    total_ce_chng: float = 0
    total_pe_chng: float = 0
    chng_oi_pcr: float = 0
    ce_writing: list = field(default_factory=list)
    pe_writing: list = field(default_factory=list)
    ce_unwinding: list = field(default_factory=list)
    pe_unwinding: list = field(default_factory=list)
    change_oi_bias: str = "NEUTRAL"
    
    # Volume Analysis
    total_ce_volume: float = 0
    total_pe_volume: float = 0
    volume_pcr: float = 0
    ce_volume_concentration: list = field(default_factory=list)
    pe_volume_concentration: list = field(default_factory=list)
    volume_bias: str = "NEUTRAL"
    
    # Support & Resistance
    supports: list = field(default_factory=list)
    resistances: list = field(default_factory=list)
    support_strength: list = field(default_factory=list)
    resistance_strength: list = field(default_factory=list)
    sr_bias: str = "NEUTRAL"
    
    # Max Pain
    max_pain: float = 0
    
    # Liquidity
    liquidity_score: float = 0
    liquidity_bias: str = "NEUTRAL"
    
    # ATM Data
    atm_strike: float = 0
    atm_ce_oi: float = 0
    atm_pe_oi: float = 0
    atm_ce_ltp: float = 0
    atm_pe_ltp: float = 0
    atm_ce_iv: float = 0
    atm_pe_iv: float = 0
    atm_ce_volume: float = 0
    atm_pe_volume: float = 0
    
    # Final Scores
    bullish_score: float = 0
    bearish_score: float = 0
    final_verdict: str = "NEUTRAL"
    confidence: float = 0
    factor_agreement: str = "NEUTRAL"
    
    # OI Migration
    oi_migration: str = "NO CLEAR SHIFT"
    
    # Metadata
    file_name: str = ""
    exchange: str = "NSE"
    expiry: str = ""


class OptionChainAnalyzer:
    """Core analysis engine for Option Chain"""
    
    def __init__(self, df: pd.DataFrame, atm_strike: float, file_name: str = ""):
        self.df = df
        self.atm_strike = atm_strike
        self.file_name = file_name
        self.result = AnalysisResult()
        self.result.atm_strike = atm_strike
        self.result.file_name = file_name
    
    def analyze(self) -> AnalysisResult:
        """Run complete analysis"""
        logger.info(f"Starting analysis for {self.file_name}")
        
        # Run all analyzers
        self._run_oi_analysis()
        self._run_change_oi_analysis()
        self._run_volume_analysis()
        self._run_support_resistance()
        self._run_max_pain()
        self._run_liquidity_analysis()
        self._extract_atm_data()
        self._analyze_oi_migration()
        self._calculate_bias_scores()
        self._determine_verdict()
        self._calculate_factor_agreement()
        
        logger.info(f"Analysis complete. Verdict: {self.result.final_verdict}")
        return self.result
    
    def _run_oi_analysis(self):
        """Run Open Interest analysis"""
        oi_analyzer = OIAnalyzer(self.df, self.atm_strike)
        oi_result = oi_analyzer.analyze()
        
        self.result.total_ce_oi = oi_result.total_ce_oi
        self.result.total_pe_oi = oi_result.total_pe_oi
        self.result.oi_pcr = oi_result.oi_pcr
        self.result.highest_ce_oi_strike = oi_result.highest_ce_strike
        self.result.highest_pe_oi_strike = oi_result.highest_pe_strike
        self.result.ce_oi_concentration = oi_result.ce_concentration
        self.result.pe_oi_concentration = oi_result.pe_concentration
        self.result.oi_positioning_bias = oi_result.bias
    
    def _run_change_oi_analysis(self):
        """Run Change in OI analysis"""
        chng_analyzer = ChangeOIAnalyzer(self.df, self.atm_strike)
        chng_result = chng_analyzer.analyze()
        
        self.result.total_ce_chng = chng_result.total_ce_chng
        self.result.total_pe_chng = chng_result.total_pe_chng
        self.result.chng_oi_pcr = chng_result.chng_pcr
        self.result.ce_writing = chng_result.ce_writing
        self.result.pe_writing = chng_result.pe_writing
        self.result.ce_unwinding = chng_result.ce_unwinding
        self.result.pe_unwinding = chng_result.pe_unwinding
        self.result.change_oi_bias = chng_result.bias
    
    def _run_volume_analysis(self):
        """Run Volume analysis"""
        vol_analyzer = VolumeAnalyzer(self.df, self.atm_strike)
        vol_result = vol_analyzer.analyze()
        
        self.result.total_ce_volume = vol_result.total_ce_volume
        self.result.total_pe_volume = vol_result.total_pe_volume
        self.result.volume_pcr = vol_result.volume_pcr
        self.result.ce_volume_concentration = vol_result.ce_concentration
        self.result.pe_volume_concentration = vol_result.pe_concentration
        self.result.volume_bias = vol_result.bias
    
    def _run_support_resistance(self):
        """Run Support & Resistance analysis"""
        sr_analyzer = SupportResistanceAnalyzer(self.df, self.atm_strike)
        sr_result = sr_analyzer.analyze()
        
        self.result.supports = sr_result.supports
        self.result.resistances = sr_result.resistances
        self.result.support_strength = sr_result.support_strength
        self.result.resistance_strength = sr_result.resistance_strength
        self.result.sr_bias = sr_result.bias
    
    def _run_max_pain(self):
        """Run Max Pain calculation"""
        max_pain_calc = MaxPainCalculator(self.df)
        self.result.max_pain = max_pain_calc.calculate()
    
    def _run_liquidity_analysis(self):
        """Run Liquidity analysis"""
        liq_analyzer = LiquidityAnalyzer(self.df, self.atm_strike)
        liq_result = liq_analyzer.analyze()
        
        self.result.liquidity_score = liq_result.liquidity_score
        self.result.liquidity_bias = liq_result.bias
    
    def _extract_atm_data(self):
        """Extract ATM strike data"""
        atm_mask = pd.to_numeric(self.df['STRIKE PRICE'], errors='coerce') == self.atm_strike
        atm_row = self.df[atm_mask]
        
        if len(atm_row) > 0:
            row = atm_row.iloc[0]
            self.result.atm_ce_oi = pd.to_numeric(row.get('OI_x', 0), errors='coerce')
            self.result.atm_pe_oi = pd.to_numeric(row.get('OI_y', 0), errors='coerce')
            self.result.atm_ce_ltp = pd.to_numeric(row.get('LTP_x', 0), errors='coerce')
            self.result.atm_pe_ltp = pd.to_numeric(row.get('LTP_y', 0), errors='coerce')
            self.result.atm_ce_iv = pd.to_numeric(row.get('IV_x', 0), errors='coerce')
            self.result.atm_pe_iv = pd.to_numeric(row.get('IV_y', 0), errors='coerce')
            self.result.atm_ce_volume = pd.to_numeric(row.get('VOLUME_x', 0), errors='coerce')
            self.result.atm_pe_volume = pd.to_numeric(row.get('VOLUME_y', 0), errors='coerce')
    
    def _analyze_oi_migration(self):
        """Analyze OI migration patterns"""
        # Check if OI is moving to higher strikes
        ce_oi = pd.to_numeric(self.df['OI_x'], errors='coerce').fillna(0)
        pe_oi = pd.to_numeric(self.df['OI_y'], errors='coerce').fillna(0)
        strikes = pd.to_numeric(self.df['STRIKE PRICE'], errors='coerce')
        
        # Compare OI concentration above vs below ATM
        above_atm = strikes > self.atm_strike
        below_atm = strikes < self.atm_strike
        
        ce_above = ce_oi[above_atm].sum()
        ce_below = ce_oi[below_atm].sum()
        pe_above = pe_oi[above_atm].sum()
        pe_below = pe_oi[below_atm].sum()
        
        if ce_above > ce_below * 1.2 and pe_above > pe_below * 1.2:
            self.result.oi_migration = "BULLISH SHIFT (Higher strikes)"
        elif ce_above < ce_below * 0.8 and pe_above < pe_below * 0.8:
            self.result.oi_migration = "BEARISH SHIFT (Lower strikes)"
        else:
            self.result.oi_migration = "RANGE-BOUND (No clear shift)"
    
    def _calculate_bias_scores(self):
        """Calculate bullish/bearish scores based on all factors"""
        scores = {
            'oi_positioning': self._score_oi_positioning(),
            'change_oi': self._score_change_oi(),
            'volume': self._score_volume(),
            'support_resistance': self._score_sr(),
            'pcr': self._score_pcr(),
            'liquidity': self._score_liquidity()
        }
        
        weights = {
            'oi_positioning': 0.25,
            'change_oi': 0.20,
            'volume': 0.15,
            'support_resistance': 0.20,
            'pcr': 0.10,
            'liquidity': 0.10
        }
        
        self.result.bullish_score = sum(scores[k] * weights[k] for k in scores)
        self.result.bearish_score = 100 - self.result.bullish_score
    
    def _score_oi_positioning(self) -> float:
        """Score OI positioning"""
        if self.result.oi_pcr < 0.7:
            return 85
        elif self.result.oi_pcr < 0.9:
            return 70
        elif self.result.oi_pcr < 1.1:
            return 50
        elif self.result.oi_pcr < 1.3:
            return 30
        else:
            return 15
    
    def _score_change_oi(self) -> float:
        """Score Change in OI"""
        if self.result.chng_oi_pcr < 0.7:
            return 80
        elif self.result.chng_oi_pcr < 0.9:
            return 65
        elif self.result.chng_oi_pcr < 1.1:
            return 50
        elif self.result.chng_oi_pcr < 1.3:
            return 35
        else:
            return 20
    
    def _score_volume(self) -> float:
        """Score Volume"""
        if self.result.volume_pcr < 0.7:
            return 75
        elif self.result.volume_pcr < 0.9:
            return 60
        elif self.result.volume_pcr < 1.1:
            return 50
        elif self.result.volume_pcr < 1.3:
            return 35
        else:
            return 25
    
    def _score_sr(self) -> float:
        """Score Support/Resistance"""
        if self.result.sr_bias == "BULLISH":
            return 75
        elif self.result.sr_bias == "BEARISH":
            return 25
        else:
            return 50
    
    def _score_pcr(self) -> float:
        """Score PCR"""
        # Use OI PCR as base
        if self.result.oi_pcr < 0.7:
            return 80
        elif self.result.oi_pcr < 0.9:
            return 65
        elif self.result.oi_pcr < 1.1:
            return 50
        elif self.result.oi_pcr < 1.3:
            return 35
        else:
            return 20
    
    def _score_liquidity(self) -> float:
        """Score Liquidity"""
        if self.result.liquidity_score > 80:
            return 70
        elif self.result.liquidity_score > 60:
            return 55
        else:
            return 40
    
    def _determine_verdict(self):
        """Determine final market verdict"""
        score = self.result.bullish_score
        
        if score >= 80:
            self.result.final_verdict = "STRONG BULLISH"
            self.result.confidence = 85
        elif score >= 70:
            self.result.final_verdict = "BULLISH"
            self.result.confidence = 75
        elif score >= 60:
            self.result.final_verdict = "WEAK BULLISH"
            self.result.confidence = 65
        elif score >= 50:
            self.result.final_verdict = "NEUTRAL"
            self.result.confidence = 55
        elif score >= 40:
            self.result.final_verdict = "WEAK BEARISH"
            self.result.confidence = 65
        elif score >= 30:
            self.result.final_verdict = "BEARISH"
            self.result.confidence = 75
        else:
            self.result.final_verdict = "STRONG BEARISH"
            self.result.confidence = 85
    
    def _calculate_factor_agreement(self):
        """Calculate agreement between factors"""
        biases = [
            self.result.oi_positioning_bias,
            self.result.change_oi_bias,
            self.result.volume_bias,
            self.result.sr_bias
        ]
        
        bullish_count = sum(1 for b in biases if b == "BULLISH")
        bearish_count = sum(1 for b in biases if b == "BEARISH")
        neutral_count = sum(1 for b in biases if b == "NEUTRAL")
        
        total = len(biases)
        if bullish_count >= total * 0.75:
            self.result.factor_agreement = "STRONG BULLISH AGREEMENT"
        elif bullish_count >= total * 0.6:
            self.result.factor_agreement = "MODERATE BULLISH AGREEMENT"
        elif bearish_count >= total * 0.75:
            self.result.factor_agreement = "STRONG BEARISH AGREEMENT"
        elif bearish_count >= total * 0.6:
            self.result.factor_agreement = "MODERATE BEARISH AGREEMENT"
        elif neutral_count >= total * 0.5:
            self.result.factor_agreement = "CONFLICTING / NEUTRAL"
        else:
            self.result.factor_agreement = "MIXED"