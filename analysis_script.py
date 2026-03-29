import pandas as pd
import numpy as np
from scipy import stats
import os

def analyze():
    workspace = '/Users/keyan/Documents/DS_TASK'
    df = pd.read_csv(os.path.join(workspace, 'processed_data.csv'))
    
    print(f"Loaded records: {len(df)}")
    
    # 1. Segmentation
    # Calculate account-level average traits
    account_stats = df.groupby('Account').agg({
        'trades_per_day': 'mean',
        'leverage_proxy': 'mean'
    }).reset_index()

    # Define segments based on medians
    med_trades = account_stats['trades_per_day'].median()
    med_lev = account_stats['leverage_proxy'].median()

    def determine_segment(row):
        if row['trades_per_day'] > med_trades and row['leverage_proxy'] > med_lev:
            return 'High-Freq & High-Leverage'
        elif row['trades_per_day'] <= med_trades and row['leverage_proxy'] <= med_lev:
            return 'Low-Freq & Low-Leverage'
        elif row['trades_per_day'] > med_trades:
            return 'High-Freq & Low-Leverage'
        else:
            return 'Low-Freq & High-Leverage'

    account_stats['segment'] = account_stats.apply(determine_segment, axis=1)
    df = df.merge(account_stats[['Account', 'segment']], on='Account', how='left')

    # Add a simplified sentiment group for comparison: Fear vs Greed (ignore Neutral for test)
    # The FGI classification is typically 'Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed'
    df['sentiment_group'] = df['fgi_classification'].replace({
        'Extreme Fear': 'Fear',
        'Extreme Greed': 'Greed'
    })

    # Save segmented data
    df.to_csv(os.path.join(workspace, 'segmented_data.csv'), index=False)

    print("\n--- Trader Segments Overview ---")
    print(account_stats['segment'].value_counts())

    print("\n--- Sentiment Groups available ---")
    print(df['sentiment_group'].value_counts())

    # 2. Statistical Validation (T-Tests)
    # Compare Fear vs Greed for key metrics across the whole population
    metrics_to_test = ['Closed PnL', 'win_rate', 'drawdown', 'trades_per_day', 'leverage_proxy', 'ls_ratio']
    
    fear_df = df[df['sentiment_group'] == 'Fear']
    greed_df = df[df['sentiment_group'] == 'Greed']
    
    print(f"\n--- Statistical Tests (Fear vs Greed) ---")
    print(f"Fear count: {len(fear_df)}, Greed count: {len(greed_df)}")
    
    if len(fear_df) > 0 and len(greed_df) > 0:
        for m in metrics_to_test:
            f_vals = fear_df[m].dropna()
            g_vals = greed_df[m].dropna()
            
            if len(f_vals) > 1 and len(g_vals) > 1:
                stat, p = stats.ttest_ind(f_vals, g_vals, equal_var=False)
                print(f"Metric: {m:<15} | Fear Mean: {f_vals.mean():.4f} | Greed Mean: {g_vals.mean():.4f} | p-value: {p:.4f}")
                if p < 0.05:
                    print(f"  -> SIGNIFICANT difference found in {m}.")
            else:
                print(f"Not enough data to test {m}")

    # Grouped analysis to spot specific insight opportunities
    print("\n--- Segment & Sentiment Behavior ---")
    pivot = df.groupby(['segment', 'sentiment_group'])[metrics_to_test].mean().round(4)
    print(pivot)

if __name__ == "__main__":
    analyze()
