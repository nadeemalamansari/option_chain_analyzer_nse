import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def show_pcr_analysis():
    df = st.session_state.get('df')
    if df is None:
        st.warning("⚠️ Upload CSV first")
        return
    
    # Find ATM
    total_vol = df['CE_VOLUME'] + df['PE_VOLUME']
    atm = df.loc[total_vol.idxmax(), 'STRIKE'] if total_vol.max() > 0 else df['STRIKE'].iloc[len(df)//2]
    
    # ============================================================
    # 1. OI PCR = PE OI / CE OI
    # ============================================================
    ce_oi = pd.to_numeric(df['CE_OI'], errors='coerce').fillna(0).sum()
    pe_oi = pd.to_numeric(df['PE_OI'], errors='coerce').fillna(0).sum()
    oi_pcr = pe_oi / ce_oi if ce_oi > 0 else 0
    
    # ============================================================
    # 2. Volume PCR = PE VOLUME / CE VOLUME
    # ============================================================
    ce_vol = pd.to_numeric(df['CE_VOLUME'], errors='coerce').fillna(0).sum()
    pe_vol = pd.to_numeric(df['PE_VOLUME'], errors='coerce').fillna(0).sum()
    vol_pcr = pe_vol / ce_vol if ce_vol > 0 else 0
    
    # ============================================================
    # 3. ATM PCR = PE OI / CE OI at ATM
    # ============================================================
    atm_data = df[df['STRIKE'] == atm]
    if len(atm_data) > 0:
        atm_ce = pd.to_numeric(atm_data['CE_OI'], errors='coerce').fillna(0).sum()
        atm_pe = pd.to_numeric(atm_data['PE_OI'], errors='coerce').fillna(0).sum()
        atm_pcr = atm_pe / atm_ce if atm_ce > 0 else 0
    else:
        atm_pcr = 0
    
    # ============================================================
    # 4. PCR Status (Based on OI PCR)
    # ============================================================
    if oi_pcr < 0.7:
        bias, score, color, txt = "BEARISH", 30, "🔴", "Put OI कम, Call OI ज्यादा"
    elif oi_pcr < 0.9:
        bias, score, color, txt = "WEAK BEARISH", 40, "🟠", "Bearish pressure, moderate"
    elif oi_pcr < 1.1:
        bias, score, color, txt = "NEUTRAL", 50, "⚪", "Put और Call OI balanced"
    elif oi_pcr < 1.3:
        bias, score, color, txt = "WEAK BULLISH", 60, "🟢", "Put OI ज्यादा, bullish support"
    else:
        bias, score, color, txt = "BULLISH", 70, "🟢", "Put OI काफी ज्यादा"
    
    # Store in session
    st.session_state.pcr_result = {
        'final_bias': bias,
        'pcr_score': score,
        'oi_pcr': oi_pcr,
        'vol_pcr': vol_pcr,
        'atm_pcr': atm_pcr,
        'primary_text': f'OI PCR: {oi_pcr:.2f}, Volume PCR: {vol_pcr:.2f}, ATM PCR: {atm_pcr:.2f}'
    }
    
    # ============================================================
    # DISPLAY
    # ============================================================
    st.markdown("""
    <div style="text-align:center;padding:10px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:12px;color:white;margin-bottom:20px;">
        <h2 style="margin:0;">📉 PCR Analysis</h2>
        <p style="margin:0;opacity:0.9;">OI PCR | Volume PCR | ATM PCR</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 3 PCR Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 OI PCR", f"{oi_pcr:.2f}")
    with col2:
        st.metric("📊 Volume PCR", f"{vol_pcr:.2f}")
    with col3:
        st.metric("📊 ATM PCR", f"{atm_pcr:.2f}")
    
    # Status
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Status", f"{color} {bias}")
    with col2:
        st.metric("Score", f"{score:.0f}/100")
    
    st.info(f"**{txt}**")
    
    # ============================================================
    # PCR COMPARISON CHART
    # ============================================================
    st.subheader("📊 PCR Comparison")
    
    fig = go.Figure()
    
    # Colors based on PCR value
    colors = []
    for val in [oi_pcr, vol_pcr, atm_pcr]:
        if val >= 1.3:
            colors.append('#00cc66')
        elif val >= 1.1:
            colors.append('#88dd88')
        elif val >= 0.9:
            colors.append('#ffaa00')
        elif val >= 0.7:
            colors.append('#ff8800')
        else:
            colors.append('#ff4444')
    
    fig.add_trace(go.Bar(
        x=['OI PCR', 'Volume PCR', 'ATM PCR'],
        y=[oi_pcr, vol_pcr, atm_pcr],
        marker_color=colors,
        text=[f"{oi_pcr:.2f}", f"{vol_pcr:.2f}", f"{atm_pcr:.2f}"],
        textposition='auto',
        textfont=dict(color='white', size=14)
    ))
    
    # Neutral line
    fig.add_hline(y=1.0, line_dash="dash", line_color="white", annotation_text="Neutral (1.0)")
    
    # Zones
    fig.add_hrect(y0=1.3, y1=2.5, fillcolor="rgba(0,200,83,0.15)", annotation_text="BULLISH", annotation_font_color="green")
    fig.add_hrect(y0=0.7, y1=1.3, fillcolor="rgba(255,214,0,0.1)", annotation_text="NEUTRAL", annotation_font_color="yellow")
    fig.add_hrect(y0=0, y1=0.7, fillcolor="rgba(255,23,68,0.15)", annotation_text="BEARISH", annotation_font_color="red")
    
    fig.update_layout(
        xaxis_title="PCR Type",
        yaxis_title="PCR Value",
        height=350,
        template="plotly_dark",
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#8892b0'
    )
    
    st.plotly_chart(fig, width='stretch')
    
    # ============================================================
    # PCR STATUS SUMMARY
    # ============================================================
    st.markdown("### 📊 PCR Status Summary")
    
    def get_status(val):
        if val >= 1.3:
            return "🟢 BULLISH"
        elif val >= 1.1:
            return "🟢 WEAK BULLISH"
        elif val >= 0.9:
            return "⚪ NEUTRAL"
        elif val >= 0.7:
            return "🟠 WEAK BEARISH"
        else:
            return "🔴 BEARISH"
    
    summary = pd.DataFrame([
        ["OI PCR", f"{oi_pcr:.2f}", get_status(oi_pcr), "PE OI / CE OI"],
        ["Volume PCR", f"{vol_pcr:.2f}", get_status(vol_pcr), "PE Volume / CE Volume"],
        ["ATM PCR", f"{atm_pcr:.2f}", get_status(atm_pcr), f"PCR at ATM ({atm:,.0f})"],
        ["Final Status", f"{color} {bias}", "", txt]
    ], columns=["Metric", "Value", "Status", "Description"])
    
    st.dataframe(summary, width='stretch', hide_index=True)
    
    # ============================================================
    # PCR RULES TABLE
    # ============================================================
    st.markdown("### 📊 PCR Rules")
    
    rules = [
        ["< 0.70", "🔴", "BEARISH", "Put OI कम, Call OI ज्यादा"],
        ["0.70 - 0.90", "🟠", "WEAK BEARISH", "Bearish pressure, moderate"],
        ["0.90 - 1.10", "⚪", "NEUTRAL", "Put और Call OI balanced"],
        ["1.10 - 1.30", "🟢", "WEAK BULLISH", "Put OI ज्यादा, bullish support"],
        ["> 1.30", "🟢", "BULLISH", "Put OI काफी ज्यादा"]
    ]
    
    rules_df = pd.DataFrame(rules, columns=["PCR Value", "Signal", "Status", "Meaning"])
    
    def highlight(row):
        if row["Status"] == bias:
            return ['background-color: #2a2a4a; color: #64ffda; font-weight: bold'] * len(row)
        return [''] * len(row)
    
    st.dataframe(rules_df.style.apply(highlight, axis=1), width='stretch', hide_index=True)

show_pcr_analysis()