import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

print("Loading data...")
# 1. Data Loading & Cleaning
fear_greed_file = '/Users/keyan/Documents/DS_TASK/fear_greed_index.csv'
hist_file = '/Users/keyan/Documents/DS_TASK/historical_data.csv'

fg_df = pd.read_csv(fear_greed_file)
# fear_greed_index dates are like '2018-02-01'
fg_df['date'] = pd.to_datetime(fg_df['date'])

trades_df = pd.read_csv(hist_file)
# historical_data timestamps are '02-12-2024 22:50'
trades_df['Timestamp IST'] = pd.to_datetime(trades_df['Timestamp IST'], format='%d-%m-%Y %H:%M', errors='coerce')
trades_df['date'] = trades_df['Timestamp IST'].dt.floor('D')

print("Merging data...")
# Merge
df = pd.merge(trades_df, fg_df, on='date', how='inner')

# Add missing columns if they exist under slightly different names
if 'Leverage' not in df.columns:
    lever_cols = [c for c in df.columns if 'lever' in c.lower()]
    if lever_cols:
        df['Leverage'] = df[lever_cols[0]]
    else:
        df['Leverage'] = np.nan

df['Closed PnL'] = pd.to_numeric(df['Closed PnL'], errors='coerce').fillna(0)
df['Size USD'] = pd.to_numeric(df['Size USD'], errors='coerce').fillna(0)

# Is Profitable trade
# Assuming a trade is explicitly "closed" or has a PnL element to be profitable
# 'Closed PnL' > 0 means a win. 
# Some rows might literally have 0 PnL, we can count them as non-wins or neutral. We'll count >0 as win.
df['is_profitable'] = df['Closed PnL'] > 0

# Market Sentiment string normalization
df['classification'] = df['classification'].astype(str).str.strip()

output_md = "/Users/keyan/Documents/DS_TASK/trading_sentiment_insights.md"

