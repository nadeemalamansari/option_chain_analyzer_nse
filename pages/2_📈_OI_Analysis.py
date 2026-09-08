import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def show_oi_analysis():
    df = st.session_state.get('df')
    if df is None:
        st.warning("⚠️ Upload CSV first")
        return
    
    # Find ATM
    total_vol = df['CE_VOLUME'] + df['PE_VOLUME']
    atm = df.loc[total_vol.idxmax(), 'STRIKE'] if total_vol.max() > 0 else df['STRIKE'].iloc[len(df)//2]
    
    # ============================================================
    # 1. OI PCR (Overall)
    # ============================================================
    ce_oi = pd.to_numeric(df['CE_OI'], errors='coerce').fillna(0)
    pe_oi = pd.to_numeric(df['PE_OI'], errors='coerce').fillna(0)
    
    total_ce = ce_oi.sum()
    total_pe = pe_oi.sum()
    oi_pcr = total_pe / total_ce if total_ce > 0 else 0
    
    # ============================================================
    # 2. TOP 5 CE STRIKES (Resistance)
    # ============================================================
    top_ce = df.nlargest(5, 'CE_OI')[['STRIKE', 'CE_OI']]
    top_ce_list = top_ce.values.tolist()
    
    # ============================================================
    # 3. TOP 5 PE STRIKES (Support)
    # ============================================================
    top_pe = df.nlargest(5, 'PE_OI')[['STRIKE', 'PE_OI']]
    top_pe_list = top_pe.values.tolist()
    
    # ============================================================
    # 4. STRIKE-WISE DECISION
    # ============================================================
    # CE Strikes = Resistance (Bearish signal)
    # PE Strikes = Support (Bullish signal)
    
    ce_bearish_strikes = [s for s, _ in top_ce_list]
    pe_bullish_strikes = [s for s, _ in top_pe_list]
    
    # Check if CE strikes are above ATM (Resistance) or below ATM
    ce_above_atm = [s for s in ce_bearish_strikes if s > atm]
    ce_below_atm = [s for s in ce_bearish_strikes if s < atm]
    
    # Check if PE strikes are below ATM (Support) or above ATM
    pe_below_atm = [s for s in pe_bullish_strikes if s < atm]
    pe_above_atm = [s for s in pe_bullish_strikes if s > atm]
    
    # ============================================================
    # 5. BIAS DECISION
    # ============================================================
    # Based on PCR
    if oi_pcr < 0.7:
        pcr_bias, pcr_score, pcr_color = "BEARISH", 30, "🔴"
    elif oi_pcr < 0.9:
        pcr_bias, pcr_score, pcr_color = "WEAK BEARISH", 40, "🟠"
    elif oi_pcr < 1.1:
        pcr_bias, pcr_score, pcr_color = "NEUTRAL", 50, "⚪"
    elif oi_pcr < 1.3:
        pcr_bias, pcr_score, pcr_color = "WEAK BULLISH", 60, "🟢"
    else:
        pcr_bias, pcr_score, pcr_color = "BULLISH", 70, "🟢"
    
    # Based on Strike Positions
    # More CE above ATM = Bearish (Resistance)
    # More PE below ATM = Bullish (Support)
    ce_bearish_count = len(ce_above_atm)
    pe_bullish_count = len(pe_below_atm)
    
    if ce_bearish_count >= 4 and pe_bullish_count <= 2:
        strike_bias = "BEARISH"
        strike_color = "🔴"
        strike_text = f"CE Resistance: {ce_bearish_count} strikes above ATM"
    elif pe_bullish_count >= 4 and ce_bearish_count <= 2:
        strike_bias = "BULLISH"
        strike_color = "🟢"
        strike_text = f"PE Support: {pe_bullish_count} strikes below ATM"
    elif ce_bearish_count >= 3 and pe_bullish_count >= 3:
        strike_bias = "NEUTRAL"
        strike_color = "⚪"
        strike_text = f"Balanced: CE {ce_bearish_count} above, PE {pe_bullish_count} below"
    else:
        strike_bias = "NEUTRAL"
        strike_color = "⚪"
        strike_text = f"Mixed signals"
    
    # Final Bias = Combine PCR + Strike Bias
    if pcr_bias in ["BULLISH", "WEAK BULLISH"] and strike_bias == "BULLISH":
        final_bias, final_score, final_color = "STRONG BULLISH", 85, "🟢"
    elif pcr_bias in ["BEARISH", "WEAK BEARISH"] and strike_bias == "BEARISH":
        final_bias, final_score, final_color = "STRONG BEARISH", 15, "🔴"
    elif pcr_bias in ["BULLISH", "WEAK BULLISH"] or strike_bias == "BULLISH":
        final_bias, final_score, final_color = "BULLISH", 70, "🟢"
    elif pcr_bias in ["BEARISH", "WEAK BEARISH"] or strike_bias == "BEARISH":
        final_bias, final_score, final_color = "BEARISH", 30, "🔴"
    else:
        final_bias, final_score, final_color = "NEUTRAL", 50, "⚪"
    
    # ============================================================
    # 6. STORE IN SESSION
    # ============================================================
    st.session_state.oi_result = {
        'final_bias': final_bias,
        'bias_score': final_score,
        'oi_pcr': oi_pcr,
        'total_ce_oi': total_ce,
        'total_pe_oi': total_pe,
        'imbalance_text': f'PCR: {oi_pcr:.2f} | CE: {len(ce_above_atm)} above ATM | PE: {len(pe_below_atm)} below ATM'
    }
    
    # ============================================================
    # 7. DISPLAY
    # ============================================================
    st.markdown("""
    <div style="text-align:center;padding:10px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:12px;color:white;margin-bottom:20px;">
        <h2 style="margin:0;">📉 OI Analysis</h2>
        <p style="margin:0;opacity:0.9;">Top 5 CE Strikes (Resistance) | Top 5 PE Strikes (Support)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ============================================================
    # TOP 5 CE STRIKES (Resistance - Bearish)
    # ============================================================
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Top 5 CE Strikes (Resistance)")
        st.caption("🔴 High CE OI = Resistance (Bearish)")
        
        for strike, oi in top_ce_list:
            above = "⬆️ Above ATM" if strike > atm else "⬇️ Below ATM"
            color = "🔴" if strike > atm else "🟡"
            st.write(f"{color} **₹{strike:,.0f}** : {oi:,.0f} ({above})")
        
        st.metric("CE Above ATM", f"{len(ce_above_atm)}/5", delta="Bearish Signal" if len(ce_above_atm) >= 3 else "Neutral")
    
    # ============================================================
    # TOP 5 PE STRIKES (Support - Bullish)
    # ============================================================
    with col2:
        st.markdown("### 📊 Top 5 PE Strikes (Support)")
        st.caption("🟢 High PE OI = Support (Bullish)")
        
        for strike, oi in top_pe_list:
            below = "⬇️ Below ATM" if strike < atm else "⬆️ Above ATM"
            color = "🟢" if strike < atm else "🟡"
            st.write(f"{color} **₹{strike:,.0f}** : {oi:,.0f} ({below})")
        
        st.metric("PE Below ATM", f"{len(pe_below_atm)}/5", delta="Bullish Signal" if len(pe_below_atm) >= 3 else "Neutral")
    
    st.markdown("---")
    
    # ============================================================
    # STRIKE-WISE DECISION SUMMARY
    # ============================================================
    st.subheader("🎯 Strike-wise Decision")
    
    strike_data = []
    for strike, oi in top_ce_list:
        strike_data.append({
            "Strike": f"₹{strike:,.0f}",
            "Type": "CE",
            "OI": f"{oi:,.0f}",
            "Position": "⬆️ Above ATM" if strike > atm else "⬇️ Below ATM",
            "Signal": "🔴 Resistance (Bearish)" if strike > atm else "🟡 Neutral"
        })
    
    for strike, oi in top_pe_list:
        strike_data.append({
            "Strike": f"₹{strike:,.0f}",
            "Type": "PE",
            "OI": f"{oi:,.0f}",
            "Position": "⬇️ Below ATM" if strike < atm else "⬆️ Above ATM",
            "Signal": "🟢 Support (Bullish)" if strike < atm else "🟡 Neutral"
        })
    
    st.dataframe(pd.DataFrame(strike_data), width='stretch', hide_index=True)
    
    st.markdown("---")
    
    # ============================================================
    # FINAL DECISION
    # ============================================================
    st.subheader("🏆 Final OI Decision")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("OI PCR", f"{oi_pcr:.2f}")
    with col2:
        st.metric("PCR Bias", f"{pcr_color} {pcr_bias}")
    with col3:
        st.metric("Strike Bias", f"{strike_color} {strike_bias}")
    with col4:
        st.metric("Final Decision", f"{final_color} {final_bias}", delta=f"Score: {final_score:.0f}")
    
    st.info(f"**{strike_text}**")
    
    # ============================================================
    # OI CHART with ATM, Support, Resistance
    # ============================================================
    st.subheader("📊 OI Distribution")
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['STRIKE'],
        y=df['CE_OI'],
        name='CE OI',
        marker_color='#00cc66',
        opacity=0.7
    ))
    
    fig.add_trace(go.Bar(
        x=df['STRIKE'],
        y=df['PE_OI'],
        name='PE OI',
        marker_color='#ff4444',
        opacity=0.7
    ))
    
    # ATM Line
    fig.add_vline(x=atm, line_dash="dash", line_color="yellow", annotation_text=f"ATM {atm:,.0f}")
    
    # Top CE Strikes (Resistance)
    for strike, _ in top_ce_list:
        fig.add_vline(x=strike, line_dash="dot", line_color="red", opacity=0.5)
    
    # Top PE Strikes (Support)
    for strike, _ in top_pe_list:
        fig.add_vline(x=strike, line_dash="dot", line_color="green", opacity=0.5)
    
    fig.update_layout(
        xaxis_title="Strike Price",
        yaxis_title="Open Interest",
        height=400,
        template="plotly_dark",
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#8892b0'
    )
    
    st.plotly_chart(fig, width='stretch')

show_oi_analysis()