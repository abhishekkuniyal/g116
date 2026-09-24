import pandas as pd
import numpy as np

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor


# =========================================================
# 1. Load dataset
# =========================================================

DATA_PATH = "data/processed/demand_forecasting.csv"

df = pd.read_csv(DATA_PATH)

df["year_start"] = df["financial_year"].str[:4].astype(int)

# Only rows where actual next-year sales are available
df = df[df["target_sales"].notna()].copy()

print("Loaded dataset:", df.shape)


# =========================================================
# 2. Forecast years
# =========================================================

forecast_years = [
    "2019-20",
    "2020-21",
    "2021-22",
    "2022-23",
    "2023-24"
]


# =========================================================
# 3. Random Forest features
# =========================================================

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


# =========================================================
# 4. Preprocessing
# =========================================================

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


# =========================================================
# 5. Random Forest
# =========================================================

random_forest = Pipeline(
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


# =========================================================
# 6. Store prediction-level results
# =========================================================

prediction_results = []


# =========================================================
# 7. Expanding-window evaluation
# =========================================================

for forecast_year in forecast_years:

    print("\n" + "=" * 70)
    print("Forecast year:", forecast_year)
    print("=" * 70)

    forecast_year_start = int(forecast_year[:4])

    # -----------------------------------------------------
    # Training data
    # -----------------------------------------------------

    train = df[
        df["year_start"] < forecast_year_start
    ].copy()

    # -----------------------------------------------------
    # Test data
    # -----------------------------------------------------

    test = df[
        df["financial_year"] == forecast_year
    ].copy()

    print("Training rows:", len(train))
    print("Test rows:", len(test))


    # -----------------------------------------------------
    # Train Random Forest
    # -----------------------------------------------------

    X_train = train[all_features]
    y_train = train["target_sales"]

    X_test = test[all_features]
    y_test = test["target_sales"]

    random_forest.fit(
        X_train,
        y_train
    )

    rf_predictions = random_forest.predict(
        X_test
    )


    # -----------------------------------------------------
    # Create prediction records
    # -----------------------------------------------------

    for i in range(len(test)):

        row = test.iloc[i]

        actual = row["target_sales"]

        naive_prediction = row["sales_current"]

        rf_prediction = rf_predictions[i]

        prediction_results.append({
            "forecast_year": forecast_year,
            "state": row["state"],
            "fertilizer_type": row["fertilizer_type"],

            "actual_sales": actual,

            "naive_prediction": naive_prediction,

            "random_forest_prediction": rf_prediction,

            "naive_error": (
                actual - naive_prediction
            ),

            "naive_absolute_error": (
                abs(actual - naive_prediction)
            ),

            "random_forest_error": (
                actual - rf_prediction
            ),

            "random_forest_absolute_error": (
                abs(actual - rf_prediction)
            ),

            "potential_reporting_break": (
                row["potential_reporting_break"]
            )
        })


# =========================================================
# 8. Convert to DataFrame
# =========================================================

predictions_df = pd.DataFrame(
    prediction_results
)


# =========================================================
# 9. Overall metrics
# =========================================================

print("\n")
print("=" * 80)
print("OVERALL ROLLING PERFORMANCE")
print("=" * 80)


for model_name, prediction_column in [
    ("Naive", "naive_prediction"),
    ("Random Forest", "random_forest_prediction")
]:

    y_true = predictions_df["actual_sales"]

    y_pred = predictions_df[prediction_column]

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

    print(
        f"{model_name:15s} "
        f"MAE={mae:.4f} "
        f"RMSE={rmse:.4f} "
        f"R2={r2:.4f}"
    )


# =========================================================
# 10. Model comparison by forecast year
# =========================================================

year_results = []

for forecast_year in forecast_years:

    subset = predictions_df[
        predictions_df["forecast_year"]
        == forecast_year
    ]

    y_true = subset["actual_sales"]

    # Naive
    naive_pred = subset["naive_prediction"]

    naive_mae = mean_absolute_error(
        y_true,
        naive_pred
    )

    naive_rmse = np.sqrt(
        mean_squared_error(
            y_true,
            naive_pred
        )
    )

    # Random Forest
    rf_pred = subset["random_forest_prediction"]

    rf_mae = mean_absolute_error(
        y_true,
        rf_pred
    )

    rf_rmse = np.sqrt(
        mean_squared_error(
            y_true,
            rf_pred
        )
    )

    year_results.append({
        "forecast_year": forecast_year,

        "naive_MAE": naive_mae,
        "naive_RMSE": naive_rmse,

        "random_forest_MAE": rf_mae,
        "random_forest_RMSE": rf_rmse
    })


year_results_df = pd.DataFrame(
    year_results
)


print("\n")
print("=" * 80)
print("PER-YEAR MODEL COMPARISON")
print("=" * 80)

print(
    year_results_df.to_string(
        index=False
    )
)


# =========================================================
# 11. Naive error by fertilizer
# =========================================================

fertilizer_errors = (
    predictions_df
    .groupby("fertilizer_type")
    .agg(
        observations=("actual_sales", "count"),
        naive_MAE=("naive_absolute_error", "mean"),
        rf_MAE=(
            "random_forest_absolute_error",
            "mean"
        )
    )
    .reset_index()
    .sort_values(
        "naive_MAE",
        ascending=False
    )
)


print("\n")
print("=" * 80)
print("ERROR BY FERTILIZER")
print("=" * 80)

print(
    fertilizer_errors.to_string(
        index=False
    )
)


# =========================================================
# 12. Naive error by state
# =========================================================

state_errors = (
    predictions_df
    .groupby("state")
    .agg(
        observations=("actual_sales", "count"),
        naive_MAE=("naive_absolute_error", "mean"),
        rf_MAE=(
            "random_forest_absolute_error",
            "mean"
        )
    )
    .reset_index()
    .sort_values(
        "naive_MAE",
        ascending=False
    )
)


print("\n")
print("=" * 80)
print("ERROR BY STATE")
print("=" * 80)

print(
    state_errors.to_string(
        index=False
    )
)


# =========================================================
# 13. Largest Naive errors
# =========================================================

largest_errors = (
    predictions_df
    .sort_values(
        "naive_absolute_error",
        ascending=False
    )
    .head(20)
)


print("\n")
print("=" * 80)
print("TOP 20 NAIVE FORECAST ERRORS")
print("=" * 80)

print(
    largest_errors[
        [
            "forecast_year",
            "state",
            "fertilizer_type",
            "actual_sales",
            "naive_prediction",
            "naive_absolute_error",
            "potential_reporting_break"
        ]
    ].to_string(index=False)
)


# =========================================================
# 14. Reporting-break observations
# =========================================================

break_rows = predictions_df[
    predictions_df["potential_reporting_break"] == 1
].copy()


print("\n")
print("=" * 80)
print("REPORTING-BREAK OBSERVATIONS")
print("=" * 80)

print(
    break_rows[
        [
            "forecast_year",
            "state",
            "fertilizer_type",
            "actual_sales",
            "naive_prediction",
            "naive_absolute_error",
            "random_forest_prediction",
            "random_forest_absolute_error"
        ]
    ].to_string(index=False)
)


# =========================================================
# 15. Save outputs
# =========================================================

predictions_path = (
    "data/processed/"
    "rolling_prediction_details.csv"
)

year_results_path = (
    "data/processed/"
    "rolling_year_comparison.csv"
)

fertilizer_path = (
    "data/processed/"
    "rolling_fertilizer_errors.csv"
)

state_path = (
    "data/processed/"
    "rolling_state_errors.csv"
)


predictions_df.to_csv(
    predictions_path,
    index=False
)

year_results_df.to_csv(
    year_results_path,
    index=False
)

fertilizer_errors.to_csv(
    fertilizer_path,
    index=False
)

state_errors.to_csv(
    state_path,
    index=False
)


print("\n")
print("=" * 80)
print("FILES SAVED")
print("=" * 80)

print(predictions_path)
print(year_results_path)
print(fertilizer_path)
print(state_path)
