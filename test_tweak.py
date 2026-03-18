import subprocess, re

params_to_try = [
    ("atr_trail=4.5", {"atr_trail_multiplier": 4.5}),
    ("atr_trail=4.0", {"atr_trail_multiplier": 4.0}),
    ("atr_trail=3.5", {"atr_trail_multiplier": 3.5}),
    ("atr_trail=5.0", {"atr_trail_multiplier": 5.0}),
    ("adx_thresh=18", {"adx_threshold": 18}),
    ("adx_thresh=15", {"adx_threshold": 15}),
    ("cooldown=3", {"cooldown_bars": 3}),
    ("cooldown=0", {"cooldown_bars": 0}),
    ("trend_margin=0.001", {"trend_margin": 0.001}),
    ("trend_margin=0.002", {"trend_margin": 0.002}),
    ("rsi_upper=65", {"rsi_upper": 65}),
    ("rsi_upper=70", {"rsi_upper": 70}),
    ("vol_mult=1.0", {"vol_mult": 1.0}),
]

for name, overrides in params_to_try:
    with open("backtest.py", "r") as f:
        code = f.read()
    for k, v in overrides.items():
        import re as re2
        code = re2.sub(rf'{k}\s*=\s*[\d.]+', f'{k} = {v}', code)
    with open("backtest_tmp2.py", "w") as f:
        f.write(code)
    result = subprocess.run(["python3", "backtest_tmp2.py"], capture_output=True, text=True)
    score_line = [l for l in result.stdout.strip().split('\n') if l.startswith("SCORE:")]
    score = score_line[0].split(":")[1].strip() if score_line else "ERROR"
    trades_line = [l for l in result.stdout.strip().split('\n') if 'Trades' in l]
    trades = trades_line[0].strip() if trades_line else ""
    print(f"{name:25s} => SCORE: {score:>10s}  {trades}")
