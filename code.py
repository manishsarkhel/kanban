import streamlit as st
import pandas as pd
import random

# Page Configuration
st.set_page_config(page_title="Lean Kanban Simulator", layout="wide")

st.title("Lean Factory & Kanban Simulator")
st.markdown("""
**Objective:** Optimize your Work-In-Process (WIP) Kanban limits to maximize profit. 
* **Revenue:** \$100 per unit sold.
* **Holding Cost (Muda):** \$5 per unit in inventory per day.
* **Stockout Penalty:** \$50 for every unit of unfulfilled customer demand.
""")

# Initialize Session State
if 'day' not in st.session_state:
    st.session_state.day = 0
    st.session_state.wip_assembly = 0
    st.session_state.wip_testing = 0
    st.session_state.warehouse = 0
    st.session_state.profit = 0
    st.session_state.history = []

def reset_sim():
    st.session_state.day = 0
    st.session_state.wip_assembly = 0
    st.session_state.wip_testing = 0
    st.session_state.warehouse = 0
    st.session_state.profit = 0
    st.session_state.history = []

# Sidebar Controls: Kanban Limits
st.sidebar.header("Set Kanban Limits (WIP)")
st.sidebar.markdown("Determine the maximum allowable inventory at each stage.")
kanban_assembly = st.sidebar.slider("Assembly Limit", 1, 20, 5)
kanban_testing = st.sidebar.slider("Testing Limit", 1, 20, 5)
kanban_warehouse = st.sidebar.slider("Warehouse Limit", 1, 20, 5)

st.sidebar.header("Market Settings")
max_demand = st.sidebar.slider("Max Daily Demand", 1, 15, 8)

if st.sidebar.button("Reset Simulation", use_container_width=True):
    reset_sim()

# Game Logic: Advance One Day
if st.button("Simulate Next Day", type="primary", use_container_width=True):
    st.session_state.day += 1
    
    # 1. Generate Random Market Demand
    demand = random.randint(1, max_demand)
    
    # 2. Fulfill Demand (Pull from Warehouse)
    sold = min(demand, st.session_state.warehouse)
    missed_demand = demand - sold
    st.session_state.warehouse -= sold
    
    # 3. Kanban Pull System (Information flows upstream, materials flow downstream)
    
    # Warehouse pulls from Testing to replenish what was sold
    space_in_warehouse = kanban_warehouse - st.session_state.warehouse
    pulled_to_warehouse = min(space_in_warehouse, st.session_state.wip_testing)
    st.session_state.warehouse += pulled_to_warehouse
    st.session_state.wip_testing -= pulled_to_warehouse
    
    # Testing pulls from Assembly
    space_in_testing = kanban_testing - st.session_state.wip_testing
    pulled_to_testing = min(space_in_testing, st.session_state.wip_assembly)
    st.session_state.wip_testing += pulled_to_testing
    st.session_state.wip_assembly -= pulled_to_testing
    
    # Assembly pulls from Raw Materials (Assuming infinite raw materials for this simulation)
    space_in_assembly = kanban_assembly - st.session_state.wip_assembly
    pulled_to_assembly = space_in_assembly 
    st.session_state.wip_assembly += pulled_to_assembly
    
    # 4. Calculate Financials
    revenue = sold * 100
    holding_cost = (st.session_state.wip_assembly + st.session_state.wip_testing + st.session_state.warehouse) * 5
    penalty = missed_demand * 50
    daily_profit = revenue - holding_cost - penalty
    st.session_state.profit += daily_profit
    
    # 5. Record Data
    st.session_state.history.append({
        "Day": st.session_state.day,
        "Demand": demand,
        "Sold": sold,
        "Missed": missed_demand,
        "Assembly Stock": st.session_state.wip_assembly,
        "Testing Stock": st.session_state.wip_testing,
        "Warehouse Stock": st.session_state.warehouse,
        "Daily Profit": daily_profit,
        "Cumulative Profit": st.session_state.profit
    })

# Dashboard Display
col1, col2, col3, col4 = st.columns(4)
col1.metric("Current Day", st.session_state.day)
col2.metric("Cumulative Profit ($)", st.session_state.profit)

if len(st.session_state.history) > 0:
    last_turn = st.session_state.history[-1]
    col3.metric("Last Day's Demand", last_turn["Demand"])
    col4.metric("Missed Sales (Stockout)", last_turn["Missed"], delta_color="inverse")

st.markdown("---")
st.subheader("Factory Floor Status (Current Inventory)")

# Visualizing the flow and Kanban constraints
f_col1, f_col2, f_col3 = st.columns(3)
f_col1.metric(f"Assembly WIP (Max: {kanban_assembly})", st.session_state.wip_assembly)
f_col2.metric(f"Testing WIP (Max: {kanban_testing})", st.session_state.wip_testing)
f_col3.metric(f"Warehouse Stock (Max: {kanban_warehouse})", st.session_state.warehouse)

# Analytics and Charts
if st.session_state.history:
    st.markdown("---")
    st.subheader("Simulation Analytics")
    df = pd.DataFrame(st.session_state.history)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Inventory Levels Over Time (Identifying Bottlenecks)**")
        st.line_chart(df.set_index("Day")[["Assembly Stock", "Testing Stock", "Warehouse Stock"]])
    with c2:
        st.markdown("**Financial Performance**")
        st.line_chart(df.set_index("Day")[["Cumulative Profit"]])
        
    st.markdown("**Detailed Ledger**")
    st.dataframe(
        df.style.highlight_min(subset=['Daily Profit'], color='#ffcccc')
                .highlight_max(subset=['Daily Profit'], color='#ccffcc'), 
        use_container_width=True
    )
