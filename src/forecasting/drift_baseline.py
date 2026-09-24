import pandas as pd
import numpy as np

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ---------------------------------------------------------
# 1. Load the modeling dataset
# ---------------------------------------------------------

DATA_PATH = "data/processed/demand_forecasting.csv"

df = pd.read_csv(DATA_PATH)

df["year_start"] = df["financial_year"].str[:4].astype(int)

# Only rows where the next year's actual sales are known
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

    # Historical data available before the forecast year
    train = df[df["year_start"] < forecast_year_start].copy()

    # Year we want to forecast
    test = df[df["financial_year"] == forecast_year].copy()

    print("Training rows:", len(train))
    print("Test rows:", len(test))


    # -----------------------------------------------------
    # Calculate historical annual change
    #
    # sales_change =
    # current year's sales - previous year's sales
    # -----------------------------------------------------

    train = train.sort_values(
        ["state", "fertilizer_type", "year_start"]
    )

    train["sales_change"] = (
        train.groupby(
            ["state", "fertilizer_type"]
        )["sales_current"]
        .diff()
    )


    # -----------------------------------------------------
    # Average historical change for each
    # State + Fertilizer combination
    # -----------------------------------------------------

    average_change = (
        train
        .groupby(["state", "fertilizer_type"])["sales_change"]
        .mean()
        .reset_index()
        .rename(
            columns={
                "sales_change": "average_change"
            }
        )
    )


    # -----------------------------------------------------
    # Attach historical trend to test rows
    # -----------------------------------------------------

    test = test.merge(
        average_change,
        on=["state", "fertilizer_type"],
        how="left"
    )


    # -----------------------------------------------------
    # Drift prediction
    #
    # Forecast =
    # current sales + average historical change
    # -----------------------------------------------------

    test["drift_prediction"] = (
        test["sales_current"]
        + test["average_change"].fillna(0)
    )


    # -----------------------------------------------------
    # Calculate metrics
    # -----------------------------------------------------

    y_true = test["target_sales"]
    y_pred = test["drift_prediction"]

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
        "model": "Drift",
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
print("DRIFT BASELINE RESULTS")
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
print("AVERAGE DRIFT PERFORMANCE")
print("=" * 80)

print(f"MAE : {summary['MAE']:.4f}")
print(f"RMSE: {summary['RMSE']:.4f}")
print(f"R2  : {summary['R2']:.4f}")


# ---------------------------------------------------------
# 7. Save results
# ---------------------------------------------------------

OUTPUT_PATH = (
    "data/processed/"
    "drift_baseline_results.csv"
)

results_df.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\nResults saved to:", OUTPUT_PATH)
