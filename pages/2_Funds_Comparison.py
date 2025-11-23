import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re

st.title("Funds Comparison")

# Helper function to parse AUM value (M stands for million)
def parse_aum(aum_value):
    """Parse AUM value, handling 'M' for million. 
    If AUM contains 'M', it's in millions. Otherwise, assume it's already in the base unit."""
    if pd.isna(aum_value) or aum_value == 'N/A' or aum_value == '':
        return None
    
    try:
        # Convert to string and remove whitespace
        aum_str = str(aum_value).strip().upper()
        
        # Check if it contains 'M' for million
        if 'M' in aum_str:
            # Extract number part (handles decimals)
            number_str = re.sub(r'[^\d.]', '', aum_str)
            if number_str:
                return float(number_str) * 1e6  # Convert millions to actual number
        elif 'B' in aum_str:
            # Handle billions
            number_str = re.sub(r'[^\d.]', '', aum_str)
            if number_str:
                return float(number_str) * 1e9
        elif 'K' in aum_str:
            # Handle thousands
            number_str = re.sub(r'[^\d.]', '', aum_str)
            if number_str:
                return float(number_str) * 1e3
        else:
            # Try to parse as float directly (assume it's already in base units)
            return float(aum_value)
    except (ValueError, TypeError):
        return None

# Helper function to parse fees (percentage)
def parse_fees(fees_value):
    """Parse fees value, assuming it's a percentage"""
    if pd.isna(fees_value) or fees_value == 'N/A' or fees_value == '':
        return None
    
    try:
        # Convert to string and remove % sign if present
        fees_str = str(fees_value).strip().replace('%', '').replace(',', '.')
        fees_float = float(fees_str)
        # Return as decimal (e.g., 1.5% becomes 0.015)
        return fees_float / 100.0
    except (ValueError, TypeError):
        return None

# Helper function to calculate revenue
def calculate_revenue(aum_value, fees_value):
    """Calculate fund revenue = AUM × Fees"""
    aum = parse_aum(aum_value)
    fees = parse_fees(fees_value)
    
    if aum is not None and fees is not None:
        return aum * fees
    return None

# Function to calculate metrics for a fund
def calculate_fund_metrics(fund_name, nav_df, periods):
    """Calculate performance, volatility, and excess return for different periods"""
    metrics = {}
    
    # Convert date to datetime
    calc_df = nav_df.copy()
    calc_df['date'] = pd.to_datetime(calc_df['date'])
    calc_df = calc_df.sort_values('date')
    
    # Calculate daily returns
    calc_df['fund_returns'] = calc_df['nav'].pct_change()
    calc_df['bench_returns'] = calc_df['bench'].pct_change()
    calc_df['excess_returns'] = calc_df['fund_returns'] - calc_df['bench_returns']
    
    # Get the fund's current date (last date in its data)
    fund_current_date = calc_df['date'].max()
    
    for period_name, years_offset in periods.items():
        # Calculate start date relative to fund's current date
        start_date = fund_current_date - pd.DateOffset(years=years_offset)
        period_df = calc_df[calc_df['date'] >= start_date].copy()
        
        if len(period_df) < 2:
            metrics[period_name] = {
                'perf': 'N/A',
                'excess_return': 'N/A',
                'volatility': 'N/A'
            }
            continue
        
        # Calculate number of trading days per year (approximately 252)
        trading_days = len(period_df)
        years = trading_days / 252.0
        
        if years <= 0:
            years = 1.0
        
        # Performance (annualized return)
        if period_df['nav'].iloc[0] > 0 and period_df['nav'].iloc[-1] > 0:
            fund_perf = ((period_df['nav'].iloc[-1] / period_df['nav'].iloc[0]) ** (1/years) - 1) * 100
        else:
            fund_perf = 0
        
        if period_df['bench'].iloc[0] > 0 and period_df['bench'].iloc[-1] > 0:
            bench_perf = ((period_df['bench'].iloc[-1] / period_df['bench'].iloc[0]) ** (1/years) - 1) * 100
        else:
            bench_perf = 0
        
        # Excess return (fund performance - benchmark performance)
        excess_return = fund_perf - bench_perf
        
        # Volatility (annualized standard deviation)
        fund_vol = period_df['fund_returns'].std() * np.sqrt(252) * 100
        
        metrics[period_name] = {
            'perf': fund_perf,
            'excess_return': excess_return,
            'volatility': fund_vol
        }
    
    return metrics

# Get all funds data
funds_list = st.session_state["funds_list"]
nav_dfs = st.session_state["nav_dfs"]

# Periods defined as number of years
periods = {
    '1Y': 1,
    '3Y': 3
}

# Calculate metrics for all funds
all_funds_data = []

