import subprocess, re

# Test different take-profit multipliers
for tp_mult in [0, 4, 5, 6, 7, 8, 10]:
    # Read current file
    with open("backtest.py") as f:
        code = f.read()
    
    # We'll just test by modifying and running
    # For tp_mult=0, skip (baseline)
    if tp_mult == 0:
        result = subprocess.run(["python3", "backtest.py"], capture_output=True, text=True)
        score = re.search(r"SCORE: ([\-\d.]+)", result.stdout)
        trades = re.search(r"Trades:\s+(\d+)", result.stdout)
        wr = re.search(r"Win rate:\s+([\d.]+)", result.stdout)
        print(f"Baseline: score={score.group(1) if score else 'N/A'}, trades={trades.group(1) if trades else 'N/A'}, wr={wr.group(1) if wr else 'N/A'}")
        continue
    
    # Add take-profit parameter and logic
    modified = code.replace(
        "    atr_trail_multiplier = 3.5",
        f"    atr_trail_multiplier = 3.5\n    atr_tp_multiplier = {tp_mult}.0"
    )
    
    # Add TP exit for longs
    modified = modified.replace(
        """            # Exit on trailing stop OR EMA bearish crossover
            if low <= stop_price or (prev_ema_f >= prev_ema_s and ema_f < ema_s):""",
        """            # Exit on take-profit, trailing stop, OR EMA bearish crossover
            tp_price_long = entry_price + atr_tp_multiplier * df["atr"].iloc[entry_idx]
            if price >= tp_price_long:
                exit_price = tp_price_long
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
                highest_close = None
                lowest_close = None
                continue
            if low <= stop_price or (prev_ema_f >= prev_ema_s and ema_f < ema_s):"""
    )
    
    # Add TP exit for shorts
    modified = modified.replace(
        """            high = df["high"].iloc[i]
            # Exit on trailing stop OR EMA bullish crossover
            if high >= stop_price or (prev_ema_f <= prev_ema_s and ema_f > ema_s):""",
        """            high = df["high"].iloc[i]
            # Exit on take-profit, trailing stop, OR EMA bullish crossover
            tp_price_short = entry_price - atr_tp_multiplier * df["atr"].iloc[entry_idx]
            if price <= tp_price_short:
                exit_price = tp_price_short
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
                highest_close = None
                lowest_close = None
                continue
            if high >= stop_price or (prev_ema_f <= prev_ema_s and ema_f > ema_s):"""
    )
    
    with open("backtest_tmp.py", "w") as f:
        f.write(modified)
    
    result = subprocess.run(["python3", "backtest_tmp.py"], capture_output=True, text=True)
    score = re.search(r"SCORE: ([\-\d.]+)", result.stdout)
    trades_m = re.search(r"Trades:\s+(\d+)", result.stdout)
    wr = re.search(r"Win rate:\s+([\d.]+)", result.stdout)
    sharpe = re.search(r"Sharpe:\s+([\-\d.]+)", result.stdout)
    dd = re.search(r"Max DD:\s+([\d.]+)", result.stdout)
    print(f"TP mult={tp_mult}: score={score.group(1) if score else 'N/A'}, trades={trades_m.group(1) if trades_m else 'N/A'}, wr={wr.group(1) if wr else 'N/A'}, sharpe={sharpe.group(1) if sharpe else 'N/A'}, dd={dd.group(1) if dd else 'N/A'}")

