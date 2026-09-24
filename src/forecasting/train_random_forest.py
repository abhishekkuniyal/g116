import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# --------------------------------------------------
# 1. Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

MODEL_DIR = BASE_DIR / "processed" / "modeling"

TRAIN_PATH = MODEL_DIR / "train.csv"
VALIDATION_PATH = MODEL_DIR / "validation.csv"
TEST_PATH = MODEL_DIR / "test.csv"


# --------------------------------------------------
# 2. Load datasets
# --------------------------------------------------

train = pd.read_csv(TRAIN_PATH)
validation = pd.read_csv(VALIDATION_PATH)
test = pd.read_csv(TEST_PATH)

print("Train shape:", train.shape)
print("Validation shape:", validation.shape)
print("Test shape:", test.shape)


# --------------------------------------------------
# 3. Define features
# --------------------------------------------------

numeric_features = [
    "sales_current",
    "sales_lag_1",
    "requirement_current",
    "requirement_lag_1",
    "availability_current",
    "availability_lag_1",
]

categorical_features = [
    "state",
    "fertilizer_type",
]

target = "target_sales"


# --------------------------------------------------
# 4. Separate X and y
# --------------------------------------------------

X_train = train[
    numeric_features + categorical_features
]

y_train = train[target]

X_validation = validation[
    numeric_features + categorical_features
]

y_validation = validation[target]

X_test = test[
    numeric_features + categorical_features
]

y_test = test[target]


# --------------------------------------------------
# 5. Preprocessing
# --------------------------------------------------

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features,
        ),
        (
            "numeric",
            "passthrough",
            numeric_features,
        ),
    ]
)


# --------------------------------------------------
# 6. Random Forest
# --------------------------------------------------

regressor = RandomForestRegressor(
    n_estimators=200,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    random_state=42,
    n_jobs=-1
)


# --------------------------------------------------
# 7. Create pipeline
# --------------------------------------------------

model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("regressor", regressor),
    ]
)


# --------------------------------------------------
# 8. Train
# --------------------------------------------------

print("\nTraining Random Forest...")

model.fit(
    X_train,
    y_train
)

print("Training complete.")


# --------------------------------------------------
# 9. Evaluation function
# --------------------------------------------------

def evaluate_model(model, X, y, dataset_name):

    predictions = model.predict(X)

    mae = mean_absolute_error(
        y,
        predictions
    )

    rmse = np.sqrt(
        mean_squared_error(
            y,
            predictions
        )
    )

    r2 = r2_score(
        y,
        predictions
    )

    print(f"\n--- {dataset_name} ---")

    print(f"MAE  : {mae:.4f}")
    print(f"RMSE : {rmse:.4f}")
    print(f"R²   : {r2:.4f}")

    return mae, rmse, r2


# --------------------------------------------------
# 10. Evaluate
# --------------------------------------------------

validation_metrics = evaluate_model(
    model,
    X_validation,
    y_validation,
    "Validation"
)

test_metrics = evaluate_model(
    model,
    X_test,
    y_test,
    "Test"
)


# --------------------------------------------------
# 11. Sample predictions
# --------------------------------------------------

validation_predictions = model.predict(
    X_validation
)

sample = validation[
    [
        "financial_year",
        "state",
        "fertilizer_type",
        "sales_current",
        "target_sales",
    ]
].copy()

sample["prediction"] = validation_predictions

print("\n--- SAMPLE VALIDATION PREDICTIONS ---")

print(
    sample
    .head(10)
    .to_string(index=False)
)

# --------------------------------------------------
# 11A. Random Forest error analysis
# --------------------------------------------------

test_predictions = model.predict(X_test)

test_analysis = test[
    [
        "financial_year",
        "state",
        "fertilizer_type",
        "sales_current",
        "target_sales",
    ]
].copy()

test_analysis["prediction"] = test_predictions

test_analysis["error"] = (
    test_analysis["target_sales"]
    - test_analysis["prediction"]
)

test_analysis["absolute_error"] = (
    test_analysis["error"].abs()
)


print("\n--- RANDOM FOREST ERROR ANALYSIS ---")

print(
    "Mean absolute error:",
    test_analysis["absolute_error"].mean()
)

print(
    "Median absolute error:",
    test_analysis["absolute_error"].median()
)

print(
    "Maximum absolute error:",
    test_analysis["absolute_error"].max()
)


print("\n--- TOP 15 LARGEST ERRORS ---")

print(
    test_analysis
    .sort_values(
        "absolute_error",
        ascending=False
    )
    [
        [
            "financial_year",
            "state",
            "fertilizer_type",
            "sales_current",
            "target_sales",
            "prediction",
            "error",
            "absolute_error",
        ]
    ]
    .head(15)
    .to_string(index=False)
)


print("\n--- ERROR BY FERTILIZER ---")

fertilizer_error = (
    test_analysis
    .groupby("fertilizer_type")["absolute_error"]
    .agg(
        mean="mean",
        median="median",
        maximum="max",
        count="count"
    )
    .sort_values(
        "mean",
        ascending=False
    )
)

print(fertilizer_error)


print("\n--- TOP STATES BY MAE ---")

state_error = (
    test_analysis
    .groupby("state")["absolute_error"]
    .agg(
        MAE="mean",
        maximum="max",
        count="count"
    )
    .sort_values(
        "MAE",
        ascending=False
    )
)

print(
    state_error.head(15)
)


# --------------------------------------------------
# 12. Save results
# --------------------------------------------------

results = pd.DataFrame(
    [
        {
            "model": "Random Forest",
            "dataset": "validation",
            "MAE": validation_metrics[0],
            "RMSE": validation_metrics[1],
            "R2": validation_metrics[2],
        },
        {
            "model": "Random Forest",
            "dataset": "test",
            "MAE": test_metrics[0],
            "RMSE": test_metrics[1],
            "R2": test_metrics[2],
        },
    ]
)

RESULT_PATH = MODEL_DIR / "random_forest_results.csv"

results.to_csv(
    RESULT_PATH,
    index=False
)

print("\nResults saved to:")
print(RESULT_PATH)