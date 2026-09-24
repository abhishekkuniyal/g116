import pandas as pd
import numpy as np
from pathlib import Path


# --------------------------------------------------
# 1. Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

MODEL_DIR = BASE_DIR / "processed" / "modeling"

TEST_PATH = MODEL_DIR / "test.csv"


# --------------------------------------------------
# 2. Load test data
# --------------------------------------------------

test = pd.read_csv(TEST_PATH)


# --------------------------------------------------
# 3. Baseline prediction
# --------------------------------------------------

test["prediction"] = test["sales_current"]


# --------------------------------------------------
# 4. Calculate errors
# --------------------------------------------------

test["error"] = (
    test["target_sales"] - test["prediction"]
)

test["absolute_error"] = (
    test["error"].abs()
)

test["percentage_error"] = np.where(
    test["target_sales"] != 0,
    (
        test["absolute_error"]
        / test["target_sales"]
    ) * 100,
    np.nan
)


# --------------------------------------------------
# 5. Overall error statistics
# --------------------------------------------------

print("\n--- BASELINE ERROR ANALYSIS ---")

print(
    "\nMean absolute error:",
    test["absolute_error"].mean()
)

print(
    "Median absolute error:",
    test["absolute_error"].median()
)

print(
    "Maximum absolute error:",
    test["absolute_error"].max()
)


# --------------------------------------------------
# 6. Largest errors
# --------------------------------------------------

print("\n--- TOP 15 LARGEST ERRORS ---")

largest_errors = test.sort_values(
    "absolute_error",
    ascending=False
)

print(
    largest_errors[
        [
            "financial_year",
            "state",
            "fertilizer_type",
            "sales_current",
            "target_sales",
            "error",
            "absolute_error"
        ]
    ]
    .head(15)
    .to_string(index=False)
)


# --------------------------------------------------
# 7. Error by fertilizer
# --------------------------------------------------

print("\n--- ERROR BY FERTILIZER ---")

fertilizer_error = (
    test
    .groupby("fertilizer_type")
    ["absolute_error"]
    .agg(
        mean="mean",
        median="median",
        maximum="max",
        count="count"
    )
    .sort_values("mean", ascending=False)
)

print(fertilizer_error)


# --------------------------------------------------
# 8. Error by state
# --------------------------------------------------

print("\n--- TOP 15 STATES BY MAE ---")

state_error = (
    test
    .groupby("state")
    ["absolute_error"]
    .agg(
        MAE="mean",
        maximum="max",
        count="count"
    )
    .sort_values("MAE", ascending=False)
)

print(
    state_error.head(15)
)


# --------------------------------------------------
# 9. Large-error observations
# --------------------------------------------------

print("\n--- ERRORS GREATER THAN 2 ---")

large_errors = test[
    test["absolute_error"] > 2
]

print(
    large_errors[
        [
            "financial_year",
            "state",
            "fertilizer_type",
            "sales_current",
            "target_sales",
            "absolute_error"
        ]
    ]
    .to_string(index=False)
)

print(
    "\nNumber of errors > 2:",
    len(large_errors)
)