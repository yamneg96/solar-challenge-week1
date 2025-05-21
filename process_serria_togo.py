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

# === FUNCTION: PROCESS A COUNTRY DATASET ===
def process_country_data(country_name, raw_filename, cleaned_filename):
    print(f"\n=== Processing: {country_name} ===")

    # Load raw data
    file_path = os.path.join("data", raw_filename)
    df = pd.read_csv(file_path, parse_dates=["Timestamp"])
    df.set_index("Timestamp", inplace=True)

    # Summary statistics and missing value report
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

    # Outlier Detection & Cleaning
    zscore_cols = ["GHI", "DNI", "DHI", "ModA", "ModB", "WS", "WSgust"]
    z_scores = df[zscore_cols].apply(lambda x: stats.zscore(x, nan_policy='omit'))
    outlier_flags = (np.abs(z_scores) > 3)

    df_cleaned = df.copy()

    # Drop rows with NaN or outliers in GHI, DNI, DHI
    irradiance_outliers = outlier_flags[["GHI", "DNI", "DHI"]].any(axis=1)
    df_cleaned = df_cleaned[~irradiance_outliers]
    df_cleaned = df_cleaned.dropna(subset=["GHI", "DNI", "DHI"])

    # Impute ModA, ModB, WS, WSgust outliers/missing with median
    for col in ["ModA", "ModB", "WS", "WSgust"]:
        median_val = df_cleaned[col].median()
        df_cleaned.loc[outlier_flags[col], col] = np.nan
        df_cleaned[col] = df_cleaned[col].fillna(median_val)

    # Export cleaned data
    cleaned_path = os.path.join("data", cleaned_filename)
    df_cleaned.to_csv(cleaned_path)
    print(f"\nCleaned data exported to: {cleaned_path}")

    # Time Series Plot
    fig, axs = plt.subplots(4, 1, figsize=(14, 18), sharex=True)
    df_cleaned["GHI"].plot(ax=axs[0], title=f"{country_name} - GHI Over Time")
    df_cleaned["DNI"].plot(ax=axs[1], title=f"{country_name} - DNI Over Time")
    df_cleaned["DHI"].plot(ax=axs[2], title=f"{country_name} - DHI Over Time")
    df_cleaned["Tamb"].plot(ax=axs[3], title=f"{country_name} - Tamb Over Time")

    for ax in axs:
        ax.set_ylabel("Value")
        ax.grid(True)

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, f"time_series_{country_name.lower().replace(' ', '_')}.png"))
    plt.close()

    # Cleaning Impact Analysis
    if "Cleaning" in df.columns:
        grouped = df.groupby("Cleaning")[["ModA", "ModB"]].mean()
        grouped.plot(kind="bar", title=f"{country_name} - Effect of Cleaning on ModA and ModB", rot=0)
        plt.ylabel("Average Value")
        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_DIR, f"cleaning_impact_{country_name.lower().replace(' ', '_')}.png"))
        plt.close()

    # Correlation & Relationships
    corr_cols = ["GHI", "DNI", "DHI", "TModA", "TModB", "Tamb", "RH", "WS", "BP"]
    corr_matrix = df_cleaned[corr_cols].corr()

    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title(f"{country_name} - Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, f"correlation_heatmap_{country_name.lower().replace(' ', '_')}.png"))
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
        plt.title(f"{country_name}: {y} vs {x}")
        plt.tight_layout()
        filename = f"{x.lower()}_{y.lower()}_scatter_{country_name.lower().replace(' ', '_')}.png"
        plt.savefig(os.path.join(PLOTS_DIR, filename))
        plt.close()

    # Wind Rose Simulation
    if "WD" in df_cleaned.columns and "WS" in df_cleaned.columns:
        wd_rad = np.radians(df_cleaned["WD"].dropna())
        ws = df_cleaned["WS"].dropna()

        plt.figure(figsize=(8, 8))
        ax = plt.subplot(111, polar=True)
        ax.scatter(wd_rad, ws, alpha=0.5)
        ax.set_title(f"{country_name} - Simulated Wind Rose", y=1.1)
        plt.savefig(os.path.join(PLOTS_DIR, f"wind_rose_{country_name.lower().replace(' ', '_')}.png"))
        plt.close()

    # Histograms
    for col in ["GHI", "WS"]:
        plt.figure()
        sns.histplot(df_cleaned[col].dropna(), kde=True, bins=50)
        plt.title(f"{country_name} - Histogram of {col}")
        plt.xlabel(col)
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_DIR, f"{col.lower()}_histogram_{country_name.lower().replace(' ', '_')}.png"))
        plt.close()

    # Temperature Analysis
    plt.figure()
    sns.scatterplot(data=df_cleaned, x="RH", y="Tamb", hue="GHI", palette="viridis", alpha=0.7)
    plt.title(f"{country_name} - Tamb vs RH colored by GHI")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, f"tamb_rh_ghi_scatter_{country_name.lower().replace(' ', '_')}.png"))
    plt.close()

    # Bubble Chart
    plt.figure()
    bubble_sizes = df_cleaned["RH"].fillna(0) * 2
    plt.scatter(df_cleaned["GHI"], df_cleaned["Tamb"], s=bubble_sizes,
                alpha=0.4, c="skyblue", edgecolors="w", linewidths=0.5)
    plt.title(f"{country_name} - Bubble Chart: GHI vs Tamb (size = RH)")
    plt.xlabel("GHI (W/m²)")
    plt.ylabel("Tamb (°C)")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, f"ghi_tamb_bubble_{country_name.lower().replace(' ', '_')}.png"))
    plt.close()

# === PROCESS SIERRA LEONE ===
process_country_data(
    country_name="Sierra Leone",
    raw_filename="sierraleone-bumbuna.csv",
    cleaned_filename="sierra_leone_clean.csv"
)

# === PROCESS TOGO ===
process_country_data(
    country_name="Togo",
    raw_filename="togo-dapaong_qc.csv",
    cleaned_filename="togo_clean.csv"
)
