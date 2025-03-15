import matplotlib.pyplot as plt
import pandas as pd

# Load all datasets
datasets = {
    'Score': pd.read_csv("tetris_scores-Score.csv")["Max Score"],
    'Score + Height': pd.read_csv("tetris_scores-Score+Height.csv")["Max Score"],
    'Full Heuristics': pd.read_csv("tetris_scores-noAB.csv")["Max Score"],
    'Full Heuristics + AB Pruning': pd.read_csv("tetris_scores-AB.csv")["Max Score"]
}

# Create figure and axis
plt.figure(figsize=(14, 8))
ax = plt.gca()

# Create boxplot
boxplot = ax.boxplot(
    datasets.values(),
    patch_artist=True,
    labels=datasets.keys(),
    showmeans=True,
    meanline=True,
    medianprops={'color': 'black', 'linewidth': 2},
    meanprops={'color': 'red', 'linewidth': 2}
)

# Color boxes
colors = ['#B3CDE3', '#FBB4AE', '#CCEBC5', '#DECBE4']
for patch, color in zip(boxplot['boxes'], colors):
    patch.set_facecolor(color)

# Add labels and title
plt.xlabel('Experiments', fontsize=12)
plt.ylabel('Max Score', fontsize=12)
plt.title('Tetris Performance Comparison Across Different Experiments', fontsize=14, pad=20)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Add legend
plt.legend([boxplot['medians'][0], boxplot['means'][0]], 
           ['Median', 'Mean'], 
           loc='upper right')

plt.tight_layout()
plt.show()