import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def show_change_oi_analysis():
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
    # 1. TOTAL CHANGE OI
    # ============================================================
    ce_chng = pd.to_numeric(df['CE_CHNG_IN_OI'], errors='coerce').fillna(0)
    pe_chng = pd.to_numeric(df['PE_CHNG_IN_OI'], errors='coerce').fillna(0)
    
    total_ce_chng = ce_chng.sum()
    total_pe_chng = pe_chng.sum()
    
    # ============================================================
    # 2. TOP 5 CE CHANGE STRIKES (Call Writing = Bearish)
    # ============================================================
    top_ce_chng = df.nlargest(5, 'CE_CHNG_IN_OI')[['STRIKE', 'CE_CHNG_IN_OI']]
    top_ce_chng_list = top_ce_chng.values.tolist()
    
    # ============================================================
    # 3. TOP 5 PE CHANGE STRIKES (Put Writing = Bullish)
    # ============================================================
    top_pe_chng = df.nlargest(5, 'PE_CHNG_IN_OI')[['STRIKE', 'PE_CHNG_IN_OI']]
    top_pe_chng_list = top_pe_chng.values.tolist()
    
    # ============================================================
    # 4. STRIKE-WISE DECISION
    # ============================================================
    # CE Change = Call Writing (Bearish)
    # PE Change = Put Writing (Bullish)
    
    # Check where OI is increasing (Writing)
    ce_writing = [s for s, _ in top_ce_chng_list if _ > 0]  # CE OI increasing = Call Writing = Bearish
    pe_writing = [s for s, _ in top_pe_chng_list if _ > 0]  # PE OI increasing = Put Writing = Bullish
    
    # Check where OI is decreasing (Unwinding)
    ce_unwinding = [s for s, _ in top_ce_chng_list if _ < 0]  # CE OI decreasing = Call Unwinding = Bullish
    pe_unwinding = [s for s, _ in top_pe_chng_list if _ < 0]  # PE OI decreasing = Put Unwinding = Bearish
    
    # ============================================================
    # 5. BIAS DECISION
    # ============================================================
    # Based on Total Change
    if total_ce_chng > 0 and total_pe_chng > 0:
        if total_ce_chng > total_pe_chng * 2:
            total_bias, total_score, total_color = "STRONG BEARISH", 15, "🔴"
        elif total_ce_chng > total_pe_chng * 1.3:
            total_bias, total_score, total_color = "BEARISH", 30, "🔴"
        elif total_ce_chng > total_pe_chng:
            total_bias, total_score, total_color = "WEAK BEARISH", 40, "🟠"
        elif total_pe_chng > total_ce_chng * 2:
            total_bias, total_score, total_color = "STRONG BULLISH", 90, "🟢"
        elif total_pe_chng > total_ce_chng * 1.3:
            total_bias, total_score, total_color = "BULLISH", 75, "🟢"
        elif total_pe_chng > total_ce_chng:
            total_bias, total_score, total_color = "WEAK BULLISH", 60, "🟢"
        else:
            total_bias, total_score, total_color = "NEUTRAL", 50, "⚪"
    elif total_pe_chng > 0 and total_ce_chng <= 0:
        total_bias, total_score, total_color = "BULLISH", 80, "🟢"
    elif total_ce_chng > 0 and total_pe_chng <= 0:
        total_bias, total_score, total_color = "BEARISH", 20, "🔴"
    else:
        total_bias, total_score, total_color = "NEUTRAL", 50, "⚪"
    
    # Based on Strike Positions
    ce_writing_count = len(ce_writing)  # Call Writing = Bearish
    pe_writing_count = len(pe_writing)  # Put Writing = Bullish
    
    if ce_writing_count >= 4 and pe_writing_count <= 2:
        strike_bias = "BEARISH"
        strike_color = "🔴"
        strike_text = f"Call Writing: {ce_writing_count} strikes (Bearish)"
    elif pe_writing_count >= 4 and ce_writing_count <= 2:
        strike_bias = "BULLISH"
        strike_color = "🟢"
        strike_text = f"Put Writing: {pe_writing_count} strikes (Bullish)"
    elif ce_writing_count >= 3 and pe_writing_count >= 3:
        strike_bias = "NEUTRAL"
        strike_color = "⚪"
        strike_text = f"Balanced: CE {ce_writing_count}, PE {pe_writing_count}"
    else:
        strike_bias = "NEUTRAL"
        strike_color = "⚪"
        strike_text = f"Mixed signals"
    
    # Final Bias = Combine Total + Strike Bias
    if total_bias in ["BULLISH", "WEAK BULLISH"] and strike_bias == "BULLISH":
        final_bias, final_score, final_color = "STRONG BULLISH", 90, "🟢"
    elif total_bias in ["BEARISH", "WEAK BEARISH"] and strike_bias == "BEARISH":
        final_bias, final_score, final_color = "STRONG BEARISH", 15, "🔴"
    elif total_bias in ["BULLISH", "WEAK BULLISH"] or strike_bias == "BULLISH":
        final_bias, final_score, final_color = "BULLISH", 75, "🟢"
    elif total_bias in ["BEARISH", "WEAK BEARISH"] or strike_bias == "BEARISH":
        final_bias, final_score, final_color = "BEARISH", 30, "🔴"
    else:
        final_bias, final_score, final_color = "NEUTRAL", 50, "⚪"
    
    # ============================================================
    # 6. STORE IN SESSION
    # ============================================================
    st.session_state.change_oi_result = {
        'final_bias': final_bias,
        'bias_score': final_score,
        'total_ce_chng': total_ce_chng,
        'total_pe_chng': total_pe_chng,
        'bias_text': f'CE: {total_ce_chng:+.0f}, PE: {total_pe_chng:+.0f} | CE Writing: {ce_writing_count}, PE Writing: {pe_writing_count}'
    }
    
    # ============================================================
    # 7. DISPLAY
    # ============================================================
    st.markdown("""
    <div style="text-align:center;padding:10px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:12px;color:white;margin-bottom:20px;">
        <h2 style="margin:0;">🔄 Change OI Analysis</h2>
        <p style="margin:0;opacity:0.9;">Top 5 CE Change (Call Writing) | Top 5 PE Change (Put Writing)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ============================================================
    # TOP 5 CE CHANGE (Call Writing = Bearish)
    # ============================================================
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Top 5 CE Change (Call Writing)")
        st.caption("🔴 CE OI ↑ = Call Writing (Bearish)")
        
        for strike, chng in top_ce_chng_list:
            signal = "🔴 Writing" if chng > 0 else "🟢 Unwinding"
            color = "🔴" if chng > 0 else "🟢"
            st.write(f"{color} **₹{strike:,.0f}** : {chng:+,.0f} ({signal})")
        
        st.metric("CE Writing Count", f"{ce_writing_count}/5", delta="Bearish" if ce_writing_count >= 3 else "Neutral")
    
    # ============================================================
    # TOP 5 PE CHANGE (Put Writing = Bullish)
    # ============================================================
    with col2:
        st.markdown("### 📉 Top 5 PE Change (Put Writing)")
        st.caption("🟢 PE OI ↑ = Put Writing (Bullish)")
        
        for strike, chng in top_pe_chng_list:
            signal = "🟢 Writing" if chng > 0 else "🔴 Unwinding"
            color = "🟢" if chng > 0 else "🔴"
            st.write(f"{color} **₹{strike:,.0f}** : {chng:+,.0f} ({signal})")
        
        st.metric("PE Writing Count", f"{pe_writing_count}/5", delta="Bullish" if pe_writing_count >= 3 else "Neutral")
    
    st.markdown("---")
    
    # ============================================================
    # STRIKE-WISE DECISION SUMMARY
    # ============================================================
    st.subheader("🎯 Strike-wise Decision")
    
    strike_data = []
    for strike, chng in top_ce_chng_list:
        strike_data.append({
            "Strike": f"₹{strike:,.0f}",
            "Type": "CE",
            "Change": f"{chng:+,.0f}",
            "Signal": "🔴 Call Writing (Bearish)" if chng > 0 else "🟢 Call Unwinding (Bullish)"
        })
    
    for strike, chng in top_pe_chng_list:
        strike_data.append({
            "Strike": f"₹{strike:,.0f}",
            "Type": "PE",
            "Change": f"{chng:+,.0f}",
            "Signal": "🟢 Put Writing (Bullish)" if chng > 0 else "🔴 Put Unwinding (Bearish)"
        })
    
    st.dataframe(pd.DataFrame(strike_data), width='stretch', hide_index=True)
    
    st.markdown("---")
    
    # ============================================================
    # FINAL DECISION
    # ============================================================
    st.subheader("🏆 Final Change OI Decision")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("CE Change", f"{total_ce_chng:+,.0f}")
    with col2:
        st.metric("PE Change", f"{total_pe_chng:+,.0f}")
    with col3:
        st.metric("Strike Bias", f"{strike_color} {strike_bias}")
    with col4:
        st.metric("Final Decision", f"{final_color} {final_bias}", delta=f"Score: {final_score:.0f}")
    
    st.info(f"**{strike_text}**")
    
    # ============================================================
    # CHANGE OI CHART
    # ============================================================
    st.subheader("📊 Change in OI Distribution")
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['STRIKE'],
        y=df['CE_CHNG_IN_OI'],
        name='CE Change',
        marker_color='#00cc66',
        opacity=0.7
    ))
    
    fig.add_trace(go.Bar(
        x=df['STRIKE'],
        y=df['PE_CHNG_IN_OI'],
        name='PE Change',
        marker_color='#ff4444',
        opacity=0.7
    ))
    
    # ATM Line
    fig.add_vline(x=atm, line_dash="dash", line_color="yellow", annotation_text=f"ATM {atm:,.0f}")
    
    # Top CE Change Strikes
    for strike, _ in top_ce_chng_list:
        fig.add_vline(x=strike, line_dash="dot", line_color="red", opacity=0.5)
    
    # Top PE Change Strikes
    for strike, _ in top_pe_chng_list:
        fig.add_vline(x=strike, line_dash="dot", line_color="green", opacity=0.5)
    
    # Zero line
    fig.add_hline(y=0, line_dash="dash", line_color="white", annotation_text="Neutral")
    
    fig.update_layout(
        xaxis_title="Strike Price",
        yaxis_title="Change in OI",
        height=400,
        template="plotly_dark",
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#8892b0'
    )
    
    st.plotly_chart(fig, width='stretch')

show_change_oi_analysis()