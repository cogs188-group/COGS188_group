import pandas as pd
import matplotlib.pyplot as plt

# Load datasets with correct column names
dqn_scores = pd.read_csv("tetris_scores-DQN.csv")["Score"]
ab_scores = pd.read_csv("tetris_scores-AB.csv")["Max Score"]

# Create a figure and axis
plt.figure(figsize=(10, 6))
ax = plt.gca()

# Create boxplot
boxplot = ax.boxplot(
    [dqn_scores, ab_scores],
    patch_artist=True,
    labels=["DQN", "AB Pruning"],
    showmeans=True,
    meanline=True,
    medianprops={'color': 'black', 'linewidth': 2},
    meanprops={'color': 'red', 'linewidth': 2}
)

# Color boxes
colors = ['#B3CDE3', '#FBB4AE']
for patch, color in zip(boxplot['boxes'], colors):
    patch.set_facecolor(color)

# Add labels and title
plt.xlabel('Experiment', fontsize=12)
plt.ylabel('Score', fontsize=12)
plt.title('Comparison of DQN vs AB Pruning in Tetris', fontsize=14, pad=20)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Add legend
plt.legend([boxplot['medians'][0], boxplot['means'][0]], 
           ['Median', 'Mean'], 
           loc='upper right')

plt.tight_layout()
plt.show()
