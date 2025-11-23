import streamlit as st
import pandas as pd
import numpy as np

st.title("Bonus Allocation Task")

st.markdown("### 💰 Bonus Allocation Decision Guide")
with st.expander("How to Allocate Your €1,000,000 Bonus Budget", expanded=True):
    st.markdown("""
    #### Your Task
    You have **€1,000,000** to allocate as bonuses to portfolio managers based on their fund's performance and characteristics.
    
    #### Step-by-Step Decision Framework
    
    **Step 1: Identify Top Performers**
    - Look at **Performance (1Y and 3Y)** - prioritize managers with consistent strong returns
    - Check **Excess Return** - reward managers who beat their benchmarks
    - Consider **Peer Rankings** - lower numbers (1-20) indicate top performers
    
    **Step 2: Evaluate Risk Management**
    - Review **Volatility** - reward managers who achieved good returns with lower risk
    - Check **Sharpe Ratio** - higher ratios indicate better risk-adjusted performance
    - Lower **Tracking Error** can indicate more consistent performance
    
    **Step 3: Consider Long-term Consistency**
    - Compare **1Y vs 3Y performance** - consistent performers over time deserve recognition
    - Managers with strong **3Y rankings** show sustained excellence
    
    **Step 4: Factor in Quality Indicators**
    - **Rating** (out of 5) - higher ratings indicate overall fund quality
    - **AUM** - larger funds may indicate investor confidence
    - **ESG Score** - consider rewarding sustainable practices (lower E Score is better)
    
    **Step 5: Allocation Strategy Suggestions**
    
    **Option A: Performance-Based (Recommended)**
    - Allocate 60-70% based on performance metrics (returns, excess returns, rankings)
    - Allocate 20-30% based on risk-adjusted metrics (Sharpe ratio, volatility)
    - Allocate 10% based on quality factors (rating, ESG)
    
    **Option B: Balanced Approach**
    - Weight 1Y performance: 30%
    - Weight 3Y performance: 40% (emphasize consistency)
    - Weight risk metrics: 20%
    - Weight quality/ESG: 10%
    
    **Option C: Top Performers Focus**
    - Identify top 5-10 performers across multiple metrics
    - Allocate larger bonuses to these top performers
    - Distribute remaining budget to other managers proportionally
    
    #### Key Questions to Ask Yourself:
    1. **Who consistently outperformed?** (Check 1Y and 3Y performance)
    2. **Who took smart risks?** (High returns with reasonable volatility)
    3. **Who beat the market?** (Positive excess returns)
    4. **Who ranks highest?** (Low peer rankings = top performers)
    5. **Who manages quality funds?** (High ratings, good ESG scores)
    
    #### Tips for Fair Allocation:
    - Don't just look at one metric - use multiple indicators
    - Consider both short-term (1Y) and long-term (3Y) performance
    - Reward consistency - managers who perform well over time
    - Balance performance with risk - high returns with high risk may not be ideal
    - Consider ESG factors if sustainability is important to your organization
    
    #### Example Allocation Logic:
    ```
    Base Allocation = (Performance Score × 0.5) + (Risk-Adjusted Score × 0.3) + (Quality Score × 0.2)
    Final Bonus = (Base Allocation / Sum of All Base Allocations) × €1,000,000
    ```
    
    **Remember:** There's no single "right" answer. Use the data to make informed, fair decisions that align with your organization's priorities.
    """)

st.markdown("---")

# Bonus Allocation Form
st.markdown("### 📊 Test Your Bonus Allocation")

