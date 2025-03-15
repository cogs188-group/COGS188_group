import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("tetris_scores-AB.csv")

# Plotting the scores
plt.figure(figsize=(12, 6))
plt.plot(df["Game"], df["Max Score"], marker='o', linestyle='-', color='b', alpha=0.7, label="Max Score")
plt.axhline(y=df["Max Score"].mean(), color='r', linestyle='--', label=f'Average Score ({df["Max Score"].mean():.2f})')

# Labels and Title
plt.xlabel("Game Number")
plt.ylabel("Max Score")
plt.title("Tetris AB Performance Over 100 Games")
plt.legend()
plt.grid(True)

# Show plot
plt.show()