import pandas as pd

# Load datasets
datasets = {
    'Score': pd.read_csv("tetris_scores-Score.csv")["Max Score"],
    'Score + Height': pd.read_csv("tetris_scores-Score+Height.csv")["Max Score"],
    'Full Heuristics': pd.read_csv("tetris_scores-noAB.csv")["Max Score"],
    'Full Heuristics + AB Pruning': pd.read_csv("tetris_scores-AB.csv")["Max Score"]
}

# Compute statistics
stats = {
    'Experiment': [],
    'Mean': [],
    'Median': [],
    'Standard Deviation': []
}

for key, data in datasets.items():
    stats['Experiment'].append(key)
    stats['Mean'].append(data.mean())
    stats['Median'].append(data.median())
    stats['Standard Deviation'].append(data.std())

# Create DataFrame
stats_df = pd.DataFrame(stats)

print(stats_df)


# Load datasets with correct column names
dqn_scores = pd.read_csv("tetris_scores-DQN.csv")["Score"]
ab_scores = pd.read_csv("tetris_scores-AB.csv")["Max Score"]

# Compute statistics
stats = {
    'Experiment': ['DQN', 'AB Pruning'],
    'Mean': [dqn_scores.mean(), ab_scores.mean()],
    'Median': [dqn_scores.median(), ab_scores.median()],
    'Standard Deviation': [dqn_scores.std(), ab_scores.std()]
}

# Create DataFrame
comparison_df = pd.DataFrame(stats)

print(comparison_df)