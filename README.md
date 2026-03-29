# Trader Sentiment Analysis

This project analyzes the relationship between trader performance, trading behaviors, and Bitcoin market sentiment (using the Fear & Greed Index). Included is a comprehensive Streamlit dashboard to explore the dynamic visualizations, a predictive model for trader performance, and clear strategy recommendations tailored toward distinct trader segments.

## Setup Instructions

1. **Prerequisites**
   Ensure you have Python 3.8+ installed on your system.

2. **Install Dependencies**
   Navigate to the project directory and run the following command to install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Dashboard**
   Launch the interactive Streamlit application to explore the visual insights and the integrated predictive model:
   ```bash
   streamlit run app.py
   ```

4. **Static Outputs**
   If you wish to view static representations of the charts, simply navigate to the `output/` directory, which contains our key statistical visualizations and summary segment tables.

---

## Project Write-Up

### Data Audit Summary
Before processing, the raw datasets were thoroughly audited for dimensions, missing values, and duplicating records:
- **Historical Trades Data:** 211,224 rows, 16 columns. Investigated to contain 0% missing values and 0 true duplicate instances.
- **Fear & Greed Index Data:** 2,644 rows, 4 columns. Clean tracking with 0% missing values.
This upfront audit ensured transparency in data quality and proved that our explicit temporal-alignment and aggregation techniques were built upon a mathematically sound foundation.

### Methodology
1. **Data Processing & Alignment:**
   We ingested the raw trades from `historical_data.csv` alongside the `fear_greed_index.csv`. Timestamps were structurally converted to rigorous UTC `datetime` formats to securely align datasets at a daily grain. 
2. **Feature Engineering & Drawdown:**
   Custom daily aggregated metrics were dynamically calculated per trader: Total PnL, Win Rate (profitable vs un-profitable trade completion), Leverage Proxy (Average Trade Size vs. Account Top Size), Long/Short Bias (Volume Ratio), and Frequency (Trades per Day). **Crucially, absolute cumulative drawdowns were generated and actively analyzed alongside PnL and win rate to capture a true underlying picture of downside risk profiles across the different sentiment regimes.**
3. **Trader Segmentation:**
   Traders were robustly clustered into **4 distinct behavioral archetypes** (High-Freq/High-Lev, High-Freq/Low-Lev, Low-Freq/High-Lev, Low-Freq/Low-Lev) utilizing measurable mathematical medians calculated strictly from their Trade Frequencies and normalized Leverage levels. This ensures segmentation remains clearly interpretable and identically tied to precise structural behavioral differences over arbitrary delineations.
4. **Statistical Testing:**
   We incorporated two-tailed independent student t-tests across isolated `Fear` and `Greed` conditions to properly validate that behavioral findings actively separated true variance capabilities from generic statistical noise.
5. **Predictive Modeling:**
   A lightweight Random Forest Classifier was built within the dashboard to iteratively predict "next-day profitability" (defined as achieving an aggregated daily win rate > 50%) drawing exclusively upon lagging sentiment thresholds and previous-day behavioral activities.

### Key Insights
1. **Fear Promotes Consistency:** Win rates are significantly higher on days classified under Fear compared to Greed regimes. Our statistical validation confirms mean win rates jump from 73% (Greed) to 87% (Fear) with a valid p-value of 0.037.
2. **The High-Frequency Edge:** Trade frequencies spike exponentially during Fear periods (p=0.007). Opportunities appear to uniquely compound during market drawdowns; successful high-frequency traders capitalize efficiently on this heightened volatility instead of recoiling.
3. **Leverage & Sentiment Bias:** The volumetric Long/Short ratio heavily skews toward long positioning universally during Greed periods (underlining typical retail FOMO behaviors), while returning to a heavily balanced state (~1.0) actively amidst Fear conditions.

### Strategy Recommendations
1. **Capitalize on Fear (Tailored for High-Frequency Traders):**
   * **Rule of Thumb:** Maintain or explicitly scale-up trading frequency execution levels whenever the FGI crashes actively into "Fear".
   * **Why applies:** Analysis statistically validates that active algorithmic win probabilities are naturally elevated amidst panic dynamics. Fast/High-frequency segments suffer drastically by suppressing organic activity models due to "macro caution".
2. **Prune Leverage in Greed (Tailored for High-Leverage Traders):**
   * **Rule of Thumb:** Systematically tighten internal position sizing constraints and restrict accessible leverage when the FGI scales cleanly into "Greed".
   * **Why applies:** Individual win rates collapse structurally toward ~73% inside generalized Greed markets. Blind heavy long bias exposes massive leverage traders aggressively toward sudden catastrophic whipsaws or trend liquidations.

### Conclusion
Overall, **trader performance varies significantly alongside underlying market sentiment.** By thoroughly plotting metrics—including our newly constructed downside drawdown metrics—across independent sentiment boundaries, it becomes explicitly clear that adapting strategic execution behavior limits downside. Dynamically shifting scaling levers involving internal algorithmic trade execution frequency and actively slashing volumetric leverage exposure specifically predicated on Fear & Greed index locations can profoundly maximize long-term positive trade outcomes.
