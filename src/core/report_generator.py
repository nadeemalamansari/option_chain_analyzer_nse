"""
Report Generator Module
Generates reports in multiple formats: PDF, HTML, Markdown, Excel
"""

import pandas as pd
import numpy as np
from datetime import datetime
import io
import base64
import json
from typing import Dict, Any, Optional
import streamlit as st


class ReportGenerator:
    """Generate comprehensive reports from analysis data"""
    
    def __init__(self, df: pd.DataFrame, analysis: Dict):
        """
        Initialize Report Generator
        
        Args:
            df: Option chain DataFrame
            analysis: Analysis results dictionary
        """
        self.df = df
        self.analysis = analysis
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.report_date = datetime.now().strftime("%d-%b-%Y")
        
    def generate_markdown(self) -> str:
        """Generate Markdown report"""
        
        md = []
        
        # Header
        md.append("# 📊 NSE Option Chain Analysis Report")
        md.append(f"**Generated:** {self.timestamp}")
        md.append("")
        md.append("---")
        md.append("")
        
        # Summary
        md.append("## 📈 Executive Summary")
        md.append("")
        md.append(f"| Metric | Value |")
        md.append(f"|--------|-------|")
        md.append(f"| **Decision** | {self.analysis.get('decision', 'N/A')} |")
        md.append(f"| **Score** | {self.analysis.get('score', 0):.1f}/100 |")
        md.append(f"| **ATM Strike** | {self.analysis.get('atm', 0):,.0f} |")
        md.append(f"| **PCR (OI)** | {self.analysis.get('pcr_oi', 0):.2f} |")
        md.append(f"| **Support** | {self.analysis.get('support', 0):,.0f} |")
        md.append(f"| **Resistance** | {self.analysis.get('resistance', 0):,.0f} |")
        md.append(f"| **Max Pain** | {self.analysis.get('max_pain', 0):,.0f} |")
        md.append(f"| **Total Strikes** | {self.analysis.get('total_strikes', 0)} |")
        md.append("")
        md.append("---")
        md.append("")
        
        # 11 Factors
        md.append("## 📊 11 Factors Breakdown")
        md.append("")
        md.append("| Factor | Score | Status | Weight |")
        md.append("|--------|-------|--------|--------|")
        
        factors = [
            ("OI", self.analysis.get('oi_score', 50), "18%"),
            ("PCR", self.analysis.get('pcr_score', 50), "10%"),
            ("Volume", self.analysis.get('vol_score', 50), "8%"),
            ("Change OI", self.analysis.get('chng_score', 50), "15%"),
            ("S&R", self.analysis.get('sr_score', 50), "12%"),
            ("Max Pain", self.analysis.get('maxpain_score', 50), "5%"),
            ("Liquidity", self.analysis.get('liquidity_score', 50), "4%"),
            ("Sentiment", self.analysis.get('sentiment_score', 50), "10%"),
            ("ATM", self.analysis.get('atm_score', 50), "8%"),
            ("Concentration", self.analysis.get('concentration_score', 50), "5%"),
            ("Migration", self.analysis.get('migration_score', 50), "5%")
        ]
        
        for name, score, weight in factors:
            if score >= 70:
                status = "🟢 Strong Bullish"
            elif score >= 60:
                status = "🟢 Bullish"
            elif score >= 45:
                status = "🟡 Neutral"
            elif score >= 30:
                status = "🔴 Bearish"
            else:
                status = "🔴 Strong Bearish"
            
            md.append(f"| {name} | {score:.1f} | {status} | {weight} |")
        
        md.append("")
        md.append("---")
        md.append("")
        
        # ATM Structure
        md.append("## 🏗️ ATM Structure")
        md.append("")
        md.append(f"| Metric | Value |")
        md.append(f"|--------|-------|")
        md.append(f"| **ATM Strike** | {self.analysis.get('atm', 0):,.0f} |")
        md.append(f"| **CE OI** | {self.analysis.get('atm_ce_oi', 0):,.0f} |")
        md.append(f"| **PE OI** | {self.analysis.get('atm_pe_oi', 0):,.0f} |")
        md.append(f"| **ATM OI Ratio** | {self.analysis.get('atm_pe_oi', 0) / self.analysis.get('atm_ce_oi', 1) if self.analysis.get('atm_ce_oi', 0) > 0 else 0:.2f} |")
        md.append(f"| **CE LTP** | ₹{self.analysis.get('atm_ce_ltp', 0):.2f} |")
        md.append(f"| **PE LTP** | ₹{self.analysis.get('atm_pe_ltp', 0):.2f} |")
        md.append(f"| **CE IV** | {self.analysis.get('atm_ce_iv', 0):.2f}% |")
        md.append(f"| **PE IV** | {self.analysis.get('atm_pe_iv', 0):.2f}% |")
        md.append("")
        md.append("---")
        md.append("")
        
        # OI Totals
        md.append("## 📊 Open Interest Summary")
        md.append("")
        md.append(f"| Metric | Value |")
        md.append(f"|--------|-------|")
        md.append(f"| **Total CE OI** | {self.analysis.get('total_ce_oi', 0):,.0f} |")
        md.append(f"| **Total PE OI** | {self.analysis.get('total_pe_oi', 0):,.0f} |")
        md.append(f"| **Total OI** | {self.analysis.get('total_oi', 0):,.0f} |")
        md.append(f"| **Total CE Volume** | {self.analysis.get('total_ce_vol', 0):,.0f} |")
        md.append(f"| **Total PE Volume** | {self.analysis.get('total_pe_vol', 0):,.0f} |")
        md.append(f"| **Total Volume** | {self.analysis.get('total_volume', 0):,.0f} |")
        md.append("")
        md.append("---")
        md.append("")
        
        # Top OI Strikes
        md.append("## 🎯 Top OI Strikes")
        md.append("")
        
        # Top CE OI
        md.append("### 📈 Top CE OI Strikes")
        md.append("")
        top_ce = self.df.nlargest(10, 'CE_OI')[['STRIKE', 'CE_OI']]
        md.append("| Strike | CE OI |")
        md.append("|--------|-------|")
        for _, row in top_ce.iterrows():
            md.append(f"| {row['STRIKE']:,.0f} | {row['CE_OI']:,.0f} |")
        md.append("")
        
        # Top PE OI
        md.append("### 📉 Top PE OI Strikes")
        md.append("")
        top_pe = self.df.nlargest(10, 'PE_OI')[['STRIKE', 'PE_OI']]
        md.append("| Strike | PE OI |")
        md.append("|--------|-------|")
        for _, row in top_pe.iterrows():
            md.append(f"| {row['STRIKE']:,.0f} | {row['PE_OI']:,.0f} |")
        md.append("")
        md.append("---")
        md.append("")
        
        # Footer
        md.append("---")
        md.append("")
        md.append("*Report generated by NSE Option Chain Analyzer PRO*")
        md.append(f"*Date: {self.report_date}*")
        
        return "\n".join(md)
    
    def generate_html(self) -> str:
        """Generate HTML report"""
        
        # Get factor status
        def get_status(score):
            if score >= 70:
                return "Strong Bullish", "#00C853"
            elif score >= 60:
                return "Bullish", "#66BB6A"
            elif score >= 45:
                return "Neutral", "#FFD600"
            elif score >= 30:
                return "Bearish", "#FF6D00"
            else:
                return "Strong Bearish", "#FF1744"
        
        factors = [
            ("OI", self.analysis.get('oi_score', 50), "18%"),
            ("PCR", self.analysis.get('pcr_score', 50), "10%"),
            ("Volume", self.analysis.get('vol_score', 50), "8%"),
            ("Change OI", self.analysis.get('chng_score', 50), "15%"),
            ("S&R", self.analysis.get('sr_score', 50), "12%"),
            ("Max Pain", self.analysis.get('maxpain_score', 50), "5%"),
            ("Liquidity", self.analysis.get('liquidity_score', 50), "4%"),
            ("Sentiment", self.analysis.get('sentiment_score', 50), "10%"),
            ("ATM", self.analysis.get('atm_score', 50), "8%"),
            ("Concentration", self.analysis.get('concentration_score', 50), "5%"),
            ("Migration", self.analysis.get('migration_score', 50), "5%")
        ]
        
        factors_html = ""
        for name, score, weight in factors:
            status, color = get_status(score)
            factors_html += f"""
            <tr>
                <td><strong>{name}</strong></td>
                <td style="font-size:1.2rem;font-weight:bold;">{score:.1f}</td>
                <td><span style="color:{color};font-weight:bold;">{status}</span></td>
                <td>{weight}</td>
            </tr>
            """
        
        # Decision color
        decision = self.analysis.get('decision', 'NEUTRAL')
        if "BULLISH" in decision:
            decision_color = "#00C853"
        elif "BEARISH" in decision:
            decision_color = "#FF1744"
        else:
            decision_color = "#FFD600"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Option Chain Analysis Report</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    margin: 40px;
                    background: #0e1117;
                    color: #fafafa;
                    line-height: 1.6;
                }}
                .container {{
                    max-width: 1000px;
                    margin: 0 auto;
                    background: #1a1a2e;
                    padding: 30px;
                    border-radius: 15px;
                    box-shadow: 0 8px 30px rgba(0,0,0,0.5);
                }}
                h1 {{ color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
                h2 {{ color: #64ffda; margin-top: 30px; }}
                h3 {{ color: #8892b0; }}
                .header-info {{ color: #8892b0; font-size: 0.9rem; }}
                .decision-box {{
                    background: {decision_color};
                    padding: 20px;
                    border-radius: 12px;
                    text-align: center;
                    font-size: 2rem;
                    font-weight: bold;
                    color: white;
                    margin: 20px 0;
                }}
                .decision-box .score {{
                    font-size: 1rem;
                    opacity: 0.9;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                }}
                th {{
                    background: #667eea;
                    color: white;
                    padding: 12px;
                    text-align: left;
                }}
                td {{
                    padding: 10px 12px;
                    border-bottom: 1px solid #2a2a4a;
                }}
                tr:hover {{
                    background: rgba(102, 126, 234, 0.1);
                }}
                .metric-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin: 15px 0;
                }}
                .metric-card {{
                    background: #1a1a2e;
                    padding: 15px;
                    border-radius: 10px;
                    border: 1px solid #2a2a4a;
                    text-align: center;
                }}
                .metric-card .label {{
                    color: #8892b0;
                    font-size: 0.8rem;
                    text-transform: uppercase;
                }}
                .metric-card .value {{
                    font-size: 1.5rem;
                    font-weight: bold;
                    color: #64ffda;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #2a2a4a;
                    color: #8892b0;
                    font-size: 0.8rem;
                    text-align: center;
                }}
                .status-bullish {{ color: #00C853; }}
                .status-neutral {{ color: #FFD600; }}
                .status-bearish {{ color: #FF1744; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 NSE Option Chain Analysis Report</h1>
                <div class="header-info">
                    Generated: {self.timestamp} | Report Date: {self.report_date}
                </div>
                
                <div class="decision-box">
                    {self.analysis.get('decision', 'NEUTRAL')}
                    <div class="score">Score: {self.analysis.get('score', 0):.1f}/100</div>
                </div>
                
                <h2>📈 Executive Summary</h2>
                <div class="metric-grid">
                    <div class="metric-card">
                        <div class="label">ATM Strike</div>
                        <div class="value">₹{self.analysis.get('atm', 0):,.0f}</div>
                    </div>
                    <div class="metric-card">
                        <div class="label">PCR (OI)</div>
                        <div class="value">{self.analysis.get('pcr_oi', 0):.2f}</div>
                    </div>
                    <div class="metric-card">
                        <div class="label">Support</div>
                        <div class="value">₹{self.analysis.get('support', 0):,.0f}</div>
                    </div>
                    <div class="metric-card">
                        <div class="label">Resistance</div>
                        <div class="value">₹{self.analysis.get('resistance', 0):,.0f}</div>
                    </div>
                    <div class="metric-card">
                        <div class="label">Max Pain</div>
                        <div class="value">₹{self.analysis.get('max_pain', 0):,.0f}</div>
                    </div>
                    <div class="metric-card">
                        <div class="label">Total Strikes</div>
                        <div class="value">{self.analysis.get('total_strikes', 0)}</div>
                    </div>
                </div>
                
                <h2>📊 11 Factors Breakdown</h2>
                <table>
                    <tr>
                        <th>Factor</th>
                        <th>Score</th>
                        <th>Status</th>
                        <th>Weight</th>
                    </tr>
                    {factors_html}
                </table>
                
                <h2>🏗️ ATM Structure</h2>
                <table>
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>ATM Strike</td><td>₹{self.analysis.get('atm', 0):,.0f}</td></tr>
                    <tr><td>CE OI</td><td>{self.analysis.get('atm_ce_oi', 0):,.0f}</td></tr>
                    <tr><td>PE OI</td><td>{self.analysis.get('atm_pe_oi', 0):,.0f}</td></tr>
                    <tr><td>ATM OI Ratio</td><td>{self.analysis.get('atm_pe_oi', 0) / self.analysis.get('atm_ce_oi', 1) if self.analysis.get('atm_ce_oi', 0) > 0 else 0:.2f}</td></tr>
                    <tr><td>CE LTP</td><td>₹{self.analysis.get('atm_ce_ltp', 0):.2f}</td></tr>
                    <tr><td>PE LTP</td><td>₹{self.analysis.get('atm_pe_ltp', 0):.2f}</td></tr>
                    <tr><td>CE IV</td><td>{self.analysis.get('atm_ce_iv', 0):.2f}%</td></tr>
                    <tr><td>PE IV</td><td>{self.analysis.get('atm_pe_iv', 0):.2f}%</td></tr>
                </table>
                
                <h2>📊 Open Interest Summary</h2>
                <table>
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Total CE OI</td><td>{self.analysis.get('total_ce_oi', 0):,.0f}</td></tr>
                    <tr><td>Total PE OI</td><td>{self.analysis.get('total_pe_oi', 0):,.0f}</td></tr>
                    <tr><td>Total OI</td><td>{self.analysis.get('total_oi', 0):,.0f}</td></tr>
                    <tr><td>Total CE Volume</td><td>{self.analysis.get('total_ce_vol', 0):,.0f}</td></tr>
                    <tr><td>Total PE Volume</td><td>{self.analysis.get('total_pe_vol', 0):,.0f}</td></tr>
                    <tr><td>Total Volume</td><td>{self.analysis.get('total_volume', 0):,.0f}</td></tr>
                </table>
                
                <div class="footer">
                    Report generated by NSE Option Chain Analyzer PRO<br>
                    Date: {self.report_date}
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def generate_excel(self) -> io.BytesIO:
        """Generate Excel report"""
        
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            
            # Sheet 1: Summary
            summary_data = {
                'Metric': ['Decision', 'Score', 'ATM Strike', 'PCR (OI)', 'PCR (Volume)',
                          'Support', 'Resistance', 'Max Pain', 'Total CE OI', 'Total PE OI',
                          'Total OI', 'Total CE Volume', 'Total PE Volume', 'Total Volume',
                          'Total Strikes'],
                'Value': [
                    self.analysis.get('decision', 'N/A'),
                    f"{self.analysis.get('score', 0):.1f}/100",
                    f"{self.analysis.get('atm', 0):,.0f}",
                    f"{self.analysis.get('pcr_oi', 0):.2f}",
                    f"{self.analysis.get('pcr_vol', 0):.2f}",
                    f"{self.analysis.get('support', 0):,.0f}",
                    f"{self.analysis.get('resistance', 0):,.0f}",
                    f"{self.analysis.get('max_pain', 0):,.0f}",
                    f"{self.analysis.get('total_ce_oi', 0):,.0f}",
                    f"{self.analysis.get('total_pe_oi', 0):,.0f}",
                    f"{self.analysis.get('total_oi', 0):,.0f}",
                    f"{self.analysis.get('total_ce_vol', 0):,.0f}",
                    f"{self.analysis.get('total_pe_vol', 0):,.0f}",
                    f"{self.analysis.get('total_volume', 0):,.0f}",
                    f"{self.analysis.get('total_strikes', 0)}"
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
            
            # Sheet 2: 11 Factors
            factors_data = []
            factors = [
                ('OI', self.analysis.get('oi_score', 50), '18%'),
                ('PCR', self.analysis.get('pcr_score', 50), '10%'),
                ('Volume', self.analysis.get('vol_score', 50), '8%'),
                ('Change OI', self.analysis.get('chng_score', 50), '15%'),
                ('S&R', self.analysis.get('sr_score', 50), '12%'),
                ('Max Pain', self.analysis.get('maxpain_score', 50), '5%'),
                ('Liquidity', self.analysis.get('liquidity_score', 50), '4%'),
                ('Sentiment', self.analysis.get('sentiment_score', 50), '10%'),
                ('ATM', self.analysis.get('atm_score', 50), '8%'),
                ('Concentration', self.analysis.get('concentration_score', 50), '5%'),
                ('Migration', self.analysis.get('migration_score', 50), '5%')
            ]
            
            for name, score, weight in factors:
                if score >= 70:
                    status = 'Strong Bullish'
                elif score >= 60:
                    status = 'Bullish'
                elif score >= 45:
                    status = 'Neutral'
                elif score >= 30:
                    status = 'Bearish'
                else:
                    status = 'Strong Bearish'
                
                factors_data.append({
                    'Factor': name,
                    'Score': score,
                    'Status': status,
                    'Weight': weight
                })
            
            pd.DataFrame(factors_data).to_excel(writer, sheet_name='Factors', index=False)
            
            # Sheet 3: ATM Structure
            atm_data = {
                'Metric': ['ATM Strike', 'CE OI', 'PE OI', 'ATM OI Ratio', 'CE LTP', 'PE LTP', 'CE IV', 'PE IV'],
                'Value': [
                    f"{self.analysis.get('atm', 0):,.0f}",
                    f"{self.analysis.get('atm_ce_oi', 0):,.0f}",
                    f"{self.analysis.get('atm_pe_oi', 0):,.0f}",
                    f"{self.analysis.get('atm_pe_oi', 0) / self.analysis.get('atm_ce_oi', 1) if self.analysis.get('atm_ce_oi', 0) > 0 else 0:.2f}",
                    f"₹{self.analysis.get('atm_ce_ltp', 0):.2f}",
                    f"₹{self.analysis.get('atm_pe_ltp', 0):.2f}",
                    f"{self.analysis.get('atm_ce_iv', 0):.2f}%",
                    f"{self.analysis.get('atm_pe_iv', 0):.2f}%"
                ]
            }
            pd.DataFrame(atm_data).to_excel(writer, sheet_name='ATM_Structure', index=False)
            
            # Sheet 4: Top OI Strikes
            top_ce = self.df.nlargest(20, 'CE_OI')[['STRIKE', 'CE_OI']].copy()
            top_ce.columns = ['Strike', 'CE OI']
            top_ce.to_excel(writer, sheet_name='Top_CE_OI', index=False)
            
            top_pe = self.df.nlargest(20, 'PE_OI')[['STRIKE', 'PE_OI']].copy()
            top_pe.columns = ['Strike', 'PE OI']
            top_pe.to_excel(writer, sheet_name='Top_PE_OI', index=False)
            
            # Sheet 5: Full Data
            self.df.to_excel(writer, sheet_name='Full_Data', index=False)
        
        output.seek(0)
        return output
    
    def generate_json(self) -> str:
        """Generate JSON report"""
        
        report = {
            'generated_at': self.timestamp,
            'report_date': self.report_date,
            'summary': {
                'decision': self.analysis.get('decision', 'N/A'),
                'score': self.analysis.get('score', 0),
                'atm': self.analysis.get('atm', 0),
                'pcr_oi': self.analysis.get('pcr_oi', 0),
                'pcr_vol': self.analysis.get('pcr_vol', 0),
                'support': self.analysis.get('support', 0),
                'resistance': self.analysis.get('resistance', 0),
                'max_pain': self.analysis.get('max_pain', 0),
                'total_strikes': self.analysis.get('total_strikes', 0)
            },
            'factors': {
                'OI': self.analysis.get('oi_score', 50),
                'PCR': self.analysis.get('pcr_score', 50),
                'Volume': self.analysis.get('vol_score', 50),
                'Change_OI': self.analysis.get('chng_score', 50),
                'S_R': self.analysis.get('sr_score', 50),
                'Max_Pain': self.analysis.get('maxpain_score', 50),
                'Liquidity': self.analysis.get('liquidity_score', 50),
                'Sentiment': self.analysis.get('sentiment_score', 50),
                'ATM': self.analysis.get('atm_score', 50),
                'Concentration': self.analysis.get('concentration_score', 50),
                'Migration': self.analysis.get('migration_score', 50)
            },
            'atm_structure': {
                'strike': self.analysis.get('atm', 0),
                'ce_oi': self.analysis.get('atm_ce_oi', 0),
                'pe_oi': self.analysis.get('atm_pe_oi', 0),
                'ce_ltp': self.analysis.get('atm_ce_ltp', 0),
                'pe_ltp': self.analysis.get('atm_pe_ltp', 0),
                'ce_iv': self.analysis.get('atm_ce_iv', 0),
                'pe_iv': self.analysis.get('atm_pe_iv', 0)
            },
            'oi_totals': {
                'total_ce_oi': self.analysis.get('total_ce_oi', 0),
                'total_pe_oi': self.analysis.get('total_pe_oi', 0),
                'total_oi': self.analysis.get('total_oi', 0),
                'total_ce_vol': self.analysis.get('total_ce_vol', 0),
                'total_pe_vol': self.analysis.get('total_pe_vol', 0),
                'total_volume': self.analysis.get('total_volume', 0)
            }
        }
        
        return json.dumps(report, indent=2)
    
    def generate_txt(self) -> str:
        """Generate plain text report"""
        
        lines = []
        lines.append("=" * 60)
        lines.append("📊 NSE OPTION CHAIN ANALYSIS REPORT")
        lines.append("=" * 60)
        lines.append(f"Generated: {self.timestamp}")
        lines.append("")
        
        lines.append("-" * 60)
        lines.append("📈 EXECUTIVE SUMMARY")
        lines.append("-" * 60)
        lines.append(f"Decision   : {self.analysis.get('decision', 'N/A')}")
        lines.append(f"Score      : {self.analysis.get('score', 0):.1f}/100")
        lines.append(f"ATM Strike : {self.analysis.get('atm', 0):,.0f}")
        lines.append(f"PCR (OI)   : {self.analysis.get('pcr_oi', 0):.2f}")
        lines.append(f"Support    : {self.analysis.get('support', 0):,.0f}")
        lines.append(f"Resistance : {self.analysis.get('resistance', 0):,.0f}")
        lines.append(f"Max Pain   : {self.analysis.get('max_pain', 0):,.0f}")
        lines.append(f"Total Strikes : {self.analysis.get('total_strikes', 0)}")
        lines.append("")
        
        lines.append("-" * 60)
        lines.append("📊 11 FACTORS BREAKDOWN")
        lines.append("-" * 60)
        
        factors = [
            ("OI", self.analysis.get('oi_score', 50), "18%"),
            ("PCR", self.analysis.get('pcr_score', 50), "10%"),
            ("Volume", self.analysis.get('vol_score', 50), "8%"),
            ("Change OI", self.analysis.get('chng_score', 50), "15%"),
            ("S&R", self.analysis.get('sr_score', 50), "12%"),
            ("Max Pain", self.analysis.get('maxpain_score', 50), "5%"),
            ("Liquidity", self.analysis.get('liquidity_score', 50), "4%"),
            ("Sentiment", self.analysis.get('sentiment_score', 50), "10%"),
            ("ATM", self.analysis.get('atm_score', 50), "8%"),
            ("Concentration", self.analysis.get('concentration_score', 50), "5%"),
            ("Migration", self.analysis.get('migration_score', 50), "5%")
        ]
        
        for name, score, weight in factors:
            if score >= 70:
                status = "🟢 Strong Bullish"
            elif score >= 60:
                status = "🟢 Bullish"
            elif score >= 45:
                status = "🟡 Neutral"
            elif score >= 30:
                status = "🔴 Bearish"
            else:
                status = "🔴 Strong Bearish"
            
            lines.append(f"{name:12} : {score:5.1f}  {status:16}  {weight}")
        
        lines.append("")
        lines.append("-" * 60)
        lines.append("🏗️ ATM STRUCTURE")
        lines.append("-" * 60)
        lines.append(f"ATM Strike  : {self.analysis.get('atm', 0):,.0f}")
        lines.append(f"CE OI       : {self.analysis.get('atm_ce_oi', 0):,.0f}")
        lines.append(f"PE OI       : {self.analysis.get('atm_pe_oi', 0):,.0f}")
        lines.append(f"ATM OI Ratio: {self.analysis.get('atm_pe_oi', 0) / self.analysis.get('atm_ce_oi', 1) if self.analysis.get('atm_ce_oi', 0) > 0 else 0:.2f}")
        lines.append(f"CE LTP      : ₹{self.analysis.get('atm_ce_ltp', 0):.2f}")
        lines.append(f"PE LTP      : ₹{self.analysis.get('atm_pe_ltp', 0):.2f}")
        lines.append(f"CE IV       : {self.analysis.get('atm_ce_iv', 0):.2f}%")
        lines.append(f"PE IV       : {self.analysis.get('atm_pe_iv', 0):.2f}%")
        lines.append("")
        
        lines.append("-" * 60)
        lines.append("📊 OPEN INTEREST SUMMARY")
        lines.append("-" * 60)
        lines.append(f"Total CE OI     : {self.analysis.get('total_ce_oi', 0):,.0f}")
        lines.append(f"Total PE OI     : {self.analysis.get('total_pe_oi', 0):,.0f}")
        lines.append(f"Total OI        : {self.analysis.get('total_oi', 0):,.0f}")
        lines.append(f"Total CE Volume : {self.analysis.get('total_ce_vol', 0):,.0f}")
        lines.append(f"Total PE Volume : {self.analysis.get('total_pe_vol', 0):,.0f}")
        lines.append(f"Total Volume    : {self.analysis.get('total_volume', 0):,.0f}")
        lines.append("")
        
        lines.append("=" * 60)
        lines.append(f"Report generated by NSE Option Chain Analyzer PRO")
        lines.append(f"Date: {self.report_date}")
        lines.append("=" * 60)
        
        return "\n".join(lines)