for idx, fund_row in funds_list.iterrows():
    fund_name = fund_row['Fund']
    
    if fund_name not in nav_dfs:
        continue
    
    nav_df = nav_dfs[fund_name]
    metrics = calculate_fund_metrics(fund_name, nav_df, periods)
    
    # Calculate revenue
    aum = fund_row.get('AUM', 'N/A')
    fees = fund_row.get('Fees', 'N/A')
    revenue = calculate_revenue(aum, fees)
    
    # Format revenue for display
    if revenue is not None:
        if revenue >= 1e6:
            revenue_display = f"€{revenue/1e6:.2f}M"
        elif revenue >= 1e3:
            revenue_display = f"€{revenue/1e3:.2f}K"
        else:
            revenue_display = f"€{revenue:.2f}"
    else:
        revenue_display = 'N/A'
    
    # Get fund characteristics
    fund_data = {
        'Fund': fund_name,
        'Type': fund_row.get('Type', 'N/A'),
        'Sub Type': fund_row.get('Sub Type', 'N/A'),
        'Perf 1Y (%)': f"{metrics['1Y']['perf']:.2f}" if metrics['1Y']['perf'] != 'N/A' else 'N/A',
        'Perf 3Y (%)': f"{metrics['3Y']['perf']:.2f}" if metrics['3Y']['perf'] != 'N/A' else 'N/A',
        'Excess Return 1Y (%)': f"{metrics['1Y']['excess_return']:.2f}" if metrics['1Y']['excess_return'] != 'N/A' else 'N/A',
        'Excess Return 3Y (%)': f"{metrics['3Y']['excess_return']:.2f}" if metrics['3Y']['excess_return'] != 'N/A' else 'N/A',
        'Volatility 1Y (%)': f"{metrics['1Y']['volatility']:.2f}" if metrics['1Y']['volatility'] != 'N/A' else 'N/A',
        'Volatility 3Y (%)': f"{metrics['3Y']['volatility']:.2f}" if metrics['3Y']['volatility'] != 'N/A' else 'N/A',
        'Revenue': revenue_display,
        'E Score': fund_row.get('E Score', 'N/A') if pd.notna(fund_row.get('E Score')) else 'N/A',
        'Rating': fund_row.get('Rating', 'N/A') if pd.notna(fund_row.get('Rating')) else 'N/A',
        'Peer Ranking 1Y': fund_row.get('Peer Ranking 1Y', 'N/A') if pd.notna(fund_row.get('Peer Ranking 1Y')) else 'N/A',
        'Peer Ranking 3Y': fund_row.get('Peer Ranking 3Y', 'N/A') if pd.notna(fund_row.get('Peer Ranking 3Y')) else 'N/A'
    }
    
    all_funds_data.append(fund_data)

# Create DataFrame
all_funds_df = pd.DataFrame(all_funds_data)

if len(all_funds_df) > 0:
    # Group by Type first, then Sub Type if Type is the same
    if 'Type' in all_funds_df.columns and all_funds_df['Type'].notna().any():
        # Group by Type
        types = sorted(all_funds_df['Type'].dropna().unique())
        
        for fund_type in types:
            type_df = all_funds_df[all_funds_df['Type'] == fund_type].copy()
            
            # If Sub Type exists and has values, group by Sub Type within Type
            if 'Sub Type' in type_df.columns and type_df['Sub Type'].notna().any():
                sub_types = sorted(type_df['Sub Type'].dropna().unique())
                
                for sub_type in sub_types:
                    sub_type_df = type_df[type_df['Sub Type'] == sub_type].copy()
                    
                    # Remove grouping columns from display
                    display_cols = [col for col in sub_type_df.columns if col not in ['Type', 'Sub Type']]
                    category_display = sub_type_df[display_cols]
                    
                    st.write(f"### {fund_type} - {sub_type}")
                    st.dataframe(
                        category_display,
                        use_container_width=True,
                        hide_index=True
                    )
                    st.markdown("---")
            else:
                # No Sub Type, just show Type
                display_cols = [col for col in type_df.columns if col not in ['Type', 'Sub Type']]
                category_display = type_df[display_cols]
                
                st.write(f"### {fund_type}")
                st.dataframe(
                    category_display,
                    use_container_width=True,
                    hide_index=True
                )
                st.markdown("---")
    elif 'Sub Type' in all_funds_df.columns and all_funds_df['Sub Type'].notna().any():
        # Group by Sub Type only
        sub_types = sorted(all_funds_df['Sub Type'].dropna().unique())
        
        for sub_type in sub_types:
            sub_type_df = all_funds_df[all_funds_df['Sub Type'] == sub_type].copy()
            
            display_cols = [col for col in sub_type_df.columns if col != 'Sub Type']
            category_display = sub_type_df[display_cols]
            
            st.write(f"### {sub_type}")
            st.dataframe(
                category_display,
                use_container_width=True,
                hide_index=True
            )
            st.markdown("---")
    else:
        # If no category column, show all funds
        st.dataframe(
            all_funds_df,
            use_container_width=True,
            hide_index=True
        )
else:
    st.warning("No fund data available for comparison.")

