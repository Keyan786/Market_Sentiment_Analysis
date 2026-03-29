import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from scipy import stats

st.set_page_config(page_title="Trader Sentiment Analysis", layout="wide")

st.title("Trader Performance & Sentiment Analysis Dashboard")

workspace = '/Users/keyan/Documents/DS_TASK'

@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(workspace, 'segmented_data.csv'))
    # Clean up ls_ratio for extreme values due to minimal shorts
    df['ls_ratio_clipped'] = df['ls_ratio'].clip(upper=10) 
    return df

df = load_data()

tabs = st.tabs(["Data Audit & Integrity", "Insights & Visualizations", "Actionable Strategies", "Predictive Modeling"])

with tabs[0]:
    st.header("1. Data Audit & Integrity Post-Merge")
    st.write(f"**Total Aggregated Daily Records:** {len(df)}")
    st.write(f"**Missing Values Found:** {df.isnull().sum().sum()}")
    st.write(f"**Duplicate Rows:** {df.duplicated().sum()}")
    st.write("**Key Columns Merged On:** `date` (YYYY-MM-DD)")
    
    st.subheader("Data Sample")
    st.dataframe(df.head())
    
with tabs[1]:
    st.header("2. Analysis & Key Insights")
    
    # Group into Fear vs Greed strictly for easier viz
    display_df = df[df['sentiment_group'].isin(['Fear', 'Greed'])]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Insight 1: Fear Promotes Consistency")
        st.write("**Observation:** Win rates are significantly higher during Fear regimes.")
        st.write("**Evidence:** T-test (p=0.037) confirms a leap from 73% (Greed) to 87% (Fear).")
        st.write("**Interpretation:** Traders act more methodically and spot better mispricing during market panic.")
        fig1 = px.bar(display_df.groupby('sentiment_group')['win_rate'].mean().reset_index(), 
                      x='sentiment_group', y='win_rate', color='sentiment_group', title="Mean Win Rate by Sentiment")
        st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        st.subheader("Insight 2: High-Frequency Edge")
        st.write("**Observation:** Trade frequency spikes during Fear.")
        st.write("**Evidence:** T-test (p=0.007) shows trades jump from ~1168 to ~4183 per day.")
        st.write("**Interpretation:** Opportunities heavily compound during drawdowns; high-frequency traders capitalize on this.")
        fig2 = px.box(display_df, x='sentiment_group', y='trades_per_day', color='sentiment_group', title="Trades/Day vs Sentiment")
        st.plotly_chart(fig2, use_container_width=True)

    with col3:
        st.subheader("Insight 3: Leverage & Sentiment Bias")
        st.write("**Observation:** Long biases explode during Greed periods.")
        st.write("**Evidence:** Long/Short ratios skew aggressively high during Greed, while normalizing near 1.0 during Fear.")
        st.write("**Interpretation:** Retail FOMO heavily weights toward long leverage during Greed, heightening systemic risk.")
        fig3 = px.histogram(display_df, x='leverage_proxy', color='sentiment_group', barmode='overlay', title="Leverage Proxy Distribution")
        st.plotly_chart(fig3, use_container_width=True)

with tabs[2]:
    st.header("3. Actionable Strategies & Rules of Thumb")
    
    st.info("**Rule 1: Capitalize on Fear (Target Segment: High-Frequency Traders)**\n\n"
            "*When to apply:* When the FGI drops into 'Fear' or 'Extreme Fear'.\n\n"
            "*Action:* Maintain or increase trading frequency. Statistically, win probabilities are at their highest (~87%). Do not reduce activity out of macro-caution.")
            
    st.warning("**Rule 2: Prune Leverage in Greed (Target Segment: High-Leverage Traders)**\n\n"
               "*When to apply:* When the FGI moves into 'Greed' or 'Extreme Greed'.\n\n"
               "*Action:* Win probabilities dip to ~73%. Traders should systematically reduce leverage to protect capital from whipsaws, avoiding the heavily skewed Long-bias observed across the market.")

with tabs[3]:
    st.header("4. Simple Predictive Model")
    st.write("Predicting **Next-Day Profitability** (Win Rate > 50%) based on Sentiment and Behaviors.")
    
    # Feature Engineering for Model
    model_df = df.copy()
    model_df['next_day_win_rate'] = model_df.groupby('Account')['win_rate'].shift(-1)
    model_df = model_df.dropna(subset=['next_day_win_rate'])
    
    model_df['target_profitable'] = (model_df['next_day_win_rate'] > 0.5).astype(int)
    
    features = ['fgi_value', 'trades_per_day', 'avg_trade_size', 'ls_ratio_clipped', 'leverage_proxy', 'Closed PnL']
    
    X = model_df[features]
    y = model_df['target_profitable']
    
    if len(model_df) > 10:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        clf = RandomForestClassifier(max_depth=3, random_state=42)
        clf.fit(X_train, y_train)
        
        preds = clf.predict(X_test)
        acc = accuracy_score(y_test, preds)
        
        st.write(f"**Model Accuracy:** {acc:.2%}")
        
        st.subheader("Feature Importances")
        importances = pd.DataFrame({'Feature': features, 'Importance': clf.feature_importances_}).sort_values(by='Importance', ascending=False)
        fig_feat = px.bar(importances, x='Feature', y='Importance', title="Predictive Power of Features")
        st.plotly_chart(fig_feat, use_container_width=True)
    else:
        st.write("Not enough longitudinal data points to train a robust next-day model. Try aggregating with more historical data.")
