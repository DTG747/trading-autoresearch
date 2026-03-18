# Trading AutoResearch — Program Objectives

## Goal
Develop a BTC 4H trading strategy that is **profitable AND generalizes** out-of-sample.

The composite score is evaluated on BOTH a training window AND a holdout window:

```
final_score = 0.6 * train_composite + 0.4 * holdout_composite
```

where:
```
composite_score = sharpe_ratio - 0.5 * max_drawdown_pct
```

**Sharpe is hard-capped at 20.0** — strategies with near-zero variance returns are automatically scored 0.0 Sharpe, not infinity.

## Hard Requirements (any violation → score = -100)
- Minimum **10 trades** on training data
- Minimum **1% total return** on training data
- Minimum **profit factor ≥ 1.0** on training data (gross profit > gross loss)

## Overfitting Penalty
If holdout composite_score < -20, a penalty of **-40** is applied to the raw train score.
Strategies must generalize — it is not enough to win on the training window only.

## Data
- **3,479 candles** of BTC/USD 4H OHLCV (March 2024 → March 2026)
- **Train window:** first 75% of data (~2,609 candles, ~14 months)
- **Holdout window:** last 25% (~870 candles, ~3.5 months) — never used during optimization
- All candles have real volume (zero-volume rows are filtered out)

## What the Agent CAN Change (in run_strategy only)
- Entry and exit logic (signals, conditions, timing)
- Technical indicators and their parameters (EMA periods, RSI thresholds, etc.)
- Adding new indicators (Bollinger Bands, MACD, ATR, volume filters, etc.)
- Stop-loss and take-profit levels
- Position sizing rules
- Trade filters (volatility regimes, time-of-day, trend confirmation, etc.)
- Combining multiple signals

## What the Agent Must NOT Change
- `load_data()` function
- `compute_metrics()` function
- The main block (train/test split + scoring logic)
- The `SCORE: <float>` output format (must be the last line of stdout)
- Must not introduce look-ahead bias (no peeking at future candles)

## No Look-Ahead Bias Rule
At any candle index `i`, the strategy may only use data from indices `0..i` (inclusive).
Do NOT use future close prices, future indicator values, or shift signals backward in time.

## Target Performance (what "good" looks like)
- Sharpe > 1.0 on both train and holdout
- Max drawdown < 15%
- Win rate > 40%
- Profit factor > 1.3
- Total return > 5%

## Agent Workflow
1. Read this file (`program.md`) and current `backtest.py`
2. Check `state.json` for score history — what has worked, what hasn't
3. Analyze the current strategy and its weaknesses
4. Propose ONE focused improvement (not a full rewrite)
5. Edit only the `run_strategy()` function in `backtest.py`
6. The runner will execute, evaluate train+holdout, and score

## Example Good Changes
- "Add ATR-based stop loss to reduce drawdown"
- "Add RSI overbought filter to avoid entering extended moves"
- "Require EMA trend alignment before taking crossover signals"
- "Add volume confirmation: only enter when volume > 1.5x 20-period average"
- "Add ADX filter: only trade when trend strength > 25"
- "Combine MACD histogram direction with EMA crossover for better signal quality"
- "Use Bollinger Band width to filter out low-volatility, choppy conditions"

## Example Bad Changes
- Rewriting the entire file from scratch
- Changing compute_metrics(), load_data(), or the main block
- Using `df['close'].shift(-1)` (look-ahead bias)
- Setting tp_pct to an absurdly small value to game variance
- Setting position_size to 0 or negative
- Removing the SCORE output line
- Making changes outside run_strategy()
