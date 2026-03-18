import subprocess, re

params_to_try = [
    ("atr_trail=4.85", {"atr_trail_multiplier": 4.85}),
    ("atr_trail=4.9", {"atr_trail_multiplier": 4.9}),
    ("atr_trail=4.95", {"atr_trail_multiplier": 4.95}),
    ("4.9+adx18", {"atr_trail_multiplier": 4.9, "adx_threshold": 18}),
    ("4.9+adx20", {"atr_trail_multiplier": 4.9, "adx_threshold": 20}),
    ("4.9+margin0.002", {"atr_trail_multiplier": 4.9, "trend_margin": 0.002}),
    ("4.9+cool3", {"atr_trail_multiplier": 4.9, "cooldown_bars": 3}),
    ("4.9+cool0", {"atr_trail_multiplier": 4.9, "cooldown_bars": 0}),
    ("4.9+volm1.0", {"atr_trail_multiplier": 4.9, "vol_mult": 1.0}),
    ("4.9+trend45", {"atr_trail_multiplier": 4.9, "trend_ema": 45}),
    ("4.9+trend55", {"atr_trail_multiplier": 4.9, "trend_ema": 55}),
]

for name, overrides in params_to_try:
    with open("backtest.py", "r") as f:
        code = f.read()
    for k, v in overrides.items():
        code = re.sub(rf'{k}\s*=\s*[\d.]+', f'{k} = {v}', code)
    with open("backtest_tmp2.py", "w") as f:
        f.write(code)
    result = subprocess.run(["python3", "backtest_tmp2.py"], capture_output=True, text=True)
    score_line = [l for l in result.stdout.strip().split('\n') if l.startswith("SCORE:")]
    score = score_line[0].split(":")[1].strip() if score_line else "ERROR"
    trades_line = [l for l in result.stdout.strip().split('\n') if 'Trades' in l]
    trades = trades_line[0].strip() if trades_line else ""
    dd_line = [l for l in result.stdout.strip().split('\n') if 'Max DD' in l]
    dd = dd_line[0].strip() if dd_line else ""
    sharpe_line = [l for l in result.stdout.strip().split('\n') if 'Sharpe' in l]
    sharpe = sharpe_line[0].strip() if sharpe_line else ""
    print(f"{name:25s} => SCORE: {score:>10s}  {trades}  {dd}  {sharpe}")
