import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def show_support_resistance():
    df = st.session_state.get('df')
    if df is None:
        st.warning("⚠️ Upload CSV first")
        return
    
    # Find ATM
    total_vol = df['CE_VOLUME'] + df['PE_VOLUME']
    atm = df.loc[total_vol.idxmax(), 'STRIKE'] if total_vol.max() > 0 else df['STRIKE'].iloc[len(df)//2]
    
    ce_oi = pd.to_numeric(df['CE_OI'], errors='coerce').fillna(0)
    pe_oi = pd.to_numeric(df['PE_OI'], errors='coerce').fillna(0)
    
    below = df[df['STRIKE'] < atm]
    above = df[df['STRIKE'] > atm]
    
    if len(below) > 0:
        support = below.loc[below['PE_OI'].idxmax(), 'STRIKE']
        sup_oi = below['PE_OI'].max()
    else:
        support, sup_oi = atm, 0
    
    if len(above) > 0:
        resistance = above.loc[above['CE_OI'].idxmax(), 'STRIKE']
        res_oi = above['CE_OI'].max()
    else:
        resistance, res_oi = atm, 0
    
    if sup_oi > res_oi * 1.5:
        bias, score = "BULLISH", 75
    elif sup_oi > res_oi:
        bias, score = "WEAK BULLISH", 60
    elif res_oi > sup_oi * 1.5:
        bias, score = "BEARISH", 30
    elif res_oi > sup_oi:
        bias, score = "WEAK BEARISH", 40
    else:
        bias, score = "NEUTRAL", 50
    
    st.session_state.sr_result = {
        'bias': bias, 'bias_score': score,
        'bias_text': f'S: {support:,.0f}, R: {resistance:,.0f}',
        'support_strike': float(support), 'resistance_strike': float(resistance)
    }
    
    st.markdown("### 🎯 Support/Resistance")
    col1, col2, col3 = st.columns(3)
    col1.metric("🛡️ Support", f"₹{support:,.0f}", delta=f"OI: {sup_oi:,.0f}")
    col2.metric("⚔️ Resistance", f"₹{resistance:,.0f}", delta=f"OI: {res_oi:,.0f}")
    col3.metric("Bias", bias, delta=f"Score: {score}")
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['STRIKE'], y=df['CE_OI'], name='CE', marker_color='#00cc66', opacity=0.6))
    fig.add_trace(go.Bar(x=df['STRIKE'], y=df['PE_OI'], name='PE', marker_color='#ff4444', opacity=0.6))
    fig.add_vline(x=support, line_dash="dash", line_color="green", annotation_text=f"S {support:,.0f}")
    fig.add_vline(x=resistance, line_dash="dash", line_color="red", annotation_text=f"R {resistance:,.0f}")
    fig.add_vline(x=atm, line_dash="dash", line_color="yellow", annotation_text=f"ATM {atm:,.0f}")
    fig.update_layout(height=350, template="plotly_dark", barmode='group')
    st.plotly_chart(fig, width='stretch')

show_support_resistance()