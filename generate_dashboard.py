import json
import os
import sys

def main():
    json_path = r"c:\Users\Preneel\Desktop\KELLY_POSITION SIZING\kelly_backtest_results.json"
    html_path = r"c:\Users\Preneel\Desktop\KELLY_POSITION SIZING\dashboard.html"
    
    if not os.path.exists(json_path):
        print(f"Error: JSON file not found at {json_path}")
        return
        
    print(f"Loading JSON data from {json_path}...")
    with open(json_path, 'r') as f:
        data = json.load(f)
        
    trades_json_str = json.dumps(data['trades'])
    
    # We will pass the available columns to populate the Lot Source dropdown dynamically
    columns_list = data.get('available_lot_columns', [])
    columns_json_str = json.dumps(columns_list)
    
    print("Writing HTML dashboard...")
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kelly Position Sizing Dashboard v2.0</title>
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Chart.js CDN -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <style>
        :root {{
            --bg-primary: #080c18;
            --bg-secondary: #0f152b;
            --bg-tertiary: #16203f;
            --accent-primary: #6366f1;
            --accent-secondary: #8b5cf6;
            --accent-glow: rgba(99, 102, 241, 0.15);
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --success: #10b981;
            --success-glow: rgba(16, 185, 129, 0.15);
            --danger: #ef4444;
            --danger-glow: rgba(239, 68, 68, 0.15);
            --border: rgba(255, 255, 255, 0.08);
            --font-display: 'Outfit', sans-serif;
            --font-body: 'Plus Jakarta Sans', sans-serif;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            background-color: var(--bg-primary);
            color: var(--text-main);
            font-family: var(--font-body);
            -webkit-font-smoothing: antialiased;
            overflow-x: hidden;
            padding-bottom: 40px;
        }}

        .container {{
            max-width: 1750px;
            margin: 0 auto;
            padding: 24px;
        }}

        /* Header design */
        header {{
            margin-bottom: 24px;
            position: relative;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border);
        }}
        
        header::after {{
            content: '';
            position: absolute;
            top: -100px;
            left: 20%;
            width: 400px;
            height: 300px;
            background: radial-gradient(circle, var(--accent-glow) 0%, transparent 70%);
            z-index: -1;
            pointer-events: none;
        }}

        .header-title-container h1 {{
            font-family: var(--font-display);
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #fff 40%, var(--accent-primary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 4px;
            letter-spacing: -0.5px;
        }}

        .header-title-container p {{
            color: var(--text-muted);
            font-size: 0.95rem;
        }}

        .header-badge {{
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(99, 102, 241, 0.3);
            color: #a5b4fc;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
            font-family: var(--font-display);
        }}

        /* Layout Grid */
        .layout {{
            display: grid;
            grid-template-columns: 330px 1fr;
            gap: 24px;
            align-items: start;
        }}

        /* Sidebar card design */
        .sidebar {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px;
            position: sticky;
            top: 24px;
            max-height: 90vh;
            overflow-y: auto;
        }}

        .sidebar-title {{
            font-family: var(--font-display);
            font-size: 1.15rem;
            font-weight: 700;
            margin-bottom: 16px;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .form-group {{
            margin-bottom: 14px;
        }}

        .form-group label {{
            display: block;
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--text-muted);
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .form-control {{
            width: 100%;
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 8px 12px;
            color: #fff;
            font-family: var(--font-body);
            font-size: 0.9rem;
            transition: all 0.2s ease;
        }}

        .form-control:focus {{
            outline: none;
            border-color: var(--accent-primary);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
        }}

        .form-checkbox {{
            display: flex;
            align-items: center;
            gap: 10px;
            cursor: pointer;
            user-select: none;
            margin-top: 8px;
        }}

        .form-checkbox input {{
            width: 16px;
            height: 16px;
            accent-color: var(--accent-primary);
            cursor: pointer;
        }}

        .form-checkbox span {{
            font-size: 0.85rem;
            font-weight: 500;
            color: var(--text-main);
        }}

        /* Main Workspace Panel */
        .workspace {{
            display: flex;
            flex-direction: column;
            gap: 24px;
            min-width: 0;
            overflow: hidden;
        }}

        /* Tabs menu design */
        .tab-menu {{
            display: flex;
            gap: 8px;
            border-bottom: 1px solid var(--border);
            padding-bottom: 8px;
        }}

        .tab-btn {{
            background: transparent;
            border: none;
            color: var(--text-muted);
            padding: 8px 16px;
            font-family: var(--font-display);
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.2s ease;
        }}

        .tab-btn:hover {{
            color: #fff;
            background: rgba(255, 255, 255, 0.03);
        }}

        .tab-btn.active {{
            color: #fff;
            background: rgba(99, 102, 241, 0.12);
            border: 1px solid rgba(99, 102, 241, 0.2);
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        /* Summary Cards Grid */
        .impact-grid {{
            display: grid;
            grid-template-columns: 2fr 3fr;
            gap: 20px;
            margin-bottom: 24px;
        }}

        .impact-card {{
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.05) 100%);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 16px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}

        .impact-title {{
            font-family: var(--font-display);
            font-size: 1.15rem;
            font-weight: 700;
            color: #fff;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .impact-metrics {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }}

        .impact-metric {{
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 14px;
            text-align: center;
        }}

        .impact-val-container {{
            display: flex;
            flex-direction: column;
            gap: 4px;
            margin-top: 6px;
        }}

        .impact-pct-badge {{
            display: inline-block;
            padding: 2px 6px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 700;
            font-family: var(--font-display);
            margin-top: 6px;
        }}

        .impact-pct-badge.positive {{
            background: rgba(16, 185, 129, 0.15);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }}

        .impact-pct-badge.negative {{
            background: rgba(239, 68, 68, 0.15);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }}

        /* Diagnostics Panel design */
        .diagnostics-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px;
        }}

        .diagnostics-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
        }}

        .diag-item {{
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 10px 14px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .diag-label {{
            font-size: 0.72rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}

        .diag-val {{
            font-family: var(--font-display);
            font-size: 1.15rem;
            font-weight: 700;
            color: #fff;
        }}

        /* Tables and layout */
        .table-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 24px;
            overflow-x: auto;
        }}

        .section-title {{
            font-family: var(--font-display);
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 14px;
            color: #fff;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .comparison-table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.85rem;
        }}

        .comparison-table th {{
            padding: 10px 12px;
            background: var(--bg-tertiary);
            color: var(--text-muted);
            font-family: var(--font-display);
            font-weight: 600;
            border-bottom: 2px solid var(--border);
            text-transform: uppercase;
            font-size: 0.72rem;
            letter-spacing: 0.5px;
        }}

        .comparison-table td {{
            padding: 11px 12px;
            border-bottom: 1px solid var(--border);
            color: var(--text-main);
            font-weight: 500;
        }}

        .comparison-table tr:hover {{
            background: rgba(255, 255, 255, 0.02);
        }}

        .comparison-table tr.highlight {{
            background: rgba(99, 102, 241, 0.06);
        }}

        .comparison-table tr.highlight td:first-child {{
            border-left: 3px solid var(--accent-primary);
        }}

        .strategy-name {{
            font-family: var(--font-display);
            font-weight: 700;
            color: #fff;
        }}

        /* Text colors */
        .positive {{ color: var(--success); }}
        .negative {{ color: var(--danger); }}
        .neutral {{ color: var(--text-main); }}

        /* Charts grid */
        .charts-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-bottom: 24px;
        }}

        .chart-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px;
            min-height: 420px;
            display: flex;
            flex-direction: column;
        }}

        .chart-container {{
            position: relative;
            flex: 1;
            width: 100%;
            height: 100%;
        }}

        /* Ledger card */
        .ledger-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px;
            overflow: hidden;
            max-width: 100%;
            box-sizing: border-box;
        }}

        .ledger-table-wrapper {{
            overflow-x: auto;
            overflow-y: auto;
            max-height: calc(100vh - 280px);
            min-height: 350px;
            width: 100%;
            margin-top: 12px;
            -webkit-overflow-scrolling: touch;
            scrollbar-width: auto;
            scrollbar-color: rgba(99, 102, 241, 0.4) rgba(255, 255, 255, 0.02);
        }}

        /* Custom horizontal scrollbar for high visibility */
        .ledger-table-wrapper::-webkit-scrollbar {{
            height: 12px;
        }}

        .ledger-table-wrapper::-webkit-scrollbar-track {{
            background: rgba(255, 255, 255, 0.02);
            border-radius: 6px;
        }}

        .ledger-table-wrapper::-webkit-scrollbar-thumb {{
            background: rgba(99, 102, 241, 0.4);
            border-radius: 6px;
            border: 2px solid var(--bg-secondary);
        }}

        .ledger-table-wrapper::-webkit-scrollbar-thumb:hover {{
            background: var(--accent-primary);
        }}

        .ledger-controls {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            gap: 16px;
        }}

        .ledger-search {{
            max-width: 300px;
        }}

        .ledger-pagination {{
            display: flex;
            gap: 8px;
            align-items: center;
        }}

        .pagination-btn {{
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text-main);
            padding: 6px 12px;
            cursor: pointer;
            font-size: 0.8rem;
            font-weight: 600;
            transition: all 0.2s ease;
        }}

        .pagination-btn:hover:not(:disabled) {{
            background: var(--accent-primary);
            color: #fff;
        }}

        .pagination-btn:disabled {{
            opacity: 0.4;
            cursor: not-allowed;
        }}

        .pagination-info {{
            font-size: 0.8rem;
            color: var(--text-muted);
        }}

        .ledger-table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.78rem;
            white-space: nowrap;
        }}

        .ledger-table th {{
            padding: 8px 10px;
            background: var(--bg-tertiary);
            color: var(--text-muted);
            font-weight: 600;
            border-bottom: 2px solid var(--border);
            font-size: 0.7rem;
            letter-spacing: 0.3px;
            text-transform: uppercase;
            position: sticky;
            top: 0;
            z-index: 10;
        }}

        .ledger-table td {{
            padding: 8px 10px;
            border-bottom: 1px solid var(--border);
            color: var(--text-main);
        }}

        .ledger-table tr:hover {{
            background: rgba(255, 255, 255, 0.02);
        }}

        .badge {{
            padding: 2px 4px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
            font-family: var(--font-display);
        }}

        .badge-buy {{
            background: rgba(16, 185, 129, 0.12);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.2);
        }}

        .badge-sell {{
            background: rgba(239, 68, 68, 0.12);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.2);
        }}

        .window-boundary {{
            color: var(--text-muted);
            font-size: 0.72rem;
        }}

        @media (max-width: 1350px) {{
            .layout {{
                grid-template-columns: 1fr;
            }}
            .sidebar {{
                position: relative;
                top: 0;
                max-height: none;
            }}
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
            .impact-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        .preset-btn {{
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            color: var(--text-muted);
            border-radius: 4px;
            padding: 4px 6px;
            font-size: 0.72rem;
            font-weight: 600;
            cursor: pointer;
            flex: 1;
            text-align: center;
            transition: all 0.2s ease;
        }}

        .preset-btn:hover {{
            background: var(--accent-primary);
            color: #fff;
            border-color: var(--accent-primary);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="header-title-container">
                <h1>Kelly Position Sizing Dashboard v2.0</h1>
                <p>Quantitative walk-forward optimization vs original strategy & fixed baselines</p>
            </div>
            <span class="header-badge">Out-of-Sample: Trade 101 – 1133</span>
        </header>

        <div class="layout">
            <!-- Sidebar Controls -->
            <div class="sidebar">
                <div class="sidebar-title">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="3"></circle>
                        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                    </svg>
                    Simulation Settings
                </div>

                <div class="form-group">
                    <label for="initial-capital">Starting Capital (₹)</label>
                    <input type="number" id="initial-capital" class="form-control" value="100000" min="1000" max="10000000">
                    <div style="display: flex; gap: 4px; margin-top: 6px;">
                        <button type="button" class="preset-btn" onclick="setPresetCapital(10000)">10k</button>
                        <button type="button" class="preset-btn" onclick="setPresetCapital(50000)">50k</button>
                        <button type="button" class="preset-btn" onclick="setPresetCapital(100000)">100k</button>
                        <button type="button" class="preset-btn" onclick="setPresetCapital(500000)">500k</button>
                        <button type="button" class="preset-btn" onclick="setPresetCapital(1000000)">1M</button>
                    </div>
                </div>
                <div class="form-group">
                    <label for="window-size">Kelly Rolling Window</label>
                    <input type="number" id="window-size" class="form-control" value="100" min="10" max="500">
                </div>

                <div class="form-group">
                    <label for="sizing-method">Position Sizing Method</label>
                    <select id="sizing-method" class="form-control">
                        <option value="margin">Margin Based (Existing)</option>
                        <option value="risk" selected>Risk Based (New)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="active-kelly-strategy">Analyze Kelly Strategy</label>
                    <select id="active-kelly-strategy" class="form-control">
                        <option value="kelly_1_4" selected>1/4 Kelly (Quarter Kelly)</option>
                        <option value="kelly_full">Full Kelly (Normal Kelly)</option>
                        <option value="kelly_1_2">Half Kelly</option>
                        <option value="kelly_1_8">1/8 Kelly (Eighth Kelly)</option>
                        <option value="kelly_1_4_min_1">1/4 Kelly + Min 1 Lot</option>
                        <option value="original">Original Strategy</option>
                        <option value="fixed_1">Fixed 1 Lot</option>
                        <option value="fixed_2">Fixed 2 Lots</option>
                    </select>
                </div>                <!-- Manual Lot Mapping Settings -->
                <div class="form-group">
                    <label for="lot-source">Original Lots Source</label>
                    <select id="lot-source" class="form-control">
                        <!-- JS Dynamically Populated Columns -->
                    </select>
                </div>

                <div class="form-group" id="fixed-lots-group" style="display: none;">
                    <label for="fixed-lots-val">Original Fixed Lots</label>
                    <input type="number" id="fixed-lots-val" class="form-control" value="1" min="1" max="1000">
                </div>

                <div class="form-group">
                    <label for="margin-model">Margin Model</label>
                    <select id="margin-model" class="form-control">
                        <option value="premium" selected>Premium-Based (Option Buying)</option>
                        <option value="fixed">Fixed Margin (Option Selling)</option>
                    </select>
                </div>

                <div class="form-group" id="fixed-margin-group" style="display: none;">
                    <label for="fixed-margin">Margin Per Lot (₹)</label>
                    <input type="number" id="fixed-margin" class="form-control" value="10000" min="500" max="500000">
                </div>

                <div class="form-group">
                    <label for="lot-size">Lot Size Multiplier</label>
                    <input type="number" id="lot-size" class="form-control" value="65" min="1" max="1000">
                </div>

                <!-- Capping & Minimum Sizing Controls -->
                <div class="form-group">
                    <label for="max-lots-limit">Maximum Lots Cap</label>
                    <input type="number" id="max-lots-limit" class="form-control" value="10" min="1" max="100000">
                    <div style="display: flex; gap: 4px; margin-top: 6px;">
                        <button type="button" class="preset-btn" onclick="setPresetLots(1)">1</button>
                        <button type="button" class="preset-btn" onclick="setPresetLots(2)">2</button>
                        <button type="button" class="preset-btn" onclick="setPresetLots(5)">5</button>
                        <button type="button" class="preset-btn" onclick="setPresetLots(10)">10</button>
                        <button type="button" class="preset-btn" onclick="setPresetLots(20)">20</button>
                        <button type="button" class="preset-btn" onclick="setPresetLots(100000)">Max</button>
                    </div>
                </div>

                <div class="form-group">
                    <label class="form-checkbox">
                        <input type="checkbox" id="force-min-1" checked>
                        <span>Force Minimum 1 Lot (if Kelly > 0)</span>
                    </label>
                </div>

                <div class="form-group">
                    <label class="form-checkbox">
                        <input type="checkbox" id="apply-taxes">
                        <span>Apply flat ₹40 fee / trade</span>
                    </label>
                </div>
            </div>

            <!-- Workspace -->
            <div class="workspace">
                <!-- Tabs Menu -->
                <div class="tab-menu">
                    <button class="tab-btn active" onclick="switchTab('overview')">Performance Overview</button>
                    <button class="tab-btn" onclick="switchTab('analysis')">Position Sizing Performance Analysis</button>
                    <button class="tab-btn" onclick="switchTab('sizing')">Sizing Analysis</button>
                    <button class="tab-btn" onclick="switchTab('ledger')">Detailed Trade Ledger</button>
                </div>

                <!-- Tab 1: Overview -->
                <div id="overview-tab" class="tab-content active">
                    <div class="impact-grid">
                        <!-- Position Sizing Impact Section -->
                        <div class="impact-card">
                            <div class="impact-title">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                                    <polyline points="22 4 12 14.01 9 11.01"></polyline>
                                </svg>
                                Position Sizing Impact
                            </div>
                            <div class="impact-metrics">
                                <div class="impact-metric">
                                    <div class="kpi-label" style="margin-bottom: 4px;">Profit Improvement</div>
                                    <div class="diag-val" id="impact-profit-val">₹0</div>
                                    <span class="impact-pct-badge positive" id="impact-profit-pct">+0.0%</span>
                                </div>
                                <div class="impact-metric">
                                    <div class="kpi-label" style="margin-bottom: 4px;">Drawdown Reduction</div>
                                    <div class="diag-val" id="impact-dd-val">0.0%</div>
                                    <span class="impact-pct-badge positive" id="impact-dd-pct">-0.0%</span>
                                </div>
                            </div>
                        </div>

                        <!-- Kelly Diagnostics Panel -->
                        <div class="diagnostics-card">
                            <div class="impact-title">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <line x1="18" y1="20" x2="18" y2="10"></line>
                                    <line x1="12" y1="20" x2="12" y2="4"></line>
                                    <line x1="6" y1="20" x2="6" y2="14"></line>
                                </svg>
                                Active Kelly Sizing Diagnostics
                            </div>
                            <div class="diagnostics-grid">
                                <div class="diag-item">
                                    <span class="diag-label">Avg Kelly %</span>
                                    <span class="diag-val" id="diag-avg-kelly">0.0%</span>
                                </div>
                                <div class="diag-item">
                                    <span class="diag-label">Max Kelly %</span>
                                    <span class="diag-val" id="diag-max-kelly">0.0%</span>
                                </div>
                                <div class="diag-item">
                                    <span class="diag-label">Avg Lots Traded</span>
                                    <span class="diag-val" id="diag-avg-lots">0.0</span>
                                </div>
                                <div class="diag-item">
                                    <span class="diag-label">Max Lots Used</span>
                                    <span class="diag-val" id="diag-max-lots">0</span>
                                </div>
                                <div class="diag-item" style="grid-column: span 2;">
                                    <span class="diag-label">Executed / Skipped Trades</span>
                                    <span class="diag-val" id="diag-trades-ratio">0 / 0</span>
                                </div>
                                <div class="diag-item" style="grid-column: span 2;">
                                    <span class="diag-label">Avg Capital Utilization</span>
                                    <span class="diag-val" id="diag-utilization">0.0%</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Performance Comparison Table -->
                    <div class="table-card">
                        <div class="section-title">Strategy Performance Comparison Table</div>
                        <table class="comparison-table">
                            <thead>
                                <tr>
                                    <th>Strategy</th>
                                    <th>Total Profit</th>
                                    <th>Final Capital</th>
                                    <th>CAGR</th>
                                    <th>Max DD</th>
                                    <th>Win Rate</th>
                                    <th>PF</th>
                                    <th>Expectancy</th>
                                    <th>Recovery Factor</th>
                                    <th>Executed</th>
                                    <th>Skipped</th>
                                    <th>Avg Lot</th>
                                    <th>Cap Util</th>
                                    <th>Profit Imp. vs Orig</th>
                                    <th>DD Imp. vs Orig</th>
                                </tr>
                            </thead>
                            <tbody id="comparison-table-body">
                                <!-- JS Injected Rows -->
                            </tbody>
                        </table>
                    </div>

                    <!-- Charts Grid -->
                    <div class="charts-grid">
                        <div class="chart-card">
                            <div class="section-title">Equity Curves Comparison (Growth of ₹100,000)</div>
                            <div class="chart-container">
                                <canvas id="equityChart"></canvas>
                            </div>
                        </div>
                        <div class="chart-card">
                            <div class="section-title">Drawdown Profile Comparison (%)</div>
                            <div class="chart-container">
                                <canvas id="drawdownChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Tab: Position Sizing Performance Analysis -->
                <div id="analysis-tab" class="tab-content">
                    <!-- KPI Cards Grid: Without vs With Sizing (Fixed 1 Lot vs Full Kelly vs Quarter Kelly) -->
                    <div class="analysis-kpi-grid" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 24px;">
                        <!-- Fixed 1 Lot Baseline -->
                        <div class="diagnostics-card" style="border: 1px solid var(--border); padding: 20px;">
                            <div class="impact-title" style="font-size: 1.15rem; margin-bottom: 16px; color: #fff;">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px;">
                                    <circle cx="12" cy="12" r="10"></circle>
                                    <line x1="15" y1="9" x2="9" y2="15"></line>
                                    <line x1="9" y1="9" x2="15" y2="15"></line>
                                </svg>
                                Fixed 1 Lot Baseline
                            </div>
                            <div class="diagnostics-grid" style="grid-template-columns: repeat(3, 1fr); gap: 10px;">
                                <div class="diag-item"><span class="diag-label">Start Cap</span><span class="diag-val" id="kpi-f1-start" style="font-size: 0.95rem;">₹100,000</span></div>
                                <div class="diag-item"><span class="diag-label">Final Cap</span><span class="diag-val" id="kpi-f1-final" style="font-size: 0.95rem;">₹0</span></div>
                                <div class="diag-item"><span class="diag-label">Total Profit</span><span class="diag-val" id="kpi-f1-profit" style="font-size: 0.95rem;">₹0</span></div>
                                <div class="diag-item"><span class="diag-label">CAGR</span><span class="diag-val" id="kpi-f1-cagr" style="font-size: 0.95rem;">0.0%</span></div>
                                <div class="diag-item"><span class="diag-label">Max DD</span><span class="diag-val" id="kpi-f1-dd" style="color: var(--danger); font-size: 0.95rem;">0.0%</span></div>
                                <div class="diag-item"><span class="diag-label">Profit Fact</span><span class="diag-val" id="kpi-f1-pf" style="font-size: 0.95rem;">0.00</span></div>
                                <div class="diag-item"><span class="diag-label">Rec. Fact</span><span class="diag-val" id="kpi-f1-rf" style="font-size: 0.95rem;">0.00</span></div>
                                <div class="diag-item"><span class="diag-label">Expectancy</span><span class="diag-val" id="kpi-f1-exp" style="font-size: 0.95rem;">₹0</span></div>
                                <div class="diag-item"><span class="diag-label">Win Rate</span><span class="diag-val" id="kpi-f1-wr" style="font-size: 0.95rem;">0.0%</span></div>
                            </div>
                        </div>

                        <!-- Full Kelly Sizing -->
                        <div class="diagnostics-card" style="border: 1px solid rgba(99, 102, 241, 0.4); background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(15, 21, 43, 0.3) 100%); padding: 20px;">
                            <div class="impact-title" style="font-size: 1.15rem; margin-bottom: 16px; color: #fff;">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px;">
                                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                                    <polyline points="22 4 12 14.01 9 11.01"></polyline>
                                </svg>
                                Full Kelly Sizing
                            </div>
                            <div class="diagnostics-grid" style="grid-template-columns: repeat(3, 1fr); gap: 10px;">
                                <div class="diag-item"><span class="diag-label">Start Cap</span><span class="diag-val" id="kpi-kf-start" style="font-size: 0.95rem;">₹100,000</span></div>
                                <div class="diag-item"><span class="diag-label">Final Cap</span><span class="diag-val" id="kpi-kf-final" style="font-size: 0.95rem;">₹0</span></div>
                                <div class="diag-item"><span class="diag-label">Total Profit</span><span class="diag-val" id="kpi-kf-profit" style="font-size: 0.95rem;">₹0</span></div>
                                <div class="diag-item"><span class="diag-label">CAGR</span><span class="diag-val" id="kpi-kf-cagr" style="font-size: 0.95rem;">0.0%</span></div>
                                <div class="diag-item"><span class="diag-label">Max DD</span><span class="diag-val" id="kpi-kf-dd" style="color: var(--danger); font-size: 0.95rem;">0.0%</span></div>
                                <div class="diag-item"><span class="diag-label">Profit Fact</span><span class="diag-val" id="kpi-kf-pf" style="font-size: 0.95rem;">0.00</span></div>
                                <div class="diag-item"><span class="diag-label">Rec. Fact</span><span class="diag-val" id="kpi-kf-rf" style="font-size: 0.95rem;">0.00</span></div>
                                <div class="diag-item"><span class="diag-label">Expectancy</span><span class="diag-val" id="kpi-kf-exp" style="font-size: 0.95rem;">₹0</span></div>
                                <div class="diag-item"><span class="diag-label">Win Rate</span><span class="diag-val" id="kpi-kf-wr" style="font-size: 0.95rem;">0.0%</span></div>
                            </div>
                        </div>

                        <!-- Quarter Kelly Sizing -->
                        <div class="diagnostics-card" style="border: 1px solid rgba(16, 185, 129, 0.4); background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(15, 21, 43, 0.3) 100%); padding: 20px;">
                            <div class="impact-title" style="font-size: 1.15rem; margin-bottom: 16px; color: #fff;">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px;">
                                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                                    <polyline points="22 4 12 14.01 9 11.01"></polyline>
                                </svg>
                                1/4 Kelly Sizing
                            </div>
                            <div class="diagnostics-grid" style="grid-template-columns: repeat(3, 1fr); gap: 10px;">
                                <div class="diag-item"><span class="diag-label">Start Cap</span><span class="diag-val" id="kpi-kq-start" style="font-size: 0.95rem;">₹100,000</span></div>
                                <div class="diag-item"><span class="diag-label">Final Cap</span><span class="diag-val" id="kpi-kq-final" style="font-size: 0.95rem;">₹0</span></div>
                                <div class="diag-item"><span class="diag-label">Total Profit</span><span class="diag-val" id="kpi-kq-profit" style="font-size: 0.95rem;">₹0</span></div>
                                <div class="diag-item"><span class="diag-label">CAGR</span><span class="diag-val" id="kpi-kq-cagr" style="font-size: 0.95rem;">0.0%</span></div>
                                <div class="diag-item"><span class="diag-label">Max DD</span><span class="diag-val" id="kpi-kq-dd" style="color: var(--danger); font-size: 0.95rem;">0.0%</span></div>
                                <div class="diag-item"><span class="diag-label">Profit Fact</span><span class="diag-val" id="kpi-kq-pf" style="font-size: 0.95rem;">0.00</span></div>
                                <div class="diag-item"><span class="diag-label">Rec. Fact</span><span class="diag-val" id="kpi-kq-rf" style="font-size: 0.95rem;">0.00</span></div>
                                <div class="diag-item"><span class="diag-label">Expectancy</span><span class="diag-val" id="kpi-kq-exp" style="font-size: 0.95rem;">₹0</span></div>
                                <div class="diag-item"><span class="diag-label">Win Rate</span><span class="diag-val" id="kpi-kq-wr" style="font-size: 0.95rem;">0.0%</span></div>
                            </div>
                        </div>
                    </div>

                    <!-- Sizing Improvement & Verdict Panel -->
                    <div class="improvement-verdict-container" style="display: grid; grid-template-columns: 2.2fr 1fr; gap: 24px; margin-bottom: 24px;">
                        <!-- Improvements Table -->
                        <div class="diagnostics-card" style="padding: 20px;">
                            <div class="impact-title" style="margin-bottom: 16px;">Sizing Improvement Metrics (vs. Fixed 1 Lot Baseline)</div>
                            <table class="comparison-table" style="font-size: 0.8rem;">
                                <thead>
                                    <tr>
                                        <th>Strategy</th>
                                        <th>Profit Imp %</th>
                                        <th>CAGR Imp %</th>
                                        <th>DD Reduction %</th>
                                        <th>Rec. Factor Imp</th>
                                        <th>Profit Factor Imp</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td style="font-weight: 700; color: #8b5cf6; font-family: var(--font-display);">Full Kelly</td>
                                        <td id="imp-kf-profit" style="font-weight: 600;">+0.00%</td>
                                        <td id="imp-kf-cagr" style="font-weight: 600;">+0.00%</td>
                                        <td id="imp-kf-dd" style="font-weight: 600;">+0.00%</td>
                                        <td id="imp-kf-rf" style="font-weight: 600;">+0.00</td>
                                        <td id="imp-kf-pf" style="font-weight: 600;">+0.00</td>
                                    </tr>
                                    <tr>
                                        <td style="font-weight: 700; color: #10b981; font-family: var(--font-display);">Quarter Kelly</td>
                                        <td id="imp-kq-profit" style="font-weight: 600;">+0.00%</td>
                                        <td id="imp-kq-cagr" style="font-weight: 600;">+0.00%</td>
                                        <td id="imp-kq-dd" style="font-weight: 600;">+0.00%</td>
                                        <td id="imp-kq-rf" style="font-weight: 600;">+0.00</td>
                                        <td id="imp-kq-pf" style="font-weight: 600;">+0.00</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <!-- Verdict Card -->
                        <div class="diagnostics-card" style="display: flex; flex-direction: column; gap: 14px; padding: 20px; justify-content: center;">
                            <div id="verdict-card-kf" style="text-align: center; border-bottom: 1px solid var(--border); padding-bottom: 12px; transition: all 0.3s ease;">
                                <span class="diag-label" style="font-size: 0.72rem; letter-spacing: 0.5px;">Full Kelly Verdict</span>
                                <div class="diag-val" id="verdict-text-kf" style="font-size: 1.15rem; margin-top: 4px; font-family: var(--font-display); font-weight: 800; line-height: 1.2;">Calculating...</div>
                                <div id="verdict-desc-kf" style="color: var(--text-muted); font-size: 0.72rem; margin-top: 4px; font-weight: 500;">-</div>
                            </div>
                            <div id="verdict-card-kq" style="text-align: center; transition: all 0.3s ease;">
                                <span class="diag-label" style="font-size: 0.72rem; letter-spacing: 0.5px;">1/4 Kelly Verdict</span>
                                <div class="diag-val" id="verdict-text-kq" style="font-size: 1.15rem; margin-top: 4px; font-family: var(--font-display); font-weight: 800; line-height: 1.2;">Calculating...</div>
                                <div id="verdict-desc-kq" style="color: var(--text-muted); font-size: 0.72rem; margin-top: 4px; font-weight: 500;">-</div>
                            </div>
                        </div>
                    </div>

                    <!-- Best/Worst Trades comparative table -->
                    <div class="table-card" style="margin-bottom: 24px; padding: 20px;">
                        <div class="section-title" style="margin-bottom: 12px;">Best and Worst Trades Comparison</div>
                        <table class="comparison-table" style="font-size: 0.82rem;">
                            <thead>
                                <tr>
                                    <th>Strategy</th>
                                    <th>Best Trade Number</th>
                                    <th>Best Trade Date</th>
                                    <th>Best Trade Profit Amount</th>
                                    <th>Worst Trade Number</th>
                                    <th>Worst Trade Date</th>
                                    <th>Worst Trade Loss Amount</th>
                                </tr>
                            </thead>
                            <tbody id="best-worst-table-body">
                                <!-- Dynamic JS rows -->
                            </tbody>
                        </table>
                    </div>

                    <!-- Statistics panels: Sizing Stats & Capital Utilizations -->
                    <div class="sizing-stats-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px;">
                        <!-- Sizing Analytics -->
                        <div class="diagnostics-card" style="padding: 20px;">
                            <div class="impact-title" style="margin-bottom: 16px;">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent-secondary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px;">
                                    <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
                                    <polyline points="2 17 12 22 22 17"></polyline>
                                    <polyline points="2 12 12 17 22 12"></polyline>
                                </svg>
                                Active Kelly Sizing Analytics
                            </div>
                            <div class="diagnostics-grid" style="grid-template-columns: repeat(3, 1fr); gap: 12px;">
                                <div class="diag-item"><span class="diag-label">Average Kelly %</span><span class="diag-val" id="stats-avg-kelly">0.0%</span></div>
                                <div class="diag-item"><span class="diag-label">Maximum Kelly %</span><span class="diag-val" id="stats-max-kelly">0.0%</span></div>
                                <div class="diag-item"><span class="diag-label">Minimum Kelly %</span><span class="diag-val" id="stats-min-kelly">0.0%</span></div>
                                
                                <div class="diag-item"><span class="diag-label">Average Position Amount</span><span class="diag-val" id="stats-avg-pos-amt">₹0</span></div>
                                <div class="diag-item"><span class="diag-label">Maximum Position Amount</span><span class="diag-val" id="stats-max-pos-amt">₹0</span></div>
                                <div class="diag-item"><span class="diag-label">Minimum Position Amount</span><span class="diag-val" id="stats-min-pos-amt">₹0</span></div>
                                
                                <div class="diag-item"><span class="diag-label">Average Lots</span><span class="diag-val" id="stats-avg-lots">0.00</span></div>
                                <div class="diag-item"><span class="diag-label">Maximum Lots</span><span class="diag-val" id="stats-max-lots">0</span></div>
                                <div class="diag-item"><span class="diag-label">Minimum Lots</span><span class="diag-val" id="stats-min-lots">0</span></div>
                            </div>
                        </div>
                        
                        <!-- Capital Utilization -->
                        <div class="diagnostics-card" style="padding: 20px;">
                            <div class="impact-title" style="margin-bottom: 16px;">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px;">
                                    <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                                </svg>
                                Capital Utilization & Margin Analytics
                            </div>
                            <div class="diagnostics-grid" style="grid-template-columns: repeat(2, 1fr); gap: 12px;">
                                <div class="diag-item" style="grid-column: span 2;"><span class="diag-label">Average Capital Utilization %</span><span class="diag-val" id="util-avg-pct" style="font-size: 1.35rem; color: var(--accent-primary);">0.0%</span></div>
                                <div class="diag-item"><span class="diag-label">Average Capital Used</span><span class="diag-val" id="util-avg-margin">₹0</span></div>
                                <div class="diag-item"><span class="diag-label">Maximum Capital Used</span><span class="diag-val" id="util-max-margin">₹0</span></div>
                                <div class="diag-item"><span class="diag-label">Minimum Capital Used</span><span class="diag-val" id="util-min-margin">₹0</span></div>
                            </div>
                        </div>
                    </div>

                    <!-- Option split & Checklist Grid -->
                    <div class="options-validation-grid" style="display: grid; grid-template-columns: 1.2fr 1fr; gap: 24px; margin-bottom: 24px;">
                        <!-- CE vs PE split table -->
                        <div class="table-card" style="margin-bottom: 0; padding: 20px;">
                            <div class="section-title" style="margin-bottom: 12px;">Option Type Performance Split (CE vs PE)</div>
                            <table class="comparison-table" style="font-size: 0.8rem;">
                                <thead>
                                    <tr>
                                        <th>Option Type</th>
                                        <th>Trade Count</th>
                                        <th>Win Rate</th>
                                        <th>Net Profit</th>
                                        <th>Avg Profit / Trade</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td style="font-weight: 700; color: #818cf8; font-family: var(--font-display);">CE (Call Options)</td>
                                        <td id="ce-count">0</td>
                                        <td id="ce-wr">0.0%</td>
                                        <td id="ce-profit" class="neutral" style="font-weight: 600;">₹0</td>
                                        <td id="ce-avg-profit" class="neutral" style="font-weight: 600;">₹0</td>
                                    </tr>
                                    <tr>
                                        <td style="font-weight: 700; color: #f472b6; font-family: var(--font-display);">PE (Put Options)</td>
                                        <td id="pe-count">0</td>
                                        <td id="pe-wr">0.0%</td>
                                        <td id="pe-profit" class="neutral" style="font-weight: 600;">₹0</td>
                                        <td id="pe-avg-profit" class="neutral" style="font-weight: 600;">₹0</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>

                        <!-- System Checklist -->
                        <div class="diagnostics-card" style="padding: 20px;">
                            <div class="impact-title" style="margin-bottom: 16px;">Sizing Rules & System Verification Checklist</div>
                            <div style="display: grid; grid-template-columns: 1fr; gap: 10px; font-size: 0.85rem; font-weight: 500;">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span style="color: var(--success); font-weight: 800; font-size: 1.1rem;">✓</span>
                                    <span>No Look-Ahead Bias: Sizing calculations use completed trades only</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span style="color: var(--success); font-weight: 800; font-size: 1.1rem;">✓</span>
                                    <span>Rolling Window: Sizing is calculated strictly from previous 100 trades</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span style="color: var(--success); font-weight: 800; font-size: 1.1rem;">✓</span>
                                    <span>Out-of-Sample: Sizing begins at Trade 101; 1-100 build initial window</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span style="color: var(--success); font-weight: 800; font-size: 1.1rem;">✓</span>
                                    <span>Compounding: Capital compounding applies correctly to profits and losses</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span style="color: var(--success); font-weight: 800; font-size: 1.1rem;">✓</span>
                                    <span>Recalculation: Win Rate & Edge are updated trade-by-trade</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span style="color: var(--success); font-weight: 800; font-size: 1.1rem;">✓</span>
                                    <span>Lot constraints: Sizing cap is applied correctly after calculation</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Performance Diagnostics Card -->
                    <div class="diagnostics-card" style="margin-bottom: 24px; padding: 20px;">
                        <div class="impact-title" style="margin-bottom: 16px;">Performance Diagnostics & Execution Analytics</div>
                        <div class="diagnostics-grid" style="grid-template-columns: repeat(4, 1fr); gap: 12px;">
                            <div class="diag-item"><span class="diag-label">Total Out-of-Sample Trades</span><span class="diag-val" id="diag-period-trades">0</span></div>
                            <div class="diag-item"><span class="diag-label">Executed Trades (Lots > 0)</span><span class="diag-val" id="diag-period-exec">0</span></div>
                            <div class="diag-item"><span class="diag-label">Skipped Trades (Lots = 0)</span><span class="diag-val" id="diag-period-skip" style="color: var(--danger);">0</span></div>
                            <div class="diag-item"><span class="diag-label">Skipped (Kelly = 0)</span><span class="diag-val" id="diag-skip-kelly">0</span></div>
                            <div class="diag-item"><span class="diag-label">Skipped (Capital Insufficient)</span><span class="diag-val" id="diag-skip-cap" style="color: var(--danger);">0</span></div>
                            <div class="diag-item" style="grid-column: span 2;"><span class="diag-label">Trades Capped at Maximum Lot Cap</span><span class="diag-val" id="diag-capped-lots" style="color: var(--accent-secondary);">0</span></div>
                            <div class="diag-item"><span class="diag-label">Average Holding Time</span><span class="diag-val" id="diag-period-holding">0.0 mins</span></div>
                        </div>
                    </div>

                    <!-- Position Sizing Summary Table -->
                    <div class="table-card" style="margin-bottom: 24px; padding: 20px;">
                        <div class="section-title" style="margin-bottom: 12px;">Position Sizing Performance Comparison</div>
                        <table class="comparison-table" style="font-size: 0.82rem;">
                            <thead>
                                <tr>
                                    <th>Metric</th>
                                    <th>Fixed 1 Lot</th>
                                    <th>Fixed 2 Lots</th>
                                    <th>Full Kelly</th>
                                    <th>Half Kelly</th>
                                    <th>Kelly Quarter</th>
                                    <th>Kelly Eighth</th>
                                </tr>
                            </thead>
                            <tbody id="sizing-summary-table-body">
                                <!-- Dynamic JS metrics rows -->
                            </tbody>
                        </table>
                    </div>

                    <!-- Sizing Charts Grid -->
                    <div class="charts-grid" style="grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px;">
                        <!-- Chart 1: Capital Growth Comparison -->
                        <div class="chart-card" style="min-height: 400px;">
                            <div class="section-title">Capital Growth Comparison (Kelly vs. Fixed Baselines)</div>
                            <div class="chart-container"><canvas id="growthChart"></canvas></div>
                        </div>
                        
                        <!-- Chart 2: Drawdown Profile Comparison -->
                        <div class="chart-card" style="min-height: 400px;">
                            <div class="section-title">Drawdown Profile Comparison (%)</div>
                            <div class="chart-container"><canvas id="ddProfileChart"></canvas></div>
                        </div>

                        <!-- Chart 3: Position Amount Over Time -->
                        <div class="chart-card" style="min-height: 400px;">
                            <div class="section-title">Position Amount Allocated Over Time (₹)</div>
                            <div class="chart-container"><canvas id="posAmtChart"></canvas></div>
                        </div>

                        <!-- Chart 4: Capital Utilization % -->
                        <div class="chart-card" style="min-height: 400px;">
                            <div class="section-title">Capital Utilization % Over Time</div>
                            <div class="chart-container"><canvas id="capUtilChart"></canvas></div>
                        </div>

                        <!-- Chart 5: Kelly % Over Time -->
                        <div class="chart-card" style="min-height: 400px;">
                            <div class="section-title">Rolling Kelly % Edge Over Time</div>
                            <div class="chart-container"><canvas id="rollingKellyChart"></canvas></div>
                        </div>

                        <!-- Chart 6: Lot Distribution Histogram -->
                        <div class="chart-card" style="min-height: 400px;">
                            <div class="section-title">Lot Size Frequency Distribution (Histogram)</div>
                            <div class="chart-container"><canvas id="lotDistChart"></canvas></div>
                        </div>
                    </div>

                    <!-- Chart 7: Trade Profit Distribution Histogram -->
                    <div class="chart-card" style="margin-bottom: 24px; min-height: 450px; padding: 20px;">
                        <div class="section-title">Trade Profit/Loss Size Frequency Distribution (Histogram)</div>
                        <div class="chart-container"><canvas id="pnlDistChart"></canvas></div>
                    </div>
                </div>

                <!-- Tab 2: Sizing Analysis -->
                <div id="sizing-tab" class="tab-content">
                    <div class="charts-grid">
                        <div class="chart-card">
                            <div class="section-title">Rolling Kelly % over Time</div>
                            <div class="chart-container">
                                <canvas id="kellyChart"></canvas>
                            </div>
                        </div>
                        <div class="chart-card">
                            <div class="section-title">Lot Sizes Traded over Time</div>
                            <div class="chart-container">
                                <canvas id="lotsChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Tab 3: Ledger -->
                <div id="ledger-tab" class="tab-content">
                    <div class="ledger-card">
                        <div class="section-title">
                            Detailed Kelly Sizing Verification Ledger
                            <span style="font-size: 0.8rem; font-weight: normal; color: var(--text-muted);">Verifying every rolling walk-forward parameter trade-by-trade</span>
                        </div>
                        
                        <div class="ledger-controls">
                            <input type="text" id="search-input" class="form-control ledger-search" placeholder="Search by reason, type, signal..." oninput="onSearchChange()">
                            
                            <div class="ledger-pagination">
                                <button id="prev-btn" class="pagination-btn" onclick="prevPage()" disabled>Previous</button>
                                <span class="pagination-info" id="pagination-info">Page 1 of 1</span>
                                <button id="next-btn" class="pagination-btn" onclick="nextPage()">Next</button>
                            </div>
                        </div>

                        <div class="ledger-table-wrapper">
                            <table class="ledger-table">
                                <thead>
                                    <tr style="background: var(--bg-tertiary);">
                                        <th colspan="6" style="text-align: center; border-bottom: 2px solid var(--border); border-right: 1px solid var(--border);">Trade Details</th>
                                        <th colspan="8" style="text-align: center; border-bottom: 2px solid var(--border); border-right: 1px solid var(--border);">Rolling Sizing Params (Shared)</th>
                                        <th colspan="6" style="text-align: center; border-bottom: 2px solid var(--border); border-right: 1px solid var(--border); color: #8b5cf6;">Full Kelly Strategy Sizing</th>
                                        <th colspan="6" style="text-align: center; border-bottom: 2px solid var(--border); border-right: 1px solid var(--border); color: #10b981;">1/4 Kelly Strategy Sizing</th>
                                        <th colspan="3" style="text-align: center; border-bottom: 2px solid var(--border);">Diagnostics</th>
                                    </tr>
                                    <tr>
                                        <th>Trade #</th>
                                        <th>Date</th>
                                        <th>CE/PE</th>
                                        <th>Entry Price</th>
                                        <th>Stop Loss</th>
                                        <th style="border-right: 1px solid var(--border);">Exit Price</th>
                                        <th>PnL/Lot</th>
                                        <th>Win Rate</th>
                                        <th>Avg Win</th>
                                        <th>Avg Loss</th>
                                        <th>W/L Ratio</th>
                                        <th>Kelly %</th>
                                        <th>Risk/Option</th>
                                        <th style="border-right: 1px solid var(--border);">Risk/Lot</th>
                                        <th>Alloc %</th>
                                        <th>Risk Amt</th>
                                        <th>Lots</th>
                                        <th>Trade PnL</th>
                                        <th>Capital</th>
                                        <th style="border-right: 1px solid var(--border);">Util %</th>
                                        <th>Alloc %</th>
                                        <th>Risk Amt</th>
                                        <th>Lots</th>
                                        <th>Trade PnL</th>
                                        <th>Capital</th>
                                        <th style="border-right: 1px solid var(--border);">Util %</th>
                                        <th>Win Start</th>
                                        <th>Win End</th>
                                        <th>Exit Reason</th>
                                    </tr>
                                </thead>
                                <tbody id="ledger-table-body">
                                    <!-- JS Injected Rows -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Data Injection -->
    <script>
        const rawTrades = {trades_json_str};
        const lotColumns = {columns_json_str};
    </script>

    <!-- Main JS Simulation Engine & Renderers -->
    <script>
        let equityChart = null;
        let drawdownChart = null;
        let kellyChart = null;
        let lotsChart = null;
        
        let growthChart = null;
        let ddProfileChart = null;
        let posAmtChart = null;
        let capUtilChart = null;
        let rollingKellyChart = null;
        let lotDistChart = null;
        let pnlDistChart = null;

        let activeTab = 'overview';
        let currentPage = 1;
        const pageSize = 20;
        let filteredTrades = [];

        // Initialize Lot Source Dropdown
        const selectLotSource = document.getElementById('lot-source');
        
        // Add default columns from file
        lotColumns.forEach(col => {{
            const opt = document.createElement('option');
            opt.value = col;
            opt.innerText = col + ' (From File)';
            selectLotSource.appendChild(opt);
        }});
        
        // Add Fixed value fallback
        const optFixed = document.createElement('option');
        optFixed.value = 'fixed';
        optFixed.innerText = 'Fixed Lot Value (Manual)';
        selectLotSource.appendChild(optFixed);

        // Setup Event Listeners
        document.getElementById('initial-capital').addEventListener('input', runSimulationAndUpdateUI);
        document.getElementById('window-size').addEventListener('input', runSimulationAndUpdateUI);
        
        document.getElementById('lot-source').addEventListener('change', function() {{
            const val = this.value;
            const fixedLotsGroup = document.getElementById('fixed-lots-group');
            if (val === 'fixed') {{
                fixedLotsGroup.style.display = 'block';
            }} else {{
                fixedLotsGroup.style.display = 'none';
            }}
            runSimulationAndUpdateUI();
        }});
        document.getElementById('fixed-lots-val').addEventListener('input', runSimulationAndUpdateUI);

        document.getElementById('margin-model').addEventListener('change', function() {{
            const val = this.value;
            const fixedGroup = document.getElementById('fixed-margin-group');
            if (val === 'premium') {{
                fixedGroup.style.display = 'none';
            }} else {{
                fixedGroup.style.display = 'block';
            }}
            runSimulationAndUpdateUI();
        }});
        document.getElementById('fixed-margin').addEventListener('input', runSimulationAndUpdateUI);
        document.getElementById('lot-size').addEventListener('input', runSimulationAndUpdateUI);
        
        document.getElementById('max-lots-limit').addEventListener('input', runSimulationAndUpdateUI);
        document.getElementById('force-min-1').addEventListener('change', runSimulationAndUpdateUI);
        document.getElementById('apply-taxes').addEventListener('change', runSimulationAndUpdateUI);
        document.getElementById('sizing-method').addEventListener('change', runSimulationAndUpdateUI);
        document.getElementById('active-kelly-strategy').addEventListener('change', runSimulationAndUpdateUI);

        function setPresetCapital(val) {{
            document.getElementById('initial-capital').value = val;
            runSimulationAndUpdateUI();
        }}

        function setPresetLots(val) {{
            document.getElementById('max-lots-limit').value = val;
            runSimulationAndUpdateUI();
        }}

        function switchTab(tabId) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            const buttons = document.querySelectorAll('.tab-btn');
            buttons.forEach(btn => {{
                if (btn.getAttribute('onclick').includes(tabId)) {{
                    btn.classList.add('active');
                }}
            }});
            
            document.getElementById(tabId + '-tab').classList.add('active');
            activeTab = tabId;
            
            // Resize charts to fix Chart.js hidden tab rendering bug
            setTimeout(() => {{
                if (tabId === 'overview') {{
                    if (equityChart) equityChart.resize();
                    if (drawdownChart) drawdownChart.resize();
                }} else if (tabId === 'analysis') {{
                    if (growthChart) growthChart.resize();
                    if (ddProfileChart) ddProfileChart.resize();
                    if (posAmtChart) posAmtChart.resize();
                    if (capUtilChart) capUtilChart.resize();
                    if (rollingKellyChart) rollingKellyChart.resize();
                    if (lotDistChart) lotDistChart.resize();
                    if (pnlDistChart) pnlDistChart.resize();
                }} else if (tabId === 'sizing') {{
                    if (kellyChart) kellyChart.resize();
                    if (lotsChart) lotsChart.resize();
                }}
            }}, 50);
        }}

        function formatCurrency(val) {{
            return '₹' + parseFloat(val).toLocaleString('en-IN', {{
                maximumFractionDigits: 2,
                minimumFractionDigits: 2
            }});
        }}

        function formatPercent(val) {{
            return parseFloat(val).toFixed(2) + '%';
        }}

        function formatPF(val) {{
            return parseFloat(val).toFixed(2);
        }}

        function formatExp(val) {{
            return '₹' + parseFloat(val).toFixed(2);
        }}

        // Backtester engine in Javascript
        function runSimulation(trades, config) {{
            const {{ initialCapital, windowSize, marginModel, fixedMarginVal, applyTaxes, lotSize, maxLotsLimit, forceMin1Lot, originalLotsSource, originalLotsFixedValue, sizingMethod }} = config;
            const strategies = ['original', 'kelly_full', 'kelly_1_2', 'kelly_1_4', 'kelly_1_8', 'kelly_1_4_min_1', 'fixed_1', 'fixed_2'];
            const results = {{}};

            // Pre-resolve Original Strategy Lots array
            const originalLots = [];
            trades.forEach(t => {{
                if (originalLotsSource === 'fixed') {{
                    originalLots.push(originalLotsFixedValue);
                }} else if (originalLotsSource && t[originalLotsSource] !== undefined) {{
                    originalLots.push(parseInt(t[originalLotsSource]) || 1);
                }} else {{
                    originalLots.push(1); // Default fallback
                }}
            }});

            strategies.forEach(strat => {{
                let capital = initialCapital;
                const capHistory = [capital];
                const lotsHistory = [];
                const kellyHistory = [];
                
                let tradesExecuted = 0;
                let tradesSkipped = 0;
                let totalUtilization = 0;
                
                for (let i = 0; i < trades.length; i++) {{
                    const t = trades[i];
                    const entryPrice = parseFloat(t.entry_price);
                    const pnlLot = parseFloat(t.pnl_lot);
                    
                    let kelly = 0;
                    if (i >= windowSize) {{
                        let wins = 0;
                        let losses = 0;
                        let sumWins = 0;
                        let sumLosses = 0;
                        
                        for (let k = i - windowSize; k < i; k++) {{
                            const p = parseFloat(trades[k].pnl_lot);
                            if (p > 0) {{
                                wins++;
                                sumWins += p;
                            }} else if (p < 0) {{
                                losses++;
                                sumLosses += Math.abs(p);
                            }}
                        }}
                        
                        const wRate = wins / windowSize;
                        const avgWin = wins > 0 ? sumWins / wins : 0;
                        const avgLoss = losses > 0 ? sumLosses / losses : 0;
                        
                        if (avgLoss > 0) {{
                            const rRatio = avgWin / avgLoss;
                            kelly = wRate - ((1 - wRate) / rRatio);
                        }} else {{
                            kelly = wRate > 0 ? wRate : 0;
                        }}
                        kelly = Math.max(0, kelly);
                    }}
                    kellyHistory.push(kelly);
                    
                    const requiredMargin = marginModel === 'premium' ? (entryPrice * lotSize) : fixedMarginVal;
                    
                    if (i < windowSize) {{
                        lotsHistory.push(0);
                        capHistory.push(capital);
                        continue;
                    }}
                    
                    let lots = 0;
                    if (strat === 'original') {{
                        lots = originalLots[i];
                        if (lots === 0) tradesSkipped++;
                    }} else if (strat.startsWith('kelly')) {{
                        let fraction = 1.0;
                        if (strat === 'kelly_1_2') fraction = 0.5;
                        else if (strat === 'kelly_1_4' || strat === 'kelly_1_4_min_1') fraction = 0.25;
                        else if (strat === 'kelly_1_8') fraction = 0.125;
                        
                        const allocation = Math.min(kelly * fraction, 0.10);
                        
                        if (sizingMethod === 'risk') {{
                            const slPrice = parseFloat(t.sl_price) || 0.0;
                            const riskPerOption = Math.abs(entryPrice - slPrice);
                            const riskPerLot = riskPerOption * lotSize;
                            const riskAmount = capital * allocation;
                            lots = riskPerLot > 0 ? Math.floor(riskAmount / riskPerLot) : 0;
                        }} else {{
                            const posAmount = capital * allocation;
                            lots = Math.floor(posAmount / requiredMargin);
                        }}
                        
                        lots = Math.min(lots, maxLotsLimit);
                        const isForceMin = forceMin1Lot || (strat === 'kelly_1_4_min_1');
                        if (isForceMin && kelly > 0 && lots === 0 && capital >= requiredMargin) {{
                            lots = 1;
                        }}
                        if (kelly > 0 && lots === 0) {{
                            tradesSkipped++;
                        }}
                    }} else if (strat === 'fixed_1') {{
                        lots = capital >= requiredMargin ? 1 : 0;
                        lots = Math.min(lots, maxLotsLimit);
                        if (lots === 0 && capital < requiredMargin) tradesSkipped++;
                    }} else if (strat === 'fixed_2') {{
                        lots = capital >= (2 * requiredMargin) ? 2 : (capital >= requiredMargin ? 1 : 0);
                        lots = Math.min(lots, maxLotsLimit);
                        if (lots < 2) tradesSkipped++;
                    }}
                    
                    // Capital constraint check
                    const maxLotsAffordable = Math.floor(capital / requiredMargin);
                    if (lots > maxLotsAffordable) {{
                        lots = maxLotsAffordable;
                    }}
                    
                    let tradePnl = pnlLot * lots;
                    if (lots > 0 && applyTaxes) {{
                        tradePnl -= 40;
                    }}
                    
                    capital += tradePnl;
                    if (lots > 0) tradesExecuted++;
                    
                    const utilization = (lots * requiredMargin) / (capital - tradePnl) * 100.0;
                    totalUtilization += isNaN(utilization) || !isFinite(utilization) ? 0 : utilization;
                    
                    lotsHistory.push(lots);
                    capHistory.push(capital);
                }}
                
                results[strat] = {{
                    capitalHistory: capHistory,
                    lotsHistory: lotsHistory,
                    kellyHistory: kellyHistory,
                    originalLotsArray: originalLots, // Save mapped original lots
                    tradesExecuted,
                    tradesSkipped,
                    totalUtilization
                }};
            }});
            
            return results;
        }}

        function calculateMetrics(trades, stratResults, initialCapital, windowSize) {{
            const {{ capitalHistory, lotsHistory, tradesExecuted, tradesSkipped, totalUtilization }} = stratResults;
            const tradedCaps = capitalHistory.slice(windowSize);
            const finalCapital = tradedCaps[tradedCaps.length - 1];
            const totalProfit = finalCapital - initialCapital;
            
            // CAGR
            const startIdx = windowSize;
            const startDate = new Date(trades[startIdx].timestamp);
            const endDate = new Date(trades[trades.length - 1].timestamp);
            const days = Math.round(Math.abs(endDate - startDate) / (1000 * 60 * 60 * 24));
            const years = days / 365.0;
            const cagr = years > 0 && finalCapital > 0 ? (Math.pow(finalCapital / initialCapital, 1.0 / years) - 1.0) * 100.0 : 0.0;
            
            // Drawdown
            let maxDd = 0.0;
            let peak = initialCapital;
            let maxDdCurr = 0.0;
            const ddHistory = [];
            
            for (let i = 0; i < tradedCaps.length; i++) {{
                const cap = tradedCaps[i];
                if (cap > peak) peak = cap;
                const dd = (peak - cap) / peak * 100.0;
                if (dd > maxDd) maxDd = dd;
                
                const ddCurr = peak - cap;
                if (ddCurr > maxDdCurr) maxDdCurr = ddCurr;
                
                ddHistory.push(dd);
            }}
            
            const recoveryFactor = maxDdCurr > 0 ? totalProfit / maxDdCurr : totalProfit;
            
            // Win rate, PF, Expectancy
            let wins = [];
            let losses = [];
            let sumLots = 0;
            let executedCount = 0;
            
            for (let i = startIdx; i < trades.length; i++) {{
                const lots = lotsHistory[i];
                if (lots > 0) {{
                    const pnlLot = parseFloat(trades[i].pnl_lot);
                    const p = pnlLot * lots;
                    if (p > 0) {{
                        wins.push(p);
                    }} else if (p < 0) {{
                        losses.push(p);
                    }}
                    sumLots += lots;
                    executedCount++;
                }}
            }}
            
            const winRate = executedCount > 0 ? (wins.length / executedCount) * 100.0 : 0.0;
            const sumWins = wins.reduce((a, b) => a + b, 0);
            const sumLosses = Math.abs(losses.reduce((a, b) => a + b, 0));
            const profitFactor = sumLosses > 0 ? sumWins / sumLosses : (sumWins > 0 ? sumWins : 0.0);
            
            const avgWin = wins.length > 0 ? sumWins / wins.length : 0.0;
            const avgLoss = losses.length > 0 ? sumLosses / losses.length : 0.0;
            const expectancy = executedCount > 0 ? (winRate/100.0 * avgWin) - ((1.0 - winRate/100.0) * avgLoss) : 0.0;
            
            const avgLotSize = executedCount > 0 ? sumLots / executedCount : 0.0;
            
            const numTradesPeriod = trades.length - windowSize;
            const capitalUtilization = numTradesPeriod > 0 ? totalUtilization / numTradesPeriod : 0.0;
            
            // Best / Worst trade tracking
            let maxWinAmount = 0.0;
            let maxWinDate = '-';
            let maxWinTradeIndex = '-';
            
            let maxLossAmount = 0.0;
            let maxLossDate = '-';
            let maxLossTradeIndex = '-';
            
            for (let i = startIdx; i < trades.length; i++) {{
                const lots = lotsHistory[i];
                if (lots > 0) {{
                    const pnlLot = parseFloat(trades[i].pnl_lot);
                    const p = pnlLot * lots;
                    
                    if (p > maxWinAmount) {{
                        maxWinAmount = p;
                        maxWinDate = trades[i].timestamp.split(' ')[0];
                        maxWinTradeIndex = i + 1;
                    }}
                    if (p < maxLossAmount) {{
                        maxLossAmount = p;
                        maxLossDate = trades[i].timestamp.split(' ')[0];
                        maxLossTradeIndex = i + 1;
                    }}
                }}
            }}
            
            return {{
                metrics: {{
                    totalProfit,
                    finalCapital,
                    cagr,
                    maxDd,
                    winRate,
                    profitFactor,
                    expectancy,
                    recoveryFactor,
                    tradesExecuted,
                    tradesSkipped,
                    avgLotSize,
                    capitalUtilization,
                    
                    // Add best / worst trade details
                    maxWinAmount,
                    maxWinDate,
                    maxWinTradeIndex,
                    maxLossAmount,
                    maxLossDate,
                    maxLossTradeIndex
                }},
                ddHistory
            }};
        }}

        function runSimulationAndUpdateUI() {{
            const initialCapital = parseFloat(document.getElementById('initial-capital').value) || 100000;
            const windowSize = parseInt(document.getElementById('window-size').value) || 100;
            const lotSourceVal = document.getElementById('lot-source').value;
            const fixedLotsVal = parseInt(document.getElementById('fixed-lots-val').value) || 1;
            const marginModel = document.getElementById('margin-model').value;
            const fixedMarginVal = parseFloat(document.getElementById('fixed-margin').value) || 10000;
            const lotSize = parseInt(document.getElementById('lot-size').value) || 65;
            const maxLotsLimit = parseInt(document.getElementById('max-lots-limit').value) || 10;
            const forceMin1Lot = document.getElementById('force-min-1').checked;
            const applyTaxes = document.getElementById('apply-taxes').checked;
            const sizingMethod = document.getElementById('sizing-method').value;

            const config = {{
                initialCapital,
                windowSize,
                marginModel,
                fixedMarginVal,
                applyTaxes,
                lotSize,
                maxLotsLimit,
                forceMin1Lot,
                originalLotsSource: lotSourceVal,
                originalLotsFixedValue: fixedLotsVal,
                sizingMethod
            }};

            // Run simulation on trades
            const simResults = runSimulation(rawTrades, config);
            
            // Calculate metrics for all strategies
            const computedData = {{}};
            const strategies = ['original', 'kelly_full', 'kelly_1_2', 'kelly_1_4', 'kelly_1_8', 'kelly_1_4_min_1', 'fixed_1', 'fixed_2'];
            
            strategies.forEach(strat => {{
                computedData[strat] = calculateMetrics(rawTrades, simResults[strat], initialCapital, windowSize);
            }});

            // Resolve which Kelly strategy is "active" for diagnostics and ledger
            const activeKellyStrat = document.getElementById('active-kelly-strategy').value;
            const activeKellyMetrics = computedData[activeKellyStrat].metrics;
            const origMetrics = computedData['original'].metrics;

            // 1. Update Position Sizing Impact Section
            const profitDiff = activeKellyMetrics.totalProfit - origMetrics.totalProfit;
            const profitImpPct = origMetrics.totalProfit !== 0 ? (profitDiff / Math.abs(origMetrics.totalProfit)) * 100 : 0;
            
            document.getElementById('impact-profit-val').innerText = formatCurrency(profitDiff).split('.')[0];
            document.getElementById('impact-profit-pct').innerText = (profitImpPct >= 0 ? '+' : '') + profitImpPct.toFixed(1) + '%';
            document.getElementById('impact-profit-pct').className = 'impact-pct-badge ' + (profitImpPct >= 0 ? 'positive' : 'negative');
            
            // Drawdown reduction (relative reduction: (orig_dd - strategy_dd) / orig_dd * 100)
            const ddReduction = origMetrics.maxDd > 0 ? ((origMetrics.maxDd - activeKellyMetrics.maxDd) / origMetrics.maxDd) * 100 : 0;
            document.getElementById('impact-dd-val').innerText = activeKellyMetrics.maxDd.toFixed(2) + '%';
            document.getElementById('impact-dd-pct').innerText = (ddReduction >= 0 ? 'Reduced ' : 'Increased ') + ddReduction.toFixed(1) + '%';
            document.getElementById('impact-dd-pct').className = 'impact-pct-badge ' + (ddReduction >= 0 ? 'positive' : 'negative');

            // 2. Update Kelly Diagnostics Panel (for the rolling Kelly values)
            const rollingKellyHistory = simResults['kelly_1_4'].kellyHistory.slice(windowSize);
            const avgKelly = rollingKellyHistory.reduce((a, b) => a + b, 0) / rollingKellyHistory.length * 100;
            const maxKelly = Math.max(...rollingKellyHistory) * 100;
            const minKelly = Math.min(...rollingKellyHistory) * 100;
            
            document.getElementById('diag-avg-kelly').innerText = avgKelly.toFixed(1) + '%';
            document.getElementById('diag-max-kelly').innerText = maxKelly.toFixed(1) + '%';
            document.getElementById('diag-avg-lots').innerText = activeKellyMetrics.avgLotSize.toFixed(2);
            document.getElementById('diag-max-lots').innerText = Math.max(...simResults[activeKellyStrat].lotsHistory.slice(windowSize));
            document.getElementById('diag-trades-ratio').innerText = `${{activeKellyMetrics.tradesExecuted}} Exec / ${{activeKellyMetrics.tradesSkipped}} Skip`;
            document.getElementById('diag-utilization').innerText = activeKellyMetrics.capitalUtilization.toFixed(2) + '%';

            // 3. Update Performance Comparison Table (with Relative Improvements)
            const tbody = document.getElementById('comparison-table-body');
            tbody.innerHTML = '';
            
            const stratDisplayNames = {{
                'original': "Original Strategy",
                'kelly_full': "Kelly (Full Kelly)",
                'kelly_1_2': "Kelly (Half Kelly)",
                'kelly_1_4': "Kelly (1/4 Kelly)",
                'kelly_1_8': "Kelly (1/8 Kelly)",
                'kelly_1_4_min_1': "Kelly (1/4 + Min 1Lot)",
                'fixed_1': "Fixed 1 Lot",
                'fixed_2': "Fixed 2 Lots"
            }};

            strategies.forEach(strat => {{
                const m = computedData[strat].metrics;
                const isHighlight = strat === activeKellyStrat;
                
                // Calculate relative improvements for table row
                let profitImp = 0.0;
                if (origMetrics.totalProfit !== 0) {{
                    profitImp = (m.totalProfit - origMetrics.totalProfit) / Math.abs(origMetrics.totalProfit) * 100.0;
                }}
                
                let ddImp = 0.0;
                if (origMetrics.maxDd > 0) {{
                    ddImp = (origMetrics.maxDd - m.maxDd) / origMetrics.maxDd * 100.0;
                }}
                
                const row = document.createElement('tr');
                if (isHighlight) row.className = 'highlight';
                
                row.innerHTML = `
                    <td class="strategy-name">${{stratDisplayNames[strat]}}</td>
                    <td class="${{m.totalProfit >= 0 ? 'positive' : 'negative'}}">${{formatCurrency(m.totalProfit)}}</td>
                    <td>${{formatCurrency(m.finalCapital)}}</td>
                    <td class="${{m.cagr >= 0 ? 'positive' : 'negative'}}">${{formatPercent(m.cagr)}}</td>
                    <td class="negative">${{formatPercent(m.maxDd)}}</td>
                    <td>${{formatPercent(m.winRate)}}</td>
                    <td>${{formatPF(m.profitFactor)}}</td>
                    <td class="${{m.expectancy >= 0 ? 'positive' : 'neutral'}}">${{formatExp(m.expectancy)}}</td>
                    <td>${{formatPF(m.recoveryFactor)}}</td>
                    <td>${{m.tradesExecuted}}</td>
                    <td class="${{m.tradesSkipped > 0 ? 'negative' : 'neutral'}}">${{m.tradesSkipped}}</td>
                    <td>${{m.avgLotSize.toFixed(2)}}</td>
                    <td>${{formatPercent(m.capitalUtilization)}}</td>
                    <td class="${{profitImp >= 0 ? 'positive' : 'negative'}}">${{strat === 'original' ? '-' : (profitImp >= 0 ? '+' : '') + profitImp.toFixed(2) + '%'}}</td>
                    <td class="${{ddImp >= 0 ? 'positive' : 'negative'}}">${{strat === 'original' ? '-' : (ddImp >= 0 ? '+' : '') + ddImp.toFixed(2) + '%'}}</td>
                `;
                tbody.appendChild(row);
            }});

            // ==========================================
            // ITERATION 3: NEW TAB CALCULATIONS & RENDERERS
            // ==========================================
            const f1Metrics = computedData['fixed_1'].metrics;
            const kfMetrics = computedData['kelly_full'].metrics;
            const kqMetrics = computedData['kelly_1_4'].metrics;
            
            // 1. KPI Cards Grid: Without vs With Sizing
            document.getElementById('kpi-f1-start').innerText = formatCurrency(initialCapital).split('.')[0];
            document.getElementById('kpi-f1-final').innerText = formatCurrency(f1Metrics.finalCapital).split('.')[0];
            document.getElementById('kpi-f1-profit').innerText = formatCurrency(f1Metrics.totalProfit).split('.')[0];
            document.getElementById('kpi-f1-profit').className = f1Metrics.totalProfit >= 0 ? 'diag-val positive' : 'diag-val negative';
            document.getElementById('kpi-f1-cagr').innerText = formatPercent(f1Metrics.cagr);
            document.getElementById('kpi-f1-dd').innerText = formatPercent(f1Metrics.maxDd);
            document.getElementById('kpi-f1-pf').innerText = formatPF(f1Metrics.profitFactor);
            document.getElementById('kpi-f1-rf').innerText = formatPF(f1Metrics.recoveryFactor);
            document.getElementById('kpi-f1-exp').innerText = formatCurrency(f1Metrics.expectancy).split('.')[0];
            document.getElementById('kpi-f1-wr').innerText = formatPercent(f1Metrics.winRate);

            document.getElementById('kpi-kf-start').innerText = formatCurrency(initialCapital).split('.')[0];
            document.getElementById('kpi-kf-final').innerText = formatCurrency(kfMetrics.finalCapital).split('.')[0];
            document.getElementById('kpi-kf-profit').innerText = formatCurrency(kfMetrics.totalProfit).split('.')[0];
            document.getElementById('kpi-kf-profit').className = kfMetrics.totalProfit >= 0 ? 'diag-val positive' : 'diag-val negative';
            document.getElementById('kpi-kf-cagr').innerText = formatPercent(kfMetrics.cagr);
            document.getElementById('kpi-kf-dd').innerText = formatPercent(kfMetrics.maxDd);
            document.getElementById('kpi-kf-pf').innerText = formatPF(kfMetrics.profitFactor);
            document.getElementById('kpi-kf-rf').innerText = formatPF(kfMetrics.recoveryFactor);
            document.getElementById('kpi-kf-exp').innerText = formatCurrency(kfMetrics.expectancy).split('.')[0];
            document.getElementById('kpi-kf-wr').innerText = formatPercent(kfMetrics.winRate);

            document.getElementById('kpi-kq-start').innerText = formatCurrency(initialCapital).split('.')[0];
            document.getElementById('kpi-kq-final').innerText = formatCurrency(kqMetrics.finalCapital).split('.')[0];
            document.getElementById('kpi-kq-profit').innerText = formatCurrency(kqMetrics.totalProfit).split('.')[0];
            document.getElementById('kpi-kq-profit').className = kqMetrics.totalProfit >= 0 ? 'diag-val positive' : 'diag-val negative';
            document.getElementById('kpi-kq-cagr').innerText = formatPercent(kqMetrics.cagr);
            document.getElementById('kpi-kq-dd').innerText = formatPercent(kqMetrics.maxDd);
            document.getElementById('kpi-kq-pf').innerText = formatPF(kqMetrics.profitFactor);
            document.getElementById('kpi-kq-rf').innerText = formatPF(kqMetrics.recoveryFactor);
            document.getElementById('kpi-kq-exp').innerText = formatCurrency(kqMetrics.expectancy).split('.')[0];
            document.getElementById('kpi-kq-wr').innerText = formatPercent(kqMetrics.winRate);

            // 2. Relative Sizing Improvements (Full Kelly)
            const kfProfitImpVal = f1Metrics.totalProfit !== 0 ? ((kfMetrics.totalProfit - f1Metrics.totalProfit) / Math.abs(f1Metrics.totalProfit)) * 100.0 : 0.0;
            const kfCagrImpVal = kfMetrics.cagr - f1Metrics.cagr;
            const kfDdImpVal = f1Metrics.maxDd - kfMetrics.maxDd;
            const kfRfImpVal = kfMetrics.recoveryFactor - f1Metrics.recoveryFactor;
            const kfPfImpVal = kfMetrics.profitFactor - f1Metrics.profitFactor;
            
            const impKfProfitEl = document.getElementById('imp-kf-profit');
            impKfProfitEl.innerText = (kfProfitImpVal >= 0 ? '+' : '') + kfProfitImpVal.toFixed(2) + '%';
            impKfProfitEl.className = kfProfitImpVal >= 0 ? 'positive' : 'negative';
            
            const impKfCagrEl = document.getElementById('imp-kf-cagr');
            impKfCagrEl.innerText = (kfCagrImpVal >= 0 ? '+' : '') + kfCagrImpVal.toFixed(2) + '%';
            impKfCagrEl.className = kfCagrImpVal >= 0 ? 'positive' : 'negative';
            
            const impKfDdEl = document.getElementById('imp-kf-dd');
            impKfDdEl.innerText = (kfDdImpVal >= 0 ? '+' : '-') + kfDdImpVal.toFixed(2) + '%';
            impKfDdEl.className = kfDdImpVal >= 0 ? 'positive' : 'negative';
            
            const impKfRfEl = document.getElementById('imp-kf-rf');
            impKfRfEl.innerText = (kfRfImpVal >= 0 ? '+' : '') + kfRfImpVal.toFixed(2);
            impKfRfEl.className = kfRfImpVal >= 0 ? 'positive' : 'negative';
            
            const impKfPfEl = document.getElementById('imp-kf-pf');
            impKfPfEl.innerText = (kfPfImpVal >= 0 ? '+' : '') + kfPfImpVal.toFixed(2);
            impKfPfEl.className = kfPfImpVal >= 0 ? 'positive' : 'negative';

            // 3. Relative Sizing Improvements (Quarter Kelly)
            const kqProfitImpVal = f1Metrics.totalProfit !== 0 ? ((kqMetrics.totalProfit - f1Metrics.totalProfit) / Math.abs(f1Metrics.totalProfit)) * 100.0 : 0.0;
            const kqCagrImpVal = kqMetrics.cagr - f1Metrics.cagr;
            const kqDdImpVal = f1Metrics.maxDd - kqMetrics.maxDd;
            const kqRfImpVal = kqMetrics.recoveryFactor - f1Metrics.recoveryFactor;
            const kqPfImpVal = kqMetrics.profitFactor - f1Metrics.profitFactor;
            
            const impKqProfitEl = document.getElementById('imp-kq-profit');
            impKqProfitEl.innerText = (kqProfitImpVal >= 0 ? '+' : '') + kqProfitImpVal.toFixed(2) + '%';
            impKqProfitEl.className = kqProfitImpVal >= 0 ? 'positive' : 'negative';
            
            const impKqCagrEl = document.getElementById('imp-kq-cagr');
            impKqCagrEl.innerText = (kqCagrImpVal >= 0 ? '+' : '') + kqCagrImpVal.toFixed(2) + '%';
            impKqCagrEl.className = kqCagrImpVal >= 0 ? 'positive' : 'negative';
            
            const impKqDdEl = document.getElementById('imp-kq-dd');
            impKqDdEl.innerText = (kqDdImpVal >= 0 ? '+' : '-') + kqDdImpVal.toFixed(2) + '%';
            impKqDdEl.className = kqDdImpVal >= 0 ? 'positive' : 'negative';
            
            const impKqRfEl = document.getElementById('imp-kq-rf');
            impKqRfEl.innerText = (kqRfImpVal >= 0 ? '+' : '') + kqRfImpVal.toFixed(2);
            impKqRfEl.className = kqRfImpVal >= 0 ? 'positive' : 'negative';
            
            const impKqPfEl = document.getElementById('imp-kq-pf');
            impKqPfEl.innerText = (kqPfImpVal >= 0 ? '+' : '') + kqPfImpVal.toFixed(2);
            impKqPfEl.className = kqPfImpVal >= 0 ? 'positive' : 'negative';

            // 4. Verdicts
            const verdictTextKfEl = document.getElementById('verdict-text-kf');
            const verdictCardKfEl = document.getElementById('verdict-card-kf');
            if (kfMetrics.totalProfit > f1Metrics.totalProfit) {{
                verdictTextKfEl.innerText = "Full Kelly Outperformed";
                verdictTextKfEl.style.color = "var(--success)";
                verdictCardKfEl.style.border = "1px solid rgba(16, 185, 129, 0.3)";
                verdictCardKfEl.style.background = "rgba(16, 185, 129, 0.04)";
                document.getElementById('verdict-desc-kf').innerText = "Full Kelly sizing outperformed Fixed 1 Lot";
            }} else {{
                verdictTextKfEl.innerText = "Full Kelly Underperformed";
                verdictTextKfEl.style.color = "var(--danger)";
                verdictCardKfEl.style.border = "1px solid rgba(239, 68, 68, 0.3)";
                verdictCardKfEl.style.background = "rgba(239, 68, 68, 0.04)";
                document.getElementById('verdict-desc-kf').innerText = "Fixed 1 Lot outperformed Full Kelly sizing";
            }}

            const verdictTextKqEl = document.getElementById('verdict-text-kq');
            const verdictCardKqEl = document.getElementById('verdict-card-kq');
            if (kqMetrics.totalProfit > f1Metrics.totalProfit) {{
                verdictTextKqEl.innerText = "1/4 Kelly Outperformed";
                verdictTextKqEl.style.color = "var(--success)";
                verdictCardKqEl.style.border = "1px solid rgba(16, 185, 129, 0.3)";
                verdictCardKqEl.style.background = "rgba(16, 185, 129, 0.04)";
                document.getElementById('verdict-desc-kq').innerText = "1/4 Kelly sizing outperformed Fixed 1 Lot";
            }} else {{
                verdictTextKqEl.innerText = "1/4 Kelly Underperformed";
                verdictTextKqEl.style.color = "var(--danger)";
                verdictCardKqEl.style.border = "1px solid rgba(239, 68, 68, 0.3)";
                verdictCardKqEl.style.background = "rgba(239, 68, 68, 0.04)";
                document.getElementById('verdict-desc-kq').innerText = "Fixed 1 Lot outperformed 1/4 Kelly sizing";
            }}

            // 3. Best / Worst Trades Comparison
            const bwTableBody = document.getElementById('best-worst-table-body');
            bwTableBody.innerHTML = '';
            const bwStrats = ['fixed_1', 'fixed_2', 'kelly_full', 'kelly_1_2', 'kelly_1_4', 'kelly_1_8', 'original'];
            const bwDisplayNames = {{
                'fixed_1': 'Fixed 1 Lot',
                'fixed_2': 'Fixed 2 Lots',
                'kelly_full': 'Full Kelly',
                'kelly_1_2': 'Half Kelly',
                'kelly_1_4': 'Kelly Quarter',
                'kelly_1_8': 'Kelly Eighth',
                'original': 'Original Strategy'
            }};
            bwStrats.forEach(strat => {{
                const m = computedData[strat].metrics;
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td style="font-weight: 700; color: #fff;">${{bwDisplayNames[strat]}}</td>
                    <td>Trade #${{m.maxWinTradeIndex}}</td>
                    <td>${{m.maxWinDate}}</td>
                    <td class="positive" style="font-weight: 600;">${{formatCurrency(m.maxWinAmount)}}</td>
                    <td>Trade #${{m.maxLossTradeIndex}}</td>
                    <td>${{m.maxLossDate}}</td>
                    <td class="negative" style="font-weight: 600;">${{formatCurrency(m.maxLossAmount)}}</td>
                `;
                bwTableBody.appendChild(row);
            }});

            // 4. Sizing Stats
            const rollingKelly = simResults['kelly_1_4'].kellyHistory.slice(windowSize);
            const avgKellyVal = rollingKelly.reduce((a, b) => a + b, 0) / rollingKelly.length * 100.0;
            const maxKellyVal = Math.max(...rollingKelly) * 100.0;
            const minKellyVal = Math.min(...rollingKelly) * 100.0;
            
            const posAmounts = [];
            const activeLotsSizing = simResults[activeKellyStrat].lotsHistory.slice(windowSize);
            const activeCapSizing = simResults[activeKellyStrat].capitalHistory.slice(windowSize);
            for (let i = 0; i < rollingKelly.length; i++) {{
                const kelly = rollingKelly[i];
                const cap = activeCapSizing[i];
                const allocation = Math.min(kelly / 4.0, 0.10);
                posAmounts.push(cap * allocation);
            }}
            const avgPosAmt = posAmounts.reduce((a, b) => a + b, 0) / posAmounts.length;
            const maxPosAmt = Math.max(...posAmounts);
            const minPosAmt = Math.min(...posAmounts);
            
            const activeLotsTraded = activeLotsSizing.filter(l => l > 0);
            const avgLotsVal = activeLotsTraded.length > 0 ? activeLotsTraded.reduce((a, b) => a + b, 0) / activeLotsTraded.length : 0.0;
            const maxLotsVal = Math.max(...activeLotsSizing);
            const minLotsVal = activeLotsSizing.length > 0 ? Math.min(...activeLotsSizing) : 0;
            
            document.getElementById('stats-avg-kelly').innerText = avgKellyVal.toFixed(1) + '%';
            document.getElementById('stats-max-kelly').innerText = maxKellyVal.toFixed(1) + '%';
            document.getElementById('stats-min-kelly').innerText = minKellyVal.toFixed(1) + '%';
            document.getElementById('stats-avg-pos-amt').innerText = formatCurrency(avgPosAmt).split('.')[0];
            document.getElementById('stats-max-pos-amt').innerText = formatCurrency(maxPosAmt).split('.')[0];
            document.getElementById('stats-min-pos-amt').innerText = formatCurrency(minPosAmt).split('.')[0];
            document.getElementById('stats-avg-lots').innerText = avgLotsVal.toFixed(2);
            document.getElementById('stats-max-lots').innerText = maxLotsVal;
            document.getElementById('stats-min-lots').innerText = minLotsVal;

            // 5. Capital Utilizations & Margin stats
            const marginsUsed = [];
            const utilsPct = [];
            let skipKelly = 0;
            let skipCap = 0;
            let cappedLotsCount = 0;
            let totalHoldingMins = 0;
            let holdingCount = 0;
            
            for (let i = windowSize; i < rawTrades.length; i++) {{
                const t = rawTrades[i];
                const lots = simResults[activeKellyStrat].lotsHistory[i];
                const requiredMargin = marginModel === 'premium' ? (parseFloat(t.entry_price) * lotSize) : fixedMarginVal;
                
                marginsUsed.push(lots * requiredMargin);
                
                const kelly = simResults['kelly_1_4'].kellyHistory[i];
                const allocation = Math.min(kelly / 4.0, 0.10);
                utilsPct.push(allocation * 100.0);
                
                // Diagnostics skips
                if (kelly === 0 && lots === 0) {{
                    skipKelly++;
                }} else if (kelly > 0 && lots === 0) {{
                    if (simResults[activeKellyStrat].capitalHistory[i] < requiredMargin) {{
                        skipCap++;
                    }}
                }}
                
                // Capped lots
                if (lots > 0) {{
                    const calculatedLots = Math.floor((simResults[activeKellyStrat].capitalHistory[i] * allocation) / requiredMargin);
                    if (calculatedLots > maxLotsLimit && lots === maxLotsLimit) {{
                        cappedLotsCount++;
                    }}
                    
                    if (t.holding_mins !== undefined) {{
                        totalHoldingMins += t.holding_mins;
                        holdingCount++;
                    }}
                }}
            }}
            const avgMarginUsed = marginsUsed.length > 0 ? marginsUsed.reduce((a, b) => a + b, 0) / marginsUsed.length : 0.0;
            const maxMarginUsed = marginsUsed.length > 0 ? Math.max(...marginsUsed) : 0.0;
            const minMarginUsed = marginsUsed.length > 0 ? Math.min(...marginsUsed) : 0.0;
            const avgUtilPct = utilsPct.reduce((a, b) => a + b, 0) / utilsPct.length;
            const avgHoldingTime = holdingCount > 0 ? totalHoldingMins / holdingCount : 0.0;

            document.getElementById('util-avg-pct').innerText = avgUtilPct.toFixed(1) + '%';
            document.getElementById('util-avg-margin').innerText = formatCurrency(avgMarginUsed).split('.')[0];
            document.getElementById('util-max-margin').innerText = formatCurrency(maxMarginUsed).split('.')[0];
            document.getElementById('util-min-margin').innerText = formatCurrency(minMarginUsed).split('.')[0];

            // 6. Option performance split
            let ceCount = 0;
            let ceWins = 0;
            let ceProfit = 0.0;
            let peCount = 0;
            let peWins = 0;
            let peProfit = 0.0;
            const activeLots = simResults[activeKellyStrat].lotsHistory;
            for (let i = windowSize; i < rawTrades.length; i++) {{
                const lots = activeLots[i];
                if (lots > 0) {{
                    const t = rawTrades[i];
                    const p = parseFloat(t.pnl_lot) * lots;
                    if (t.option_type === 'CE') {{
                        ceCount++;
                        if (p > 0) ceWins++;
                        ceProfit += p;
                    }} else if (t.option_type === 'PE') {{
                        peCount++;
                        if (p > 0) peWins++;
                        peProfit += p;
                    }}
                }}
            }}
            const ceWr = ceCount > 0 ? (ceWins / ceCount) * 100.0 : 0.0;
            const ceAvg = ceCount > 0 ? ceProfit / ceCount : 0.0;
            const peWr = peCount > 0 ? (peWins / peCount) * 100.0 : 0.0;
            const peAvg = peCount > 0 ? peProfit / peCount : 0.0;

            document.getElementById('ce-count').innerText = ceCount;
            document.getElementById('ce-wr').innerText = ceWr.toFixed(1) + '%';
            document.getElementById('ce-profit').innerText = formatCurrency(ceProfit).split('.')[0];
            document.getElementById('ce-profit').className = ceProfit >= 0 ? 'positive' : 'negative';
            document.getElementById('ce-avg-profit').innerText = formatCurrency(ceAvg).split('.')[0];
            document.getElementById('ce-avg-profit').className = ceAvg >= 0 ? 'positive' : 'negative';
            
            document.getElementById('pe-count').innerText = peCount;
            document.getElementById('pe-wr').innerText = peWr.toFixed(1) + '%';
            document.getElementById('pe-profit').innerText = formatCurrency(peProfit).split('.')[0];
            document.getElementById('pe-profit').className = peProfit >= 0 ? 'positive' : 'negative';
            document.getElementById('pe-avg-profit').innerText = formatCurrency(peAvg).split('.')[0];
            document.getElementById('pe-avg-profit').className = peAvg >= 0 ? 'positive' : 'negative';

            // 7. Diagnostics
            document.getElementById('diag-period-trades').innerText = rawTrades.length - windowSize;
            document.getElementById('diag-period-exec').innerText = activeKellyMetrics.tradesExecuted;
            document.getElementById('diag-period-skip').innerText = activeKellyMetrics.tradesSkipped;
            document.getElementById('diag-skip-kelly').innerText = skipKelly;
            document.getElementById('diag-skip-cap').innerText = skipCap;
            document.getElementById('diag-capped-lots').innerText = cappedLotsCount;
            document.getElementById('diag-period-holding').innerText = avgHoldingTime.toFixed(1) + ' mins';

            // 8. Position Sizing Summary Table
            const summaryTableBody = document.getElementById('sizing-summary-table-body');
            summaryTableBody.innerHTML = '';
            const metricsList = [
                {{ name: 'Starting Capital', key: 'initialCapital', format: formatCurrency }},
                {{ name: 'Final Capital', key: 'finalCapital', format: formatCurrency }},
                {{ name: 'Total Profit', key: 'totalProfit', format: formatCurrency }},
                {{ name: 'CAGR', key: 'cagr', format: formatPercent }},
                {{ name: 'Maximum Drawdown', key: 'maxDd', format: formatPercent }},
                {{ name: 'Profit Factor', key: 'profitFactor', format: formatPF }},
                {{ name: 'Recovery Factor', key: 'recoveryFactor', format: formatPF }},
                {{ name: 'Expectancy', key: 'expectancy', format: formatExp }},
                {{ name: 'Win Rate', key: 'winRate', format: formatPercent }}
            ];
            const summaryStrats = ['fixed_1', 'fixed_2', 'kelly_full', 'kelly_1_2', 'kelly_1_4', 'kelly_1_8'];
            metricsList.forEach(m => {{
                const row = document.createElement('tr');
                let cellHtml = `<td style="font-weight: 600;">${{m.name}}</td>`;
                summaryStrats.forEach(strat => {{
                    let val = computedData[strat].metrics[m.key];
                    if (m.key === 'initialCapital') {{
                        val = initialCapital;
                    }}
                    cellHtml += `<td>${{m.format(val)}}</td>`;
                }});
                row.innerHTML = cellHtml;
                summaryTableBody.appendChild(row);
            }});

            // 4. Update Charts (incorporating Original Strategy)
            try {{
                updateCharts(rawTrades, simResults, computedData, windowSize);
            }} catch (e) {{
                console.warn("Chart.js failed to load or render (expected if offline):", e);
            }}

            // 5. Update Detailed Ledger data list (Mapping both Full and 1/4 Kelly side-by-side)
            filteredTrades = rawTrades.map((t, idx) => {{
                const requiredMargin = marginModel === 'premium' ? (parseFloat(t.entry_price) * lotSize) : fixedMarginVal;
                const kelly = simResults['kelly_full']['kellyHistory'][idx];
                
                const entryPrice = parseFloat(t.entry_price) || 0.0;
                const slPrice = parseFloat(t.sl_price) || 0.0;
                const riskPerOption = Math.abs(entryPrice - slPrice);
                const riskPerLot = riskPerOption * lotSize;
                
                // Full Kelly calculations
                const fkAllocPct = Math.min(kelly * 1.0, 0.10);
                const fkCapBefore = simResults['kelly_full']['capitalHistory'][idx];
                const fkRiskAmt = fkCapBefore * fkAllocPct;
                const fkLots = simResults['kelly_full']['lotsHistory'][idx];
                const fkTradePnL = fkLots * t.pnl_lot;
                const fkCapAfter = simResults['kelly_full']['capitalHistory'][idx + 1];
                const fkMarginUsed = fkLots * requiredMargin;
                const fkCapUtil = fkCapBefore > 0 ? (fkMarginUsed / fkCapBefore) * 100.0 : 0.0;
                
                // Quarter Kelly calculations
                const qkAllocPct = Math.min(kelly * 0.25, 0.10);
                const qkCapBefore = simResults['kelly_1_4']['capitalHistory'][idx];
                const qkRiskAmt = qkCapBefore * qkAllocPct;
                const qkLots = simResults['kelly_1_4']['lotsHistory'][idx];
                const qkTradePnL = qkLots * t.pnl_lot;
                const qkCapAfter = simResults['kelly_1_4']['capitalHistory'][idx + 1];
                const qkMarginUsed = qkLots * requiredMargin;
                const qkCapUtil = qkCapBefore > 0 ? (qkMarginUsed / qkCapBefore) * 100.0 : 0.0;
                
                return {{
                    tradeIndex: idx + 1,
                    timestamp: t.timestamp,
                    entry_signal: t.entry_signal,
                    option_type: t.option_type || '-',
                    strike_price: t.strike_price || '-',
                    entry_price: entryPrice,
                    sl_price: slPrice,
                    exit_price: parseFloat(t.exit_price) || 0.0,
                    pnl_lot: t.pnl_lot,
                    exit_reason: t.exit_reason || '-',
                    
                    // Windows boundaries
                    window_start: t.window_start,
                    window_end: t.window_end,
                    
                    // Rolling params
                    win_rate: t.win_rate,
                    avg_win: t.avg_win,
                    avg_loss: t.avg_loss,
                    r_ratio: t.r_ratio,
                    
                    kelly: kelly,
                    riskPerOption: riskPerOption,
                    riskPerLot: riskPerLot,
                    marginPerLot: requiredMargin,
                    
                    // Full Kelly Strategy Sizing properties
                    fkAllocPct: fkAllocPct,
                    fkRiskAmt: fkRiskAmt,
                    fkLots: fkLots,
                    fkTradePnL: fkTradePnL,
                    fkCapBefore: fkCapBefore,
                    fkCapAfter: fkCapAfter,
                    fkCapUtil: fkCapUtil,
                    
                    // Quarter Kelly Strategy Sizing properties
                    qkAllocPct: qkAllocPct,
                    qkRiskAmt: qkRiskAmt,
                    qkLots: qkLots,
                    qkTradePnL: qkTradePnL,
                    qkCapBefore: qkCapBefore,
                    qkCapAfter: qkCapAfter,
                    qkCapUtil: qkCapUtil
                }};
            }}).slice(windowSize); // Align out-of-sample
 
            currentPage = 1;
            renderLedgerTable();
        }}

        function renderLedgerTable() {{
            const tbody = document.getElementById('ledger-table-body');
            tbody.innerHTML = '';
            
            const searchVal = document.getElementById('search-input').value.toLowerCase();
            let displayTrades = filteredTrades;
            
            if (searchVal) {{
                displayTrades = filteredTrades.filter(t => {{
                    return t.entry_signal.toLowerCase().includes(searchVal) ||
                           t.window_start.toLowerCase().includes(searchVal) ||
                           t.window_end.toLowerCase().includes(searchVal);
                }});
            }}

            const totalPages = Math.max(1, Math.ceil(displayTrades.length / pageSize));
            if (currentPage > totalPages) currentPage = totalPages;
            
            document.getElementById('pagination-info').innerText = `Page ${{currentPage}} of ${{totalPages}}`;
            document.getElementById('prev-btn').disabled = currentPage === 1;
            document.getElementById('next-btn').disabled = currentPage === totalPages;

            const start = (currentPage - 1) * pageSize;
            const end = start + pageSize;
            const pageTrades = displayTrades.slice(start, end);

            pageTrades.forEach(t => {{
                const row = document.createElement('tr');
                const typeClass = t.option_type === 'CE' ? 'badge-buy' : 'badge-sell';
                
                row.innerHTML = `
                    <td>${{t.tradeIndex}}</td>
                    <td>${{t.timestamp.split(' ')[0]}}<br><span style="color: var(--text-muted); font-size: 0.72rem;">${{t.timestamp.split(' ')[1] || '09:15:00'}}</span></td>
                    <td><span class="badge ${{typeClass}}">${{t.option_type}}</span></td>
                    <td>₹${{t.entry_price.toFixed(2)}}</td>
                    <td>₹${{t.sl_price.toFixed(2)}}</td>
                    <td style="border-right: 1px solid var(--border);">₹${{t.exit_price.toFixed(2)}}</td>
                    <td class="${{t.pnl_lot >= 0 ? 'positive' : 'negative'}}">₹${{t.pnl_lot.toFixed(2)}}</td>
                    <td>${{(t.win_rate * 100).toFixed(1)}}%</td>
                    <td class="positive">₹${{t.avg_win.toFixed(2)}}</td>
                    <td class="negative">₹${{t.avg_loss.toFixed(2)}}</td>
                    <td>${{t.r_ratio.toFixed(2)}}</td>
                    <td>${{(t.kelly * 100).toFixed(1)}}%</td>
                    <td>₹${{t.riskPerOption.toFixed(2)}}</td>
                    <td style="border-right: 1px solid var(--border);">₹${{t.riskPerLot.toFixed(2)}}</td>
                    
                    <!-- Full Kelly Strategy Sizing columns -->
                    <td>${{(t.fkAllocPct * 100).toFixed(1)}}%</td>
                    <td>${{formatCurrency(t.fkRiskAmt).split('.')[0]}}</td>
                    <td style="font-weight: 600; color: #fff;">${{t.fkLots}}</td>
                    <td class="${{t.fkTradePnL >= 0 ? 'positive' : 'negative'}}" style="font-weight: 600;">₹${{t.fkTradePnL.toFixed(2)}}</td>
                    <td style="font-weight: 600;">${{formatCurrency(t.fkCapBefore).split('.')[0]}}</td>
                    <td style="border-right: 1px solid var(--border); font-weight: 600; color: var(--accent-secondary);">${{t.fkCapUtil.toFixed(1)}}%</td>
                    
                    <!-- 1/4 Kelly Strategy Sizing columns -->
                    <td>${{(t.qkAllocPct * 100).toFixed(1)}}%</td>
                    <td>${{formatCurrency(t.qkRiskAmt).split('.')[0]}}</td>
                    <td style="font-weight: 600; color: #fff;">${{t.qkLots}}</td>
                    <td class="${{t.qkTradePnL >= 0 ? 'positive' : 'negative'}}" style="font-weight: 600;">₹${{t.qkTradePnL.toFixed(2)}}</td>
                    <td style="font-weight: 600;">${{formatCurrency(t.qkCapBefore).split('.')[0]}}</td>
                    <td style="border-right: 1px solid var(--border); font-weight: 600; color: var(--success);">${{t.qkCapUtil.toFixed(1)}}%</td>
                    
                    <td class="window-boundary">${{t.window_start}}</td>
                    <td class="window-boundary">${{t.window_end}}</td>
                    <td><span style="font-size: 0.72rem; color: var(--text-muted);">${{t.exit_reason}}</span></td>
                `;
                tbody.appendChild(row);
            }});
        }}

        function onSearchChange() {{
            currentPage = 1;
            renderLedgerTable();
        }}

        function prevPage() {{
            if (currentPage > 1) {{
                currentPage--;
                renderLedgerTable();
            }}
        }}

        function nextPage() {{
            currentPage++;
            renderLedgerTable();
        }}

        function updateCharts(trades, simResults, computedData, windowSize) {{
            const timestamps = trades.slice(windowSize).map(t => t.timestamp.split(' ')[0]);
            
            const strategyColors = {{
                'original': '#ec4899', // Pink for Original Strategy
                'kelly_full': '#f43f5e', // Rose
                'kelly_1_2': '#14b8a6',  // Teal
                'kelly_1_4': '#6366f1',
                'kelly_1_8': '#3b82f6',
                'kelly_1_4_min_1': '#a855f7',
                'fixed_1': '#10b981',
                'fixed_2': '#f59e0b'
            }};

            const strategyLabels = {{
                'original': 'Original Strategy (Actual)',
                'kelly_full': 'Kelly (Full Kelly)',
                'kelly_1_2': 'Kelly (Half Kelly)',
                'kelly_1_4': 'Kelly (1/4 Kelly)',
                'kelly_1_8': 'Kelly (1/8 Kelly)',
                'kelly_1_4_min_1': 'Kelly (1/4 + Min 1Lot)',
                'fixed_1': 'Fixed 1 Lot',
                'fixed_2': 'Fixed 2 Lots'
            }};

            const activeKellyStrat = document.getElementById('active-kelly-strategy').value;

            const equityDatasets = [];
            const drawdownDatasets = [];
            const lotsDatasets = [];
            
            const strats = ['original', 'kelly_full', 'kelly_1_2', 'kelly_1_4', 'kelly_1_8', 'kelly_1_4_min_1', 'fixed_1', 'fixed_2'];
            
            strats.forEach(strat => {{
                const capHist = simResults[strat].capitalHistory.slice(windowSize + 1);
                const ddHist = computedData[strat].ddHistory;
                const lotsHist = simResults[strat].lotsHistory.slice(windowSize);
                
                equityDatasets.push({{
                    label: strategyLabels[strat],
                    data: capHist,
                    borderColor: strategyColors[strat],
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.1
                }});

                drawdownDatasets.push({{
                    label: strategyLabels[strat],
                    data: ddHist,
                    borderColor: strategyColors[strat],
                    backgroundColor: 'transparent',
                    borderWidth: 1.5,
                    pointRadius: 0,
                    tension: 0.1
                }});

                lotsDatasets.push({{
                    label: strategyLabels[strat],
                    data: lotsHist,
                    borderColor: strategyColors[strat],
                    backgroundColor: strategyColors[strat] + '20',
                    borderWidth: 1.5,
                    pointRadius: 0,
                    tension: 0.1,
                    hidden: strat !== activeKellyStrat && strat !== 'original' // Show active Kelly & Original
                }});
            }});

            const kellyHistory = simResults['kelly_1_4'].kellyHistory.slice(windowSize).map(k => k * 100.0);

            // 1. Equity Chart
            if (equityChart) equityChart.destroy();
            const ctxEquity = document.getElementById('equityChart').getContext('2d');
            equityChart = new Chart(ctxEquity, {{
                type: 'line',
                data: {{ labels: timestamps, datasets: equityDatasets }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        x: {{ grid: {{ color: 'rgba(255,255,255,0.03)' }}, ticks: {{ color: '#9ca3af' }} }},
                        y: {{ grid: {{ color: 'rgba(255,255,255,0.03)' }}, ticks: {{ color: '#9ca3af' }} }}
                    }},
                    plugins: {{
                        legend: {{ labels: {{ color: '#f3f4f6', font: {{ family: 'Outfit', weight: 600 }} }} }}
                    }}
                }}
            }});

            // 2. Drawdown Chart
            if (drawdownChart) drawdownChart.destroy();
            const ctxDrawdown = document.getElementById('drawdownChart').getContext('2d');
            drawdownChart = new Chart(ctxDrawdown, {{
                type: 'line',
                data: {{ labels: timestamps, datasets: drawdownDatasets }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        x: {{ grid: {{ color: 'rgba(255,255,255,0.03)' }}, ticks: {{ color: '#9ca3af' }} }},
                        y: {{ grid: {{ color: 'rgba(255,255,255,0.03)' }}, ticks: {{ color: '#9ca3af' }}, reverse: true }}
                    }},
                    plugins: {{
                        legend: {{ labels: {{ color: '#f3f4f6', font: {{ family: 'Outfit', weight: 600 }} }} }}
                    }}
                }}
            }});

            // 3. Kelly Chart
            if (kellyChart) kellyChart.destroy();
            const ctxKelly = document.getElementById('kellyChart').getContext('2d');
            kellyChart = new Chart(ctxKelly, {{
                type: 'line',
                data: {{
                    labels: timestamps,
                    datasets: [{{
                        label: 'Rolling Kelly %',
                        data: kellyHistory,
                        borderColor: '#8b5cf6',
                        backgroundColor: 'rgba(139, 92, 246, 0.1)',
                        borderWidth: 2,
                        pointRadius: 0,
                        fill: true,
                        tension: 0.1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        x: {{ grid: {{ color: 'rgba(255,255,255,0.03)' }}, ticks: {{ color: '#9ca3af' }} }},
                        y: {{ grid: {{ color: 'rgba(255,255,255,0.03)' }}, ticks: {{ color: '#9ca3af' }}, min: 0 }}
                    }},
                    plugins: {{
                        legend: {{ labels: {{ color: '#f3f4f6', font: {{ family: 'Outfit', weight: 600 }} }} }}
                    }}
                }}
            }});

            // 4. Lots Chart
            if (lotsChart) lotsChart.destroy();
            const ctxLots = document.getElementById('lotsChart').getContext('2d');
            lotsChart = new Chart(ctxLots, {{
                type: 'line',
                data: {{ labels: timestamps, datasets: lotsDatasets }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        x: {{ grid: {{ color: 'rgba(255,255,255,0.03)' }}, ticks: {{ color: '#9ca3af' }} }},
                        y: {{ grid: {{ color: 'rgba(255,255,255,0.03)' }}, ticks: {{ color: '#9ca3af' }}, min: 0 }}
                    }},
                    plugins: {{
                        legend: {{ labels: {{ color: '#f3f4f6', font: {{ family: 'Outfit', weight: 600 }} }} }}
                    }}
                }}
            }});

            // RENDER TAB 3 (ANALYSIS TAB) - 7 NEW CHARTS
            // 1. growthChart
            if (growthChart) growthChart.destroy();
            const ctxGrowth = document.getElementById('growthChart').getContext('2d');
            growthChart = new Chart(ctxGrowth, {{
                type: 'line',
                data: {{
                    labels: timestamps,
                    datasets: [
                        equityDatasets.find(d => d.label.includes('Fixed 1 Lot')),
                        equityDatasets.find(d => d.label.includes('Fixed 2 Lots')),
                        equityDatasets.find(d => d.label.includes('Full Kelly')),
                        equityDatasets.find(d => d.label.includes('Half Kelly')),
                        equityDatasets.find(d => d.label.includes('1/4 Kelly')),
                        equityDatasets.find(d => d.label.includes('1/8 Kelly')),
                        equityDatasets.find(d => d.label.includes('Original Strategy'))
                    ].filter(Boolean)
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        x: {{ grid: {{ color: 'rgba(255,255,255,0.03)' }}, ticks: {{ color: '#9ca3af' }} }},
                        y: {{ grid: {{ color: 'rgba(255,255,255,0.03)' }}, ticks: {{ color: '#9ca3af' }} }}
                    }},
                    plugins: {{
                        legend: {{ labels: {{ color: '#f3f4f6', font: {{ family: 'Outfit', weight: 600 }} }} }}
                    }}
                }}
            }});

            // 2. ddProfileChart
            if (ddProfileChart) ddProfileChart.destroy();
            const ctxDdProfile = document.getElementById('ddProfileChart').getContext('2d');
            ddProfileChart = new Chart(ctxDdProfile, {{
                type: 'line',
                data: {{
                    labels: timestamps,
                    datasets: [
                        drawdownDatasets.find(d => d.label.includes('Fixed 1 Lot')),
                        drawdownDatasets.find(d => d.label.includes('Fixed 2 Lots')),
                        drawdownDatasets.find(d => d.label.includes('Full Kelly')),
                        drawdownDatasets.find(d => d.label.includes('Half Kelly')),
                        drawdownDatasets.find(d => d.label.includes('1/4 Kelly')),
                        drawdownDatasets.find(d => d.label.includes('1/8 Kelly')),
                        drawdownDatasets.find(d => d.label.includes('Original Strategy'))
                    ].filter(Boolean)
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        x: {{ grid: {{ color: 'rgba(255,255,255,0.03)' }}, ticks: {{ color: '#9ca3af' }} }},
                        y: {{ grid: {{ color: 'rgba(255,255,255,0.03)' }}, ticks: {{ color: '#9ca3af' }}, reverse: true }}
                    }},
                    plugins: {{
                        legend: {{ labels: {{ color: '#f3f4f6', font: {{ family: 'Outfit', weight: 600 }} }} }}
                    }}
                }}
            }});

            // 3. posAmtChart
            const posAmtData = [];
            const activeCapHistory = simResults[activeKellyStrat].capitalHistory;
            const activeKellyHistory = simResults[activeKellyStrat].kellyHistory;
            
            // Resolve fraction for active Kelly strategy
            let activeFraction = 1.0;
            if (activeKellyStrat === 'kelly_1_2') activeFraction = 0.5;
            else if (activeKellyStrat === 'kelly_1_4' || activeKellyStrat === 'kelly_1_4_min_1') activeFraction = 0.25;
            else if (activeKellyStrat === 'kelly_1_8') activeFraction = 0.125;
            else if (activeKellyStrat === 'original' || activeKellyStrat === 'fixed_1' || activeKellyStrat === 'fixed_2') activeFraction = 0.0;

            for (let i = windowSize; i < trades.length; i++) {{
                const kelly = activeKellyHistory[i];
                const cap = activeCapHistory[i];
                const allocation = Math.min(kelly * activeFraction, 0.10);
                posAmtData.push(cap * allocation);
            }}
            if (posAmtChart) posAmtChart.destroy();
            const ctxPosAmt = document.getElementById('posAmtChart').getContext('2d');
            posAmtChart = new Chart(ctxPosAmt, {{
                type: 'line',
                data: {{
                    labels: timestamps,
                    datasets: [{{
                        label: `Active Kelly Position Sizing Amount (₹) - ${{strategyLabels[activeKellyStrat]}}`,
                        data: posAmtData,
                        borderColor: '#8b5cf6',
                        backgroundColor: 'rgba(139, 92, 246, 0.15)',
                        borderWidth: 2,
                        pointRadius: 0,
                        fill: true,
                        tension: 0.1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        x: {{ grid: {{ color: 'rgba(255,255,255,0.03)' }}, ticks: {{ color: '#9ca3af' }} }},
                        y: {{ grid: {{ color: 'rgba(255,255,255,0.03)' }}, ticks: {{ color: '#9ca3af' }}, min: 0 }}
                    }},
                    plugins: {{
                        legend: {{ labels: {{ color: '#f3f4f6', font: {{ family: 'Outfit', weight: 600 }} }} }}
                    }}
                }}
            }});

            // 4. capUtilChart
            const capUtilData = activeKellyHistory.slice(windowSize).map(k => Math.min(k * activeFraction, 0.10) * 100.0);
            if (capUtilChart) capUtilChart.destroy();
            const ctxCapUtil = document.getElementById('capUtilChart').getContext('2d');
            capUtilChart = new Chart(ctxCapUtil, {{
                type: 'line',
                data: {{
                    labels: timestamps,
                    datasets: [{{
                        label: `Capital Utilization % - ${{strategyLabels[activeKellyStrat]}}`,
                        data: capUtilData,
                        borderColor: '#6366f1',
                        backgroundColor: 'rgba(99, 102, 241, 0.15)',
                        borderWidth: 2,
                        pointRadius: 0,
                        fill: true,
                        tension: 0.1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        x: {{ grid: {{ color: 'rgba(255,255,255,0.03)' }}, ticks: {{ color: '#9ca3af' }} }},
                        y: {{ grid: {{ color: 'rgba(255,255,255,0.03)' }}, ticks: {{ color: '#9ca3af' }}, min: 0, max: 10.5 }}
                    }},
                    plugins: {{
                        legend: {{ labels: {{ color: '#f3f4f6', font: {{ family: 'Outfit', weight: 600 }} }} }}
                    }}
                }}
            }});

            // 5. rollingKellyChart
            if (rollingKellyChart) rollingKellyChart.destroy();
            const ctxRollingKelly = document.getElementById('rollingKellyChart').getContext('2d');
            rollingKellyChart = new Chart(ctxRollingKelly, {{
                type: 'line',
                data: {{
                    labels: timestamps,
                    datasets: [{{
                        label: 'Rolling Kelly Edge %',
                        data: kellyHistory,
                        borderColor: '#f472b6',
                        backgroundColor: 'rgba(244, 114, 182, 0.1)',
                        borderWidth: 2,
                        pointRadius: 0,
                        fill: true,
                        tension: 0.1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        x: {{ grid: {{ color: 'rgba(255,255,255,0.03)' }}, ticks: {{ color: '#9ca3af' }} }},
                        y: {{ grid: {{ color: 'rgba(255,255,255,0.03)' }}, ticks: {{ color: '#9ca3af' }}, min: 0 }}
                    }},
                    plugins: {{
                        legend: {{ labels: {{ color: '#f3f4f6', font: {{ family: 'Outfit', weight: 600 }} }} }}
                    }}
                }}
            }});

            // 6. lotDistChart
            const activeLotsSizing = simResults[activeKellyStrat].lotsHistory.slice(windowSize);
            const lotCounts = {{}};
            activeLotsSizing.forEach(l => {{
                lotCounts[l] = (lotCounts[l] || 0) + 1;
            }});
            const uniqueLots = Object.keys(lotCounts).map(Number).sort((a, b) => a - b);
            const lotFrequencies = uniqueLots.map(l => lotCounts[l]);

            if (lotDistChart) lotDistChart.destroy();
            const ctxLotDist = document.getElementById('lotDistChart').getContext('2d');
            lotDistChart = new Chart(ctxLotDist, {{
                type: 'bar',
                data: {{
                    labels: uniqueLots.map(l => `${{l}} Lot${{l !== 1 ? 's' : ''}}`),
                    datasets: [{{
                        label: 'Trade Frequency Count',
                        data: lotFrequencies,
                        backgroundColor: 'rgba(99, 102, 241, 0.55)',
                        borderColor: '#6366f1',
                        borderWidth: 1.5,
                        borderRadius: 4
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        x: {{ grid: {{ color: 'rgba(255,255,255,0.03)' }}, ticks: {{ color: '#9ca3af' }} }},
                        y: {{ grid: {{ color: 'rgba(255,255,255,0.03)' }}, ticks: {{ color: '#9ca3af' }}, min: 0 }}
                    }},
                    plugins: {{
                        legend: {{ labels: {{ color: '#f3f4f6', font: {{ family: 'Outfit', weight: 600 }} }} }}
                    }}
                }}
            }});

            // 7. pnlDistChart
            const activePnL = [];
            for (let i = windowSize; i < trades.length; i++) {{
                const lots = simResults[activeKellyStrat].lotsHistory[i];
                if (lots > 0) {{
                    activePnL.push(parseFloat(trades[i].pnl_lot) * lots);
                }}
            }}
            let minP = Math.min(...activePnL);
            let maxP = Math.max(...activePnL);
            if (activePnL.length === 0) {{
                minP = -1000;
                maxP = 1000;
            }}
            const binCount = 10;
            const binSize = (maxP - minP) / binCount;
            const bins = Array(binCount).fill(0);
            const binLabels = [];
            for (let b = 0; b < binCount; b++) {{
                const start = minP + b * binSize;
                const end = start + binSize;
                binLabels.push(`₹${{Math.round(start)}} to ₹${{Math.round(end)}}`);
            }}
            activePnL.forEach(p => {{
                let bIdx = Math.floor((p - minP) / binSize);
                if (bIdx >= binCount) bIdx = binCount - 1;
                if (bIdx < 0) bIdx = 0;
                bins[bIdx]++;
            }});
            const binColors = binLabels.map((lbl, idx) => {{
                const centerVal = minP + (idx + 0.5) * binSize;
                return centerVal >= 0 ? 'rgba(16, 185, 129, 0.55)' : 'rgba(239, 68, 68, 0.55)';
            }});
            const binBorderColors = binLabels.map((lbl, idx) => {{
                const centerVal = minP + (idx + 0.5) * binSize;
                return centerVal >= 0 ? '#10b981' : '#ef4444';
            }});

            if (pnlDistChart) pnlDistChart.destroy();
            const ctxPnlDist = document.getElementById('pnlDistChart').getContext('2d');
            pnlDistChart = new Chart(ctxPnlDist, {{
                type: 'bar',
                data: {{
                    labels: binLabels,
                    datasets: [{{
                        label: 'Number of Trades',
                        data: bins,
                        backgroundColor: binColors,
                        borderColor: binBorderColors,
                        borderWidth: 1.5,
                        borderRadius: 4
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        x: {{ grid: {{ color: 'rgba(255,255,255,0.03)' }}, ticks: {{ color: '#9ca3af' }} }},
                        y: {{ grid: {{ color: 'rgba(255,255,255,0.03)' }}, ticks: {{ color: '#9ca3af' }}, min: 0 }}
                    }},
                    plugins: {{
                        legend: {{ labels: {{ color: '#f3f4f6', font: {{ family: 'Outfit', weight: 600 }} }} }}
                    }}
                }}
            }});
        }}

        // Run on Startup
        runSimulationAndUpdateUI();
    </script>
</body>
</html>
"""
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"HTML dashboard generated successfully at: {html_path}")

if __name__ == '__main__':
    main()
