import os
import sys
import math
import json
import pandas as pd
import numpy as np

# Reconfigure stdout to handle special characters on Windows CLI
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def load_data(file_path):
    """Loads and cleans the historical trade database."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Historical data file not found at: {file_path}")
    
    df = pd.read_excel(file_path)
    # Sort by timestamp to ensure chronological order
    df = df.sort_values('timestamp').reset_index(drop=True)
    return df

def precalculate_rolling_params(df, window_size=100):
    """Pre-calculates rolling window boundaries and Kelly parameters once to avoid redundant loops."""
    kelly_history = []
    win_rate_history = []
    avg_win_history = []
    avg_loss_history = []
    r_ratio_history = []
    window_boundaries = []
    
    for i in range(len(df)):
        if i >= window_size:
            window = df.iloc[i - window_size : i]
            
            wins = window[window['pnl_lot'] > 0]['pnl_lot']
            losses = window[window['pnl_lot'] < 0]['pnl_lot']
            
            w_rate = len(wins) / window_size
            avg_win = wins.mean() if len(wins) > 0 else 0.0
            avg_loss = abs(losses.mean()) if len(losses) > 0 else 0.0
            
            if avg_loss > 0:
                r_ratio = avg_win / avg_loss
                kelly = w_rate - ((1.0 - w_rate) / r_ratio)
            else:
                kelly = w_rate if avg_win > 0 else 0.0
                r_ratio = 0.0
                
            kelly = max(0.0, kelly)
            
            # Save boundaries
            start_num = i - window_size + 1
            start_time = df.loc[i - window_size, 'timestamp']
            end_num = i
            end_time = df.loc[i - 1, 'timestamp']
            
            win_rate_history.append(w_rate)
            avg_win_history.append(avg_win)
            avg_loss_history.append(avg_loss)
            r_ratio_history.append(r_ratio)
            kelly_history.append(kelly)
            window_boundaries.append({
                'start_num': start_num,
                'start_time': str(start_time),
                'end_num': end_num,
                'end_time': str(end_time)
            })
        else:
            win_rate_history.append(0.0)
            avg_win_history.append(0.0)
            avg_loss_history.append(0.0)
            r_ratio_history.append(0.0)
            kelly_history.append(0.0)
            window_boundaries.append(None)
            
    return {
        'kelly': kelly_history,
        'win_rate': win_rate_history,
        'avg_win': avg_win_history,
        'avg_loss': avg_loss_history,
        'r_ratio': r_ratio_history,
        'boundaries': window_boundaries
    }

def run_backtest_strategy(df, strategy_name, initial_capital, window_size, margin_model, fixed_margin_val, rolling_params, original_lots_source=1, lot_size=65, max_lots_limit=10, force_min_1_lot=False, sizing_method='risk'):
    """Runs the backtest for a specific strategy using pre-calculated rolling parameters."""
    capital = initial_capital
    cap_history = [capital]
    lots_history = []
    
    trades_executed = 0
    trades_skipped = 0
    total_utilization = 0.0
    
    # Resolve Original Strategy Lots array
    original_lots = []
    if isinstance(original_lots_source, str) and original_lots_source in df.columns:
        original_lots = df[original_lots_source].fillna(1).astype(int).tolist()
    else:
        try:
            val = int(original_lots_source)
        except (ValueError, TypeError):
            val = 1
        original_lots = [val] * len(df)
        
    # Sizing starts at trade 101 (index 100)
    for i in range(len(df)):
        entry_price = float(df.loc[i, 'entry_price'])
        pnl_lot = float(df.loc[i, 'pnl_lot'])
        
        kelly = rolling_params['kelly'][i]
        
        # Determine RequiredMarginPerLot for this trade
        if margin_model == 'premium':
            required_margin = entry_price * lot_size
        else:
            required_margin = fixed_margin_val
            
        # Before Trade 101, we don't trade in our simulation
        if i < window_size:
            lots = 0
            lots_history.append(lots)
            cap_history.append(capital)
            continue
            
        # Sizing calculations based on strategy
        if strategy_name == 'original':
            lots = original_lots[i]
            if lots == 0:
                trades_skipped += 1
                
        elif strategy_name in ['kelly_full', 'kelly_1_2', 'kelly_1_4', 'kelly_1_8', 'kelly_1_4_min_1']:
            if strategy_name == 'kelly_full':
                fraction = 1.0
            elif strategy_name == 'kelly_1_2':
                fraction = 0.5
            elif strategy_name == 'kelly_1_4':
                fraction = 0.25
            elif strategy_name == 'kelly_1_8':
                fraction = 0.125
            elif strategy_name == 'kelly_1_4_min_1':
                fraction = 0.25
                
            allocation = min(kelly * fraction, 0.10) # cap allocation at 10%
            
            if sizing_method == 'risk':
                sl_price = float(df.loc[i, 'sl_price'])
                risk_per_option = abs(entry_price - sl_price)
                risk_per_lot = risk_per_option * lot_size
                risk_amount = capital * allocation
                lots = math.floor(risk_amount / risk_per_lot) if risk_per_lot > 0 else 0
            else:
                position_amount = capital * allocation
                lots = math.floor(position_amount / required_margin)
            
            # Apply maximum lots control
            lots = min(lots, max_lots_limit)
            
            # Apply Force Min 1 Lot if active
            is_force_min = force_min_1_lot or (strategy_name == 'kelly_1_4_min_1')
            if is_force_min and kelly > 0 and lots == 0 and capital >= required_margin:
                lots = 1
                
            if kelly > 0 and lots == 0:
                trades_skipped += 1
                
        elif strategy_name == 'fixed_1':
            lots = 1 if capital >= required_margin else 0
            lots = min(lots, max_lots_limit)
            if lots == 0 and capital < required_margin:
                trades_skipped += 1
                
        elif strategy_name == 'fixed_2':
            lots = 2 if capital >= (2 * required_margin) else (1 if capital >= required_margin else 0)
            lots = min(lots, max_lots_limit)
            if lots < 2:
                trades_skipped += 1
                
        else:
            lots = 0
            
        # Affordability check (capital constraint)
        max_lots_affordable = math.floor(capital / required_margin)
        if lots > max_lots_affordable:
            lots = max_lots_affordable
            
        # Execution
        trade_pnl = pnl_lot * lots
        capital += trade_pnl
        
        if lots > 0:
            trades_executed += 1
            
        utilization = (lots * required_margin) / (capital - trade_pnl) * 100.0 if (capital - trade_pnl) > 0 else 0.0
        total_utilization += utilization
        
        lots_history.append(lots)
        cap_history.append(capital)
        
    return {
        'capital_history': cap_history,
        'lots_history': lots_history,
        'trades_executed': trades_executed,
        'trades_skipped': trades_skipped,
        'total_utilization': total_utilization
    }

def calculate_metrics(df, results, initial_capital, start_idx=100):
    """Calculates all performance metrics for a strategy over the trading period."""
    cap_hist = results['capital_history']
    lots_hist = results['lots_history']
    
    # Trading starts from start_idx to the end
    traded_caps = cap_hist[start_idx:]
    final_cap = traded_caps[-1]
    total_profit = final_cap - initial_capital
    
    # CAGR
    start_date = df.loc[start_idx, 'timestamp']
    end_date = df.iloc[-1]['timestamp']
    days = (end_date - start_date).days
    years = days / 365.0
    cagr = (final_cap / initial_capital) ** (1.0 / years) - 1.0 if years > 0 and final_cap > 0 else 0.0
    
    # Drawdown
    traded_caps_arr = np.array(traded_caps)
    peaks = np.maximum.accumulate(traded_caps_arr)
    drawdowns = (peaks - traded_caps_arr) / peaks * 100.0
    max_dd = np.max(drawdowns) if len(drawdowns) > 0 else 0.0
    
    max_dd_curr = np.max(peaks - traded_caps_arr) if len(traded_caps_arr) > 0 else 0.0
    recovery_factor = total_profit / max_dd_curr if max_dd_curr > 0 else total_profit
    
    # Win Rate, PF, Expectancy
    strategy_pnls = []
    for i in range(start_idx, len(df)):
        lots = lots_hist[i]
        pnl_lot = df.loc[i, 'pnl_lot']
        strategy_pnls.append(pnl_lot * lots)
        
    strategy_pnls = np.array(strategy_pnls)
    executed_pnls = strategy_pnls[strategy_pnls != 0]
    
    if len(executed_pnls) > 0:
        wins = executed_pnls[executed_pnls > 0]
        losses = executed_pnls[executed_pnls < 0]
        win_rate = len(wins) / len(executed_pnls)
        
        sum_wins = np.sum(wins)
        sum_losses = abs(np.sum(losses))
        profit_factor = sum_wins / sum_losses if sum_losses > 0 else (sum_wins if sum_wins > 0 else 0.0)
        
        avg_win = np.mean(wins) if len(wins) > 0 else 0.0
        avg_loss = abs(np.mean(losses)) if len(losses) > 0 else 0.0
        expectancy = (win_rate * avg_win) - ((1.0 - win_rate) * avg_loss)
        
        avg_lot_size = np.mean([l for l in lots_hist[start_idx:] if l > 0])
    else:
        win_rate = 0.0
        profit_factor = 0.0
        expectancy = 0.0
        avg_lot_size = 0.0
        
    num_trades_in_period = len(df) - start_idx
    avg_utilization = results['total_utilization'] / num_trades_in_period if num_trades_in_period > 0 else 0.0
    
    return {
        'total_profit': total_profit,
        'final_capital': final_cap,
        'cagr': cagr * 100.0,
        'max_dd': max_dd,
        'win_rate': win_rate * 100.0,
        'profit_factor': profit_factor,
        'expectancy': expectancy,
        'recovery_factor': recovery_factor,
        'trades_executed': results['trades_executed'],
        'trades_skipped': results['trades_skipped'],
        'avg_lot_size': avg_lot_size,
        'capital_utilization': avg_utilization
    }

def export_detailed_ledger(df, strategy_name, initial_capital, window_size, margin_model, fixed_margin_val, rolling_params, lot_size=65, max_lots_limit=10, force_min_1_lot=False, sizing_method='risk', output_path=""):
    """Runs a simulation and exports the detailed ledger to Excel with specific columns."""
    capital = initial_capital
    rows = []
    
    # Resolve allocation fraction
    if strategy_name == 'kelly_full':
        fraction = 1.0
    elif strategy_name == 'kelly_1_4':
        fraction = 0.25
    else:
        fraction = 1.0
        
    for i in range(len(df)):
        timestamp = df.loc[i, 'timestamp']
        option_type = df.loc[i, 'option_type']
        entry_price = float(df.loc[i, 'entry_price'])
        sl_price = float(df.loc[i, 'sl_price'])
        exit_price = float(df.loc[i, 'exit_price'])
        pnl_lot = float(df.loc[i, 'pnl_lot'])
        kelly = rolling_params['kelly'][i]
        
        # Determine RequiredMarginPerLot for this trade
        required_margin = (entry_price * lot_size) if margin_model == 'premium' else fixed_margin_val
        
        # Sizing calculations
        allocation = min(kelly * fraction, 0.10)
        risk_amount = capital * allocation
        risk_per_option = abs(entry_price - sl_price)
        risk_per_lot = risk_per_option * lot_size
        
        # Before Trade 101, we don't trade in our simulation
        if i < window_size:
            lots = 0
        else:
            if sizing_method == 'risk':
                lots = math.floor(risk_amount / risk_per_lot) if risk_per_lot > 0 else 0
            else:
                position_amount = capital * allocation
                lots = math.floor(position_amount / required_margin)
                
            lots = min(lots, max_lots_limit)
            
            if force_min_1_lot and kelly > 0 and lots == 0 and capital >= required_margin:
                lots = 1
                
            max_lots_affordable = math.floor(capital / required_margin)
            if lots > max_lots_affordable:
                lots = max_lots_affordable
            
        trade_pnl = pnl_lot * lots
        cap_before = capital
        capital += trade_pnl
        cap_after = capital
        running_equity = capital
        
        utilization = (lots * required_margin) / cap_before * 100.0 if cap_before > 0 else 0.0
        
        # Only trades starting from Trade 101 are included in the output ledger
        if i >= window_size:
            rows.append({
                'Trade Number': i + 1,
                'Date': str(timestamp).split(' ')[0],
                'CE/PE': option_type,
                'Entry Price': entry_price,
                'Stop Loss': sl_price,
                'Exit Price': exit_price,
                'Kelly %': kelly * 100.0,
                'Kelly Allocation %': allocation * 100.0,
                'Risk Amount': risk_amount,
                'Risk Per Option': risk_per_option,
                'Risk Per Lot': risk_per_lot,
                'Lots Purchased': lots,
                'Trade PnL': trade_pnl,
                'Capital Before': cap_before,
                'Capital After': cap_after,
                'Running Equity': running_equity,
                'Capital Utilization %': utilization
            })
        
    out_df = pd.DataFrame(rows)
    out_df.to_excel(output_path, index=False)
    print(f"Exported detailed trade ledger for {strategy_name} to {output_path}")

def main():
    print("==========================================================")
    print("   WALK-FORWARD KELLY POSITION SIZING BACKTESTER v2.0")
    print("==========================================================")
    
    input_file = r"C:\Users\Preneel\Desktop\pos_try\new_tsl_5_2022-23(1).xlsx"
    if not os.path.exists(input_file):
        print(f"Error: Could not find trade history file at: {input_file}")
        return
        
    # Load data
    try:
        df = load_data(input_file)
        print(f"Loaded {len(df)} trades successfully.")
    except Exception as e:
        print(f"Error reading trade log: {e}")
        return

    # Simulation Config
    initial_capital = 100000.0
    window_size = 100
    margin_models = ['premium', 'fixed']
    fixed_margin_val = 10000.0
    
    # Pre-calculate rolling Kelly params once
    print("Calculating rolling window parameters...")
    rolling_params = precalculate_rolling_params(df, window_size)
    print("Rolling parameters pre-calculated successfully.")
    
    # Auto-detect Original Lots source
    original_lots_source = 1
    for col in ['actual_lots', 'lots', 'simulated_lots']:
        if col in df.columns:
            original_lots_source = col
            print(f"Auto-detected '{col}' as the Original Strategy lot source.")
            break
    if original_lots_source == 1:
        print("No lot size column found. Original Strategy will fall back to Fixed 1 Lot (default).")

    all_results = {}
    
    for mm in margin_models:
        print(f"\nRunning simulation for Margin Model: {mm.upper()}...")
        mm_results = {}
        strategies = ['original', 'kelly_full', 'kelly_1_2', 'kelly_1_4', 'kelly_1_8', 'kelly_1_4_min_1', 'fixed_1', 'fixed_2']
        
        for strat in strategies:
            res = run_backtest_strategy(df, strat, initial_capital, window_size, mm, fixed_margin_val, rolling_params, original_lots_source=original_lots_source, sizing_method='risk')
            metrics = calculate_metrics(df, res, initial_capital, window_size)
            
            mm_results[strat] = {
                'metrics': metrics,
                'capital_history': res['capital_history'],
                'lots_history': res['lots_history'],
                'total_utilization': res['total_utilization'],
                'trades_executed': res['trades_executed'],
                'trades_skipped': res['trades_skipped']
            }
            
        # Calculate comparative metrics vs Original Strategy
        orig_profit = mm_results['original']['metrics']['total_profit']
        orig_dd = mm_results['original']['metrics']['max_dd']
        
        for strat in strategies:
            m = mm_results[strat]['metrics']
            
            # Profit Improvement vs Original
            if orig_profit != 0:
                m['profit_improvement'] = (m['total_profit'] - orig_profit) / abs(orig_profit) * 100.0
            else:
                m['profit_improvement'] = 0.0
                
            # Drawdown Improvement (Relative Reduction)
            if orig_dd > 0:
                m['dd_improvement'] = (orig_dd - m['max_dd']) / orig_dd * 100.0
            else:
                m['dd_improvement'] = 0.0
                
        all_results[mm] = mm_results
        
        # Print CLI table
        print(f"\n--- PERFORMANCE COMPARISON ({mm.upper()} MARGIN) ---")
        headers = ["Strategy", "Profit (INR)", "CAGR (%)", "Max DD (%)", "PF", "Win Rate (%)", "Expectancy", "Rec. Factor", "Avg Lot", "Prof. Imp.", "DD Imp."]
        print(f"{headers[0]:<23} | {headers[1]:<12} | {headers[2]:<8} | {headers[3]:<10} | {headers[4]:<6} | {headers[5]:<12} | {headers[6]:<10} | {headers[7]:<11} | {headers[8]:<7} | {headers[9]:<10} | {headers[10]:<10}")
        print("-" * 140)
        
        strat_display_names = {
            'original': "Original Strategy",
            'kelly_full': "Kelly (Full Kelly)",
            'kelly_1_2': "Kelly (Half Kelly)",
            'kelly_1_4': "Kelly (1/4 Kelly)",
            'kelly_1_8': "Kelly (1/8 Kelly)",
            'kelly_1_4_min_1': "Kelly (1/4 + Min 1Lot)",
            'fixed_1': "Fixed 1 Lot",
            'fixed_2': "Fixed 2 Lots"
        }
        
        for strat in strategies:
            m = mm_results[strat]['metrics']
            name = strat_display_names[strat]
            print(f"{name:<23} | {m['total_profit']:12,.2f} | {m['cagr']:8.2f}% | {m['max_dd']:10.2f}% | {m['profit_factor']:6.2f} | {m['win_rate']:12.2f}% | {m['expectancy']:10.2f} | {m['recovery_factor']:11.2f} | {m['avg_lot_size']:7.2f} | {m['profit_improvement']:+.2f}% | {m['dd_improvement']:+.2f}%")

    # Save to Excel (detailed logs for primary premium model)
    output_excel = r"c:\Users\Preneel\Desktop\KELLY_POSITION SIZING\kelly_backtest_results.xlsx"
    print(f"\nSaving detailed trade-by-trade Excel sheet to: {output_excel}...")
    
    out_df = df.copy()
    premium_data = all_results['premium']
    
    # Save ledger parameters
    out_df['rolling_kelly'] = rolling_params['kelly']
    out_df['rolling_win_rate'] = rolling_params['win_rate']
    out_df['rolling_avg_win'] = rolling_params['avg_win']
    out_df['rolling_avg_loss'] = rolling_params['avg_loss']
    out_df['rolling_r_ratio'] = rolling_params['r_ratio']
    
    # Save window boundary text representation
    wb_starts = []
    wb_ends = []
    for wb in rolling_params['boundaries']:
        if wb:
            wb_starts.append(f"Trade #{wb['start_num']} ({wb['start_time'][:16]})")
            wb_ends.append(f"Trade #{wb['end_num']} ({wb['end_time'][:16]})")
        else:
            wb_starts.append("-")
            wb_ends.append("-")
    out_df['kelly_window_start'] = wb_starts
    out_df['kelly_window_end'] = wb_ends
    
    # Save strategy lot sizes and capital curves
    for strat in ['original', 'kelly_full', 'kelly_1_2', 'kelly_1_4', 'kelly_1_8', 'kelly_1_4_min_1', 'fixed_1', 'fixed_2']:
        out_df[f'{strat}_lots'] = premium_data[strat]['lots_history']
        out_df[f'{strat}_capital'] = premium_data[strat]['capital_history'][1:]
        
    try:
        out_df.to_excel(output_excel, index=False)
        print("Excel sheet saved successfully.")
    except Exception as e:
        print(f"Error saving Excel sheet: {e}")

    # Save simulation JSON for Dashboard
    output_json = r"c:\Users\Preneel\Desktop\KELLY_POSITION SIZING\kelly_backtest_results.json"
    print(f"Saving JSON simulation data to: {output_json}...")
    
    json_data = {
        'trades': [],
        'available_lot_columns': [col for col in df.columns if ('lots' in col.lower() or 'lot_size' in col.lower()) and 'pnl' not in col.lower()]
    }
    
    # Include all trades with rolling calculation elements
    for idx, row in df.iterrows():
        wb = rolling_params['boundaries'][idx]
        
        # Compute holding minutes
        entry_time = row.get('entry_signal_time', row['timestamp'])
        exit_time = row.get('exit_signal_time', row['timestamp'])
        try:
            holding_mins = (pd.to_datetime(exit_time) - pd.to_datetime(entry_time)).total_seconds() / 60.0
            if pd.isna(holding_mins):
                holding_mins = 0.0
        except Exception:
            holding_mins = 0.0
        json_data['trades'].append({
            'timestamp': str(row['timestamp']),
            'entry_price': float(row['entry_price']),
            'sl_price': float(row['sl_price']),
            'exit_price': float(row['exit_price']),
            'pnl_lot': float(row['pnl_lot']),
            'pnl_pct': float(row['pnl_pct']),
            'entry_signal': str(row['entry_signal']),
            'option_type': str(row['option_type']),
            'strike_price': int(row['strike_price']),
            'exit_reason': str(row['exit_reason']),
            'holding_mins': float(holding_mins),
            
            # Diagnostics details
            'win_rate': float(rolling_params['win_rate'][idx]),
            'avg_win': float(rolling_params['avg_win'][idx]),
            'avg_loss': float(rolling_params['avg_loss'][idx]),
            'r_ratio': float(rolling_params['r_ratio'][idx]),
            'kelly': float(rolling_params['kelly'][idx]),
            'window_start': f"Trade #{wb['start_num']} ({wb['start_time'][:16]})" if wb else "-",
            'window_end': f"Trade #{wb['end_num']} ({wb['end_time'][:16]})" if wb else "-"
        })
        
    # Embed full simulations
    json_data['simulations'] = {}
    for mm in margin_models:
        mm_data = {}
        for strat in all_results[mm]:
            mm_data[strat] = {
                'metrics': all_results[mm][strat]['metrics'],
                'capital_history': all_results[mm][strat]['capital_history'],
                'lots_history': all_results[mm][strat]['lots_history'],
                'kelly_history': rolling_params['kelly']
            }
        json_data['simulations'][mm] = mm_data
        
    try:
        with open(output_json, 'w') as f:
            json.dump(json_data, f, indent=2)
        print("JSON data saved successfully.")
    except Exception as e:
        print(f"Error saving JSON data: {e}")
        
    # Export the two detailed ledger Excel files for Risk-based method (premium model as default)
    try:
        export_detailed_ledger(
            df=df,
            strategy_name='kelly_full',
            initial_capital=initial_capital,
            window_size=window_size,
            margin_model='premium',
            fixed_margin_val=fixed_margin_val,
            rolling_params=rolling_params,
            lot_size=65,
            max_lots_limit=10,
            force_min_1_lot=True,
            output_path=r"c:\Users\Preneel\Desktop\KELLY_POSITION SIZING\kelly_full_trade_ledger.xlsx"
        )
        export_detailed_ledger(
            df=df,
            strategy_name='kelly_1_4',
            initial_capital=initial_capital,
            window_size=window_size,
            margin_model='premium',
            fixed_margin_val=fixed_margin_val,
            rolling_params=rolling_params,
            lot_size=65,
            max_lots_limit=10,
            force_min_1_lot=True,
            output_path=r"c:\Users\Preneel\Desktop\KELLY_POSITION SIZING\kelly_quarter_trade_ledger.xlsx"
        )
    except Exception as e:
        print(f"Error exporting detailed ledgers: {e}")
        
    try:
        print("Generating HTML dashboard...")
        import generate_dashboard
        generate_dashboard.main()
        
        import webbrowser
        dashboard_path = os.path.abspath("dashboard.html")
        print(f"Opening dashboard in web browser: {dashboard_path}")
        webbrowser.open(f"file:///{dashboard_path}")
    except Exception as e:
        print(f"Error launching dashboard: {e}")
        
    print("\nProcessing complete!")

if __name__ == '__main__':
    main()
