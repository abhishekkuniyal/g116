import pandas as pd


# =========================================================
# 1. Load modeling dataset
# =========================================================

DATA_PATH = "data/processed/demand_forecasting.csv"

df = pd.read_csv(DATA_PATH)

print("Loaded dataset:", df.shape)


# =========================================================
# 2. Select the latest available year
#
# We are forecasting 2025-26 using information
# available through 2024-25.
# =========================================================

latest_year = "2024-25"

future = df[
    df["financial_year"] == latest_year
].copy()

print("2024-25 rows:", len(future))


# =========================================================
# 3. Naive persistence forecast
#
# Forecast for 2025-26 =
# actual sales in 2024-25
# =========================================================

future["forecast_year"] = "2025-26"

future["predicted_sales"] = (
    future["sales_current"]
)


# =========================================================
# 4. Add methodology information
# =========================================================

future["forecast_method"] = (
    "Naive Persistence"
)

future["forecast_basis"] = (
    "2024-25 sales"
)


# =========================================================
# 5. Select final output columns
# =========================================================

forecast = future[
    [
        "forecast_year",
        "state",
        "fertilizer_type",
        "sales_current",
        "predicted_sales",
        "forecast_method",
        "forecast_basis"
    ]
].copy()


# =========================================================
# 6. Rename for clarity
# =========================================================

forecast = forecast.rename(
    columns={
        "sales_current": "sales_2024_25"
    }
)


# =========================================================
# 7. Display forecast
# =========================================================

print("\n")
print("=" * 80)
print("FINAL 2025-26 FORECAST")
print("=" * 80)

print(
    forecast.to_string(index=False)
)


# =========================================================
# 8. Basic validation
# =========================================================

print("\n")
print("=" * 80)
print("FORECAST VALIDATION")
print("=" * 80)

print(
    "Forecast rows:",
    len(forecast)
)

print(
    "Missing predictions:",
    forecast["predicted_sales"].isna().sum()
)

print(
    "Negative predictions:",
    (forecast["predicted_sales"] < 0).sum()
)

print(
    "Unique states:",
    forecast["state"].nunique()
)

print(
    "Unique fertilizer types:",
    forecast["fertilizer_type"].nunique()
)


# =========================================================
# 9. Save final forecast
# =========================================================

OUTPUT_PATH = (
    "data/processed/"
    "final_forecast_2025_26.csv"
)

forecast.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\n")
print("=" * 80)
print("FINAL FORECAST SAVED")
print("=" * 80)

print(OUTPUT_PATH)
