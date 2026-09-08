import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def show_buildup_analysis():
    df = st.session_state.get('df')
    if df is None:
        st.warning("⚠️ Upload CSV first")
        return
    
    if 'CE_CHNG_IN_OI' not in df.columns:
        st.warning("⚠️ Change OI data not available")
        return
    
    # Find ATM
    total_vol = df['CE_VOLUME'] + df['PE_VOLUME']
    atm = df.loc[total_vol.idxmax(), 'STRIKE'] if total_vol.max() > 0 else df['STRIKE'].iloc[len(df)//2]
    
    # ============================================================
    # 1. PRICE + OI CALCULATIONS
    # ============================================================
    ce_ltp = pd.to_numeric(df['CE_LTP'], errors='coerce').fillna(0)
    ce_chng = pd.to_numeric(df['CE_CHNG_IN_OI'], errors='coerce').fillna(0)
    pe_ltp = pd.to_numeric(df['PE_LTP'], errors='coerce').fillna(0)
    pe_chng = pd.to_numeric(df['PE_CHNG_IN_OI'], errors='coerce').fillna(0)
    
    ce_pc = ce_ltp.diff()
    pe_pc = pe_ltp.diff()
    
    # ============================================================
    # 2. CE BUILDUP (20 Strikes)
    # ============================================================
    ce_data = []
    ce_bullish = 0
    ce_bearish = 0
    
    for i in range(1, len(df)):
        strike = float(df['STRIKE'].iloc[i])
        price_chng = ce_pc.iloc[i]
        oi_chng = ce_chng.iloc[i]
        
        if pd.isna(price_chng) or pd.isna(oi_chng):
            continue
        
        if price_chng > 0 and oi_chng > 0:
            signal = "🟢 Long Buildup (Bullish)"
            ce_bullish += 1
            ce_data.append({"Strike": strike, "Price": "↑", "OI": "↑", "Signal": signal})
        elif price_chng < 0 and oi_chng > 0:
            signal = "🔴 Short Buildup (Bearish)"
            ce_bearish += 1
            ce_data.append({"Strike": strike, "Price": "↓", "OI": "↑", "Signal": signal})
        elif price_chng > 0 and oi_chng < 0:
            signal = "🟢 Short Covering (Bullish)"
            ce_bullish += 1
            ce_data.append({"Strike": strike, "Price": "↑", "OI": "↓", "Signal": signal})
        elif price_chng < 0 and oi_chng < 0:
            signal = "🔴 Long Unwinding (Bearish)"
            ce_bearish += 1
            ce_data.append({"Strike": strike, "Price": "↓", "OI": "↓", "Signal": signal})
        else:
            signal = "⚪ Neutral"
            ce_data.append({"Strike": strike, "Price": "=", "OI": "=", "Signal": signal})
    
    # ============================================================
    # 3. PE BUILDUP (20 Strikes)
    # ============================================================
    pe_data = []
    pe_bullish = 0
    pe_bearish = 0
    
    for i in range(1, len(df)):
        strike = float(df['STRIKE'].iloc[i])
        price_chng = pe_pc.iloc[i]
        oi_chng = pe_chng.iloc[i]
        
        if pd.isna(price_chng) or pd.isna(oi_chng):
            continue
        
        if price_chng > 0 and oi_chng > 0:
            signal = "🔴 Long Buildup (Bearish for market)"
            pe_bearish += 1
            pe_data.append({"Strike": strike, "Price": "↑", "OI": "↑", "Signal": signal})
        elif price_chng < 0 and oi_chng > 0:
            signal = "🟢 Short Buildup (Bullish for market)"
            pe_bullish += 1
            pe_data.append({"Strike": strike, "Price": "↓", "OI": "↑", "Signal": signal})
        elif price_chng > 0 and oi_chng < 0:
            signal = "🔴 Short Covering (Bearish for market)"
            pe_bearish += 1
            pe_data.append({"Strike": strike, "Price": "↑", "OI": "↓", "Signal": signal})
        elif price_chng < 0 and oi_chng < 0:
            signal = "🟢 Long Unwinding (Bullish for market)"
            pe_bullish += 1
            pe_data.append({"Strike": strike, "Price": "↓", "OI": "↓", "Signal": signal})
        else:
            signal = "⚪ Neutral"
            pe_data.append({"Strike": strike, "Price": "=", "OI": "=", "Signal": signal})
    
    # ============================================================
    # 4. TOP 20 CE STRIKES
    # ============================================================
    top_ce = sorted([d for d in ce_data if d["Signal"] != "⚪ Neutral"], 
                    key=lambda x: (1 if "🟢" in x["Signal"] else 0, abs(x["Strike"] - atm)), 
                    reverse=True)[:20]
    
    # ============================================================
    # 5. TOP 20 PE STRIKES
    # ============================================================
    top_pe = sorted([d for d in pe_data if d["Signal"] != "⚪ Neutral"], 
                    key=lambda x: (1 if "🟢" in x["Signal"] else 0, abs(x["Strike"] - atm)), 
                    reverse=True)[:20]
    
    # ============================================================
    # 6. COUNT BULLISH/BEARISH FROM TOP 20
    # ============================================================
    ce_bull_count = len([d for d in top_ce if "🟢" in d["Signal"]])
    ce_bear_count = len([d for d in top_ce if "🔴" in d["Signal"]])
    
    pe_bull_count = len([d for d in top_pe if "🟢" in d["Signal"]])
    pe_bear_count = len([d for d in top_pe if "🔴" in d["Signal"]])
    
    total_bullish = ce_bull_count + pe_bull_count
    total_bearish = ce_bear_count + pe_bear_count
    
    # ============================================================
    # 7. BIAS DECISION
    # ============================================================
    if total_bearish > total_bullish * 5:
        bias, score, color = "STRONG BEARISH", 13, "🔴"
    elif total_bearish > total_bullish * 3:
        bias, score, color = "STRONG BEARISH", 18, "🔴"
    elif total_bearish > total_bullish * 2:
        bias, score, color = "BEARISH", 30, "🔴"
    elif total_bearish > total_bullish:
        bias, score, color = "WEAK BEARISH", 40, "🟠"
    elif total_bullish > total_bearish * 2:
        bias, score, color = "STRONG BULLISH", 85, "🟢"
    elif total_bullish > total_bearish:
        bias, score, color = "BULLISH", 70, "🟢"
    else:
        bias, score, color = "NEUTRAL", 50, "⚪"
    
    # ============================================================
    # 8. STORE IN SESSION
    # ============================================================
    st.session_state.buildup_result = {
        'buildup_bias': bias,
        'bias_score': score,
        'bias_text': f'Bullish: {total_bullish}, Bearish: {total_bearish}',
        'total_bullish': total_bullish,
        'total_bearish': total_bearish,
        'ce_bull_count': ce_bull_count,
        'ce_bear_count': ce_bear_count,
        'pe_bull_count': pe_bull_count,
        'pe_bear_count': pe_bear_count
    }
    
    # ============================================================
    # 9. DISPLAY
    # ============================================================
    st.markdown("""
    <div style="text-align:center;padding:10px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:12px;color:white;margin-bottom:20px;">
        <h2 style="margin:0;">📊 Price + OI / Buildup Analysis</h2>
        <p style="margin:0;opacity:0.9;">Top 20 CE + Top 20 PE Buildup Signals</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ============================================================
    # TOP 20 CE STRIKES
    # ============================================================
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Top 20 CE Buildup")
        
        for d in top_ce[:10]:
            st.write(f"{d['Signal']} **₹{d['Strike']:,.0f}** (P:{d['Price']} OI:{d['OI']})")
        
        if len(top_ce) > 10:
            with st.expander(f"View {len(top_ce)-10} more CE strikes"):
                for d in top_ce[10:]:
                    st.write(f"{d['Signal']} **₹{d['Strike']:,.0f}** (P:{d['Price']} OI:{d['OI']})")
        
        st.metric("CE Bullish", ce_bull_count, delta="🟢")
        st.metric("CE Bearish", ce_bear_count, delta="🔴")
    
    # ============================================================
    # TOP 20 PE STRIKES
    # ============================================================
    with col2:
        st.markdown("### 📉 Top 20 PE Buildup")
        
        for d in top_pe[:10]:
            st.write(f"{d['Signal']} **₹{d['Strike']:,.0f}** (P:{d['Price']} OI:{d['OI']})")
        
        if len(top_pe) > 10:
            with st.expander(f"View {len(top_pe)-10} more PE strikes"):
                for d in top_pe[10:]:
                    st.write(f"{d['Signal']} **₹{d['Strike']:,.0f}** (P:{d['Price']} OI:{d['OI']})")
        
        st.metric("PE Bullish (Market)", pe_bull_count, delta="🟢")
        st.metric("PE Bearish (Market)", pe_bear_count, delta="🔴")
    
    st.markdown("---")
    
    # ============================================================
    # FINAL DECISION
    # ============================================================
    st.subheader("🏆 Final Buildup Decision")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🟢 Total Bullish", total_bullish)
    with col2:
        st.metric("🔴 Total Bearish", total_bearish)
    with col3:
        st.metric("Final Bias", f"{color} {bias}", delta=f"Score: {score:.0f}")
    
    # ✅ FIXED: Progress bar with correct 0-1 range
    if total_bullish == 0 and total_bearish == 0:
        progress_val = 0.5
        progress_text = "No signals"
    elif total_bullish > total_bearish:
        # Bullish dominant: show bullish percentage
        progress_val = min(total_bullish / (total_bullish + total_bearish), 1.0)
        progress_text = f"Bullish: {total_bullish} ({progress_val*100:.0f}%)"
    else:
        # Bearish dominant: show bearish percentage
        progress_val = total_bullish / (total_bullish + total_bearish) if (total_bullish + total_bearish) > 0 else 0.5
        progress_text = f"Bullish: {total_bullish}/{total_bearish} ({progress_val*100:.0f}%)"
    
    st.progress(progress_val, text=progress_text)
    
    st.info(f"**Result:** {bias} - Bullish: {total_bullish}, Bearish: {total_bearish}")
    
    st.markdown("---")
    
    # ============================================================
    # BUILDUP GUIDE
    # ============================================================
    with st.expander("📖 Buildup Guide"):
        st.markdown("""
        ### 📊 Buildup Rules
        
        | # | Price | OI | CE Interpretation | PE Interpretation | Market Signal |
        |---|-------|-----|-------------------|-------------------|---------------|
        | 1 | ↑ | ↑ | Long Buildup | Long Buildup | CE: 🟢 Bullish, PE: 🔴 Bearish |
        | 2 | ↓ | ↑ | Short Buildup | Short Buildup | CE: 🔴 Bearish, PE: 🟢 Bullish |
        | 3 | ↑ | ↓ | Short Covering | Short Covering | CE: 🟢 Bullish, PE: 🔴 Bearish |
        | 4 | ↓ | ↓ | Long Unwinding | Long Unwinding | CE: 🔴 Bearish, PE: 🟢 Bullish |
        
        **PE interpretation is opposite to CE because:**
        - Put price ↑ + Put OI ↑ = More put buying = Bearish for market
        - Put price ↓ + Put OI ↑ = More put selling = Bullish for market
        """)
    
    # ============================================================
    # CHART
    # ============================================================
    st.subheader("📊 Buildup Distribution")
    
    fig = go.Figure()
    
    ce_bull = len([d for d in top_ce if "🟢" in d["Signal"]])
    ce_bear = len([d for d in top_ce if "🔴" in d["Signal"]])
    pe_bull = len([d for d in top_pe if "🟢" in d["Signal"]])
    pe_bear = len([d for d in top_pe if "🔴" in d["Signal"]])
    
    fig.add_trace(go.Bar(
        x=['CE Bullish', 'CE Bearish', 'PE Bullish', 'PE Bearish'],
        y=[ce_bull, ce_bear, pe_bull, pe_bear],
        marker_color=['#00cc66', '#ff4444', '#00cc66', '#ff4444'],
        text=[ce_bull, ce_bear, pe_bull, pe_bear],
        textposition='auto',
        textfont=dict(color='white', size=14)
    ))
    
    fig.update_layout(
        xaxis_title="Buildup Type",
        yaxis_title="Count (Top 20)",
        height=350,
        template="plotly_dark",
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#8892b0'
    )
    
    st.plotly_chart(fig, width='stretch')
    
    # ============================================================
    # STRIKE-WISE DETAILED TABLE
    # ============================================================
    with st.expander("📋 Full Strike-wise Buildup Table"):
        
        all_data = []
        for d in ce_data:
            all_data.append({
                "Strike": f"₹{d['Strike']:,.0f}",
                "Type": "CE",
                "Price": d['Price'],
                "OI": d['OI'],
                "Signal": d['Signal'],
                "Top 20": "✅" if d in top_ce else ""
            })
        
        for d in pe_data:
            all_data.append({
                "Strike": f"₹{d['Strike']:,.0f}",
                "Type": "PE",
                "Price": d['Price'],
                "OI": d['OI'],
                "Signal": d['Signal'],
                "Top 20": "✅" if d in top_pe else ""
            })
        
        st.dataframe(pd.DataFrame(all_data), width='stretch', height=400)

show_buildup_analysis()