import pandas as pd
import numpy as np
import os

def audit_data(df, name):
    print(f"--- Data Audit: {name} ---")
    print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    missing_pct = df.isnull().mean() * 100
    missing = missing_pct[missing_pct > 0]
    if len(missing) > 0:
        print("Missing Values %:")
        print(missing)
    else:
        print("Missing Values %: None")
    
    # Try to calculate duplicates if data allows
    try:
        duplicates = df.duplicated().sum()
        print(f"Duplicate Rows: {duplicates}\n")
    except Exception as e:
        print(f"Could not calculate duplicates: {e}\n")
        
    return df.drop_duplicates()

def process_data():
    workspace = '/Users/keyan/Documents/DS_TASK'
    fgi_path = os.path.join(workspace, 'fear_greed_index.csv')
    trades_path = os.path.join(workspace, 'historical_data.csv')
    
    # 1. Load Data & Audit
    fgi = pd.read_csv(fgi_path)
    trades = pd.read_csv(trades_path)

    fgi = audit_data(fgi, "Fear & Greed Index")
    trades = audit_data(trades, "Historical Trades")

    print("Key columns for merging will be 'date' from FGI and a derived 'date' string (YYYY-MM-DD) from the Historical Trades 'Timestamp'.\n")

    # 2. Timestamp Conversion
    print("Converting timestamps to datetime...")
    # Convert 'Timestamp' from milliseconds to UTC datetime
    trades['datetime_utc'] = pd.to_datetime(trades['Timestamp'], unit='ms', errors='coerce', utc=True)
    
    # We can also fall back to 'Timestamp IST' if Timestamp is invalid for some rows
    ist_mask = trades['datetime_utc'].isna()
    if ist_mask.sum() > 0:
        print(f"Found {ist_mask.sum()} invalid ms timestamps, attempting parse of Timestamp IST...")
        # IST is UTC+5:30. '02-12-2024 22:50'
        trades.loc[ist_mask, 'datetime_utc'] = pd.to_datetime(trades.loc[ist_mask, 'Timestamp IST'], format='%d-%m-%Y %H:%M', errors='coerce').dt.tz_localize('Asia/Kolkata').dt.tz_convert('UTC')

    trades = trades.dropna(subset=['datetime_utc'])
    trades['date'] = trades['datetime_utc'].dt.strftime('%Y-%m-%d')
    
    # Convert string columns to numeric
    for col in ['Size USD', 'Closed PnL', 'Execution Price']:
        if trades[col].dtype == object:
            trades[col] = pd.to_numeric(trades[col].astype(str).str.replace(',', ''), errors='coerce')
        trades[col] = trades[col].fillna(0)

    # 3. Create Key Metrics per Trader per Day
    print("Computing metrics...")
    # Win Rate
    trades_with_pnl = trades[trades['Closed PnL'] != 0].copy()
    trades_with_pnl['is_win'] = (trades_with_pnl['Closed PnL'] > 0).astype(int)
    win_rate_df = trades_with_pnl.groupby(['Account', 'date'])['is_win'].agg(['mean', 'count']).reset_index()
    win_rate_df.rename(columns={'mean': 'win_rate', 'count': 'pnl_trades'}, inplace=True)
    
    # Average Trade Size & Trades per day
    size_df = trades.groupby(['Account', 'date']).agg(
        avg_trade_size=('Size USD', 'mean'),
        trades_per_day=('Size USD', 'count'),
        total_volume=('Size USD', 'sum')
    ).reset_index()
    
    # Long/Short Ratio
    buys = trades[trades['Side'] == 'BUY'].groupby(['Account', 'date'])['Size USD'].sum().reset_index(name='buy_vol')
    sells = trades[trades['Side'] == 'SELL'].groupby(['Account', 'date'])['Size USD'].sum().reset_index(name='sell_vol')
    ls_df = pd.merge(buys, sells, on=['Account', 'date'], how='outer').fillna(0)
    ls_df['ls_ratio'] = ls_df['buy_vol'] / (ls_df['sell_vol'] + 1e-9)

    # Daily PnL
    daily_pnl = trades.groupby(['Account', 'date'])['Closed PnL'].sum().reset_index()

    # Merge metrics
    metrics = size_df.merge(win_rate_df, on=['Account', 'date'], how='left')
    metrics = metrics.merge(daily_pnl, on=['Account', 'date'], how='left')
    metrics = metrics.merge(ls_df[['Account', 'date', 'ls_ratio']], on=['Account', 'date'], how='left')
    
    # Missing win rates imply 0 pnl trades in that day
    metrics['win_rate'] = metrics['win_rate'].fillna(0)
    metrics['pnl_trades'] = metrics['pnl_trades'].fillna(0)

    # Leverage proxy based on Account max size
    max_size_df = trades.groupby(['Account'])['Size USD'].max().reset_index(name='account_max_size')
    metrics = metrics.merge(max_size_df, on='Account', how='left')
    metrics['leverage_proxy'] = metrics['avg_trade_size'] / (metrics['account_max_size'] + 1e-9)

    # 4. Alignment
    print("Aligning with Fear & Greed Index...")
    fgi['date'] = pd.to_datetime(fgi['date']).dt.strftime('%Y-%m-%d')
    
    merged_data = pd.merge(metrics, fgi[['date', 'value', 'classification']], on='date', how='inner')
    merged_data.rename(columns={'value': 'fgi_value', 'classification': 'fgi_classification'}, inplace=True)

    # Data Integrity Checks post merge
    print("--- Integrity Validation ---")
    dates_in_trades = metrics['date'].nunique()
    dates_in_merged = merged_data['date'].nunique()
    print(f"Dates in trades: {dates_in_trades}, Dates in merged data: {dates_in_merged}")
    if dates_in_merged == 0:
        print("WARNING: Merge failed! Dates do not match. Let's inspect the dates:")
        print("FGI Dates:", fgi['date'].unique()[:5])
        print("Trade Dates:", metrics['date'].unique()[:5])
    else:
        print("Merge successful!")

    # 5. Drawdown Proxy
    print("Calculating Drawdown proxy...")
    merged_data = merged_data.sort_values(['Account', 'date'])
    merged_data['cum_pnl'] = merged_data.groupby('Account')['Closed PnL'].cumsum()
    merged_data['cum_max'] = merged_data.groupby('Account')['cum_pnl'].cummax()
    merged_data['drawdown'] = merged_data['cum_pnl'] - merged_data['cum_max']
    
    print("Data processing complete. Saving to 'processed_data.csv'...")
    output_path = os.path.join(workspace, 'processed_data.csv')
    merged_data.to_csv(output_path, index=False)
    print(f"Output saved to {output_path}")

if __name__ == "__main__":
    process_data()
