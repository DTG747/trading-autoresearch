"""
BTC 4H Backtesting Engine — Trading AutoResearch
=================================================

## AGENT-MODIFIABLE SECTION (between the markers below)
You CAN change:
  - run_strategy() logic: indicators, entry/exit signals, thresholds
  - Helper functions for indicators or signal generation
  - Constants like EMA periods, RSI levels, stop-loss/take-profit %

## FIXED SECTION (do NOT modify)
  - load_data()
  - compute_metrics()
  - main block and SCORE output
"""

import pandas as pd
import numpy as np

# ============================================================
# FIXED — Data Loading
# ============================================================

def load_data(path="data/btc_4h.csv"):
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


# ============================================================
# FIXED — Metric Computation
# ============================================================

def compute_metrics(trades, df):
    """
    Compute composite_score = sharpe_ratio - 0.5 * max_drawdown_pct.

    trades: list of dicts with keys:
        entry_idx, exit_idx, entry_price, exit_price, direction ('long'/'short'), size
    """
    if not trades:
        return {"sharpe_ratio": 0.0, "max_drawdown_pct": 100.0, "composite_score": -50.0,
                "total_return_pct": 0.0, "num_trades": 0, "win_rate": 0.0}

    # Build equity curve from trades
    initial_capital = 10000.0
    equity = initial_capital
    equity_curve = [initial_capital]
    returns = []

    for t in trades:
        if t["direction"] == "long":
            pnl = (t["exit_price"] - t["entry_price"]) / t["entry_price"] * t["size"]
        else:
            pnl = (t["entry_price"] - t["exit_price"]) / t["entry_price"] * t["size"]
        equity += pnl
        equity_curve.append(equity)
        returns.append(pnl / (equity - pnl) if (equity - pnl) > 0 else 0.0)

    # Sharpe ratio (annualized, 4H bars => 6 per day => ~2190 per year)
    if len(returns) < 2:
        sharpe_ratio = 0.0
    else:
        mean_r = np.mean(returns)
        std_r = np.std(returns, ddof=1)
        if std_r == 0:
            sharpe_ratio = 0.0
        else:
            # Annualize: assume average holding ~1 bar, scale by sqrt(bars/year)
            sharpe_ratio = (mean_r / std_r) * np.sqrt(2190 / max(len(trades), 1) * len(trades))

    # Max drawdown
    peak = equity_curve[0]
    max_dd = 0.0
    for eq in equity_curve:
        if eq > peak:
            peak = eq
        dd = (peak - eq) / peak
        if dd > max_dd:
            max_dd = dd
    max_drawdown_pct = max_dd * 100.0

    # Win rate
    wins = sum(1 for r in returns if r > 0)
    win_rate = wins / len(returns) * 100.0 if returns else 0.0

    total_return_pct = (equity - initial_capital) / initial_capital * 100.0
    composite_score = sharpe_ratio - 0.5 * max_drawdown_pct

    return {
        "sharpe_ratio": round(sharpe_ratio, 4),
        "max_drawdown_pct": round(max_drawdown_pct, 2),
        "composite_score": round(composite_score, 4),
        "total_return_pct": round(total_return_pct, 2),
        "num_trades": len(trades),
        "win_rate": round(win_rate, 2),
    }


# ============================================================
# AGENT-MODIFIABLE — Strategy
# ============================================================

