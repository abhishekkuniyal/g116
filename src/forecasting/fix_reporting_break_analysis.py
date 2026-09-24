import pandas as pd


# =========================================================
# 1. Load modeling dataset
# =========================================================

DATA_PATH = "data/processed/demand_forecasting.csv"

df = pd.read_csv(DATA_PATH)

print("Loaded dataset:", df.shape)


# =========================================================
# 2. Select reporting-break observations
# =========================================================

break_rows = df[
    df["potential_reporting_break"] == 1
].copy()

print("\n")
print("=" * 80)
print("REPORTING-BREAK OBSERVATIONS")
print("=" * 80)

print(
    break_rows[
        [
            "financial_year",
            "state",
            "fertilizer_type",
            "sales_current",
            "sales_lag_1",
            "target_sales",
            "potential_reporting_break"
        ]
    ].to_string(index=False)
)


# =========================================================
# 3. Calculate Naive forecast error
# =========================================================

break_rows["naive_prediction"] = (
    break_rows["sales_current"]
)

break_rows["naive_error"] = (
    break_rows["target_sales"]
    - break_rows["naive_prediction"]
)

break_rows["naive_absolute_error"] = (
    break_rows["naive_error"].abs()
)


# =========================================================
# 4. Print forecast impact
# =========================================================

print("\n")
print("=" * 80)
print("REPORTING-BREAK FORECAST IMPACT")
print("=" * 80)

print(
    break_rows[
        [
            "financial_year",
            "state",
            "fertilizer_type",
            "sales_lag_1",
            "sales_current",
            "target_sales",
            "naive_prediction",
            "naive_error",
            "naive_absolute_error"
        ]
    ].to_string(index=False)
)


# =========================================================
# 5. Compare the transition
#
# 2017-18 → 2018-19 → 2019-20
# =========================================================

comparison_rows = []

for _, row in break_rows.iterrows():

    state = row["state"]
    fertilizer = row["fertilizer_type"]

    series = df[
        (df["state"] == state)
        & (df["fertilizer_type"] == fertilizer)
    ].copy()

    relevant = series[
        series["financial_year"].isin(
            ["2017-18", "2018-19", "2019-20"]
        )
    ].copy()

    comparison_rows.append(relevant)


comparison_df = pd.concat(
    comparison_rows,
    ignore_index=True
)


# =========================================================
# 6. Print transition
# =========================================================

print("\n")
print("=" * 80)
print("2017-18 → 2018-19 → 2019-20 TRANSITIONS")
print("=" * 80)

columns_to_show = [
    "financial_year",
    "state",
    "fertilizer_type",
    "sales_current",
    "requirement_current",
    "availability_current",
    "target_sales",
    "potential_reporting_break"
]

print(
    comparison_df[columns_to_show].to_string(index=False)
)


# =========================================================
# 7. Save analysis
# =========================================================

OUTPUT_PATH = (
    "data/processed/"
    "reporting_break_forecast_analysis.csv"
)

output_columns = [
    "financial_year",
    "state",
    "fertilizer_type",
    "sales_lag_1",
    "sales_current",
    "target_sales",
    "naive_prediction",
    "naive_error",
    "naive_absolute_error"
]

break_rows[output_columns].to_csv(
    OUTPUT_PATH,
    index=False
)

print("\n")
print("Analysis saved to:", OUTPUT_PATH)
