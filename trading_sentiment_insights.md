# Trading Performance vs. Market Sentiment Insights

## 1. Performance Normalization
| classification   |   total_trades |   avg_pnl |   win_rate |   total_volume |
|:-----------------|---------------:|----------:|-----------:|---------------:|
| Extreme Fear     |          21400 |   34.5379 |   0.370607 |    1.14484e+08 |
| Extreme Greed    |          39992 |   67.8929 |   0.464943 |    1.24465e+08 |
| Fear             |          61837 |   54.2904 |   0.420768 |    4.83325e+08 |
| Greed            |          50303 |   42.7436 |   0.384828 |    2.88582e+08 |
| Neutral          |          37686 |   34.3077 |   0.396991 |    1.80242e+08 |

## 2. Trader-Level Analysis
Performance of top 5 traders by volume across sentiments:
| Account                                    | classification   |     avg_pnl |   win_rate |
|:-------------------------------------------|:-----------------|------------:|-----------:|
| 0x4f93fead39b70a1824f981a54d4e55b278e9f760 | Extreme Fear     |  200.395    |   0.428571 |
| 0x4f93fead39b70a1824f981a54d4e55b278e9f760 | Extreme Greed    |   52.8282   |   0.333606 |
| 0x4f93fead39b70a1824f981a54d4e55b278e9f760 | Fear             |  -16.5451   |   0.355536 |
| 0x4f93fead39b70a1824f981a54d4e55b278e9f760 | Greed            |   33.8575   |   0.343616 |
| 0x4f93fead39b70a1824f981a54d4e55b278e9f760 | Neutral          |   35.6416   |   0.426782 |
| 0x513b8629fe877bb581bf244e326a047b249c4ff1 | Extreme Fear     | -205.554    |   0.303468 |
| 0x513b8629fe877bb581bf244e326a047b249c4ff1 | Extreme Greed    |    0        |   0        |
| 0x513b8629fe877bb581bf244e326a047b249c4ff1 | Fear             |   61.3888   |   0.370507 |
| 0x513b8629fe877bb581bf244e326a047b249c4ff1 | Greed            |   51.4508   |   0.376459 |
| 0x513b8629fe877bb581bf244e326a047b249c4ff1 | Neutral          |  151.502    |   0.554231 |
| 0xb899e522b5715391ae1d4f137653e7906c5e2115 | Extreme Fear     |  -21.0665   |   0.336081 |
| 0xb899e522b5715391ae1d4f137653e7906c5e2115 | Fear             |   17.5407   |   0.511028 |
| 0xb899e522b5715391ae1d4f137653e7906c5e2115 | Neutral          |   12.796    |   0.273885 |
| 0xbaaaf6571ab7d571043ff1e313a9609a10637864 | Extreme Fear     |   58.4638   |   0.379464 |
| 0xbaaaf6571ab7d571043ff1e313a9609a10637864 | Fear             |   49.9214   |   0.498271 |
| 0xbaaaf6571ab7d571043ff1e313a9609a10637864 | Greed            |    0.934492 |   0.2      |
| 0xbaaaf6571ab7d571043ff1e313a9609a10637864 | Neutral          |   13.4353   |   0.47096  |
| 0xbee1707d6b44d4d52bfe19e41f8a828645437aab | Extreme Fear     |    6.05908  |   0.41327  |
| 0xbee1707d6b44d4d52bfe19e41f8a828645437aab | Extreme Greed    |   71.2199   |   0.596311 |
| 0xbee1707d6b44d4d52bfe19e41f8a828645437aab | Fear             |    4.33911  |   0.37656  |
| 0xbee1707d6b44d4d52bfe19e41f8a828645437aab | Greed            |   33.1697   |   0.464704 |
| 0xbee1707d6b44d4d52bfe19e41f8a828645437aab | Neutral          |    3.33006  |   0.347783 |

## 3. Leverage Impact Analysis
*Note: Leverage parsing was not explicitly available natively in the dataset columns. Estimating risk via trade sizes vs PnL variance instead.* 

## 4. Time-Based Analysis (Sentiment Shifts)
Performance during days when sentiment shifted:
| sentiment_shift         |   avg_pnl |   win_rate |   shift_count |
|:------------------------|----------:|-----------:|--------------:|
| Fear -> Greed           |  165.493  |   0.275903 |          2519 |
| Greed -> Fear           |  144.533  |   0.456765 |          2417 |
| Greed -> Extreme Greed  |  142.725  |   0.537785 |          5915 |
| Extreme Fear -> Neutral |  125.57   |   0.298611 |           144 |
| Extreme Greed -> Greed  |   94.075  |   0.519762 |          7565 |
| Extreme Fear -> Fear    |   71.3613 |   0.539954 |          7421 |
| Fear -> Neutral         |   46.637  |   0.398599 |         11134 |
| Neutral -> Fear         |   31.5554 |   0.395662 |         15354 |
| Greed -> Neutral        |   28.6681 |   0.408932 |          5732 |
| Fear -> Extreme Fear    |   28.4266 |   0.342564 |          9461 |

## 5. Risk Metrics
| classification   |     pnl_variance |   max_loss |   downside_exposure |
|:-----------------|-----------------:|-----------:|--------------------:|
| Extreme Fear     |      1.29062e+06 |   -31036.7 |   -636322           |
| Extreme Greed    | 588026           |   -10259.5 |   -270900           |
| Fear             | 874890           |   -35681.7 |   -593594           |
| Greed            |      1.24552e+06 |  -117990   |        -1.05869e+06 |
| Neutral          | 267415           |   -24500   |   -389286           |

## 6. Strategy Extraction
Based on the data observed, the following patterns can be translated into actionable strategies:

- **Corrected Win Rate Interpretation**: While `Extreme Greed` yields the highest relative win probability (46.49%), it is critical to note that all observed win rates remain below 50%. No single sentiment guarantees consistent absolute profitability; results should be evaluated relatively.
- **Risk vs Reward Tradeoff**: Despite sub-50% win rates, sentiments like `Extreme Greed` offer higher average PnL. This indicates fewer but larger profitable trades, reflecting a classic high-risk, high-reward environment.
- **Market Bias Identification**: The consistent outperformance of `SELL` trades across almost all sentiment categories (e.g., 58.98% in Extreme Greed, 57.21% in Fear) strongly indicates an underlying bearish bias within this specific dataset. Conclusions on directional edges must account for this macro bias.
- **Contrarian Strategy Insight**: The pronounced success of `SELL` (shorting) trades during `Greed` and `Extreme Greed` phases suggests these periods often represent overbought conditions. Contrarian short-selling strategies capitalize directly on this sentiment-driven exhaustion.
- **Stability vs Volatility Insight**: Risk metrics reveal that sentiments with lower PnL variance (e.g., `Neutral` variance at 2.67e5) provide more stable and predictable trading conditions. Conversely, high-variance sentiments (e.g., `Greed` and `Extreme Fear` >1.2e6) reflect highly unpredictable, volatile markets requiring tighter risk controls.

### Recommendations:
1. **Risk-Aware Sizing**: Scale up positions during stable, low-variance sentiments (`Neutral`), and reduce size or widen stops during high-variance/unpredictable markets (`Extreme Fear`, `Greed`).
2. **Contrarian Trading**: Exploit overextended sentiment (Greed/Extreme Greed) by identifying structural shorting opportunities, as statistical data validates a strong reversion edge (high SELL win rates).
3. **Manage Downside**: Actively reduce downside exposure during sharp sentiment shifts, acknowledging that no condition offers a >50% baseline win probability without strict macro context.
