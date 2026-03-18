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
    ret = re.search(r"Return:\s+([\-\d.]+)", result.stdout)
    print(f"{changes_desc}: score={score.group(1) if score else 'N/A'}, trades={trades_m.group(1) if trades_m else 'N/A'}, wr={wr.group(1) if wr else 'N/A'}, sharpe={sharpe.group(1) if sharpe else 'N/A'}, dd={dd.group(1) if dd else 'N/A'}, ret={ret.group(1) if ret else 'N/A'}")

# Combo: RSI 60 + Trend EMA 100
run_with_params("RSI=60 + TrendEMA=100", [
    ("rsi_upper = 70", "rsi_upper = 60"),
    ("trend_ema = 50", "trend_ema = 100"),
])

# More combos
for rsi_u in [55, 60, 65]:
    for te in [80, 100, 120]:
        run_with_params(f"RSI={rsi_u} TE={te}", [
            ("rsi_upper = 70", f"rsi_upper = {rsi_u}"),
            ("trend_ema = 50", f"trend_ema = {te}"),
        ])

# Try trend EMA 100 with ATR trail variations
for atr_t in [3.0, 3.5, 4.0]:
    run_with_params(f"TE=100 ATR={atr_t}", [
        ("trend_ema = 50", "trend_ema = 100"),
        ("atr_trail_multiplier = 3.5", f"atr_trail_multiplier = {atr_t}"),
    ])

