import subprocess

with open("backtest.py", "r") as f:
    original = f.read()

base = [("or (prev_ema_f <= prev_ema_s and ema_f > ema_s)", "")]

for trail in [5.2, 5.5, 5.8, 6.0, 6.5, 7.0, 8.0, 10.0]:
    for pos_size in [800, 1000, 1500, 2000]:
        combo = base + [
            ("atr_trail_multiplier = 4.5", f"atr_trail_multiplier = {trail}"),
            ("position_size = 1000.0", f"position_size = {pos_size}.0"),
        ]
        modified = original
        for old_val, new_val in combo:
            modified = modified.replace(old_val, new_val, 1)
        with open("backtest.py", "w") as f:
            f.write(modified)
        result = subprocess.run(["python3", "backtest.py"], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        score_line = [l for l in lines if l.startswith('SCORE:')]
        if score_line:
            score = score_line[0].split(': ')[1]
            t = next((l.split(':')[1].strip() for l in lines if 'Trades:' in l), '')
            w = next((l.split(':')[1].strip() for l in lines if 'Win rate:' in l), '')
            d = next((l.split(':')[1].strip() for l in lines if 'Max DD:' in l), '')
            print(f"trail={trail:>4} pos={pos_size:>5}  SCORE={score:>10}  trades={t}  wr={w}  dd={d}")

with open("backtest.py", "w") as f:
    f.write(original)
