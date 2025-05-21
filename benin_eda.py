# === IMPORTS ===
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# === SETTINGS ===
sns.set(style="whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)

# Ensure plots directory exists
PLOTS_DIR = os.path.join("notebooks", "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

# === 1. LOAD DATA ===
file_path = os.path.join("data", "raw_data_benin.csv")
df = pd.read_csv(file_path, parse_dates=["Timestamp"])
df.set_index("Timestamp", inplace=True)

# === 2. SUMMARY STATISTICS & MISSING VALUE REPORT ===
print("\n--- Summary Statistics ---")
print(df.describe())

print("\n--- Missing Values Report ---")
missing_counts = df.isnull().sum()
missing_percent = (missing_counts / len(df)) * 100
missing_report = pd.DataFrame({
    "Missing Count": missing_counts,
    "Missing %": missing_percent
})
print(missing_report)

print("\n--- Columns with >5% Missing ---")
print(missing_report[missing_report["Missing %"] > 5])

# === 3. OUTLIER DETECTION & CLEANING ===

# Columns for Z-score based outlier detection
zscore_cols = ["GHI", "DNI", "DHI", "ModA", "ModB", "WS", "WSgust"]

# Compute Z-scores
z_scores = df[zscore_cols].apply(lambda x: stats.zscore(x, nan_policy='omit'))

# Flagging outliers with |Z| > 3
outlier_flags = (np.abs(z_scores) > 3)

# Create a copy for cleaning
df_cleaned = df.copy()

# Drop rows with NaN or outliers in key irradiance metrics
irradiance_cols = ["GHI", "DNI", "DHI"]
irradiance_outliers = outlier_flags[irradiance_cols].any(axis=1)
df_cleaned = df_cleaned[~irradiance_outliers]
df_cleaned = df_cleaned.dropna(subset=irradiance_cols)

# For other sensor values, impute NaNs and outliers with median
for col in ["ModA", "ModB", "WS", "WSgust"]:
    median_val = df_cleaned[col].median()
    df_cleaned.loc[outlier_flags[col], col] = np.nan
    df_cleaned[col] = df_cleaned[col].fillna(median_val)

# Export cleaned data
cleaned_path = os.path.join("data", "benin_clean.csv")
df_cleaned.to_csv(cleaned_path)
print(f"\nCleaned data exported to: {cleaned_path}")

# === 4. TIME SERIES ANALYSIS ===

# Plot time series of GHI, DNI, DHI, Tamb
fig, axs = plt.subplots(4, 1, figsize=(14, 18), sharex=True)
df_cleaned["GHI"].plot(ax=axs[0], title="GHI Over Time")
df_cleaned["DNI"].plot(ax=axs[1], title="DNI Over Time")
df_cleaned["DHI"].plot(ax=axs[2], title="DHI Over Time")
df_cleaned["Tamb"].plot(ax=axs[3], title="Tamb Over Time")

for ax in axs:
    ax.set_ylabel("Value")
    ax.grid(True)

plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "time_series_ghi_dni_dhi_tamb.png"))
plt.close()

# === 5. CLEANING IMPACT ANALYSIS ===

if "Cleaning" in df.columns:
    grouped = df.groupby("Cleaning")[["ModA", "ModB"]].mean()
    grouped.plot(kind="bar", title="Effect of Cleaning on ModA and ModB", rot=0)
    plt.ylabel("Average Value")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "cleaning_impact.png"))
    plt.close()

# === 6. CORRELATION & RELATIONSHIPS ===

# Heatmap
corr_cols = ["GHI", "DNI", "DHI", "TModA", "TModB", "Tamb", "RH", "WS", "BP"]
corr_matrix = df_cleaned[corr_cols].corr()

plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation Heatmap")
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "correlation_heatmap.png"))
plt.close()

# Scatter Plots
scatter_pairs = [
    ("WS", "GHI"),
    ("WSgust", "GHI"),
    ("RH", "Tamb"),
    ("RH", "GHI")
]

for x, y in scatter_pairs:
    plt.figure()
    sns.scatterplot(data=df_cleaned, x=x, y=y, alpha=0.5)
    plt.title(f"{y} vs {x}")
    plt.tight_layout()
    filename = f"{x.lower()}_{y.lower()}_scatter.png".replace(" ", "_")
    plt.savefig(os.path.join(PLOTS_DIR, filename))
    plt.close()

# === 7. WIND & DISTRIBUTION ANALYSIS ===

# Wind Rose Plot (simplified polar plot)
if "WD" in df_cleaned.columns and "WS" in df_cleaned.columns:
    wd_rad = np.radians(df_cleaned["WD"].dropna())
    ws = df_cleaned["WS"].dropna()

    plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, polar=True)
    ax.scatter(wd_rad, ws, alpha=0.5)
    ax.set_title("Simulated Wind Rose (WD vs WS)", y=1.1)
    plt.savefig(os.path.join(PLOTS_DIR, "wind_rose.png"))
    plt.close()

# Histograms
for col in ["GHI", "WS"]:
    plt.figure()
    sns.histplot(df_cleaned[col].dropna(), kde=True, bins=50)
    plt.title(f"Histogram of {col}")
    plt.xlabel(col)
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, f"{col.lower()}_histogram.png"))
    plt.close()

# === 8. TEMPERATURE ANALYSIS ===

# Analyze RH vs Tamb and GHI
plt.figure()
sns.scatterplot(data=df_cleaned, x="RH", y="Tamb", hue="GHI", palette="viridis", alpha=0.7)
plt.title("Tamb vs RH colored by GHI")
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "tamb_rh_ghi_scatter.png"))
plt.close()

# === 9. BUBBLE CHART ===

# Bubble chart: GHI (x), Tamb (y), bubble size = RH
plt.figure()
bubble_sizes = df_cleaned["RH"].fillna(0) * 2  # Scale RH for visibility
plt.scatter(df_cleaned["GHI"], df_cleaned["Tamb"], s=bubble_sizes, alpha=0.4, c="skyblue", edgecolors="w", linewidths=0.5)
plt.title("Bubble Chart: GHI vs Tamb (size = RH)")
plt.xlabel("GHI (W/m²)")
plt.ylabel("Tamb (°C)")
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "ghi_tamb_bubble.png"))
plt.close()
