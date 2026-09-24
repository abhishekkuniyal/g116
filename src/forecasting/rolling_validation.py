import pandas as pd
import numpy as np

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor


# ---------------------------------------------------------
# 1. Load the modeling dataset
# ---------------------------------------------------------

DATA_PATH = "data/processed/demand_forecasting.csv"

df = pd.read_csv(DATA_PATH)

# Convert financial year into a sortable year number.
# Example:
# "2015-16" -> 2015
df["year_start"] = df["financial_year"].str[:4].astype(int)

print("Loaded dataset:", df.shape)


# ---------------------------------------------------------
# 2. Keep only rows where the target exists
# ---------------------------------------------------------

df = df[df["target_sales"].notna()].copy()

print("Target-available rows:", len(df))


# ---------------------------------------------------------
# 3. Define the forecasting periods
# ---------------------------------------------------------

forecast_years = [
    "2019-20",
    "2020-21",
    "2021-22",
    "2022-23",
    "2023-24"
]


# ---------------------------------------------------------
# 4. Define model features
# ---------------------------------------------------------

numeric_features = [
    "sales_current",
    "sales_lag_1",
    "requirement_current",
    "requirement_lag_1",
    "availability_current",
    "availability_lag_1"
]

categorical_features = [
    "state",
    "fertilizer_type"
]

all_features = numeric_features + categorical_features


# ---------------------------------------------------------
# 5. Preprocessing for Linear Regression / Random Forest
# ---------------------------------------------------------

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),
        (
            "numeric",
            "passthrough",
            numeric_features
        )
    ]
)


# ---------------------------------------------------------
# 6. Create models
# ---------------------------------------------------------

linear_model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", LinearRegression())
    ]
)


random_forest_model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "model",
            RandomForestRegressor(
                n_estimators=200,
                random_state=42,
                n_jobs=-1
            )
        )
    ]
)


# ---------------------------------------------------------
# 7. Store results
# ---------------------------------------------------------

results = []


# ---------------------------------------------------------
# 8. Expanding-window evaluation
# ---------------------------------------------------------

for forecast_year in forecast_years:

    print("\n" + "=" * 60)
    print("Forecast year:", forecast_year)
    print("=" * 60)

    forecast_year_start = int(forecast_year[:4])

    # Training data:
    # Everything before the forecast year
    train = df[df["year_start"] < forecast_year_start].copy()

    # Test data:
    # Exactly the year we are trying to forecast
    test = df[df["financial_year"] == forecast_year].copy()

    print("Training rows:", len(train))
    print("Test rows:", len(test))

    X_train = train[all_features]
    y_train = train["target_sales"]

    X_test = test[all_features]
    y_test = test["target_sales"]


    # -----------------------------------------------------
    # Naive baseline
    # Prediction = current year's sales
    # -----------------------------------------------------

    naive_predictions = test["sales_current"]

    results.append({
        "forecast_year": forecast_year,
        "model": "Naive",
        "MAE": mean_absolute_error(
            y_test,
            naive_predictions
        ),
        "RMSE": np.sqrt(
            mean_squared_error(
                y_test,
                naive_predictions
            )
        ),
        "R2": r2_score(
            y_test,
            naive_predictions
        )
    })


    # -----------------------------------------------------
    # Linear Regression
    # -----------------------------------------------------

    linear_model.fit(X_train, y_train)

    linear_predictions = linear_model.predict(X_test)

    results.append({
        "forecast_year": forecast_year,
        "model": "Linear Regression",
        "MAE": mean_absolute_error(
            y_test,
            linear_predictions
        ),
        "RMSE": np.sqrt(
            mean_squared_error(
                y_test,
                linear_predictions
            )
        ),
        "R2": r2_score(
            y_test,
            linear_predictions
        )
    })


    # -----------------------------------------------------
    # Random Forest
    # -----------------------------------------------------

    random_forest_model.fit(X_train, y_train)

    rf_predictions = random_forest_model.predict(X_test)

    results.append({
        "forecast_year": forecast_year,
        "model": "Random Forest",
        "MAE": mean_absolute_error(
            y_test,
            rf_predictions
        ),
        "RMSE": np.sqrt(
            mean_squared_error(
                y_test,
                rf_predictions
            )
        ),
        "R2": r2_score(
            y_test,
            rf_predictions
        )
    })


# ---------------------------------------------------------
# 9. Create results DataFrame
# ---------------------------------------------------------

results_df = pd.DataFrame(results)

print("\n\n")
print("=" * 80)
print("ROLLING VALIDATION RESULTS")
print("=" * 80)

print(results_df.to_string(index=False))


# ---------------------------------------------------------
# 10. Average performance across forecast periods
# ---------------------------------------------------------

summary = (
    results_df
    .groupby("model")[["MAE", "RMSE", "R2"]]
    .mean()
    .reset_index()
)

print("\n")
print("=" * 80)
print("AVERAGE PERFORMANCE")
print("=" * 80)

print(summary.to_string(index=False))


# ---------------------------------------------------------
# 11. Save results
# ---------------------------------------------------------

output_path = "data/processed/rolling_validation_results.csv"

results_df.to_csv(output_path, index=False)

print("\nResults saved to:", output_path)
