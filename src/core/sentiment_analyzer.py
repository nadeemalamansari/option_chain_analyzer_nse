"""
Sentiment Analysis Module for Option Chain Analyzer
Calculates market sentiment from 8 different factors
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class Sentiment(Enum):
    """Sentiment classification"""
    STRONG_BULLISH = "STRONG BULLISH"
    BULLISH = "BULLISH"
    NEUTRAL = "NEUTRAL"
    BEARISH = "BEARISH"
    STRONG_BEARISH = "STRONG BEARISH"


@dataclass
class SentimentResult:
    """Sentiment analysis result"""
    overall_sentiment: str = "NEUTRAL"
    sentiment_score: float = 0.0
    confidence: float = 0.0
    factors: Dict[str, float] = field(default_factory=dict)
    key_drivers: List[str] = field(default_factory=list)
    put_call_ratio_sentiment: str = "NEUTRAL"
    oi_migration_sentiment: str = "NEUTRAL"
    max_pain_sentiment: str = "NEUTRAL"
    volume_sentiment: str = "NEUTRAL"
    iv_sentiment: str = "NEUTRAL"
    support_resistance_sentiment: str = "NEUTRAL"
    atm_sentiment: str = "NEUTRAL"
    buildup_sentiment: str = "NEUTRAL"


class SentimentAnalyzer:
    """
    Sentiment Analyzer for Option Chain Data
    Analyzes 8 different factors to determine market sentiment
    """
    
    # Weight for each factor
    FACTOR_WEIGHTS = {
        "PCR": 18,
        "OI_Migration": 15,
        "Max_Pain": 10,
        "Volume": 12,
        "IV": 10,
        "Support_Resistance": 15,
        "ATM": 10,
        "Buildup": 10
    }
    
    def __init__(self):
        self.result = SentimentResult()
    
    def analyze(self, analysis: Dict, df: pd.DataFrame) -> SentimentResult:
        """
        Perform complete sentiment analysis
        
        Args:
            analysis: Analysis results dictionary from get_analysis()
            df: Raw option chain DataFrame
        
        Returns:
            SentimentResult: Complete sentiment analysis
        """
        
        # Extract data from analysis
        atm = analysis.get('atm', 0)
        pcr_oi = analysis.get('pcr_oi', 0)
        pcr_vol = analysis.get('pcr_vol', 0)
        support = analysis.get('support', 0)
        resistance = analysis.get('resistance', 0)
        max_pain = analysis.get('max_pain', 0)
        ce_chng = analysis.get('ce_chng', 0)
        pe_chng = analysis.get('pe_chng', 0)
        atm_ce_oi = analysis.get('atm_ce_oi', 0) or df[df['STRIKE'] == atm]['CE_OI'].sum() if atm else 0
        atm_pe_oi = analysis.get('atm_pe_oi', 0) or df[df['STRIKE'] == atm]['PE_OI'].sum() if atm else 0
        
        # ============================================================
        # 1️⃣ PCR ANALYSIS (18% weight)
        # ============================================================
        pcr_score, pcr_sentiment = self._analyze_pcr(pcr_oi)
        
        # ============================================================
        # 2️⃣ OI MIGRATION ANALYSIS (15% weight)
        # ============================================================
        migration_score, migration_sentiment = self._analyze_oi_migration(df, atm)
        
        # ============================================================
        # 3️⃣ MAX PAIN ANALYSIS (10% weight)
        # ============================================================
        maxpain_score, maxpain_sentiment = self._analyze_max_pain(atm, max_pain)
        
        # ============================================================
        # 4️⃣ VOLUME ANALYSIS (12% weight)
        # ============================================================
        volume_score, volume_sentiment = self._analyze_volume(pcr_vol)
        
        # ============================================================
        # 5️⃣ IV ANALYSIS (10% weight)
        # ============================================================
        iv_score, iv_sentiment = self._analyze_iv(df, atm)
        
        # ============================================================
        # 6️⃣ SUPPORT/RESISTANCE ANALYSIS (15% weight)
        # ============================================================
        sr_score, sr_sentiment = self._analyze_support_resistance(atm, support, resistance)
        
        # ============================================================
        # 7️⃣ ATM STRUCTURE ANALYSIS (10% weight)
        # ============================================================
        atm_score, atm_sentiment = self._analyze_atm_structure(atm_ce_oi, atm_pe_oi)
        
        # ============================================================
        # 8️⃣ BUILDUP ANALYSIS (10% weight)
        # ============================================================
        buildup_score, buildup_sentiment = self._analyze_buildup(ce_chng, pe_chng)
        
        # ============================================================
        # CALCULATE FINAL SENTIMENT SCORE
        # ============================================================
        
        factors = {
            "PCR": pcr_score,
            "OI_Migration": migration_score,
            "Max_Pain": maxpain_score,
            "Volume": volume_score,
            "IV": iv_score,
            "Support_Resistance": sr_score,
            "ATM": atm_score,
            "Buildup": buildup_score
        }
        
        # Weighted average
        total_weight = sum(self.FACTOR_WEIGHTS.values())
        weighted_score = sum(
            factors[key] * self.FACTOR_WEIGHTS[key] / total_weight
            for key in factors
        )
        
        # Sentiment labels
        sentiments = {
            "PCR": pcr_sentiment,
            "OI_Migration": migration_sentiment,
            "Max_Pain": maxpain_sentiment,
            "Volume": volume_sentiment,
            "IV": iv_sentiment,
            "Support_Resistance": sr_sentiment,
            "ATM": atm_sentiment,
            "Buildup": buildup_sentiment
        }
        
        # Count bullish/bearish/neutral
        bullish_count = sum(1 for s in sentiments.values() if s == "BULLISH")
        bearish_count = sum(1 for s in sentiments.values() if s == "BEARISH")
        neutral_count = sum(1 for s in sentiments.values() if s == "NEUTRAL")
        
        # Overall sentiment
        if weighted_score >= 60:
            overall = "STRONG BULLISH"
        elif weighted_score >= 30:
            overall = "BULLISH"
        elif weighted_score >= -30:
            overall = "NEUTRAL"
        elif weighted_score >= -60:
            overall = "BEARISH"
        else:
            overall = "STRONG BEARISH"
        
        # Confidence (based on factor agreement)
        total_factors = len(sentiments)
        if bullish_count >= total_factors * 0.75:
            confidence = 85
        elif bullish_count >= total_factors * 0.6:
            confidence = 70
        elif bearish_count >= total_factors * 0.75:
            confidence = 85
        elif bearish_count >= total_factors * 0.6:
            confidence = 70
        elif neutral_count >= total_factors * 0.5:
            confidence = 50
        else:
            confidence = 60
        
        # Key drivers (top 3 factors with highest absolute scores)
        sorted_factors = sorted(factors.items(), key=lambda x: abs(x[1]), reverse=True)
        key_drivers = []
        for factor_name, score in sorted_factors[:3]:
            sentiment_label = "Bullish" if score > 0 else "Bearish" if score < 0 else "Neutral"
            if abs(score) > 20:
                key_drivers.append(f"{factor_name.replace('_', ' ')}: {sentiment_label} ({score:+.1f})")
        
        # Store result
        self.result = SentimentResult(
            overall_sentiment=overall,
            sentiment_score=weighted_score,
            confidence=confidence,
            factors=factors,
            key_drivers=key_drivers,
            put_call_ratio_sentiment=pcr_sentiment,
            oi_migration_sentiment=migration_sentiment,
            max_pain_sentiment=maxpain_sentiment,
            volume_sentiment=volume_sentiment,
            iv_sentiment=iv_sentiment,
            support_resistance_sentiment=sr_sentiment,
            atm_sentiment=atm_sentiment,
            buildup_sentiment=buildup_sentiment
        )
        
        return self.result
    
    # ============================================================
    # INDIVIDUAL FACTOR ANALYZERS
    # ============================================================
    
    def _analyze_pcr(self, pcr_oi: float) -> Tuple[float, str]:
        """Analyze Put-Call Ratio"""
        if pcr_oi < 0.3:
            return 80, "STRONG BULLISH"
        elif pcr_oi < 0.5:
            return 60, "BULLISH"
        elif pcr_oi < 0.7:
            return 30, "WEAK BULLISH"
        elif pcr_oi < 1.0:
            return 0, "NEUTRAL"
        elif pcr_oi < 1.3:
            return -30, "WEAK BEARISH"
        elif pcr_oi < 1.7:
            return -60, "BEARISH"
        else:
            return -80, "STRONG BEARISH"
    
    def _analyze_oi_migration(self, df: pd.DataFrame, atm: float) -> Tuple[float, str]:
        """Analyze OI migration towards/away from ATM"""
        if atm == 0:
            return 0, "NEUTRAL"
        
        # Get OI above and below ATM
        strikes = df['STRIKE']
        ce_oi = df['CE_OI']
        pe_oi = df['PE_OI']
        
        above_atm = strikes > atm
        below_atm = strikes < atm
        
        ce_above = ce_oi[above_atm].sum()
        ce_below = ce_oi[below_atm].sum()
        pe_above = pe_oi[above_atm].sum()
        pe_below = pe_oi[below_atm].sum()
        
        # Check if OI is migrating towards ATM
        if pe_above > pe_below * 1.2 and ce_above > ce_below * 1.2:
            return 70, "BULLISH"  # OI moving to higher strikes = Bullish
        elif pe_below > pe_above * 1.2 and ce_below > ce_above * 1.2:
            return -70, "BEARISH"  # OI moving to lower strikes = Bearish
        else:
            return 0, "NEUTRAL"
    
    def _analyze_max_pain(self, atm: float, max_pain: float) -> Tuple[float, str]:
        """Analyze Max Pain vs Spot"""
        if atm == 0 or max_pain == 0:
            return 0, "NEUTRAL"
        
        diff = atm - max_pain
        
        if diff > 200:
            return 70, "BULLISH"   # Spot above Max Pain
        elif diff > 50:
            return 40, "WEAK BULLISH"
        elif diff > -50:
            return 0, "NEUTRAL"
        elif diff > -200:
            return -40, "WEAK BEARISH"
        else:
            return -70, "BEARISH"  # Spot below Max Pain
    
    def _analyze_volume(self, pcr_vol: float) -> Tuple[float, str]:
        """Analyze Volume PCR"""
        if pcr_vol < 0.3:
            return 70, "BULLISH"
        elif pcr_vol < 0.5:
            return 50, "WEAK BULLISH"
        elif pcr_vol < 0.8:
            return 20, "NEUTRAL"
        elif pcr_vol < 1.2:
            return 0, "NEUTRAL"
        elif pcr_vol < 1.5:
            return -20, "NEUTRAL"
        elif pcr_vol < 1.8:
            return -50, "WEAK BEARISH"
        else:
            return -70, "BEARISH"
    
    def _analyze_iv(self, df: pd.DataFrame, atm: float) -> Tuple[float, str]:
        """Analyze Implied Volatility skew"""
        if atm == 0:
            return 0, "NEUTRAL"
        
        # Get IV near ATM
        near_atm = df[(df['STRIKE'] >= atm - 500) & (df['STRIKE'] <= atm + 500)]
        
        if len(near_atm) == 0:
            return 0, "NEUTRAL"
        
        ce_iv_mean = near_atm['CE_IV'].mean() if 'CE_IV' in near_atm.columns else 0
        pe_iv_mean = near_atm['PE_IV'].mean() if 'PE_IV' in near_atm.columns else 0
        
        if ce_iv_mean == 0 or pe_iv_mean == 0:
            return 0, "NEUTRAL"
        
        iv_diff = pe_iv_mean - ce_iv_mean
        
        if iv_diff < -2:  # Call IV > Put IV
            return 60, "BULLISH"
        elif iv_diff < -0.5:
            return 30, "WEAK BULLISH"
        elif iv_diff < 0.5:
            return 0, "NEUTRAL"
        elif iv_diff < 2:
            return -30, "WEAK BEARISH"
        else:  # Put IV > Call IV
            return -60, "BEARISH"
    
    def _analyze_support_resistance(self, atm: float, support: float, resistance: float) -> Tuple[float, str]:
        """Analyze Support/Resistance levels"""
        if atm == 0:
            return 0, "NEUTRAL"
        
        support_distance = atm - support if support > 0 else 0
        resistance_distance = resistance - atm if resistance > 0 else 0
        
        if support_distance < 100 and resistance_distance > 500:
            return 70, "BULLISH"   # Strong support, weak resistance
        elif support_distance < 200 and resistance_distance > 300:
            return 40, "WEAK BULLISH"
        elif support_distance < 300 and resistance_distance < 300:
            return 0, "NEUTRAL"
        elif support_distance > 300 and resistance_distance < 200:
            return -40, "WEAK BEARISH"
        elif support_distance > 500 and resistance_distance < 100:
            return -70, "BEARISH"  # Weak support, strong resistance
        else:
            return 0, "NEUTRAL"
    
    def _analyze_atm_structure(self, ce_oi: float, pe_oi: float) -> Tuple[float, str]:
        """Analyze ATM structure"""
        if ce_oi == 0 and pe_oi == 0:
            return 0, "NEUTRAL"
        
        ratio = pe_oi / ce_oi if ce_oi > 0 else 0
        
        if ratio > 2:
            return 70, "BULLISH"   # More PE OI at ATM = Support = Bullish
        elif ratio > 1.5:
            return 40, "WEAK BULLISH"
        elif ratio > 0.67:
            return 0, "NEUTRAL"
        elif ratio > 0.5:
            return -40, "WEAK BEARISH"
        else:
            return -70, "BEARISH"  # More CE OI at ATM = Resistance = Bearish
    
    def _analyze_buildup(self, ce_chng: float, pe_chng: float) -> Tuple[float, str]:
        """Analyze buildup patterns"""
        if ce_chng == 0 and pe_chng == 0:
            return 0, "NEUTRAL"
        
        if ce_chng > 0 and pe_chng < 0:
            return 80, "BULLISH"   # Call buildup, put unwinding
        elif ce_chng > 0 and pe_chng > 0:
            return 30, "WEAK BULLISH"  # Both building, calls more
        elif ce_chng < 0 and pe_chng > 0:
            return -80, "BEARISH"  # Put buildup, call unwinding
        elif ce_chng < 0 and pe_chng < 0:
            return -30, "WEAK BEARISH"  # Both unwinding, puts more
        else:
            return 0, "NEUTRAL"