print("Generating insights...")
with open(output_md, 'w') as f:
    f.write("# Trading Performance vs. Market Sentiment Insights\n\n")

    # 1. Performance Normalization
    f.write("## 1. Performance Normalization\n")
    perf_by_sentiment = df.groupby('classification').agg(
        total_trades=('Account', 'count'),  # Use 'Account' count since Trade ID could be null or non-unique depending on definition
        avg_pnl=('Closed PnL', 'mean'),
        win_rate=('is_profitable', 'mean'),
        total_volume=('Size USD', 'sum')
    ).reset_index()
    f.write(perf_by_sentiment.to_markdown(index=False) + "\n\n")
    
    # Plot Win Rate by Sentiment
    plt.figure(figsize=(10, 6))
    sns.barplot(data=perf_by_sentiment, x='classification', y='win_rate', order=['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed'])
    plt.title("Win Rate by Market Sentiment")
    plt.savefig("/Users/keyan/Documents/DS_TASK/win_rate_by_sentiment.png")
    plt.close()
    
    # Plot Avg PnL
    plt.figure(figsize=(10, 6))
    sns.barplot(data=perf_by_sentiment, x='classification', y='avg_pnl', order=['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed'])
    plt.title("Average PnL by Market Sentiment")
    plt.savefig("/Users/keyan/Documents/DS_TASK/avg_pnl_by_sentiment.png")
    plt.close()

    # 2. Trader-Level Analysis
    f.write("## 2. Trader-Level Analysis\n")
    f.write("Performance of top 5 traders by volume across sentiments:\n")
    # Top 5 traders by volume
    top_traders = df.groupby('Account')['Size USD'].sum().nlargest(5).index
    trader_perf = df[df['Account'].isin(top_traders)].groupby(['Account', 'classification']).agg(
        avg_pnl=('Closed PnL', 'mean'),
        win_rate=('is_profitable', 'mean')
    ).reset_index()
    f.write(trader_perf.to_markdown(index=False) + "\n\n")

    # 3. Leverage Impact Analysis
    f.write("## 3. Leverage Impact Analysis\n")
    if df['Leverage'].notna().any():
        lev_perf = df.groupby('classification').agg(
            avg_leverage=('Leverage', 'mean'),
            max_leverage=('Leverage', 'max')
        ).reset_index()
        f.write(lev_perf.to_markdown(index=False) + "\n\n")
    else:
        f.write("*Note: Leverage parsing was not explicitly available natively in the dataset columns. Estimating risk via trade sizes vs PnL variance instead.* \n\n")
        
    # 4. Time-Based Analysis
    f.write("## 4. Time-Based Analysis (Sentiment Shifts)\n")
    # Sentiment shifts should only be calculated day over day, independent of trades
    # But since we have trades, we sort by date. 
    daily_sent = df[['date', 'classification']].drop_duplicates().sort_values('date')
    daily_sent['prev_sentiment'] = daily_sent['classification'].shift(1)
    daily_sent['sentiment_shift'] = daily_sent['prev_sentiment'] + " -> " + daily_sent['classification']
    
    # Merge back to df to get the shift for the current trade's date
    df = pd.merge(df, daily_sent[['date', 'sentiment_shift', 'prev_sentiment']], on='date', how='left')
    
    # only care where shift actually happened
    shifts = df[df['prev_sentiment'] != df['classification']]
    if not shifts.empty:
        shift_perf = shifts.groupby('sentiment_shift').agg(
            avg_pnl=('Closed PnL', 'mean'),
            win_rate=('is_profitable', 'mean'),
            shift_count=('Account', 'count')
        ).reset_index()
        # Filter for significant shifts
        shift_perf = shift_perf[shift_perf['shift_count'] > 10].sort_values('avg_pnl', ascending=False)
        f.write("Performance during days when sentiment shifted:\n")
        f.write(shift_perf.head(10).to_markdown(index=False) + "\n\n")
    else:
        f.write("Not enough sentiment shift data intersecting with the trading timeframe.\n\n")

    # 5. Risk Metrics
    f.write("## 5. Risk Metrics\n")
    risk_metrics = df.groupby('classification').agg(
        pnl_variance=('Closed PnL', 'var'),
        max_loss=('Closed PnL', 'min'),
        downside_exposure=('Closed PnL', lambda x: x[x < 0].sum())
    ).reset_index()
    f.write(risk_metrics.to_markdown(index=False) + "\n\n")

    # 6. Strategy Extraction
    f.write("## 6. Strategy Extraction\n")
    f.write("Based on the data observed, the following patterns can be translated into actionable strategies:\n\n")
    
    if not perf_by_sentiment.empty:
        best_wr_sentiment = perf_by_sentiment.loc[perf_by_sentiment['win_rate'].idxmax()]
        worst_wr_sentiment = perf_by_sentiment.loc[perf_by_sentiment['win_rate'].idxmin()]
        
        f.write(f"- **Primary Trend**: Trading during `{best_wr_sentiment['classification']}` yields the highest win probability ({best_wr_sentiment['win_rate']:.2%}). "
                f"Conversely, `{worst_wr_sentiment['classification']}` periods are the most risky ({worst_wr_sentiment['win_rate']:.2%}).\n")
    
    # Evaluate long vs short
    if 'Side' in df.columns:
        side_perf = df.groupby(['classification', 'Side']).agg(win_rate=('is_profitable', 'mean'), avg_pnl=('Closed PnL', 'mean')).reset_index()
        for sentiment in perf_by_sentiment['classification'].unique():
            sub = side_perf[side_perf['classification'] == sentiment]
            if len(sub) >= 2:
                best_side = sub.loc[sub['win_rate'].idxmax()]
                f.write(f"- In **{sentiment}**, going `{best_side['Side']}` is statistically more profitable (Win Rate: {best_side['win_rate']:.2%}).\n")
            elif len(sub) == 1:
                f.write(f"- In **{sentiment}**, trades were primarily `{sub.iloc[0]['Side']}` (Win Rate: {sub.iloc[0]['win_rate']:.2%}).\n")
                
    f.write("\n### Recommendations:\n")
    f.write("1. Scale up positions during high win-rate sentiments and avoid overtrading when market sentiment enters the highest variance states.\n")
    f.write("2. Adopt directional biases confirmed by the Side-based Win Rate analysis during specific sentiments.\n")
    f.write("3. Manage downside actively during shifted sentiment periods.\n")

print("Analysis completed successfully. Output saved to:", output_md)
