import subprocess, re

def run_with_params(changes_desc, replacements):
    with open("backtest.py") as f:
        code = f.read()
    modified = code
    for old, new in replacements:
        modified = modified.replace(old, new)
    with open("backtest_tmp.py", "w") as f:
        f.write(modified)
    result = subprocess.run(["python3", "backtest_tmp.py"], capture_output=True, text=True)
    score = re.search(r"SCORE: ([\-\d.]+)", result.stdout)
    trades_m = re.search(r"Trades:\s+(\d+)", result.stdout)
    wr = re.search(r"Win rate:\s+([\d.]+)", result.stdout)
    sharpe = re.search(r"Sharpe:\s+([\-\d.]+)", result.stdout)
    dd = re.search(r"Max DD:\s+([\d.]+)", result.stdout)
    print(f"{changes_desc}: score={score.group(1) if score else 'N/A'}, trades={trades_m.group(1) if trades_m else 'N/A'}, wr={wr.group(1) if wr else 'N/A'}, sharpe={sharpe.group(1) if sharpe else 'N/A'}, dd={dd.group(1) if dd else 'N/A'}")

# TE=130 with ATR variations
for atr_t in [3.0, 3.5, 4.0, 4.5]:
    run_with_params(f"TE=130 ATR={atr_t}", [
        ("trend_ema = 50", "trend_ema = 130"),
        ("atr_trail_multiplier = 3.5", f"atr_trail_multiplier = {atr_t}"),
    ])

# TE=130 with ADX variations
for adx in [15, 18, 20, 22, 25]:
    run_with_params(f"TE=130 ADX={adx}", [
        ("trend_ema = 50", "trend_ema = 130"),
        ("adx_threshold = 20", f"adx_threshold = {adx}"),
    ])

# TE=130 with different fast/slow EMA
for fast, slow in [(7, 18), (8, 21), (9, 26), (10, 25), (12, 26)]:
    run_with_params(f"TE=130 F={fast} S={slow}", [
        ("trend_ema = 50", "trend_ema = 130"),
        ("fast_ema = 9", f"fast_ema = {fast}"),
        ("slow_ema = 21", f"slow_ema = {slow}"),
    ])

# TE=130 + lower RSI for shorts
for rsi_l in [30, 35, 40, 45]:
    run_with_params(f"TE=130 RSI_low={rsi_l}", [
        ("trend_ema = 50", "trend_ema = 130"),
        ("rsi_lower = 35", f"rsi_lower = {rsi_l}"),
    ])

