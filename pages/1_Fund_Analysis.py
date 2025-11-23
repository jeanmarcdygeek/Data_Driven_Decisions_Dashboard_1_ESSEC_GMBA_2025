import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re

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

st.title("Fund Analysis")

fund_list = st.session_state["funds_list"]["Fund"].tolist()

selected_fund = st.selectbox("Select a fund", fund_list)

if selected_fund:

    st.write(f"### Fund Characteristics")
    
    fund_char_df = st.session_state["funds_list"][st.session_state["funds_list"]["Fund"] == selected_fund]
    fund_row = fund_char_df.iloc[0]
    
    # Create two columns for displaying fund characteristics
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container():
            st.markdown("#### 📊 Basic Information")
            st.markdown(f"**Fund Name:** {fund_row.get('Fund', 'N/A')}")
            st.markdown(f"**Type:** {fund_row.get('Type', 'N/A')}")
            st.markdown(f"**Sub Type:** {fund_row.get('Sub Type', 'N/A')}")
            st.markdown(f"**Benchmark:** {fund_row.get('Benchmark Name', 'N/A')}")
            st.markdown(f"**Start Date:** {fund_row.get('Start date', 'N/A')}")
        
        st.markdown("")  # Add spacing
        
        with st.container():
            st.markdown("#### 👤 Manager Information")
            st.markdown(f"**Manager:** {fund_row.get('Manager', 'N/A')}")
            st.markdown(f"**Age:** {fund_row.get('Age', 'N/A')}")
            st.markdown(f"**Gender:** {fund_row.get('Gender', 'N/A')}")
    
    with col2:
        with st.container():
            st.markdown("#### 📈 Performance Metrics")
            # Format AUM if it exists
            aum = fund_row.get('AUM', 'N/A')
            if pd.notna(aum) and aum != 'N/A':
                try:
                    aum_float = float(aum)
                    if aum_float >= 1e9:
                        aum_display = f"€{aum_float/1e9:.2f}B"
                    elif aum_float >= 1e6:
                        aum_display = f"€{aum_float/1e6:.2f}M"
                    else:
                        aum_display = f"€{aum_float:,.0f}"
                except:
                    aum_display = str(aum)
            else:
                aum_display = 'N/A'
            st.markdown(f"**AUM:** {aum_display}")
            
            rating = fund_row.get('Rating', 'N/A')
            if pd.notna(rating) and rating != 'N/A':
                st.markdown(f"**Rating:** {rating}")
            else:
                st.markdown(f"**Rating:** N/A")
            
            fees = fund_row.get('Fees', 'N/A')
            if pd.notna(fees) and fees != 'N/A':
                st.markdown(f"**Fees:** {fees}")
            else:
                st.markdown(f"**Fees:** N/A")
            
            # Calculate and display revenue
            revenue = calculate_revenue(aum, fees)
            if revenue is not None:
                if revenue >= 1e6:
                    revenue_display = f"€{revenue/1e6:.2f}M"
                elif revenue >= 1e3:
                    revenue_display = f"€{revenue/1e3:.2f}K"
                else:
                    revenue_display = f"€{revenue:.2f}"
                st.markdown(f"**Revenue:** {revenue_display}")
            else:
                st.markdown(f"**Revenue:** N/A")
        
        st.markdown("")  # Add spacing
        
        with st.container():
            st.markdown("#### 🏆 Rankings")
            peer_1y = fund_row.get('Peer Ranking 1Y', 'N/A')
            peer_3y = fund_row.get('Peer Ranking 3Y', 'N/A')
            st.markdown(f"**Peer Ranking 1Y:** {peer_1y if pd.notna(peer_1y) else 'N/A'}")
            st.markdown(f"**Peer Ranking 3Y:** {peer_3y if pd.notna(peer_3y) else 'N/A'}")
        
        st.markdown("")  # Add spacing
        
        with st.container():
            st.markdown("#### 🌱 ESG")
            esg_label = fund_row.get('ESG Label', 'N/A')
            e_score = fund_row.get('E Score', 'N/A')
            st.markdown(f"**ESG Label:** {esg_label if pd.notna(esg_label) else 'N/A'}")
            st.markdown(f"**E Score:** {e_score if pd.notna(e_score) else 'N/A'}")

    df = st.session_state["nav_dfs"][selected_fund]

    col1, col2 = st.columns(2)
    with col1:
        min_date = st.date_input("Select a start date", value=df["date"].min(), min_value=df["date"].min(), max_value=df["date"].max())
    with col2:
        max_date = st.date_input("Select an end date", value=df["date"].max(), min_value=df["date"].min(), max_value=df["date"].max())

    recompute_from_date = st.checkbox("Recompute from Startdate")


    df = df[df["date"] >= min_date.strftime("%Y-%m-%d")]
    df = df[df["date"] <= max_date.strftime("%Y-%m-%d")]
    df = df.sort_values(by="date")

    if recompute_from_date:
        display_df = df.copy()
        display_df["ptf_returns"] = display_df["nav"].pct_change() + 1
        display_df["bench_returns"] = display_df["bench"].pct_change() + 1

        display_df["nav"] = display_df["ptf_returns"] 
        display_df["bench"] = display_df["bench_returns"] 

        display_df.loc[display_df["date"] == min_date.strftime("%Y-%m-%d"), "nav"] = 100
        display_df.loc[display_df["date"] == min_date.strftime("%Y-%m-%d"), "bench"] = 100
        
        display_df["nav"] = display_df["nav"].cumprod()
        display_df["bench"] = display_df["bench"].cumprod()
    else :
        display_df = df.copy()

    # Calculate summary metrics table
    st.write("## Summary Metrics")
    
    # Convert date to datetime for calculations
    calc_df = display_df.copy()
    calc_df['date'] = pd.to_datetime(calc_df['date'])
    calc_df = calc_df.sort_values('date')
    
    # Calculate daily returns
    calc_df['fund_returns'] = calc_df['nav'].pct_change()
    calc_df['bench_returns'] = calc_df['bench'].pct_change()
    calc_df['excess_returns'] = calc_df['fund_returns'] - calc_df['bench_returns']
    
    # Get current date (last date in data)
    current_date = calc_df['date'].max()
    
    # Define periods
    periods = {
        'YTD': current_date.replace(month=1, day=1),
        '3Y': current_date - pd.DateOffset(years=3),
        '5Y': current_date - pd.DateOffset(years=5)
    }
    
    # Calculate metrics for each period
    summary_data = []
    
    for period_name, start_date in periods.items():
        period_df = calc_df[calc_df['date'] >= start_date].copy()
        
        if len(period_df) < 2:
            # Not enough data for this period
            summary_data.append({
                'Period': period_name,
                'Fund Volatility (%)': 'N/A',
                'Bench Volatility (%)': 'N/A',
                'Fund Performance (%)': 'N/A',
                'Bench Performance (%)': 'N/A',
                'Tracking Error (%)': 'N/A',
                'Sharpe Ratio': 'N/A'
            })
            continue
        
        # Calculate number of trading days per year (approximately 252)
        trading_days = len(period_df)
        years = trading_days / 252.0
        
        if years <= 0:
            years = 1.0
        
        # Volatility (annualized standard deviation)
        fund_vol = period_df['fund_returns'].std() * np.sqrt(252) * 100
        bench_vol = period_df['bench_returns'].std() * np.sqrt(252) * 100
        
        # Performance (total return for YTD, annualized for 3Y and 5Y)
        if period_df['nav'].iloc[0] > 0 and period_df['nav'].iloc[-1] > 0:
            if period_name == 'YTD':
                # Total return for YTD
                fund_perf = ((period_df['nav'].iloc[-1] / period_df['nav'].iloc[0]) - 1) * 100
            else:
                # Annualized return for 3Y and 5Y
                fund_perf = ((period_df['nav'].iloc[-1] / period_df['nav'].iloc[0]) ** (1/years) - 1) * 100
        else:
            fund_perf = 0
        
        if period_df['bench'].iloc[0] > 0 and period_df['bench'].iloc[-1] > 0:
            if period_name == 'YTD':
                # Total return for YTD
                bench_perf = ((period_df['bench'].iloc[-1] / period_df['bench'].iloc[0]) - 1) * 100
            else:
                # Annualized return for 3Y and 5Y
                bench_perf = ((period_df['bench'].iloc[-1] / period_df['bench'].iloc[0]) ** (1/years) - 1) * 100
        else:
            bench_perf = 0
        
        # Tracking Error (Fund Volatility - Benchmark Volatility)
        tracking_error = fund_vol - bench_vol
        
        # Sharpe Ratio (annualized return / annualized volatility, assuming risk-free rate = 0)
        # Calculate annualized return for Sharpe ratio (even for YTD)
        if period_df['nav'].iloc[0] > 0 and period_df['nav'].iloc[-1] > 0:
            fund_perf_annualized = ((period_df['nav'].iloc[-1] / period_df['nav'].iloc[0]) ** (1/years) - 1) * 100
        else:
            fund_perf_annualized = 0
        
        if fund_vol > 0:
            sharpe_ratio = (fund_perf_annualized / 100) / (fund_vol / 100)
        else:
            sharpe_ratio = 0
        
        summary_data.append({
            'Period': period_name,
            'Fund Volatility (%)': f'{fund_vol:.2f}',
            'Bench Volatility (%)': f'{bench_vol:.2f}',
            'Fund Performance (%)': f'{fund_perf:.2f}',
            'Bench Performance (%)': f'{bench_perf:.2f}',
            'Tracking Error (%)': f'{tracking_error:.2f}',
            'Sharpe Ratio': f'{sharpe_ratio:.2f}'
        })
    
    # Create and display summary table
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    st.write("## Performance Chart")
    display_df = display_df.rename(columns={"nav": "Fund", "bench": "Benchmark"})
    st.line_chart(x="date", y=["Fund","Benchmark"], data=display_df, y_label="Performance (%)")