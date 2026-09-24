import pandas as pd
import numpy as np

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ---------------------------------------------------------
# 1. Load modeling dataset
# ---------------------------------------------------------

DATA_PATH = "data/processed/demand_forecasting.csv"

df = pd.read_csv(DATA_PATH)

df["year_start"] = df["financial_year"].str[:4].astype(int)

# Keep only rows where the next year's actual sales are known
df = df[df["target_sales"].notna()].copy()

print("Loaded dataset:", df.shape)


# ---------------------------------------------------------
# 2. Forecast years
# ---------------------------------------------------------

forecast_years = [
    "2019-20",
    "2020-21",
    "2021-22",
    "2022-23",
    "2023-24"
]


# ---------------------------------------------------------
# 3. Store results
# ---------------------------------------------------------

results = []


# ---------------------------------------------------------
# 4. Expanding-window evaluation
# ---------------------------------------------------------

for forecast_year in forecast_years:

    print("\n" + "=" * 60)
    print("Forecast year:", forecast_year)
    print("=" * 60)

    forecast_year_start = int(forecast_year[:4])

    # All information available before forecast year
    train = df[df["year_start"] < forecast_year_start].copy()

    # Year being forecast
    test = df[df["financial_year"] == forecast_year].copy()

    print("Training rows:", len(train))
    print("Test rows:", len(test))


    # -----------------------------------------------------
    # Recent-change prediction
    #
    # Forecast =
    # current sales + most recent annual change
    #
    # Since:
    #
    # sales_change =
    # current sales - previous year's sales
    #
    # Forecast =
    # 2 * current sales - previous year's sales
    # -----------------------------------------------------

    test["recent_change_prediction"] = (
        2 * test["sales_current"]
        - test["sales_lag_1"]
    )


    # -----------------------------------------------------
    # Actual values
    # -----------------------------------------------------

    y_true = test["target_sales"]
    y_pred = test["recent_change_prediction"]


    # -----------------------------------------------------
    # Metrics
    # -----------------------------------------------------

    mae = mean_absolute_error(
        y_true,
        y_pred
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_true,
            y_pred
        )
    )

    r2 = r2_score(
        y_true,
        y_pred
    )


    results.append({
        "forecast_year": forecast_year,
        "model": "Recent Change",
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2
    })


    print(f"MAE : {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R2  : {r2:.4f}")


# ---------------------------------------------------------
# 5. Results
# ---------------------------------------------------------

results_df = pd.DataFrame(results)

print("\n")
print("=" * 80)
print("RECENT CHANGE BASELINE RESULTS")
print("=" * 80)

print(
    results_df.to_string(index=False)
)


# ---------------------------------------------------------
# 6. Average performance
# ---------------------------------------------------------

summary = (
    results_df[
        ["MAE", "RMSE", "R2"]
    ]
    .mean()
)

print("\n")
print("=" * 80)
print("AVERAGE RECENT CHANGE PERFORMANCE")
print("=" * 80)

print(f"MAE : {summary['MAE']:.4f}")
print(f"RMSE: {summary['RMSE']:.4f}")
print(f"R2  : {summary['R2']:.4f}")


# ---------------------------------------------------------
# 7. Save results
# ---------------------------------------------------------

OUTPUT_PATH = (
    "data/processed/"
    "recent_change_baseline_results.csv"
)

results_df.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\nResults saved to:", OUTPUT_PATH)
