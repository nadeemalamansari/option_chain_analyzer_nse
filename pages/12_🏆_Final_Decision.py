"""
Final Decision Page - 5 Module Combined Analysis
EXACT SCORE FETCHING: Jo score module page mein dikhta hai, wahi final decision mein dikhega
"""

import streamlit as st
import pandas as pd
import numpy as np


def validate_data(df, filename):
    symbol = 'NIFTY' if 'NIFTY' in filename.upper() else 'BANKNIFTY' if 'BANKNIFTY' in filename.upper() else 'SENSEX' if 'SENSEX' in filename.upper() else 'UNKNOWN'
    total_volume = df['CE_VOLUME'] + df['PE_VOLUME']
    if total_volume.max() > 0:
        atm_idx = total_volume.idxmax()
        atm_strike = float(df.loc[atm_idx, 'STRIKE'])
    else:
        atm_strike = float(df['STRIKE'].iloc[len(df)//2])
    return {'symbol': symbol, 'atm_strike': atm_strike, 'num_strikes': len(df)}


def fetch_all_module_results():
    """Fetch results from ALL 5 modules - EXACT SCORE MATCH"""
    
    results = {}
    
    # 1. OI Analysis (22%)
    oi = st.session_state.get('oi_result', {})
    if oi and oi.get('final_bias'):
        results['oi'] = {
            'name': '📉 OI Analysis',
            'bias': oi.get('final_bias', 'NEUTRAL'),
            'score': oi.get('bias_score', 50),
            'text': oi.get('imbalance_text', 'Balanced'),
            'weight': 0.22,
            'contribution': oi.get('bias_score', 50) * 0.22,
            'status': '✅ Loaded'
        }
    else:
        results['oi'] = {
            'name': '📉 OI Analysis',
            'bias': 'NEUTRAL',
            'score': 50,
            'text': 'Not calculated - Please visit OI Analysis page',
            'weight': 0.22,
            'contribution': 11.0,
            'status': '⚠️ Not loaded'
        }
    
    # 2. Change OI Analysis (22%)
    change_oi = st.session_state.get('change_oi_result', {})
    if change_oi and change_oi.get('final_bias'):
        results['change_oi'] = {
            'name': '🔄 Change OI Analysis',
            'bias': change_oi.get('final_bias', 'NEUTRAL'),
            'score': change_oi.get('bias_score', 50),
            'text': change_oi.get('bias_text', 'Balanced'),
            'weight': 0.22,
            'contribution': change_oi.get('bias_score', 50) * 0.22,
            'status': '✅ Loaded'
        }
    else:
        results['change_oi'] = {
            'name': '🔄 Change OI Analysis',
            'bias': 'NEUTRAL',
            'score': 50,
            'text': 'Not calculated - Please visit Change OI Analysis page',
            'weight': 0.22,
            'contribution': 11.0,
            'status': '⚠️ Not loaded'
        }
    
    # 3. Price+OI Buildup (20%)
    buildup = st.session_state.get('buildup_result', {})
    if buildup and buildup.get('buildup_bias'):
        results['buildup'] = {
            'name': '📊 Price+OI Buildup',
            'bias': buildup.get('buildup_bias', 'NEUTRAL'),
            'score': buildup.get('bias_score', 50),
            'text': buildup.get('bias_text', 'Balanced'),
            'weight': 0.20,
            'contribution': buildup.get('bias_score', 50) * 0.20,
            'status': '✅ Loaded'
        }
    else:
        results['buildup'] = {
            'name': '📊 Price+OI Buildup',
            'bias': 'NEUTRAL',
            'score': 50,
            'text': 'Not calculated - Please visit Price+OI Buildup page',
            'weight': 0.20,
            'contribution': 10.0,
            'status': '⚠️ Not loaded'
        }
    
    # 4. Support/Resistance (20%) - ✅ FIXED
    sr = st.session_state.get('sr_result', {})
    if sr and sr.get('bias'):  # ✅ Check if bias exists
        results['sr'] = {
            'name': '🎯 Support/Resistance',
            'bias': sr.get('bias', 'NEUTRAL'),
            'score': sr.get('bias_score', 50),
            'text': sr.get('bias_text', 'Balanced S&R'),
            'support_strike': sr.get('support_strike', 0),
            'resistance_strike': sr.get('resistance_strike', 0),
            'weight': 0.20,
            'contribution': sr.get('bias_score', 50) * 0.20,
            'status': '✅ Loaded'
        }
    else:
        results['sr'] = {
            'name': '🎯 Support/Resistance',
            'bias': 'NEUTRAL',
            'score': 50,
            'text': 'Not calculated - Please visit Support/Resistance page',
            'support_strike': 0,
            'resistance_strike': 0,
            'weight': 0.20,
            'contribution': 10.0,
            'status': '⚠️ Not loaded'
        }
    
    # 5. PCR Analysis (16%)
    pcr = st.session_state.get('pcr_result', {})
    if pcr and pcr.get('final_bias'):
        results['pcr'] = {
            'name': '📉 PCR Analysis',
            'bias': pcr.get('final_bias', 'NEUTRAL'),
            'score': pcr.get('pcr_score', 50),
            'text': pcr.get('primary_text', 'Balanced'),
            'weight': 0.16,
            'contribution': pcr.get('pcr_score', 50) * 0.16,
            'status': '✅ Loaded'
        }
    else:
        results['pcr'] = {
            'name': '📉 PCR Analysis',
            'bias': 'NEUTRAL',
            'score': 50,
            'text': 'Not calculated - Please visit PCR Analysis page',
            'weight': 0.16,
            'contribution': 8.0,
            'status': '⚠️ Not loaded'
        }
    
    return results


def show_final_decision():
    """Final Decision Page - 5 Modules"""
    
    df = st.session_state.get('df')
    filename = st.session_state.get('filename', '')
    
    if df is None:
        st.warning("⚠️ No data available. Please upload a CSV file.")
        st.info("💡 Go to the main page, upload your CSV file, then come back here.")
        return
    
    validation = validate_data(df, filename)
    atm = validation['atm_strike']
    
    # Fetch results
    results = fetch_all_module_results()
    
    st.markdown("""
    <div style="text-align:center;padding:10px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:12px;color:white;margin-bottom:20px;">
        <h2 style="margin:0;">🏆 Final Market Decision</h2>
        <p style="margin:0;opacity:0.9;">5 Module Combined Analysis (100% Weight Distribution)</p>
        <p style="margin:0;opacity:0.7;font-size:0.8rem;">✅ Exact scores from individual module pages</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Exchange", "NSE")
    with col2:
        st.metric("Symbol", validation['symbol'])
    with col3:
        st.metric("ATM", f"₹{validation['atm_strike']:,.0f}")
    with col4:
        st.metric("Strikes", validation['num_strikes'])
    
    st.markdown("---")
    
    # Check loaded modules
    loaded_modules = [k for k, v in results.items() if v['status'] == '✅ Loaded']
    not_loaded_modules = [k for k, v in results.items() if v['status'] == '⚠️ Not loaded']
    
    if not_loaded_modules:
        st.warning(f"⚠️ **Modules not loaded:** {', '.join([results[k]['name'] for k in not_loaded_modules])}")
        st.info("💡 Please visit the following pages first:\n" + 
                "\n".join([f"  • {results[k]['name']}" for k in not_loaded_modules]))
    
    st.markdown("---")
    
    # 5 Modules Weight Distribution
    st.subheader("📊 5 Modules Weight Distribution (Exact Scores from Pages)")
    
    weight_data = []
    for key, val in results.items():
        if 'BULLISH' in val['bias']:
            emoji = '🟢'
        elif 'BEARISH' in val['bias']:
            emoji = '🔴'
        else:
            emoji = '🟡'
        
        weight_data.append({
            "Module": val['name'],
            "Weight": f"{val['weight']*100:.0f}%",
            "Score": f"{val['score']:.0f}",
            "Bias": f"{emoji} {val['bias']}",
            "Contribution": f"{val['contribution']:.1f}",
            "Status": val['status']
        })
    
    df_weights = pd.DataFrame(weight_data)
    st.dataframe(df_weights, width='stretch', hide_index=True)
    
    st.markdown("---")
    
    # Calculate final score
    final_score = sum([v['contribution'] for v in results.values()])
    
    # Count loaded modules
    loaded_results = [v for v in results.values() if v['status'] == '✅ Loaded']
    
    bullish_modules = [v for v in loaded_results if 'BULLISH' in v['bias']]
    bearish_modules = [v for v in loaded_results if 'BEARISH' in v['bias']]
    neutral_modules = [v for v in loaded_results if v['bias'] == 'NEUTRAL']
    
    bullish_count = len(bullish_modules)
    bearish_count = len(bearish_modules)
    neutral_count = len(neutral_modules)
    
    # Final Decision
    if bullish_count >= 3 and final_score >= 45:
        if final_score >= 80:
            final_decision = 'STRONG BULLISH'
            emoji = '🚀'
            color = '#00C853'
            confidence = 85
        elif final_score >= 70:
            final_decision = 'BULLISH'
            emoji = '📈'
            color = '#66BB6A'
            confidence = 75
        else:
            final_decision = 'WEAK BULLISH'
            emoji = '📈'
            color = '#81C784'
            confidence = 65
    elif bearish_count >= 3 and final_score <= 55:
        if final_score <= 20:
            final_decision = 'STRONG BEARISH'
            emoji = '💥'
            color = '#FF1744'
            confidence = 85
        elif final_score <= 35:
            final_decision = 'BEARISH'
            emoji = '📉'
            color = '#FF1744'
            confidence = 75
        else:
            final_decision = 'WEAK BEARISH'
            emoji = '📉'
            color = '#FF6D00'
            confidence = 65
    else:
        if final_score >= 80:
            final_decision = 'STRONG BULLISH'
            emoji = '🚀'
            color = '#00C853'
            confidence = 85
        elif final_score >= 70:
            final_decision = 'BULLISH'
            emoji = '📈'
            color = '#66BB6A'
            confidence = 75
        elif final_score >= 60:
            final_decision = 'WEAK BULLISH'
            emoji = '📈'
            color = '#81C784'
            confidence = 65
        elif final_score >= 50:
            final_decision = 'NEUTRAL'
            emoji = '⚖️'
            color = '#FFD600'
            confidence = 55
        elif final_score >= 40:
            final_decision = 'WEAK BEARISH'
            emoji = '📉'
            color = '#FF6D00'
            confidence = 65
        elif final_score >= 30:
            final_decision = 'BEARISH'
            emoji = '📉'
            color = '#FF1744'
            confidence = 75
        else:
            final_decision = 'STRONG BEARISH'
            emoji = '💥'
            color = '#FF1744'
            confidence = 85
    
    # FINAL DECISION BOX
    st.markdown(f"""
    <div style="background:{color};border-radius:20px;padding:30px 40px;margin:10px 0 25px 0;box-shadow:0 10px 40px rgba(0,0,0,0.4);text-align:center;">
        <div style="color:#ffffff;font-size:0.8rem;text-transform:uppercase;letter-spacing:3px;opacity:0.8;">🏆 FINAL MARKET DECISION</div>
        <div style="color:#ffffff;font-size:3.5rem;font-weight:900;margin:8px 0;">{emoji} {final_decision}</div>
        <div style="color:rgba(255,255,255,0.95);font-size:1.2rem;font-weight:500;">Confidence: {confidence:.0f}% | Score: {final_score:.1f}/100</div>
        <div style="color:rgba(255,255,255,0.7);font-size:0.9rem;margin-top:4px;">
            🟢 Bullish: {bullish_count} | 🟡 Neutral: {neutral_count} | 🔴 Bearish: {bearish_count}
        </div>
        <div style="color:rgba(255,255,255,0.5);font-size:0.8rem;margin-top:6px;">
            Based on {len(loaded_modules)}/5 Modules | 100% Weight Distribution
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # KEY REASONS
    st.subheader("📝 KEY REASONS")
    
    reasons = []
    for key, val in results.items():
        if val['status'] == '✅ Loaded':
            if 'BULLISH' in val['bias']:
                reasons.append(f"🟢 **{val['name']}:** {val['text']}")
            elif 'BEARISH' in val['bias']:
                reasons.append(f"🔴 **{val['name']}:** {val['text']}")
            else:
                reasons.append(f"🟡 **{val['name']}:** {val['text']}")
    
    for i, reason in enumerate(reasons[:5], 1):
        if '🟢' in reason:
            st.success(f"{i}. {reason}")
        elif '🔴' in reason:
            st.error(f"{i}. {reason}")
        else:
            st.warning(f"{i}. {reason}")
    
    st.markdown("---")
    
    # FINAL VERDICT
    st.subheader("📌 FINAL VERDICT")
    
    st.markdown(f"""
    ✅ **Based strictly on the uploaded NSE Option Chain, the market is {final_decision} with {confidence:.0f}% confidence because {bullish_count} bullish factors vs {bearish_count} bearish factors (out of {len(loaded_modules)} loaded modules).**
    """)
    
    st.markdown("---")
    
    # SUMMARY TABLE
    st.subheader("📋 Final Decision Summary")
    
    support = results.get('sr', {}).get('support_strike', 0)
    resistance = results.get('sr', {}).get('resistance_strike', 0)
    
    summary_data = {
        'Metric': [
            'Final Decision',
            'Confidence',
            'Bullish Score',
            'Bearish Score',
            'Signal Strength',
            'ATM Strike',
            'Support',
            'Resistance',
            'Bullish Modules',
            'Bearish Modules',
            'Neutral Modules'
        ],
        'Value': [
            final_decision,
            f"{confidence:.0f}%",
            f"{final_score:.1f}/100",
            f"{100 - final_score:.1f}/100",
            f"{final_score:.0f}/100",
            f"₹{atm:,.0f}",
            f"₹{support:,.0f}" if support > 0 else 'N/A',
            f"₹{resistance:,.0f}" if resistance > 0 else 'N/A',
            f"{bullish_count}",
            f"{bearish_count}",
            f"{neutral_count}"
        ]
    }
    
    df_summary = pd.DataFrame(summary_data)
    st.dataframe(df_summary, width='stretch', hide_index=True)
    
    st.markdown("---")
    
    st.warning("""
    ⚠️ **IMPORTANT WARNING**
    
    This analysis is based ONLY on the uploaded Option Chain.
    Do not claim certainty. Do not say that the market MUST move up or down.
    """)


show_final_decision()