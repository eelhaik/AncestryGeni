import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load data
file_path = 'Filtered_New_Test_Samples_No_Code6.xlsx'
data = pd.read_excel(file_path)

# Rename admixture columns
admixture_column_names = [
    'Z_Africa1', 'Z_Africa2', 'Z_CentralAsia', 'Z_CentralEurope', 
    'Z_EastAsia', 'Z_FarEastAsia', 'Z_India', 'Z_NativeAmerica', 
    'Z_Scandinavia', 'Z_SouthEastAsia', 'Z_SouthEurope', 'Z_UK'
]
admixture_columns = [col for col in data.columns if col.startswith('Col')]
data.rename(columns=dict(zip(admixture_columns, admixture_column_names)), inplace=True)

# Filter data
filtered_data = data[data['Code'].isin([1, 2])]
selected_samples = filtered_data.groupby('Code')['Sample'].unique().apply(lambda x: x[:4])
selected_samples = np.concatenate(selected_samples.values)
filtered_data = filtered_data[filtered_data['Sample'].isin(selected_samples)]

# Extract admixture columns and prepare data
admixture_columns = [col for col in data.columns if col in admixture_column_names]
noise_levels = [f"f{i}" for i in range(10)]
grouped_data = filtered_data.set_index(['Sample', 'Noise_Level'])[admixture_columns]

# Map population codes to samples
population_codes = filtered_data.drop_duplicates(subset='Sample')[['Sample', 'Code']].set_index('Sample')
x_labels = [f"{sample} (Code {population_codes.loc[sample, 'Code']})" for sample in selected_samples]

# Plot settings
fig, ax = plt.subplots(figsize=(20, 10))
x = np.arange(len(selected_samples))
width = 0.9 / len(noise_levels)  # Compact bar groups more
colors = plt.cm.tab20(np.linspace(0, 1, len(admixture_columns)))

# Remove top and left spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Draw bars
for i, noise_level in enumerate(noise_levels):
    offsets = x + (i - (len(noise_levels) - 1) / 2) * width
    for j, sample in enumerate(selected_samples):
        values = grouped_data.loc[(sample, noise_level)].values.flatten()
        bottom = 0
        for k, value in enumerate(values):
            ax.bar(offsets[j], value, width, bottom=bottom,
                   color=colors[k], edgecolor='black', linewidth=0.2,
                   label=f"{admixture_columns[k]}" if i == 0 and j == 0 else "")
            bottom += value

# Adjust x-axis limits to remove extra white space
ax.set_xlim(-0.5, len(selected_samples) - 0.5)

# Set x-ticks and labels
ax.set_xticks(x)
ax.set_xticklabels(x_labels, rotation=45, ha="right")

# Add y-axis label
ax.set_ylabel("Admixture Proportions", fontsize=12)

# Add legend
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles, labels, loc='center left', bbox_to_anchor=(1, 0.5),
          title="Components", fontsize=10, title_fontsize=12)

# Adjust layout to minimize space between groups
plt.subplots_adjust(left=0.05, right=0.85, top=0.95, bottom=0.15)

# Save plot as .tif
output_path = 'admixture_proportions_plot_corrected.tif'
plt.savefig(output_path, dpi=650, bbox_inches='tight', format='tiff')
plt.close()

print(f"Plot saved at: {output_path}")
