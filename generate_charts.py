import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def generate_outputs():
    workspace = '/Users/keyan/Documents/DS_TASK'
    output_dir = os.path.join(workspace, 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    df = pd.read_csv(os.path.join(workspace, 'segmented_data.csv'))
    display_df = df[df['sentiment_group'].isin(['Fear', 'Greed'])]
    
    sns.set_theme(style="whitegrid")
    
    # 1. Bar Chart: Win Rate vs Sentiment
    plt.figure(figsize=(8, 6))
    win_rate_plot = sns.barplot(data=display_df, x='sentiment_group', y='win_rate', errorbar=None, palette='viridis')
    plt.title('Mean Win Rate by Sentiment Regime', fontsize=14)
    plt.ylabel('Win Rate (%)')
    plt.xlabel('Sentiment Group')
    plt.savefig(os.path.join(output_dir, 'win_rate_by_sentiment.png'), dpi=300)
    plt.close()
    
    # 2. Boxplot: Trades per Day vs Sentiment
    plt.figure(figsize=(8, 6))
    box_plot = sns.boxplot(data=display_df, x='sentiment_group', y='trades_per_day', palette='magma')
    plt.title('Trades per Day vs Sentiment (Log Scale)', fontsize=14)
    plt.ylabel('Trades per Day')
    plt.xlabel('Sentiment Group')
    plt.yscale('log')
    plt.savefig(os.path.join(output_dir, 'trades_freq_by_sentiment.png'), dpi=300)
    plt.close()
    
    # 3. Histogram: Leverage Distribution
    plt.figure(figsize=(10, 6))
    hist_plot = sns.histplot(data=display_df, x='leverage_proxy', hue='sentiment_group', element="step", stat="density", common_norm=False, bins=20)
    plt.title('Leverage Proxy Distribution by Sentiment', fontsize=14)
    plt.ylabel('Density')
    plt.xlabel('Leverage Proxy')
    plt.savefig(os.path.join(output_dir, 'leverage_distribution.png'), dpi=300)
    plt.close()
    
    # 4. Save segments summary table
    summary_table = display_df.groupby(['segment', 'sentiment_group']).agg({
        'win_rate': 'mean',
        'trades_per_day': 'mean',
        'leverage_proxy': 'mean',
        'Closed PnL': 'mean'
    }).round(4).reset_index()
    
    summary_table.to_csv(os.path.join(output_dir, 'segments_summary.csv'), index=False)
    print("Static output charts and tables generated successfully in 'output/' directory.")

if __name__ == "__main__":
    generate_outputs()
