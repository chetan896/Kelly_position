# User Manual & Operating Guide: Kelly Position Sizing Backtester

Welcome to the **Walk-Forward Kelly Criterion Position Sizing Backtesting Framework**. This framework is designed to help you backtest options and futures strategies, apply rolling walk-forward Kelly optimization, compare performance against fixed-lot and original trading baselines, and verify calculations trade-by-trade in an interactive dashboard.

All files are located in your workspace directory:
`C:\Users\Preneel\Desktop\KELLY_POSITION SIZING\`

---

## 1. Quick Start Guide

### Step 1: Run the Backtest in Python
To execute the walk-forward simulation engine, calculate rolling window parameters, and compile the dashboard, open your terminal/PowerShell and run:
```powershell
python kelly_backtest.py
```
This script will:
1. Load your historical trade database from `..\pos_try\new_tsl_5_2022-23(1).xlsx`.
2. Compute the rolling walk-forward win rate, win/loss ratio, and Kelly values.
3. Simulate all 8 position sizing strategies under both Premium-Based and Fixed Margin models.
4. Export the detailed spreadsheet to `kelly_backtest_results.xlsx`.
5. Compile the self-contained JSON and generate `dashboard.html`.
6. Automatically open the interactive dashboard in your default web browser.

### Step 2: Open the Dashboard Manually
If the dashboard does not open automatically, simply go to your workspace directory and double-click the **`dashboard.html`** file. It is fully self-contained and works offline in any browser (Chrome, Edge, Safari, Firefox) without any security or CORS issues.

---

## 2. Dashboard Interface & Features

The interactive dashboard is split into three main sections: the **Control Sidebar**, the **Upper Analytics panels**, and the **Content Tabs**.

### A. The Control Sidebar (Real-time Recalibration)
Any adjustments made here will instantly re-run the quantitative backtester engine in JavaScript and redraw all charts, tables, and KPIs:
- **Starting Capital (₹)**: Set your starting account capital (default: `₹100,000`). Change this to `₹1,000,000` to see how Kelly scales up lots as account size increases.
- **Kelly Rolling Window**: Adjust the number of historical completed trades used to estimate the edge (default: `100` trades).
- **Position Sizing Method**: 
  - **Margin-Based**: Sizing based on required margin (premium or fixed).
  - **Risk-Based**: Sizing based on stop loss distance: RiskAmount = Capital × KellyAllocation, RiskPerOption = |Entry - StopLoss|, RiskPerLot = RiskPerOption × LotSize, Lots = RiskAmount / RiskPerLot.
- **Original Lots Source**: 
  - Select a column name from your Excel file (e.g. `simulated_lots`) to load actual traded lots.
  - Choose **"Fixed Lot Value (Manual)"** to manually map a fixed lot size (e.g., `1` or `2` lots).
- **Margin Model**: 
  - **Premium-Based**: Computes margin required per lot dynamically as `entry_price × Lot Size` (represents option buying).
  - **Fixed Margin**: Uses a constant margin value per lot (represents option selling/writing or futures).
- **Margin Per Lot (₹)**: The margin requirement per contract when Fixed Margin is selected (default: `₹10,000`).
- **Maximum Lots Cap**: Restricts the maximum trade size to prevent excessive exposure (default: `10` lots).
- **Force Minimum 1 Lot**: 
  - **ON (Checked)**: If a positive edge exists ($Kelly > 0$) but the allocated capital is less than the required margin, it executes exactly `1` lot (provided capital is available).
  - **OFF (Unchecked)**: Pure fractional Kelly sizing (executes `0` lots if the allocated capital is less than the margin).
- **Apply flat ₹40 fee / trade**: Applies flat exchange and transaction costs to show net post-tax performance.

---

## 3. Interpreting the Content Tabs

### Tab 1: Performance Overview
This is your main dashboard workspace:
1. **Position Sizing Impact Section**: Displays the exact profit increase (in ₹ and %) and drawdown reduction achieved by your active Kelly strategy compared to your Original Strategy.
2. **Kelly Diagnostics Panel**: Displays critical trading characteristics for the active Kelly sizing model, including average rolling Kelly %, average and maximum lots traded, executed/skipped trade counts, and average capital utilization.
3. **Comparison Table**: Compares all 12 key metrics side-by-side for all 8 strategies, including Profit Factor, Expectancy, CAGR, and Recovery Factor.
4. **Equity & Drawdown Charts**: Renders interactive lines representing capital growth and drawdown depth for all 8 strategies. Hover over any point to see trade-by-trade values.

### Tab 2: Position Sizing Performance Analysis
This tab provides high-fidelity performance metrics comparing the portfolio with vs. without sizing:
- Portfolio statistics side-by-side (Fixed 1 Lot vs. Active Kelly sizing).
- Relative Sizing Improvement Metrics.
- Dynamic Verdict Card evaluation.
- Best/Worst trade comparison records.
- Capital Utilization and CE/PE Option splits.
- 7 visual charts displaying growth curves, drawdown profiles, position sizing amount, capital utilization %, rolling edge, and histograms.

### Tab 3: Detailed Trade Ledger
The ultimate verification spreadsheet showing **23 diagnostic columns** starting from Trade 101:
- **Trade Number & Timestamp**
- **Signal**: BUY or SELL.
- **CE / PE**: Option contract type.
- **Entry Price / Exit Price / PnL Per Lot**
- **Win Rate (W), Avg Win, Avg Loss, W/L Ratio (R)**: The raw mathematical inputs.
- **Kelly % & Kelly Allocation %**: The resulting Kelly fractions.
- **Position Amount**: The target capital allocation (`Capital × KellyAllocation`).
- **Margin per Lot**: The margin cost for one contract.
- **Lots Purchased**: Mapped Original Lots vs. simulated Kelly Lots.
- **Trade Profit / Capital Before / Capital After / Running Equity**: Compounding capital details.
- **Capital Utilization %**: Percentage of margin used to capital.
- **Kelly Window Boundaries**: Shows the exact starting trade (e.g., Trade #1) and ending trade (e.g., Trade #100) of the rolling window used to size that specific trade.
- **Exit Reason**: How the trade was exited.

Use the search bar at the top to filter by Signal, Window Start, Window End, or exit reasons (e.g. type `SL` to see stopped-out trades).

---

## 4. Key Quantitative Concepts

### Why does Pure Kelly execute 0 trades on small accounts?
In standard retail trading with a capital of ₹100,000, pure Kelly allocations are often smaller than the required margin per lot (e.g. allocating ₹3,750 when a lot requires ₹10,000). The fraction rounds down to **0 lots**, sizing you out of the market. Enabling **"Force Minimum 1 Lot"** resolves this, executing 1 lot when an edge is present.

### How does Kelly improve capital efficiency?
By recalculating the win rate and payoff ratio over the previous 100 trades, Kelly identifies periods where the strategy has no statistical edge ($Kelly = 0$). In the historical Nifty options database, Kelly successfully skipped **310 flat trades** that generated virtually zero aggregate profit, saving you ₹12,400 in transaction costs and reducing your active market risk.
