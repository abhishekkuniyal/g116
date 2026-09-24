import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


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
# 3. Naive forecasting rule
# --------------------------------------------------
#
# Our baseline assumption:
#
# Next year's sales ≈ current year's sales
#
# Therefore:
#
# prediction = sales_current
# --------------------------------------------------

validation["prediction"] = validation["sales_current"]

test["prediction"] = test["sales_current"]


# --------------------------------------------------
# 4. Evaluation function
# --------------------------------------------------

def evaluate_model(data, dataset_name):

    actual = data["target_sales"]
    predicted = data["prediction"]

    mae = mean_absolute_error(actual, predicted)

    rmse = np.sqrt(
        mean_squared_error(actual, predicted)
    )

    r2 = r2_score(actual, predicted)

    print(f"\n--- {dataset_name} ---")

    print(f"MAE  : {mae:.4f}")
    print(f"RMSE : {rmse:.4f}")
    print(f"R²   : {r2:.4f}")

    return mae, rmse, r2


# --------------------------------------------------
# 5. Evaluate baseline
# --------------------------------------------------

validation_metrics = evaluate_model(
    validation,
    "Validation"
)

test_metrics = evaluate_model(
    test,
    "Test"
)


# --------------------------------------------------
# 6. Show a few predictions
# --------------------------------------------------

print("\n--- SAMPLE VALIDATION PREDICTIONS ---")

print(
    validation[
        [
            "financial_year",
            "state",
            "fertilizer_type",
            "sales_current",
            "target_sales",
            "prediction"
        ]
    ].head(10).to_string(index=False)
)


# --------------------------------------------------
# 7. Save baseline results
# --------------------------------------------------

results = pd.DataFrame(
    [
        {
            "model": "Naive Baseline",
            "dataset": "validation",
            "MAE": validation_metrics[0],
            "RMSE": validation_metrics[1],
            "R2": validation_metrics[2],
        },
        {
            "model": "Naive Baseline",
            "dataset": "test",
            "MAE": test_metrics[0],
            "RMSE": test_metrics[1],
            "R2": test_metrics[2],
        },
    ]
)

RESULT_PATH = MODEL_DIR / "baseline_results.csv"

results.to_csv(
    RESULT_PATH,
    index=False
)

print("\nBaseline results saved to:")
print(RESULT_PATH)