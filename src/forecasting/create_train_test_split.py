import pandas as pd
from pathlib import Path


# --------------------------------------------------
# 1. Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    BASE_DIR
    / "processed"
    / "modeling"
    / "demand_forecasting.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "processed"
    / "modeling"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. Load modeling dataset
# --------------------------------------------------

df = pd.read_csv(INPUT_PATH)

print("Original shape:", df.shape)


# --------------------------------------------------
# 3. Separate rows with and without target
# --------------------------------------------------

df_with_target = df[
    df["target_sales"].notna()
].copy()

df_without_target = df[
    df["target_sales"].isna()
].copy()


print(
    "Rows with target:",
    len(df_with_target)
)

print(
    "Rows without target:",
    len(df_without_target)
)


# --------------------------------------------------
# 4. Define chronological periods
# --------------------------------------------------

TRAIN_YEARS = [
    "2015-16",
    "2016-17",
    "2017-18",
    "2018-19",
    "2019-20",
    "2020-21",
]

VALIDATION_YEARS = [
    "2021-22",
    "2022-23",
]

TEST_YEARS = [
    "2023-24",
]

FUTURE_YEARS = [
    "2024-25",
]


# --------------------------------------------------
# 5. Create datasets
# --------------------------------------------------

train = df_with_target[
    df_with_target["financial_year"].isin(TRAIN_YEARS)
].copy()

validation = df_with_target[
    df_with_target["financial_year"].isin(VALIDATION_YEARS)
].copy()

test = df_with_target[
    df_with_target["financial_year"].isin(TEST_YEARS)
].copy()

future = df_without_target[
    df_without_target["financial_year"].isin(FUTURE_YEARS)
].copy()


# --------------------------------------------------
# 6. Validate chronological separation
# --------------------------------------------------

assert set(train["financial_year"]).isdisjoint(
    set(validation["financial_year"])
)

assert set(train["financial_year"]).isdisjoint(
    set(test["financial_year"])
)

assert set(validation["financial_year"]).isdisjoint(
    set(test["financial_year"])
)


# --------------------------------------------------
# 7. Validate target availability
# --------------------------------------------------

assert train["target_sales"].notna().all()
assert validation["target_sales"].notna().all()
assert test["target_sales"].notna().all()

assert future["target_sales"].isna().all()


# --------------------------------------------------
# 8. Print summary
# --------------------------------------------------

print("\n--- CHRONOLOGICAL SPLIT ---")

print(
    "\nTrain:",
    train.shape,
    "| Years:",
    sorted(train["financial_year"].unique())
)

print(
    "Validation:",
    validation.shape,
    "| Years:",
    sorted(validation["financial_year"].unique())
)

print(
    "Test:",
    test.shape,
    "| Years:",
    sorted(test["financial_year"].unique())
)

print(
    "Future prediction:",
    future.shape,
    "| Years:",
    sorted(future["financial_year"].unique())
)


# --------------------------------------------------
# 9. Save datasets
# --------------------------------------------------

train.to_csv(
    OUTPUT_DIR / "train.csv",
    index=False
)

validation.to_csv(
    OUTPUT_DIR / "validation.csv",
    index=False
)

test.to_csv(
    OUTPUT_DIR / "test.csv",
    index=False
)

future.to_csv(
    OUTPUT_DIR / "future_prediction.csv",
    index=False
)


# --------------------------------------------------
# 10. Final confirmation
# --------------------------------------------------

print("\nFiles created:")

print(OUTPUT_DIR / "train.csv")
print(OUTPUT_DIR / "validation.csv")
print(OUTPUT_DIR / "test.csv")
print(OUTPUT_DIR / "future_prediction.csv")

print("\nSplit validation passed.")