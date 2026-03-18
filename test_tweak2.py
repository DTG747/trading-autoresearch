import subprocess, re

params_to_try = [
    ("atr_trail=4.8", {"atr_trail_multiplier": 4.8}),
    ("atr_trail=4.9", {"atr_trail_multiplier": 4.9}),
    ("atr_trail=5.0", {"atr_trail_multiplier": 5.0}),
    ("atr_trail=5.1", {"atr_trail_multiplier": 5.1}),
    ("atr_trail=5.2", {"atr_trail_multiplier": 5.2}),
    ("atr_trail=5.3", {"atr_trail_multiplier": 5.3}),
    ("5.0+adx18", {"atr_trail_multiplier": 5.0, "adx_threshold": 18}),
    ("5.0+adx15", {"atr_trail_multiplier": 5.0, "adx_threshold": 15}),
    ("5.0+adx20", {"atr_trail_multiplier": 5.0, "adx_threshold": 20}),
    ("5.0+margin0.002", {"atr_trail_multiplier": 5.0, "trend_margin": 0.002}),
    ("5.0+margin0.001", {"atr_trail_multiplier": 5.0, "trend_margin": 0.001}),
    ("5.0+rsi65", {"atr_trail_multiplier": 5.0, "rsi_upper": 65}),
    ("5.0+fast8", {"atr_trail_multiplier": 5.0, "fast_ema": 8}),
    ("5.0+fast10", {"atr_trail_multiplier": 5.0, "fast_ema": 10}),
    ("5.0+slow20", {"atr_trail_multiplier": 5.0, "slow_ema": 20}),
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
    print(f"{name:25s} => SCORE: {score:>10s}  {trades}  {dd}")
