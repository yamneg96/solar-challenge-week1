# === IMPORTS ===
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import f_oneway

# === SETTINGS ===
sns.set(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)

# Ensure plots directory exists
PLOTS_DIR = os.path.join("notebooks", "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

# === 1. LOAD CLEANED DATA ===

def load_and_label_data(filepath, country_name):
    df = pd.read_csv(filepath, parse_dates=["Timestamp"])
    df["Country"] = country_name
    return df

benin = load_and_label_data(os.path.join("data", "benin_clean.csv"), "Benin")
sierra_leone = load_and_label_data(os.path.join("data", "sierra_leone_clean.csv"), "Sierra Leone")
togo = load_and_label_data(os.path.join("data", "togo_clean.csv"), "Togo")

# Combine all data
df_all = pd.concat([benin, sierra_leone, togo], ignore_index=True)

# === 2. METRIC COMPARISON - BOXPLOTS ===

for metric in ["GHI", "DNI", "DHI"]:
    plt.figure()
    sns.boxplot(x="Country", y=metric, data=df_all, palette="Set2")
    plt.title(f"{metric} Comparison by Country")
    plt.xlabel("Country")
    plt.ylabel(metric)
    plt.tight_layout()
    plot_filename = f"{metric.lower()}_boxplot_comparison.png"
    plt.savefig(os.path.join(PLOTS_DIR, plot_filename))
    plt.close()

# === 3. SUMMARY STATISTICS TABLE ===

summary_stats = df_all.groupby("Country")[["GHI", "DNI", "DHI"]].agg(["mean", "median", "std"])
summary_stats.columns = ["_".join(col) for col in summary_stats.columns]
print("\n--- Summary Statistics Table ---")
print(summary_stats)

# Optionally save to CSV
summary_stats_path = os.path.join("data", "summary_statistics_comparison.csv")
summary_stats.to_csv(summary_stats_path)
print(f"\nSummary statistics saved to {summary_stats_path}")

# === 4. STATISTICAL TESTING - ONE-WAY ANOVA ===

# Extract GHI values by country
ghi_benin = benin["GHI"].dropna()
ghi_sl = sierra_leone["GHI"].dropna()
ghi_togo = togo["GHI"].dropna()

f_stat, p_val = f_oneway(ghi_benin, ghi_sl, ghi_togo)

print("\n--- One-way ANOVA on GHI ---")
print(f"F-statistic: {f_stat:.4f}")
print(f"P-value: {p_val:.4e}")

# Interpretation
if p_val < 0.05:
    print("Interpretation: Statistically significant differences exist in GHI between countries.")
else:
    print("Interpretation: No statistically significant difference in GHI between countries.")

# === 5. KEY OBSERVATIONS ===

print("\n--- Key Observations ---")
print("""
• Benin shows consistently higher median GHI compared to Sierra Leone and Togo.
• GHI variability is greatest in Sierra Leone, suggesting less predictability in solar yield.
• Togo has moderate and consistent solar irradiance, potentially balancing yield and stability.
""")

# === 6. BONUS - VISUAL SUMMARY ===

avg_ghi = df_all.groupby("Country")["GHI"].mean().sort_values(ascending=False)

plt.figure()
sns.barplot(x=avg_ghi.index, y=avg_ghi.values, palette="viridis")
plt.title("Average GHI by Country")
plt.xlabel("Country")
plt.ylabel("Average GHI (W/m²)")
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "avg_ghi_ranking.png"))
plt.close()
