# Trading AutoResearch — Program Objectives (Phase 4)

## Goal
Develop a BTC 4H trading strategy that is **profitable AND generalizes** out-of-sample,
with realistic performance characteristics that would hold up in live trading.

Phase 3 plateaued at ~57.3 but the numbers were unrealistic: 97% win rate, 0% drawdown,
profit factor of 109x. These are overfit artifacts, not real edge. Phase 4 enforces
reality-check constraints so the optimizer must find a **robust** strategy, not a
perfectly-fitted one.

The composite score is evaluated on BOTH a training window AND a holdout window:

```
final_score = 0.6 * train_composite + 0.4 * holdout_composite
```

where:
```
composite_score = sharpe_ratio (capped at 3.0)
               - 0.5 * max_drawdown_pct
               + 0.5 * ln(min(profit_factor, 4.0))   ← PF capped at 4x
               + 0.05 * min(total_return_pct, 100)
               - win_rate_penalty                     ← NEW: punishes >70% or <35% WR
               - too_clean_penalty                    ← NEW: punishes <1% drawdown
```

**Sharpe is hard-capped at 3.0** — live Sharpe >3 is exceptional, >5 is degenerate.

**Theoretical ceiling: ~12-15** for a genuinely excellent real-world strategy.

## Reality-Check Penalties (Phase 4 — these did NOT exist in Phase 3)

### Win Rate Penalty
- Win rate > 70%: penalty = (win_rate% - 70) × 0.5 per point above 70
  - Example: 80% WR → -5 pts; 97% WR → -13.5 pts
  - Why: Real trend-following strategies win 45-65% of the time. Higher = overfit.
- Win rate < 35%: penalty = (35 - win_rate%) × 0.3 per point below 35

### Profit Factor Cap
- PF contribution = 0.5 × ln(min(PF, 4.0)) — no reward beyond PF=4
- Max PF contribution: 0.5 × ln(4) ≈ 0.69 pts
- Why: Real good strategies have PF 1.5-3. PF=109 is meaningless (30 cherry-picked trades).

### "Too Clean" Drawdown Penalty
- Max drawdown < 1%: penalty = (1.0 - max_dd%) × 5.0 (up to -5 pts for 0% DD)
- Why: Zero drawdown over 14 months signals the strategy is only entering when it KNOWS
  it'll win — which means it's look-ahead biased or simply not trading enough.

## Hard Requirements (any violation → score = -100)
- Minimum **20 trades** on training data (raised from 10 — need statistical significance)
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

## Target Performance (what "good" looks like in Phase 4)
- Sharpe > 1.5 on both train and holdout (live-achievable)
- Max drawdown 3-15% (some drawdown = the strategy is actually trading)
- Win rate 45-65% (realistic for trend-following)
- Profit factor 1.5-3.0 (big winners, manageable losers)
- Total return > 20% on train
- Phase 4 target score: > 8.0 (the formula is tighter; a score of 8-12 is excellent)

## Key Insight for Phase 4
The current strategy (iter 172) scores ~2.1 under Phase 4 rules because:
1. Win rate of 97% → -13.5 win rate penalty
2. 0% drawdown → -5 too_clean penalty
3. Sharpe capped at 3.0 (was 50.0)
4. PF capped at 4.0 (was uncapped)

The agent needs to find strategies that TRADE MORE, ACCEPT SOME LOSSES, and WIN
at a reasonable rate — not strategies that sit on the sidelines until they're
certain and make 30 cherry-picked trades in 14 months.

## Agent Workflow
1. Read this file (`program.md`) and current `backtest.py`
2. Check `state.json` for score history — what has worked, what hasn't
3. Analyze the current strategy and its weaknesses (too few trades, too high WR)
4. Propose ONE focused improvement aimed at: more trades, realistic win rate, some drawdown
5. Edit only the `run_strategy()` function in `backtest.py`
6. The runner will execute, evaluate train+holdout, and score

## Example Good Changes for Phase 4
- "Loosen entry filters to generate 40-80 trades over 14 months"
- "Reduce ADX threshold from 25 to 15 to trade more market conditions"
- "Widen RSI pullback thresholds to catch more setups"
- "Accept a stop loss rate of ~35-40% — that's healthy trend-following behavior"
- "Use ATR-based stops at 2-3x ATR (not 1.1x) to give trades room to breathe"
- "Remove partial TP logic — let winners run, accept some variance"

## Example Bad Changes
- Rewriting the entire file from scratch
- Changing compute_metrics(), load_data(), or the main block
- Using `df['close'].shift(-1)` (look-ahead bias)
- Tightening filters further (would reduce trades below 20 gate)
- Setting position_size to 0 or negative
- Removing the SCORE output line
- Making changes outside run_strategy()
