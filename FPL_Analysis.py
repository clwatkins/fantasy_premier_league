import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(context="poster", style="whitegrid", font_scale=.75)

data = pd.read_json('~/OneDrive/Projects/FPL_Tracker/Data/FPL_API_Dump.json')
data = data.transpose()

data['now_cost'] = data['now_cost'].astype(int)/10
data['total_points'] = data['total_points'].astype(int)
data['points_per_game'] = data['points_per_game'].astype(float)
data['PPGBP'] = data['total_points']/data['now_cost']

fig = sns.jointplot(x='now_cost', y='points_per_game', data=data, kind='reg', color='k', scatter_kws={"s": data['total_points']/5})
plt.xlabel('Transfer Cost (Millions)')
plt.ylabel('Points per Game')
# plt.title('Pricing rationality: PPG v Transfer fee')
plt.savefig("joint1.png", dpi=300, transparent=True, pad_inches=0.25)
plt.close()

fig2 = sns.violinplot(x='team_name', y='points_per_game', data=data, palette='Set3', inner='quartile', width=0.75, scale='area')
plt.xlabel('Team')
plt.xticks(rotation='vertical')
plt.ylabel('Points Per Game')
plt.title('Points per Game distribution by team')
plt.gcf().subplots_adjust(bottom=0.3)
plt.savefig("violin1.png", dpi=300, transparent=True, pad_inches=0.25)
plt.close()

fig3 = sns.boxplot(x='type_name', y='PPGBP', data=data)
plt.xlabel('Position')
plt.ylabel('Points earned/Transfer price (M)')
plt.title('Value for money by position')
plt.savefig("box1.png", dpi=300, transparent=True, pad_inches=0.25)
plt.close()


fig4 = sns.boxplot(x='type_name', y='points_per_game', data=data)
plt.xlabel('Position')
plt.ylabel('Points per Game')
plt.title('Points per Game distribution by Position')
plt.savefig("box2.png", dpi=300, transparent=True, pad_inches=0.25)
plt.close()


# machine learning to establish data trends
