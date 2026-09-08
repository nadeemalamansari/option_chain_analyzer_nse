"""
NSE Option Chain Analyzer PRO
Main file - Handles upload and data
Version: 2.0.0
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Page config
st.set_page_config(
    page_title="NSE Option Chain Analyzer PRO",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# ========== CUSTOM CSS ==========
st.markdown("""
    <style>
    /* Hide all default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none !important;}
    
    /* Main header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .main-header h1 { font-size: 1.8rem; margin: 0; }
    .main-header .subtitle { font-size: 0.8rem; opacity: 0.9; }
    
    /* Success message */
    .success-box {
        background: linear-gradient(135deg, #00b09b, #96c93d);
        padding: 0.8rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        font-weight: 600;
        animation: slideIn 0.5s ease-out;
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* File info */
    .file-info {
        background: rgba(102, 126, 234, 0.1);
        border-radius: 8px;
        padding: 0.5rem;
        text-align: center;
        border-left: 3px solid #667eea;
    }
    .file-info .file-name { color: #64ffda; font-weight: 600; }
    .file-info .file-detail { color: #8892b0; font-size: 0.8rem; }
    
    /* Decision box */
    .decision-box {
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        margin: 10px 0;
        font-size: 1.8rem;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .bullish { background: linear-gradient(135deg, #27ae60, #2ecc71); color: white; }
    .bearish { background: linear-gradient(135deg, #c0392b, #e74c3c); color: white; }
    .neutral { background: linear-gradient(135deg, #f39c12, #e67e22); color: white; }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        margin: 5px 0;
    }
    .metric-value { font-size: 1.8rem; font-weight: bold; }
    .metric-label { font-size: 0.8rem; color: #666; text-transform: uppercase; letter-spacing: 1px; }
    
    /* Block container */
    .block-container { padding-top: 0.5rem; padding-bottom: 0rem; }
    </style>
""", unsafe_allow_html=True)

# ========== SESSION STATE ==========
if 'df' not in st.session_state:
    st.session_state.df = None
if 'analysis' not in st.session_state:
    st.session_state.analysis = None
if 'filename' not in st.session_state:
    st.session_state.filename = None
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'upload_success' not in st.session_state:
    st.session_state.upload_success = False


# ========== DATA PARSING FUNCTIONS ==========
def parse_nse_csv(uploaded_file):
    """
    Parse NSE Option Chain CSV File
    Handles NSE website format with CALLS/PUTS headers
    Returns cleaned DataFrame
    """
    try:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, skiprows=1)
        
        # Remove unnamed columns
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # Column mapping based on position
        column_mapping = {}
        
        for i, col in enumerate(df.columns):
            col_str = str(col).strip().upper()
            
            # CE Columns (before STRIKE - index 0-10)
            if i < 11:
                if 'OI' in col_str and 'CHNG' not in col_str and 'VOL' not in col_str:
                    column_mapping[col] = 'CE_OI'
                elif 'CHNG' in col_str and 'OI' in col_str:
                    column_mapping[col] = 'CE_CHNG_IN_OI'
                elif 'VOL' in col_str:
                    column_mapping[col] = 'CE_VOLUME'
                elif 'IV' in col_str:
                    column_mapping[col] = 'CE_IV'
                elif 'LTP' in col_str:
                    column_mapping[col] = 'CE_LTP'
                elif 'CHNG' in col_str:
                    column_mapping[col] = 'CE_CHNG'
                elif 'BID' in col_str and 'QTY' in col_str:
                    column_mapping[col] = 'CE_BID_QTY'
                elif 'BID' in col_str:
                    column_mapping[col] = 'CE_BID'
                elif 'ASK' in col_str and 'QTY' in col_str:
                    column_mapping[col] = 'CE_ASK_QTY'
                elif 'ASK' in col_str:
                    column_mapping[col] = 'CE_ASK'
            
            # STRIKE column
            elif 'STRIKE' in col_str:
                column_mapping[col] = 'STRIKE'
            
            # PE Columns (after STRIKE)
            else:
                if 'OI' in col_str and 'CHNG' not in col_str and 'VOL' not in col_str:
                    column_mapping[col] = 'PE_OI'
                elif 'CHNG' in col_str and 'OI' in col_str:
                    column_mapping[col] = 'PE_CHNG_IN_OI'
                elif 'VOL' in col_str:
                    column_mapping[col] = 'PE_VOLUME'
                elif 'IV' in col_str:
                    column_mapping[col] = 'PE_IV'
                elif 'LTP' in col_str:
                    column_mapping[col] = 'PE_LTP'
                elif 'CHNG' in col_str:
                    column_mapping[col] = 'PE_CHNG'
                elif 'BID' in col_str and 'QTY' in col_str:
                    column_mapping[col] = 'PE_BID_QTY'
                elif 'BID' in col_str:
                    column_mapping[col] = 'PE_BID'
                elif 'ASK' in col_str and 'QTY' in col_str:
                    column_mapping[col] = 'PE_ASK_QTY'
                elif 'ASK' in col_str:
                    column_mapping[col] = 'PE_ASK'
        
        df = df.rename(columns=column_mapping)
        
        # Required columns check
        required = ['STRIKE', 'CE_OI', 'CE_VOLUME', 'PE_OI', 'PE_VOLUME']
        for col in required:
            if col not in df.columns:
                st.error(f"❌ Missing column: {col}")
                return None
        
        # Clean data
        for col in df.columns:
            if col != 'STRIKE':
                df[col] = df[col].replace(['-', '', ' ', 'NaN', 'nan'], '0')
                df[col] = df[col].astype(str).str.replace(',', '')
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Clean STRIKE
        df['STRIKE'] = pd.to_numeric(df['STRIKE'].astype(str).str.replace(',', ''), errors='coerce')
        df = df.dropna(subset=['STRIKE'])
        df = df[df['STRIKE'] > 0].sort_values('STRIKE').reset_index(drop=True)
        
        # Derived columns
        df['TOTAL_OI'] = df['CE_OI'] + df['PE_OI']
        df['TOTAL_VOLUME'] = df['CE_VOLUME'] + df['PE_VOLUME']
        
        return df
        
    except Exception as e:
        st.error(f"❌ CSV parsing error: {str(e)}")
        return None


def get_analysis(df):
    """
    Complete analysis calculation with 8 modules and weighted scoring
    """
    try:
        # ATM detection
        atm_idx = df['TOTAL_VOLUME'].idxmax() if df['TOTAL_VOLUME'].max() > 0 else 0
        atm = df.loc[atm_idx, 'STRIKE']
        
        # OI Totals
        total_ce_oi = df['CE_OI'].sum()
        total_pe_oi = df['PE_OI'].sum()
        total_oi = total_ce_oi + total_pe_oi
        
        # Volume Totals
        total_ce_vol = df['CE_VOLUME'].sum()
        total_pe_vol = df['PE_VOLUME'].sum()
        total_volume = total_ce_vol + total_pe_vol
        
        # PCR
        pcr_oi = total_pe_oi / total_ce_oi if total_ce_oi > 0 else 0
        pcr_vol = total_pe_vol / total_ce_vol if total_ce_vol > 0 else 0
        
        # OI Change
        ce_chng = df['CE_CHNG_IN_OI'].sum() if 'CE_CHNG_IN_OI' in df.columns else 0
        pe_chng = df['PE_CHNG_IN_OI'].sum() if 'PE_CHNG_IN_OI' in df.columns else 0
        
        # Support/Resistance
        resistance = df.loc[df['CE_OI'].idxmax(), 'STRIKE'] if df['CE_OI'].max() > 0 else atm
        support = df.loc[df['PE_OI'].idxmax(), 'STRIKE'] if df['PE_OI'].max() > 0 else atm
        
        # Max Pain
        max_pain = df.loc[df['TOTAL_OI'].idxmax(), 'STRIKE'] if df['TOTAL_OI'].max() > 0 else atm
        
        # ATM OI
        atm_ce_oi = df[df['STRIKE'] == atm]['CE_OI'].sum() if atm in df['STRIKE'].values else 0
        atm_pe_oi = df[df['STRIKE'] == atm]['PE_OI'].sum() if atm in df['STRIKE'].values else 0
        
        # ATM IV
        atm_ce_iv = df[df['STRIKE'] == atm]['CE_IV'].mean() if atm in df['STRIKE'].values and 'CE_IV' in df.columns else 0
        atm_pe_iv = df[df['STRIKE'] == atm]['PE_IV'].mean() if atm in df['STRIKE'].values and 'PE_IV' in df.columns else 0
        
        # ============================================================
        # 1️⃣ OI Analysis (18% weight)
        # ============================================================
        oi_score = 0
        if pcr_oi < 0.5:      # Strong Bullish
            oi_score = 85
        elif pcr_oi < 0.7:    # Bullish
            oi_score = 70
        elif pcr_oi < 0.9:    # Weak Bullish
            oi_score = 55
        elif pcr_oi < 1.1:    # Neutral
            oi_score = 50
        elif pcr_oi < 1.3:    # Weak Bearish
            oi_score = 40
        elif pcr_oi < 1.5:    # Bearish
            oi_score = 30
        else:                 # Strong Bearish
            oi_score = 20
        
        # ============================================================
        # 2️⃣ PCR Analysis (10% weight)
        # ============================================================
        pcr_score = 0
        if pcr_vol < 0.5:
            pcr_score = 80
        elif pcr_vol < 0.7:
            pcr_score = 65
        elif pcr_vol < 1.1:
            pcr_score = 50
        elif pcr_vol < 1.3:
            pcr_score = 40
        elif pcr_vol < 1.5:
            pcr_score = 30
        else:
            pcr_score = 20
        
        # ============================================================
        # 3️⃣ Volume Analysis (8% weight)
        # ============================================================
        vol_score = 0
        if pcr_vol < 0.5:
            vol_score = 75
        elif pcr_vol < 0.7:
            vol_score = 60
        elif pcr_vol < 1.1:
            vol_score = 50
        elif pcr_vol < 1.3:
            vol_score = 40
        elif pcr_vol < 1.5:
            vol_score = 30
        else:
            vol_score = 20
        
        # ============================================================
        # 4️⃣ Change OI Analysis (33% weight)
        # ============================================================
        chng_score = 50
        if ce_chng > 0 and pe_chng < 0:
            chng_score = 80   # Bullish
        elif ce_chng < 0 and pe_chng > 0:
            chng_score = 20   # Bearish
        elif ce_chng > pe_chng and ce_chng > 0:
            chng_score = 70
        elif pe_chng > ce_chng and pe_chng > 0:
            chng_score = 30
        elif ce_chng > 0 and pe_chng > 0:
            chng_score = 55
        elif ce_chng < 0 and pe_chng < 0:
            chng_score = 45
        
        # ============================================================
        # 5️⃣ Support/Resistance (15% weight)
        # ============================================================
        sr_score = 50
        if support > atm - 100:
            sr_score = 70    # Support near ATM = Bullish
        elif support < atm - 500:
            sr_score = 40    # Support far below = Bearish
        
        if resistance < atm + 100:
            sr_score = sr_score - 20  # Resistance near ATM = Bearish
        elif resistance > atm + 500:
            sr_score = sr_score + 10  # Resistance far above = Bullish
        
        sr_score = max(0, min(100, sr_score))
        
        # ============================================================
        # 6️⃣ Max Pain Analysis (3% weight)
        # ============================================================
        maxpain_score = 50
        diff = abs(atm - max_pain)
        if diff < 50:
            maxpain_score = 70   # Max Pain near ATM = Bullish
        elif diff < 200:
            maxpain_score = 55
        elif diff < 500:
            maxpain_score = 40
        else:
            maxpain_score = 25   # Max Pain far from ATM = Bearish
        
        # ============================================================
        # 7️⃣ Liquidity Analysis (2% weight)
        # ============================================================
        liquidity_score = 50
        if 'CE_BID' in df.columns and 'CE_ASK' in df.columns:
            spread_ce = (df['CE_ASK'] - df['CE_BID']).mean()
            if spread_ce < 1:
                liquidity_score = 70   # Tight spread = Good liquidity = Bullish
            elif spread_ce < 5:
                liquidity_score = 55
            elif spread_ce < 20:
                liquidity_score = 40
            else:
                liquidity_score = 25
        
        # ============================================================
        # 8️⃣ Sentiment Analysis (11% weight)
        # ============================================================
        sentiment_score = 50
        
        # Combined sentiment from all factors
        avg_score = (oi_score + pcr_score + vol_score + chng_score + sr_score + maxpain_score + liquidity_score) / 7
        
        # Adjust based on volatility skew
        if atm_ce_iv > 0 and atm_pe_iv > 0:
            if atm_pe_iv > atm_ce_iv * 1.2:
                sentiment_score = 40   # Higher put IV = Bearish
            elif atm_ce_iv > atm_pe_iv * 1.2:
                sentiment_score = 60   # Higher call IV = Bullish
            else:
                sentiment_score = avg_score
        else:
            sentiment_score = avg_score
        
        sentiment_score = max(0, min(100, sentiment_score))
        
        # Sentiment label
        if sentiment_score >= 70:
            sentiment = "STRONG BULLISH 🚀"
        elif sentiment_score >= 55:
            sentiment = "BULLISH 📈"
        elif sentiment_score >= 45:
            sentiment = "NEUTRAL ⚖️"
        elif sentiment_score >= 30:
            sentiment = "BEARISH 📉"
        else:
            sentiment = "STRONG BEARISH 💥"
        
        # ============================================================
        # 🎯 FINAL SCORE (Weighted Average - 8 Modules)
        # ============================================================
        final_score = (
            (oi_score * 0.18) +        # 18% weight
            (pcr_score * 0.10) +       # 10% weight
            (vol_score * 0.08) +       # 8% weight
            (chng_score * 0.33) +      # 33% weight
            (sr_score * 0.15) +        # 15% weight
            (maxpain_score * 0.03) +   # 3% weight
            (liquidity_score * 0.02) + # 2% weight
            (sentiment_score * 0.11)   # 11% weight
        )
        
        # ============================================================
        # 🏁 FINAL DECISION
        # ============================================================
        if final_score >= 70:
            decision = "🚀 BULLISH"
            decision_class = "bullish"
            emoji = "🟢"
        elif final_score >= 55:
            decision = "📈 WEAK BULLISH"
            decision_class = "bullish"
            emoji = "🟢"
        elif final_score >= 45:
            decision = "⚖️ NEUTRAL"
            decision_class = "neutral"
            emoji = "🟡"
        elif final_score >= 30:
            decision = "📉 WEAK BEARISH"
            decision_class = "bearish"
            emoji = "🔴"
        else:
            decision = "💥 BEARISH"
            decision_class = "bearish"
            emoji = "🔴"
        
        return {
            # ATM
            'atm': atm,
            'atm_ce_oi': atm_ce_oi,
            'atm_pe_oi': atm_pe_oi,
            'atm_ce_iv': atm_ce_iv,
            'atm_pe_iv': atm_pe_iv,
            
            # PCR
            'pcr_oi': round(pcr_oi, 2),
            'pcr_vol': round(pcr_vol, 2),
            
            # OI Totals
            'total_ce_oi': total_ce_oi,
            'total_pe_oi': total_pe_oi,
            'total_oi': total_oi,
            
            # Volume Totals
            'total_ce_vol': total_ce_vol,
            'total_pe_vol': total_pe_vol,
            'total_volume': total_volume,
            
            # OI Change
            'ce_chng': ce_chng,
            'pe_chng': pe_chng,
            
            # Support/Resistance
            'resistance': resistance,
            'support': support,
            
            # Max Pain
            'max_pain': max_pain,
            
            # Individual Scores (8 modules)
            'oi_score': round(oi_score, 1),
            'pcr_score': round(pcr_score, 1),
            'vol_score': round(vol_score, 1),
            'chng_score': round(chng_score, 1),
            'sr_score': round(sr_score, 1),
            'maxpain_score': round(maxpain_score, 1),
            'liquidity_score': round(liquidity_score, 1),
            'sentiment_score': round(sentiment_score, 1),
            
            # Sentiment
            'sentiment': sentiment,
            
            # Final
            'decision': decision,
            'decision_class': decision_class,
            'emoji': emoji,
            'score': round(final_score, 1),
            'total_strikes': len(df)
        }
        
    except Exception as e:
        st.error(f"❌ Analysis error: {str(e)}")
        return None


# ========== MAIN APP ==========

# Header
st.markdown("""
    <div class="main-header">
        <h1>📊 NSE Option Chain Analyzer PRO</h1>
        <div class="subtitle">Professional F&O Trading Analysis Platform</div>
    </div>
""", unsafe_allow_html=True)

# Sidebar - Upload Section
with st.sidebar:
    st.markdown("### 📁 Upload Data")
    
    uploaded_file = st.file_uploader(
        "Choose CSV file",
        type=['csv'],
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        try:
            df = parse_nse_csv(uploaded_file)
            
            if df is not None and len(df) > 0:
                analysis = get_analysis(df)
                
                if analysis:
                    st.session_state.df = df
                    st.session_state.analysis = analysis
                    st.session_state.filename = uploaded_file.name
                    st.session_state.data_loaded = True
                    st.session_state.upload_success = True
                    
                    # Success message
                    st.markdown(f"""
                        <div class="success-box">
                            ✅ Uploaded Successfully!
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # File info
                    st.markdown(f"""
                        <div class="file-info">
                            <div class="file-name">📄 {uploaded_file.name}</div>
                            <div class="file-detail">
                                📊 {len(df)} strikes &nbsp;|&nbsp; 🎯 ATM: {analysis['atm']:,.0f}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    st.markdown("---")
    st.caption("PRO v2.0 | Powered by Streamlit")

# Main Content
if st.session_state.data_loaded and st.session_state.df is not None:
    if st.session_state.upload_success:
        st.balloons()
        st.session_state.upload_success = False
    
    # Show quick stats
    analysis = st.session_state.analysis
    
    st.markdown("### 📊 Quick Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("PCR (OI)", f"{analysis['pcr_oi']:.2f}")
    with col2:
        st.metric("ATM", f"₹{analysis['atm']:,.0f}")
    with col3:
        st.metric("Support", f"₹{analysis['support']:,.0f}")
    with col4:
        st.metric("Resistance", f"₹{analysis['resistance']:,.0f}")
    with col5:
        st.metric("Sentiment", analysis['decision'].split()[1] if len(analysis['decision'].split()) > 1 else analysis['decision'])
    
    st.info("👈 **Use the sidebar navigation** to explore different analysis pages: Dashboard, OI Analysis, PCR Analysis, Volume Analysis, Change OI, Support/Resistance, Max Pain, Liquidity Analysis, and Sentiment Analysis.")

else:
    # Welcome screen
    st.markdown("""
        <div style="text-align:center;padding:2rem;">
            <h2 style="color:#64ffda;">🚀 Welcome!</h2>
            <p style="color:#8892b0;">Upload your NSE Option Chain CSV file from the sidebar</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Features - 8 Modules
    st.markdown("### ✨ 8 Analysis Modules")
    
    col1, col2, col3, col4 = st.columns(4)
    
    features = [
        ("📈", "OI Analysis", "18%", "Open Interest patterns"),
        ("📉", "PCR Analysis", "10%", "Put-Call Ratio"),
        ("📊", "Volume Analysis", "8%", "Trading volume"),
        ("🔄", "Change OI", "33%", "OI additions/unwinding"),
        ("🎯", "S&R", "15%", "Support/Resistance"),
        ("💉", "Max Pain", "3%", "Option seller's pain"),
        ("💧", "Liquidity", "2%", "Bid-Ask spread"),
        ("🧠", "Sentiment", "11%", "Market sentiment")
    ]
    
    for i, (icon, name, weight, desc) in enumerate(features):
        col_idx = i % 4
        with [col1, col2, col3, col4][col_idx]:
            st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #1a1a2e, #16213e);
                    padding: 1.2rem;
                    border-radius: 12px;
                    text-align: center;
                    border: 1px solid #2a2a4a;
                    margin: 5px 0;
                    transition: all 0.3s ease;
                ">
                    <div style="font-size: 2rem;">{icon}</div>
                    <div style="color: #ffffff; font-weight: 600; font-size: 0.9rem;">{name}</div>
                    <div style="color: #64ffda; font-size: 0.8rem; font-weight: bold;">{weight}</div>
                    <div style="color: #8892b0; font-size: 0.7rem; margin-top: 0.2rem;">{desc}</div>
                </div>
            """, unsafe_allow_html=True)