# Get funds list
if "funds_list" in st.session_state:
    funds_list = st.session_state["funds_list"]
    
    # Budget
    BUDGET = 1000000  # €1,000,000
    
    st.markdown(f"**Total Budget:** €{BUDGET:,}")
    
    # Create allocation dataframe
    if "bonus_allocations" not in st.session_state:
        # Initialize with all funds and zero allocations
        allocation_data = []
        for idx, row in funds_list.iterrows():
            allocation_data.append({
                'Fund': row['Fund'],
                'Manager': row.get('Manager', 'N/A'),
                'Bonus (€)': 0.0
            })
        st.session_state["bonus_allocations"] = pd.DataFrame(allocation_data)
    
    # Display editable dataframe
    st.markdown("**Enter bonus amounts for each fund/manager:**")
    edited_df = st.data_editor(
        st.session_state["bonus_allocations"],
        column_config={
            "Fund": st.column_config.TextColumn("Fund", disabled=True),
            "Manager": st.column_config.TextColumn("Manager", disabled=True),
            "Bonus (€)": st.column_config.NumberColumn(
                "Bonus (€)",
                min_value=0.0,
                max_value=BUDGET,
                step=1000.0,
                format="€%d"
            )
        },
        hide_index=True,
        use_container_width=True,
        num_rows="fixed"
    )
    
    # Update session state
    st.session_state["bonus_allocations"] = edited_df
    
    # Calculate metrics
    st.markdown("---")
    st.markdown("### 📈 Allocation Metrics")
    
    total_allocated = edited_df['Bonus (€)'].sum()
    remaining_budget = BUDGET - total_allocated
    percentage_used = (total_allocated / BUDGET * 100) if BUDGET > 0 else 0
    
    # Create metrics columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Allocated",
            f"€{total_allocated:,.0f}",
            delta=f"{percentage_used:.1f}% of budget" if percentage_used <= 100 else "Over budget!"
        )
    
    with col2:
        st.metric(
            "Remaining Budget",
            f"€{remaining_budget:,.0f}",
            delta=f"€{abs(remaining_budget):,.0f}" if remaining_budget < 0 else None,
            delta_color="inverse" if remaining_budget < 0 else "normal"
        )
    
    with col3:
        num_managers_with_bonus = (edited_df['Bonus (€)'] > 0).sum()
        total_managers = len(edited_df)
        st.metric(
            "Managers with Bonus",
            f"{num_managers_with_bonus}/{total_managers}",
            delta=f"{(num_managers_with_bonus/total_managers*100):.1f}%"
        )
    
    with col4:
        avg_bonus = edited_df['Bonus (€)'].mean()
        st.metric(
            "Average Bonus",
            f"€{avg_bonus:,.0f}",
            delta=f"€{edited_df['Bonus (€)'].median():,.0f} (median)"
        )
    
    # Additional statistics
    st.markdown("#### Distribution Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Minimum Bonus", f"€{edited_df['Bonus (€)'].min():,.0f}")
    
    with col2:
        st.metric("Maximum Bonus", f"€{edited_df['Bonus (€)'].max():,.0f}")
    
    with col3:
        st.metric("Median Bonus", f"€{edited_df['Bonus (€)'].median():,.0f}")
    
    with col4:
        std_bonus = edited_df['Bonus (€)'].std()
        st.metric("Standard Deviation", f"€{std_bonus:,.0f}")
    
    # Budget validation
    if total_allocated > BUDGET:
        st.error(f"⚠️ **Warning:** You have allocated €{total_allocated:,.0f}, which exceeds the budget of €{BUDGET:,} by €{remaining_budget:,.0f}!")
    elif total_allocated < BUDGET:
        st.warning(f"ℹ️ **Note:** You have €{remaining_budget:,.0f} remaining from your budget. Total allocated: €{total_allocated:,.0f}")
    else:
        st.success(f"✅ **Perfect!** You have allocated exactly €{BUDGET:,}!")
    
    # Top recipients
    if num_managers_with_bonus > 0:
        st.markdown("#### Top 10 Bonus Recipients")
        top_recipients = edited_df.nlargest(10, 'Bonus (€)')[['Fund', 'Manager', 'Bonus (€)']].copy()
        top_recipients['Bonus (€)'] = top_recipients['Bonus (€)'].apply(lambda x: f"€{x:,.0f}")
        top_recipients['Percentage of Total'] = edited_df.nlargest(10, 'Bonus (€)')['Bonus (€)'].apply(
            lambda x: f"{(x/total_allocated*100):.1f}%" if total_allocated > 0 else "0%"
        )
        st.dataframe(top_recipients, use_container_width=True, hide_index=True)
    
    # Visualization
    if num_managers_with_bonus > 0:
        st.markdown("#### Bonus Distribution Chart")
        chart_data = edited_df[edited_df['Bonus (€)'] > 0].sort_values('Bonus (€)', ascending=False)
        if len(chart_data) > 0:
            st.bar_chart(chart_data.set_index('Fund')['Bonus (€)'])
    
    # Reset button
    st.markdown("---")
    if st.button("🔄 Reset All Allocations", type="secondary"):
        st.session_state["bonus_allocations"] = pd.DataFrame([
            {
                'Fund': row['Fund'],
                'Manager': row.get('Manager', 'N/A'),
                'Bonus (€)': 0.0
            }
            for idx, row in funds_list.iterrows()
        ])
        st.rerun()
        
else:
    st.warning("Please load the funds data first by visiting the Dashboard page.")