def run_strategy(df):
    """
    EMA crossover + RSI filter + ATR stop-loss strategy.

    Changes from baseline:
    - Added ATR-based stop-loss (1.5x ATR) to cut losers early
    - Uses high/low prices for stop checks (realistic intra-bar stops)
    """
    # --- Parameters (agent: tune these) ---
    ema_fast_period = 12
    ema_slow_period = 26
    rsi_period = 14
    atr_period = 14
    atr_stop_multiplier = 1.5  # stop-loss at 1.5x ATR from entry
    rsi_long_entry = 70    # RSI must be below this to enter long
    rsi_long_exit = 80     # exit long if RSI above this
    rsi_short_entry = 30   # RSI must be above this to enter short
    rsi_short_exit = 20    # exit short if RSI below this
    position_size = 1000.0  # USD per trade

    # --- Indicators ---
    df = df.copy()
    df["ema_fast"] = df["close"].ewm(span=ema_fast_period, adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=ema_slow_period, adjust=False).mean()

    # RSI calculation
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_gain = gain.ewm(com=rsi_period - 1, min_periods=rsi_period).mean()
    avg_loss = loss.ewm(com=rsi_period - 1, min_periods=rsi_period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["rsi"] = 100.0 - (100.0 / (1.0 + rs))
    df["rsi"] = df["rsi"].fillna(50.0)

    # ATR calculation
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift(1)).abs()
    low_close = (df["low"] - df["close"].shift(1)).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["atr"] = true_range.ewm(span=atr_period, adjust=False).mean()

    # --- Signal generation (no look-ahead) ---
    trades = []
    position = None  # None, 'long', or 'short'
    entry_idx = None
    entry_price = None
    stop_price = None

    warmup = max(ema_fast_period, ema_slow_period, rsi_period, atr_period) + 1

    for i in range(warmup, len(df)):
        ema_f = df["ema_fast"].iloc[i]
        ema_s = df["ema_slow"].iloc[i]
        ema_f_prev = df["ema_fast"].iloc[i - 1]
        ema_s_prev = df["ema_slow"].iloc[i - 1]
        rsi = df["rsi"].iloc[i]
        price = df["close"].iloc[i]
        low = df["low"].iloc[i]
        high = df["high"].iloc[i]
        atr = df["atr"].iloc[i]

        cross_up = ema_f > ema_s and ema_f_prev <= ema_s_prev
        cross_down = ema_f < ema_s and ema_f_prev >= ema_s_prev

        if position is None:
            if cross_up and rsi < rsi_long_entry:
                position = "long"
                entry_idx = i
                entry_price = price
                stop_price = price - atr_stop_multiplier * atr
            elif cross_down and rsi > rsi_short_entry:
                position = "short"
                entry_idx = i
                entry_price = price
                stop_price = price + atr_stop_multiplier * atr

        elif position == "long":
            # Check ATR stop-loss (use low to see if stop was hit intra-bar)
            stopped_out = low <= stop_price
            signal_exit = cross_down or rsi > rsi_long_exit

            if stopped_out:
                exit_price = stop_price  # assume filled at stop
                trades.append({
                    "entry_idx": entry_idx,
                    "exit_idx": i,
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "direction": "long",
                    "size": position_size,
                })
                position = None
                entry_idx = None
                entry_price = None
                stop_price = None
            elif signal_exit:
                trades.append({
                    "entry_idx": entry_idx,
                    "exit_idx": i,
                    "entry_price": entry_price,
                    "exit_price": price,
                    "direction": "long",
                    "size": position_size,
                })
                position = None
                entry_idx = None
                entry_price = None
                stop_price = None

        elif position == "short":
            # Check ATR stop-loss (use high to see if stop was hit intra-bar)
            stopped_out = high >= stop_price
            signal_exit = cross_up or rsi < rsi_short_exit

            if stopped_out:
                exit_price = stop_price  # assume filled at stop
                trades.append({
                    "entry_idx": entry_idx,
                    "exit_idx": i,
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "direction": "short",
                    "size": position_size,
                })
                position = None
                entry_idx = None
                entry_price = None
                stop_price = None
            elif signal_exit:
                trades.append({
                    "entry_idx": entry_idx,
                    "exit_idx": i,
                    "entry_price": entry_price,
                    "exit_price": price,
                    "direction": "short",
                    "size": position_size,
                })
                position = None
                entry_idx = None
                entry_price = None
                stop_price = None

    # Close any open position at end
    if position is not None:
        trades.append({
            "entry_idx": entry_idx,
            "exit_idx": len(df) - 1,
            "entry_price": entry_price,
            "exit_price": df["close"].iloc[-1],
            "direction": position,
            "size": position_size,
        })

    return trades


# ============================================================
# FIXED — Main
# ============================================================

if __name__ == "__main__":
    df = load_data()
    trades = run_strategy(df)
    metrics = compute_metrics(trades, df)

    print(f"Strategy results on {len(df)} candles:")
    print(f"  Trades:      {metrics['num_trades']}")
    print(f"  Win rate:    {metrics['win_rate']}%")
    print(f"  Return:      {metrics['total_return_pct']}%")
    print(f"  Sharpe:      {metrics['sharpe_ratio']}")
    print(f"  Max DD:      {metrics['max_drawdown_pct']}%")
    print(f"SCORE: {metrics['composite_score']}")
