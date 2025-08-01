#!/usr/bin/env python3
"""
Interactive Dashboard for Licensing Analysis
Web-based dashboard with interactive charts and real-time data
"""

import json
import os
import re
from datetime import datetime
from collections import defaultdict
from flask import Flask, render_template, jsonify
import plotly.graph_objs as go
import plotly.utils
import plotly.express as px
import pandas as pd
import numpy as np

app = Flask(__name__)

class DashboardData:
    def __init__(self):
        # Use the cleaned data file from the executive directory
        self.data_file = "reports/current/cleaned_licensing_data_20250725.json"
        # Load enhanced industry analysis for benchmark data
        self.industry_analysis_file = "reports/current/enhanced_industry_analysis_20250725.json"
        # Load AI-enhanced analysis for advanced insights
        self.ai_enhanced_analysis_file = "reports/current/ai_enhanced_industry_analysis_20250725.json"
        self.load_data()
        self.load_industry_analysis()
        self.load_ai_enhanced_analysis()
        self.analyze_data()
    
    def load_data(self):
        """Load and prepare data for dashboard."""
        if not os.path.exists(self.data_file):
            print(f"Warning: Data file {self.data_file} not found. Trying fallback...")
            # Fallback to original file if cleaned data doesn't exist
            fallback_file = "reports/processed_licensing_data.json"
            if os.path.exists(fallback_file):
                self.data_file = fallback_file
                print(f"Using fallback file: {fallback_file}")
            else:
                print("No data files found!")
                self.data = []
                return
        
        with open(self.data_file, 'r') as f:
            self.data = json.load(f)
            print(f"Loaded {len(self.data)} records from {self.data_file}")
    
    def load_industry_analysis(self):
        """Load enhanced industry analysis data for benchmark comparisons."""
        self.industry_analysis = {}
        if os.path.exists(self.industry_analysis_file):
            with open(self.industry_analysis_file, 'r') as f:
                self.industry_analysis = json.load(f)
                print(f"Loaded industry analysis data from {self.industry_analysis_file}")
        else:
            print(f"Warning: Industry analysis file {self.industry_analysis_file} not found")
            self.industry_analysis = {}
    
    def load_ai_enhanced_analysis(self):
        """Load AI-enhanced analysis data for advanced insights."""
        self.ai_enhanced_analysis = {}
        if os.path.exists(self.ai_enhanced_analysis_file):
            with open(self.ai_enhanced_analysis_file, 'r') as f:
                self.ai_enhanced_analysis = json.load(f)
                print(f"Loaded AI-enhanced analysis data from {self.ai_enhanced_analysis_file}")
        else:
            print(f"Warning: AI-enhanced analysis file {self.ai_enhanced_analysis_file} not found")
            self.ai_enhanced_analysis = {}
    
    def parse_date(self, date_str):
        """Parse various date formats and extract year and month."""
        if not date_str:
            return None, None
        
        # Try to extract year first
        year_match = re.search(r'20\d{2}', date_str)
        year = int(year_match.group()) if year_match else None
        
        # Try to extract month - first check for numeric format (e.g., "3/31/2024")
        numeric_month_match = re.search(r'(\d{1,2})/\d{1,2}/20\d{2}', date_str)
        if numeric_month_match:
            month_num = int(numeric_month_match.group(1))
            month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December']
            if 1 <= month_num <= 12:
                return year, month_names[month_num - 1]
        
        # Try to extract month from text format
        month_patterns = [
            r'Jan(?:uary)?', r'Feb(?:ruary)?', r'Mar(?:ch)?', r'Apr(?:il)?',
            r'May', r'Jun(?:e)?', r'Jul(?:y)?', r'Aug(?:ust)?',
            r'Sep(?:tember)?', r'Oct(?:ober)?', r'Nov(?:ember)?', r'Dec(?:ember)?'
        ]
        
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        
        for i, pattern in enumerate(month_patterns):
            if re.search(pattern, date_str, re.IGNORECASE):
                return year, month_names[i]
        
        return year, None
    
    def consolidate_vendor_name(self, vendor_name):
        """Consolidate vendor names to handle variations."""
        vendor_lower = vendor_name.lower().strip()
        
        # Vendor consolidation rules
        vendor_mappings = {
            'synoptek': 'Synoptek',
            'synoptek, llc': 'Synoptek',
            'synoptek llc': 'Synoptek',
            'atlassian': 'Atlassian',
            'microsoft': 'Microsoft',
            'oracle': 'Oracle',
            'salesforce': 'Salesforce',
            'aws': 'AWS',
            'amazon': 'AWS',
            'amazon web services': 'AWS',
            'azure': 'Microsoft Azure',
            'google': 'Google',
            'gcp': 'Google Cloud',
            'google cloud': 'Google Cloud',
            'github': 'GitHub',
            'gitlab': 'GitLab',
            'crowdstrike': 'CrowdStrike',
            'sentinelone': 'SentinelOne',
            'palo alto': 'Palo Alto Networks',
            'proofpoint': 'Proofpoint',
            'harman': 'Harman',
            'harman connected services': 'Harman',
            'markov': 'Markov Processes',
            'markov processes': 'Markov Processes',
            'markov processes international': 'Markov Processes'
        }
        
        # Check for exact matches first
        for key, value in vendor_mappings.items():
            if vendor_lower == key:
                return value
        
        # Check for partial matches
        for key, value in vendor_mappings.items():
            if key in vendor_lower:
                return value
        
        # Return original name if no match found
        return vendor_name
    
    def extract_company_from_bill_to(self, bill_to):
        """Extract company name from bill_to field."""
        if not bill_to:
            return "Unknown Company"
        
        # Common company patterns with better consolidation
        company_patterns = [
            (r'great\s+gray\s+(?:trust\s+)?company', 'Great Gray Trust Company'),
            (r'great\s+gray\s+market', 'Great Gray Market'),
            (r'great\s+gray', 'Great Gray'),
            (r'rpag', 'RPAG'),
            (r'retirement\s+plan\s+advisory\s+group', 'RPAG'),
            (r'flexpath\s+(?:advisors?|partners?)', 'Flexpath'),
            (r'flexpath', 'Flexpath')
        ]
        
        bill_to_lower = bill_to.lower()
        
        for pattern, company_name in company_patterns:
            match = re.search(pattern, bill_to_lower)
            if match:
                return company_name
        
        # If no pattern matches, try to extract first company-like name
        # Look for words that might be company names (capitalized words)
        words = bill_to.split(',')[0].split()
        potential_company = []
        for word in words:
            if word[0].isupper() and len(word) > 2:
                potential_company.append(word)
        
        if potential_company:
            return ' '.join(potential_company[:3])  # Take first 3 words max
        
        return "Unknown Company"
    
    def analyze_data(self):
        """Analyze data for dashboard visualizations."""
        # Vendor categorization
        self.vendor_categories = {
            "synoptek": "it_services",
            "atlassian": "development_tools",
            "microsoft": "enterprise_software",
            "oracle": "enterprise_software",
            "salesforce": "enterprise_software",
            "aws": "cloud_services",
            "amazon": "cloud_services",
            "azure": "cloud_services",
            "google": "cloud_services",
            "gcp": "cloud_services",
            "github": "development_tools",
            "gitlab": "development_tools",
            "crowdstrike": "security_software",
            "sentinelone": "security_software",
            "palo alto": "security_software",
            "proofpoint": "security_software",
            "harman": "it_services",
            "markov": "it_services"
        }
        
        # Categorize data
        self.categorized_spend = defaultdict(list)
        self.category_totals = defaultdict(float)
        self.monthly_data = defaultdict(float)
        self.yearly_data = defaultdict(float)
        self.vendor_spend = defaultdict(float)
        self.company_spend = defaultdict(float)
        self.vendor_company_spend = defaultdict(lambda: defaultdict(float))
        
        for item in self.data:
            vendor = item.get('vendor', 'Unknown')
            amount = item.get('total_amount', 0)
            date_str = item.get('invoice_date', '')
            bill_to = item.get('bill_to', '')
            
            # Consolidate vendor name
            consolidated_vendor = self.consolidate_vendor_name(vendor)
            
            # Extract company from bill_to
            company = self.extract_company_from_bill_to(bill_to)
            
            category = self.categorize_vendor(consolidated_vendor)
            
            self.categorized_spend[category].append(item)
            self.category_totals[category] += amount
            self.vendor_spend[consolidated_vendor] += amount
            self.company_spend[company] += amount
            self.vendor_company_spend[consolidated_vendor][company] += amount
            
            # Parse date for trend analysis
            year, month = self.parse_date(date_str)
            if year and month:
                self.monthly_data[f"{month} {year}"] += amount
                self.yearly_data[year] += amount
        
        # Calculate metrics
        self.total_spend = sum(self.category_totals.values())
        self.total_invoices = len(self.data)
        self.vendor_count = len(self.vendor_spend)
        self.company_count = len(self.company_spend)
        
        print(f"Data spans years: {sorted(self.yearly_data.keys())}")
        print(f"Monthly data points: {len(self.monthly_data)}")
        print(f"Consolidated vendors: {len(self.vendor_spend)}")
        print(f"Companies identified: {len(self.company_spend)}")
    
    def categorize_vendor(self, vendor_name):
        """Categorize vendor based on name."""
        vendor_lower = vendor_name.lower()
        
        for vendor_key, category in self.vendor_categories.items():
            if vendor_key in vendor_lower:
                return category
        
        return "it_services"
    
    def get_spending_pie_chart(self):
        """Create spending distribution pie chart."""
        categories = []
        amounts = []
        
        for category, spend in self.category_totals.items():
            categories.append(category.replace('_', ' ').title())
            amounts.append(spend)
        
        fig = go.Figure(data=[go.Pie(
            labels=categories,
            values=amounts,
            hole=0.3,
            textinfo='label+percent',
            textposition='inside',
            marker=dict(colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
        )])
        
        fig.update_layout(
            title='Spending Distribution by Category',
            title_x=0.5,
            showlegend=True,
            height=500
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def get_vendor_bar_chart(self):
        """Create vendor spending bar chart."""
        # Get top 10 vendors
        top_vendors = sorted(self.vendor_spend.items(), key=lambda x: x[1], reverse=True)[:10]
        vendors, amounts = zip(*top_vendors)
        
        fig = go.Figure(data=[go.Bar(
            x=vendors,
            y=amounts,
            marker_color='#45B7D1',
            text=[f'${amount:,.0f}' for amount in amounts],
            textposition='auto'
        )])
        
        fig.update_layout(
            title='Top 10 Vendors by Spend (Consolidated)',
            title_x=0.5,
            xaxis_title='Vendors',
            yaxis_title='Total Spend ($)',
            height=500,
            xaxis_tickangle=-45
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def get_company_bar_chart(self):
        """Create company spending bar chart."""
        # Get top 10 companies
        top_companies = sorted(self.company_spend.items(), key=lambda x: x[1], reverse=True)[:10]
        companies, amounts = zip(*top_companies)
        
        fig = go.Figure(data=[go.Bar(
            x=companies,
            y=amounts,
            marker_color='#FF6B6B',
            text=[f'${amount:,.0f}' for amount in amounts],
            textposition='auto'
        )])
        
        fig.update_layout(
            title='Top 10 Companies by Spend',
            title_x=0.5,
            xaxis_title='Companies',
            yaxis_title='Total Spend ($)',
            height=500,
            xaxis_tickangle=-45
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def get_vendor_company_heatmap(self):
        """Create vendor vs company spending heatmap."""
        # Prepare data for heatmap
        vendors = list(self.vendor_spend.keys())[:8]  # Top 8 vendors
        companies = list(self.company_spend.keys())[:8]  # Top 8 companies
        
        # Create matrix
        matrix = []
        for vendor in vendors:
            row = []
            for company in companies:
                amount = self.vendor_company_spend[vendor].get(company, 0)
                row.append(amount)
            matrix.append(row)
        
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=companies,
            y=vendors,
            colorscale='Viridis',
            text=[[f'${val:,.0f}' if val > 0 else '' for val in row] for row in matrix],
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title='Vendor vs Company Spending Heatmap',
            title_x=0.5,
            xaxis_title='Companies',
            yaxis_title='Vendors',
            height=500
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def get_monthly_trend_chart(self):
        """Create monthly spending trend chart with proper date handling."""
        if not self.monthly_data:
            return None
        
        # Sort months chronologically
        def sort_month_year(month_year):
            month, year = month_year.rsplit(' ', 1)
            month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December']
            return (int(year), month_order.index(month))
        
        sorted_months = sorted(self.monthly_data.items(), key=lambda x: sort_month_year(x[0]))
        months, amounts = zip(*sorted_months)
        
        fig = go.Figure(data=[go.Scatter(
            x=months,
            y=amounts,
            mode='lines+markers',
            line=dict(color='#4ECDC4', width=3),
            marker=dict(size=10),
            text=[f'${amount:,.0f}' for amount in amounts],
            textposition='top center'
        )])
        
        fig.update_layout(
            title='Monthly Spending Trend (2024-2025)',
            title_x=0.5,
            xaxis_title='Month',
            yaxis_title='Total Spend ($)',
            height=400,
            xaxis_tickangle=-45
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def get_yearly_comparison_chart(self):
        """Create yearly spending comparison chart."""
        if len(self.yearly_data) < 2:
            return None
        
        years = sorted(self.yearly_data.keys())
        amounts = [self.yearly_data[year] for year in years]
        
        fig = go.Figure(data=[go.Bar(
            x=[str(year) for year in years],
            y=amounts,
            marker_color=['#FF6B6B', '#4ECDC4'],
            text=[f'${amount:,.0f}' for amount in amounts],
            textposition='auto'
        )])
        
        fig.update_layout(
            title='Yearly Spending Comparison',
            title_x=0.5,
            xaxis_title='Year',
            yaxis_title='Total Spend ($)',
            height=400
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def get_benchmark_comparison_chart(self):
        """Create industry benchmark comparison chart."""
        categories = []
        actual_spend = []
        benchmark_low = []
        benchmark_high = []
        
        for category, spend in self.category_totals.items():
            categories.append(category.replace('_', ' ').title())
            actual_spend.append(spend)
            
            # Use actual industry benchmark data if available
            if 'benchmarks' in self.industry_analysis and category in self.industry_analysis['benchmarks']:
                benchmark_data = self.industry_analysis['benchmarks'][category]['benchmark']
                benchmark_low.append(benchmark_data['low'])
                benchmark_high.append(benchmark_data['high'])
            else:
                # Fallback to simplified benchmark calculation if no specific data
                if category == "it_services":
                    benchmark_low.append(spend * 0.15)
                    benchmark_high.append(spend * 0.30)
                elif category == "development_tools":
                    benchmark_low.append(spend * 0.05)
                    benchmark_high.append(spend * 0.12)
                elif category == "enterprise_software":
                    benchmark_low.append(spend * 0.12)
                    benchmark_high.append(spend * 0.25)
                elif category == "security_software":
                    benchmark_low.append(spend * 0.08)
                    benchmark_high.append(spend * 0.15)
                elif category == "cloud_services":
                    benchmark_low.append(spend * 0.10)
                    benchmark_high.append(spend * 0.18)
                else:
                    benchmark_low.append(spend * 0.10)
                    benchmark_high.append(spend * 0.20)
        
        fig = go.Figure()
        
        # Add actual spend bars
        fig.add_trace(go.Bar(
            name='Actual Spend',
            x=categories,
            y=actual_spend,
            marker_color='#FF6B6B'
        ))
        
        # Add benchmark range
        fig.add_trace(go.Bar(
            name='Industry Benchmark (High)',
            x=categories,
            y=benchmark_high,
            marker_color='#4ECDC4'
        ))
        
        fig.update_layout(
            title='Actual Spend vs Industry Benchmark',
            title_x=0.5,
            xaxis_title='Categories',
            yaxis_title='Spend Amount ($)',
            barmode='group',
            height=500,
            xaxis_tickangle=-45
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def get_summary_metrics(self):
        """Get summary metrics for dashboard."""
        return {
            'total_spend': f'${self.total_spend:,.2f}',
            'total_invoices': f'{self.total_invoices:,}',
            'vendor_count': f'{self.vendor_count}',
            'company_count': f'{self.company_count}',
            'category_count': len(self.category_totals),
            'avg_invoice': f'${self.total_spend/self.total_invoices:,.2f}' if self.total_invoices > 0 else '$0.00',
            'years_analyzed': ', '.join(map(str, sorted(self.yearly_data.keys())))
        }
    
    def get_category_details(self):
        """Get detailed category information."""
        details = []
        
        for category, spend in sorted(self.category_totals.items(), key=lambda x: x[1], reverse=True):
            invoice_count = len(self.categorized_spend[category])
            percentage = (spend / self.total_spend) * 100 if self.total_spend > 0 else 0
            
            details.append({
                'category': category.replace('_', ' ').title(),
                'spend': f'${spend:,.2f}',
                'percentage': f'{percentage:.1f}%',
                'invoice_count': invoice_count,
                'avg_invoice': f'${spend/invoice_count:,.2f}' if invoice_count > 0 else '$0.00'
            })
        
        return details
    
    def get_company_details(self):
        """Get detailed company information."""
        details = []
        
        for company, spend in sorted(self.company_spend.items(), key=lambda x: x[1], reverse=True):
            percentage = (spend / self.total_spend) * 100 if self.total_spend > 0 else 0
            
            details.append({
                'company': company,
                'spend': f'${spend:,.2f}',
                'percentage': f'{percentage:.1f}%'
            })
        
        return details
    
    def get_benchmark_details(self):
        """Get detailed benchmark comparison information."""
        details = []
        
        if 'benchmarks' not in self.industry_analysis:
            return details
        
        for category, benchmark_data in self.industry_analysis['benchmarks'].items():
            actual_spend = benchmark_data['actual_spend']
            benchmark = benchmark_data['benchmark']
            variance = benchmark_data['variance_percentage']
            status = benchmark_data['status']
            percentage_of_total = benchmark_data['percentage_of_total']
            
            details.append({
                'category': category.replace('_', ' ').title(),
                'actual_spend': f'${actual_spend:,.2f}',
                'benchmark_low': f'${benchmark["low"]:,.2f}',
                'benchmark_high': f'${benchmark["high"]:,.2f}',
                'benchmark_typical': f'${benchmark["typical"]:,.2f}',
                'variance_percentage': f'{variance:+.1f}%',
                'status': status,
                'percentage_of_total': f'{percentage_of_total:.1f}%'
            })
        
        return details
    
    def get_recommendations(self):
        """Get cost optimization recommendations."""
        recommendations = []
        
        if 'recommendations' not in self.industry_analysis:
            return recommendations
        
        for rec in self.industry_analysis['recommendations']:
            recommendations.append({
                'type': rec['type'].replace('_', ' ').title(),
                'category': rec.get('category', '').replace('_', ' ').title(),
                'vendor': rec.get('vendor', ''),
                'company': rec.get('company', ''),
                'priority': rec['priority'].title(),
                'message': rec['message'],
                'potential_savings': f'${rec["potential_savings"]:,.2f}'
            })
        
        return recommendations
    
    def get_enhanced_benchmark_chart(self):
        """Create enhanced benchmark comparison chart with actual vs benchmark data."""
        if 'benchmarks' not in self.industry_analysis:
            return self.get_benchmark_comparison_chart()  # Fallback to original
        
        categories = []
        actual_spend = []
        benchmark_low = []
        benchmark_high = []
        benchmark_typical = []
        variance_percentages = []
        
        for category, benchmark_data in self.industry_analysis['benchmarks'].items():
            categories.append(category.replace('_', ' ').title())
            actual_spend.append(benchmark_data['actual_spend'])
            benchmark_low.append(benchmark_data['benchmark']['low'])
            benchmark_high.append(benchmark_data['benchmark']['high'])
            benchmark_typical.append(benchmark_data['benchmark']['typical'])
            variance_percentages.append(benchmark_data['variance_percentage'])
        
        fig = go.Figure()
        
        # Add actual spend bars
        fig.add_trace(go.Bar(
            name='Actual Spend',
            x=categories,
            y=actual_spend,
            marker_color='#FF6B6B',
            text=[f'${val:,.0f}' for val in actual_spend],
            textposition='auto'
        ))
        
        # Add benchmark typical line
        fig.add_trace(go.Scatter(
            name='Industry Benchmark (Typical)',
            x=categories,
            y=benchmark_typical,
            mode='lines+markers',
            line=dict(color='#4ECDC4', width=3),
            marker=dict(size=8)
        ))
        
        # Add benchmark range
        fig.add_trace(go.Bar(
            name='Industry Benchmark (High)',
            x=categories,
            y=benchmark_high,
            marker_color='rgba(78, 205, 196, 0.3)',
            text=[f'${val:,.0f}' for val in benchmark_high],
            textposition='auto'
        ))
        
        # Add variance annotations
        for i, (cat, variance) in enumerate(zip(categories, variance_percentages)):
            fig.add_annotation(
                x=cat,
                y=actual_spend[i],
                text=f'{variance:+.1f}%',
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='red' if variance > 0 else 'green',
                ax=0,
                ay=-40
            )
        
        fig.update_layout(
            title='Actual Spend vs Industry Benchmark (Enhanced)',
            title_x=0.5,
            xaxis_title='Categories',
            yaxis_title='Spend Amount ($)',
            barmode='overlay',
            height=600,
            xaxis_tickangle=-45,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def get_ai_enhanced_insights(self):
        """Get AI-enhanced insights and analysis."""
        if not self.ai_enhanced_analysis:
            return {
                "ai_categorizations": [],
                "hidden_costs": [],
                "msp_analysis": [],
                "optimization_opportunities": []
            }
        
        insights = {
            "ai_categorizations": [],
            "hidden_costs": [],
            "msp_analysis": [],
            "optimization_opportunities": []
        }
        
        # Extract AI categorizations
        if 'benchmarks' in self.ai_enhanced_analysis:
            for benchmark in self.ai_enhanced_analysis['benchmarks']:
                ai_cat = benchmark.get('ai_categorization', {})
                if ai_cat:
                    insights["ai_categorizations"].append({
                        "vendor": benchmark['vendor'],
                        "category": ai_cat.get('primary_category', 'Unknown'),
                        "subcategory": ai_cat.get('subcategory', 'Unknown'),
                        "service_type": ai_cat.get('service_type', 'Unknown'),
                        "complexity_level": ai_cat.get('complexity_level', 'Unknown')
                    })
                
                # Extract hidden costs
                hidden_costs = ai_cat.get('hidden_costs', [])
                if hidden_costs:
                    insights["hidden_costs"].extend(hidden_costs)
                
                # Extract MSP services
                msp_services = ai_cat.get('msp_services', [])
                if msp_services:
                    insights["msp_analysis"].append({
                        "vendor": benchmark['vendor'],
                        "services": msp_services
                    })
                
                # Extract optimization opportunities
                ai_analysis = benchmark.get('ai_benchmark_analysis', {})
                if ai_analysis:
                    optimization = ai_analysis.get('optimization_opportunities', {})
                    if optimization.get('immediate_savings', '$0') != '$0':
                        insights["optimization_opportunities"].append({
                            "vendor": benchmark['vendor'],
                            "savings": optimization.get('immediate_savings', '$0'),
                            "opportunities": optimization.get('strategic_opportunities', [])
                        })
        
        return insights
    
    def get_ai_enhanced_chart(self):
        """Get AI-enhanced analysis chart showing categorization and insights."""
        insights = self.get_ai_enhanced_insights()
        
        if not insights["ai_categorizations"]:
            return json.dumps(go.Figure().update_layout(title="No AI-enhanced data available"), 
                            cls=plotly.utils.PlotlyJSONEncoder)
        
        # Create categorization breakdown
        categories = {}
        subcategories = {}
        
        for cat in insights["ai_categorizations"]:
            category = cat['category']
            subcategory = cat['subcategory']
            
            categories[category] = categories.get(category, 0) + 1
            subcategories[subcategory] = subcategories.get(subcategory, 0) + 1
        
        # Create the chart
        fig = go.Figure()
        
        # Add category breakdown
        fig.add_trace(go.Bar(
            x=list(categories.keys()),
            y=list(categories.values()),
            name='AI Categories',
            marker_color='#ff7f0e',
            text=list(categories.values()),
            textposition='auto'
        ))
        
        fig.update_layout(
            title='AI-Enhanced Categorization Analysis',
            xaxis_title='Category',
            yaxis_title='Number of Items',
            height=500
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

# Initialize dashboard data
dashboard_data = DashboardData()

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/summary')
def get_summary():
    """Get summary metrics."""
    return jsonify(dashboard_data.get_summary_metrics())

@app.route('/api/categories')
def get_categories():
    """Get category details."""
    return jsonify(dashboard_data.get_category_details())

@app.route('/api/companies')
def get_companies():
    """Get company details."""
    return jsonify(dashboard_data.get_company_details())

@app.route('/api/charts/spending-pie')
def get_spending_pie():
    """Get spending pie chart."""
    return dashboard_data.get_spending_pie_chart()

@app.route('/api/charts/vendor-bar')
def get_vendor_bar():
    """Get vendor bar chart."""
    return dashboard_data.get_vendor_bar_chart()

@app.route('/api/charts/company-bar')
def get_company_bar():
    """Get company bar chart."""
    return dashboard_data.get_company_bar_chart()

@app.route('/api/charts/vendor-company-heatmap')
def get_vendor_company_heatmap():
    """Get vendor vs company heatmap."""
    return dashboard_data.get_vendor_company_heatmap()

@app.route('/api/charts/monthly-trend')
def get_monthly_trend():
    """Get monthly trend chart."""
    return dashboard_data.get_monthly_trend_chart()

@app.route('/api/charts/yearly-comparison')
def get_yearly_comparison():
    """Get yearly comparison chart."""
    return dashboard_data.get_yearly_comparison_chart()

@app.route('/api/charts/benchmark-comparison')
def get_benchmark_comparison():
    """Get benchmark comparison chart."""
    return dashboard_data.get_benchmark_comparison_chart()

@app.route('/api/charts/enhanced-benchmark')
def get_enhanced_benchmark():
    """Get enhanced benchmark comparison chart."""
    return dashboard_data.get_enhanced_benchmark_chart()

@app.route('/api/benchmarks')
def get_benchmarks():
    """Get detailed benchmark information."""
    return jsonify(dashboard_data.get_benchmark_details())

@app.route('/api/recommendations')
def get_recommendations():
    """Get cost optimization recommendations."""
    return jsonify(dashboard_data.get_recommendations())

@app.route('/api/ai-insights')
def get_ai_insights():
    """Get AI-enhanced insights data."""
    return jsonify(dashboard_data.get_ai_enhanced_insights())

@app.route('/api/charts/ai-enhanced')
def get_ai_enhanced_chart():
    """Get AI-enhanced analysis chart."""
    return dashboard_data.get_ai_enhanced_chart()

def create_dashboard_template():
    """Create the HTML template for the dashboard."""
    template_dir = "templates"
    os.makedirs(template_dir, exist_ok=True)
    
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Licensing Analysis Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .metric-card { background: white; border-radius: 10px; padding: 20px; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .chart-container { background: white; border-radius: 10px; padding: 20px; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric-value { font-size: 2rem; font-weight: bold; color: #007bff; }
        .metric-label { color: #6c757d; font-size: 0.9rem; }
        .table-container { background: white; border-radius: 10px; padding: 20px; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .nav-tabs .nav-link { color: #495057; }
        .nav-tabs .nav-link.active { color: #007bff; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <div class="col-12">
                <h1 class="text-center my-4">Licensing Analysis Dashboard</h1>
                <p class="text-center text-muted">Real-time analysis of licensing costs and industry benchmarks (2024-2025)</p>
            </div>
        </div>
        
        <!-- Summary Metrics -->
        <div class="row" id="summary-metrics">
            <div class="col-md-2">
                <div class="metric-card text-center">
                    <div class="metric-value" id="total-spend">$0</div>
                    <div class="metric-label">Total Spend</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="metric-card text-center">
                    <div class="metric-value" id="total-invoices">0</div>
                    <div class="metric-label">Total Invoices</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="metric-card text-center">
                    <div class="metric-value" id="vendor-count">0</div>
                    <div class="metric-label">Vendors</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="metric-card text-center">
                    <div class="metric-value" id="company-count">0</div>
                    <div class="metric-label">Companies</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="metric-card text-center">
                    <div class="metric-value" id="avg-invoice">$0</div>
                    <div class="metric-label">Avg Invoice</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="metric-card text-center">
                    <div class="metric-value" id="years-analyzed">-</div>
                    <div class="metric-label">Years Analyzed</div>
                </div>
            </div>
        </div>
        
        <!-- Charts Row 1 -->
        <div class="row">
            <div class="col-md-6">
                <div class="chart-container">
                    <div id="spending-pie-chart"></div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="chart-container">
                    <div id="vendor-bar-chart"></div>
                </div>
            </div>
        </div>
        
        <!-- Charts Row 2 -->
        <div class="row">
            <div class="col-md-6">
                <div class="chart-container">
                    <div id="company-bar-chart"></div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="chart-container">
                    <div id="vendor-company-heatmap"></div>
                </div>
            </div>
        </div>
        
        <!-- Charts Row 3 -->
        <div class="row">
            <div class="col-md-6">
                <div class="chart-container">
                    <div id="monthly-trend-chart"></div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="chart-container">
                    <div id="yearly-comparison-chart"></div>
                </div>
            </div>
        </div>
        
        <!-- Charts Row 4 -->
        <div class="row">
            <div class="col-12">
                <div class="chart-container">
                    <div id="enhanced-benchmark-chart"></div>
                </div>
            </div>
        </div>
        
        <!-- Charts Row 5 -->
        <div class="row">
            <div class="col-12">
                <div class="chart-container">
                    <div id="benchmark-comparison-chart"></div>
                </div>
            </div>
        </div>
        
        <!-- Details Tables -->
        <div class="row">
            <div class="col-12">
                <div class="table-container">
                    <ul class="nav nav-tabs" id="detailsTabs" role="tablist">
                        <li class="nav-item" role="presentation">
                            <button class="nav-link active" id="category-tab" data-bs-toggle="tab" data-bs-target="#category-tab-pane" type="button" role="tab">Category Details</button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link" id="company-tab" data-bs-toggle="tab" data-bs-target="#company-tab-pane" type="button" role="tab">Company Details</button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link" id="benchmark-tab" data-bs-toggle="tab" data-bs-target="#benchmark-tab-pane" type="button" role="tab">Benchmark Analysis</button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link" id="recommendations-tab" data-bs-toggle="tab" data-bs-target="#recommendations-tab-pane" type="button" role="tab">Recommendations</button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link" id="ai-insights-tab" data-bs-toggle="tab" data-bs-target="#ai-insights-tab-pane" type="button" role="tab">AI Insights</button>
                        </li>
                    </ul>
                    <div class="tab-content" id="detailsTabsContent">
                        <div class="tab-pane fade show active" id="category-tab-pane" role="tabpanel">
                            <div class="table-responsive">
                                <table class="table table-striped" id="category-table">
                                    <thead>
                                        <tr>
                                            <th>Category</th>
                                            <th>Total Spend</th>
                                            <th>Percentage</th>
                                            <th>Invoice Count</th>
                                            <th>Avg Invoice</th>
                                        </tr>
                                    </thead>
                                    <tbody id="category-tbody">
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div class="tab-pane fade" id="company-tab-pane" role="tabpanel">
                            <div class="table-responsive">
                                <table class="table table-striped" id="company-table">
                                    <thead>
                                        <tr>
                                            <th>Company</th>
                                            <th>Total Spend</th>
                                            <th>Percentage</th>
                                        </tr>
                                    </thead>
                                    <tbody id="company-tbody">
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div class="tab-pane fade" id="benchmark-tab-pane" role="tabpanel">
                            <div class="table-responsive">
                                <table class="table table-striped" id="benchmark-table">
                                    <thead>
                                        <tr>
                                            <th>Category</th>
                                            <th>Actual Spend</th>
                                            <th>Benchmark (Low)</th>
                                            <th>Benchmark (High)</th>
                                            <th>Benchmark (Typical)</th>
                                            <th>Variance</th>
                                            <th>Status</th>
                                            <th>% of Total</th>
                                        </tr>
                                    </thead>
                                    <tbody id="benchmark-tbody">
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div class="tab-pane fade" id="recommendations-tab-pane" role="tabpanel">
                            <div class="table-responsive">
                                <table class="table table-striped" id="recommendations-table">
                                    <thead>
                                        <tr>
                                            <th>Type</th>
                                            <th>Category/Vendor/Company</th>
                                            <th>Priority</th>
                                            <th>Message</th>
                                            <th>Potential Savings</th>
                                        </tr>
                                    </thead>
                                    <tbody id="recommendations-tbody">
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div class="tab-pane fade" id="ai-insights-tab-pane" role="tabpanel">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="chart-container">
                                        <div id="ai-enhanced-chart"></div>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="table-responsive">
                                        <h5>AI Categorizations</h5>
                                        <table class="table table-striped" id="ai-categorizations-table">
                                            <thead>
                                                <tr>
                                                    <th>Vendor</th>
                                                    <th>Category</th>
                                                    <th>Subcategory</th>
                                                    <th>Service Type</th>
                                                    <th>Complexity</th>
                                                </tr>
                                            </thead>
                                            <tbody id="ai-categorizations-tbody">
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                            <div class="row mt-3">
                                <div class="col-md-6">
                                    <div class="table-responsive">
                                        <h5>Hidden Costs Identified</h5>
                                        <table class="table table-striped" id="hidden-costs-table">
                                            <thead>
                                                <tr>
                                                    <th>Hidden Cost</th>
                                                    <th>Frequency</th>
                                                </tr>
                                            </thead>
                                            <tbody id="hidden-costs-tbody">
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="table-responsive">
                                        <h5>MSP Services Analysis</h5>
                                        <table class="table table-striped" id="msp-services-table">
                                            <thead>
                                                <tr>
                                                    <th>Vendor</th>
                                                    <th>Services</th>
                                                </tr>
                                            </thead>
                                            <tbody id="msp-services-tbody">
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Load summary metrics
        $.get('/api/summary', function(data) {
            $('#total-spend').text(data.total_spend);
            $('#total-invoices').text(data.total_invoices);
            $('#vendor-count').text(data.vendor_count);
            $('#company-count').text(data.company_count);
            $('#avg-invoice').text(data.avg_invoice);
            $('#years-analyzed').text(data.years_analyzed);
        });
        
        // Load category details
        $.get('/api/categories', function(data) {
            const tbody = $('#category-tbody');
            tbody.empty();
            
            data.forEach(function(category) {
                tbody.append(`
                    <tr>
                        <td>${category.category}</td>
                        <td>${category.spend}</td>
                        <td>${category.percentage}</td>
                        <td>${category.invoice_count}</td>
                        <td>${category.avg_invoice}</td>
                    </tr>
                `);
            });
        });
        
        // Load company details
        $.get('/api/companies', function(data) {
            const tbody = $('#company-tbody');
            tbody.empty();
            
            data.forEach(function(company) {
                tbody.append(`
                    <tr>
                        <td>${company.company}</td>
                        <td>${company.spend}</td>
                        <td>${company.percentage}</td>
                    </tr>
                `);
            });
        });
        
        // Load charts
        $.get('/api/charts/spending-pie', function(data) {
            Plotly.newPlot('spending-pie-chart', JSON.parse(data).data, JSON.parse(data).layout);
        });
        
        $.get('/api/charts/vendor-bar', function(data) {
            Plotly.newPlot('vendor-bar-chart', JSON.parse(data).data, JSON.parse(data).layout);
        });
        
        $.get('/api/charts/company-bar', function(data) {
            Plotly.newPlot('company-bar-chart', JSON.parse(data).data, JSON.parse(data).layout);
        });
        
        $.get('/api/charts/vendor-company-heatmap', function(data) {
            Plotly.newPlot('vendor-company-heatmap', JSON.parse(data).data, JSON.parse(data).layout);
        });
        
        $.get('/api/charts/monthly-trend', function(data) {
            if (data) {
                Plotly.newPlot('monthly-trend-chart', JSON.parse(data).data, JSON.parse(data).layout);
            } else {
                $('#monthly-trend-chart').html('<p class="text-center text-muted">No monthly data available</p>');
            }
        });
        
        $.get('/api/charts/yearly-comparison', function(data) {
            if (data) {
                Plotly.newPlot('yearly-comparison-chart', JSON.parse(data).data, JSON.parse(data).layout);
            } else {
                $('#yearly-comparison-chart').html('<p class="text-center text-muted">No yearly data available</p>');
            }
        });
        
        $.get('/api/charts/enhanced-benchmark', function(data) {
            if (data) {
                Plotly.newPlot('enhanced-benchmark-chart', JSON.parse(data).data, JSON.parse(data).layout);
            } else {
                $('#enhanced-benchmark-chart').html('<p class="text-center text-muted">No benchmark data available</p>');
            }
        });
        
        $.get('/api/charts/benchmark-comparison', function(data) {
            if (data) {
                Plotly.newPlot('benchmark-comparison-chart', JSON.parse(data).data, JSON.parse(data).layout);
            } else {
                $('#benchmark-comparison-chart').html('<p class="text-center text-muted">No benchmark data available</p>');
            }
        });
        
        // Load benchmark details
        $.get('/api/benchmarks', function(data) {
            const tbody = $('#benchmark-tbody');
            tbody.empty();
            
            data.forEach(function(benchmark) {
                tbody.append(`
                    <tr>
                        <td>${benchmark.category}</td>
                        <td>${benchmark.actual_spend}</td>
                        <td>${benchmark.benchmark_low}</td>
                        <td>${benchmark.benchmark_high}</td>
                        <td>${benchmark.benchmark_typical}</td>
                        <td>${benchmark.variance_percentage}</td>
                        <td>${benchmark.status}</td>
                        <td>${benchmark.percentage_of_total}</td>
                    </tr>
                `);
            });
        });
        
        // Load recommendations
        $.get('/api/recommendations', function(data) {
            const tbody = $('#recommendations-tbody');
            tbody.empty();
            
            data.forEach(function(rec) {
                const categoryVendorCompany = rec.category || rec.vendor || rec.company || 'N/A';
                tbody.append(`
                    <tr>
                        <td>${rec.type}</td>
                        <td>${categoryVendorCompany}</td>
                        <td><span class="badge bg-${rec.priority === 'High' ? 'danger' : rec.priority === 'Medium' ? 'warning' : 'success'}">${rec.priority}</span></td>
                        <td>${rec.message}</td>
                        <td>${rec.potential_savings}</td>
                    </tr>
                `);
            });
        });
        
        // Load AI-enhanced insights
        $.get('/api/ai-insights', function(data) {
            // Load AI categorizations
            const catTbody = $('#ai-categorizations-tbody');
            catTbody.empty();
            
            data.ai_categorizations.forEach(function(cat) {
                catTbody.append(`
                    <tr>
                        <td>${cat.vendor}</td>
                        <td>${cat.category}</td>
                        <td>${cat.subcategory}</td>
                        <td>${cat.service_type}</td>
                        <td>${cat.complexity_level}</td>
                    </tr>
                `);
            });
            
            // Load hidden costs
            const hiddenCostsTbody = $('#hidden-costs-tbody');
            hiddenCostsTbody.empty();
            
            const costFrequency = {};
            data.hidden_costs.forEach(function(cost) {
                costFrequency[cost] = (costFrequency[cost] || 0) + 1;
            });
            
            Object.entries(costFrequency).forEach(function([cost, frequency]) {
                hiddenCostsTbody.append(`
                    <tr>
                        <td>${cost}</td>
                        <td>${frequency}</td>
                    </tr>
                `);
            });
            
            // Load MSP services
            const mspTbody = $('#msp-services-tbody');
            mspTbody.empty();
            
            data.msp_analysis.forEach(function(msp) {
                mspTbody.append(`
                    <tr>
                        <td>${msp.vendor}</td>
                        <td>${msp.services.join(', ')}</td>
                    </tr>
                `);
            });
        });
        
        // Load AI-enhanced chart
        $.get('/api/charts/ai-enhanced', function(data) {
            if (data) {
                Plotly.newPlot('ai-enhanced-chart', JSON.parse(data).data, JSON.parse(data).layout);
            } else {
                $('#ai-enhanced-chart').html('<p class="text-center text-muted">No AI-enhanced data available</p>');
            }
        });
        
        // Auto-refresh every 30 seconds
        setInterval(function() {
            location.reload();
        }, 30000);
    </script>
</body>
</html>
    """
    
    with open(f"{template_dir}/dashboard.html", 'w') as f:
        f.write(html_content)

def main():
    """Start the dashboard server."""
    print("Creating interactive dashboard...")
    
    # Create template
    create_dashboard_template()
    
    print("Dashboard template created")
    print("Starting dashboard server...")
    print("Dashboard will be available at: http://localhost:5000")
    print("Auto-refresh every 30 seconds")
    print("Press Ctrl+C to stop the server")
    
    # Start Flask server
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main() 