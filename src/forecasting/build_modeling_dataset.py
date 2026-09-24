import pandas as pd
from pathlib import Path


# --------------------------------------------------
# 1. Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

GOVERNMENT_PATH = BASE_DIR / "processed" / "government_clean.csv"
IFFCO_PATH = BASE_DIR / "processed" / "iffco_urea_state_year.csv"

OUTPUT_DIR = BASE_DIR / "processed" / "modeling"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "demand_forecasting.csv"


# --------------------------------------------------
# 2. Load data
# --------------------------------------------------

government = pd.read_csv(GOVERNMENT_PATH)
iffco = pd.read_csv(IFFCO_PATH)

print("Government shape:", government.shape)
print("IFFCO shape:", iffco.shape)


# --------------------------------------------------
# 3. Standardize fertilizer names
# --------------------------------------------------

government["fertilizer_type"] = (
    government["fertilizer_type"]
    .str.strip()
    .str.lower()
)

iffco["fertilizer_type"] = (
    iffco["fertilizer_type"]
    .str.strip()
    .str.lower()
)


# --------------------------------------------------
# 4. Sort government data
# --------------------------------------------------

government = government.sort_values(
    ["state", "fertilizer_type", "financial_year"]
).reset_index(drop=True)


# --------------------------------------------------
# 5. Create current + lag features
# --------------------------------------------------

group_cols = ["state", "fertilizer_type"]

government["sales_lag_1"] = (
    government.groupby(group_cols)["sales"]
    .shift(1)
)

government["requirement_lag_1"] = (
    government.groupby(group_cols)["requirement"]
    .shift(1)
)

government["availability_lag_1"] = (
    government.groupby(group_cols)["availability"]
    .shift(1)
)


# --------------------------------------------------
# 6. Create target = next year's sales
# --------------------------------------------------

government["target_sales"] = (
    government.groupby(group_cols)["sales"]
    .shift(-1)
)


# --------------------------------------------------
# 7. Prepare IFFCO production
# --------------------------------------------------

iffco = iffco.rename(
    columns={
        "iffco_fertiliser_type": "fertilizer_type",
        "iffco_production": "iffco_production"
    }
)

iffco["fertilizer_type"] = (
    iffco["fertilizer_type"]
    .str.strip()
    .str.lower()
)

iffco = iffco[
    [
        "financial_year",
        "state",
        "fertilizer_type",
        "iffco_production"
    ]
].copy()


# --------------------------------------------------
# 8. Merge CURRENT IFFCO production
# --------------------------------------------------

government = government.merge(
    iffco,
    on=["financial_year", "state", "fertilizer_type"],
    how="left",
    validate="one_to_one"
)

government = government.rename(
    columns={
        "iffco_production": "iffco_production_current"
    }
)


# --------------------------------------------------
# 9. Create PREVIOUS-YEAR IFFCO production
# --------------------------------------------------

iffco_lag = iffco.copy()

iffco_lag["financial_year"] = (
    iffco_lag
    .groupby(["state", "fertilizer_type"])["financial_year"]
    .shift(-1)
)

iffco_lag = iffco_lag.rename(
    columns={
        "iffco_production": "iffco_production_lag_1"
    }
)

iffco_lag = iffco_lag[
    [
        "financial_year",
        "state",
        "fertilizer_type",
        "iffco_production_lag_1"
    ]
]

government = government.merge(
    iffco_lag,
    on=["financial_year", "state", "fertilizer_type"],
    how="left",
    validate="one_to_one"
)


# --------------------------------------------------
# 10. IFFCO availability indicator
# --------------------------------------------------

government["iffco_production_available"] = (
    government["iffco_production_current"].notna()
)


# --------------------------------------------------
# 11. Potential reporting-break flag
# --------------------------------------------------

government["potential_reporting_break"] = 0

reporting_breaks = [
    ("2018-19", "Uttar Pradesh", "dap"),
    ("2018-19", "Uttar Pradesh", "urea"),
    ("2018-19", "Uttarakhand", "dap"),
    ("2018-19", "Uttarakhand", "urea"),
]

for year, state, fertilizer in reporting_breaks:

    mask = (
        (government["financial_year"] == year)
        & (government["state"] == state)
        & (government["fertilizer_type"] == fertilizer)
    )

    government.loc[
        mask,
        "potential_reporting_break"
    ] = 1


# --------------------------------------------------
# 12. Select final modeling columns
# --------------------------------------------------

modeling = government[
    [
        "financial_year",
        "state",
        "fertilizer_type",

        "sales",
        "sales_lag_1",

        "requirement",
        "requirement_lag_1",

        "availability",
        "availability_lag_1",

        "iffco_production_current",
        "iffco_production_lag_1",
        "iffco_production_available",

        "potential_reporting_break",

        "target_sales"
    ]
].copy()


# Rename current features clearly

modeling = modeling.rename(
    columns={
        "sales": "sales_current",
        "requirement": "requirement_current",
        "availability": "availability_current"
    }
)


# --------------------------------------------------
# 13. Remove rows without historical information
# --------------------------------------------------

modeling = modeling.dropna(
    subset=[
        "sales_lag_1",
        "requirement_lag_1",
        "availability_lag_1"
    ]
)


# --------------------------------------------------
# 14. Validation
# --------------------------------------------------

print("\n--- MODELING DATASET VALIDATION ---")

print("Shape:", modeling.shape)

print("\nColumns:")
print(modeling.columns.tolist())

print("\nMissing values:")
print(modeling.isna().sum())

print("\nDuplicate rows:", modeling.duplicated().sum())

print(
    "Duplicate modeling keys:",
    modeling.duplicated(
        subset=[
            "financial_year",
            "state",
            "fertilizer_type"
        ]
    ).sum()
)

print("\nIFFCO current production coverage:")
print(
    modeling["iffco_production_current"]
    .notna()
    .value_counts()
)

print("\nIFFCO lag production coverage:")
print(
    modeling["iffco_production_lag_1"]
    .notna()
    .value_counts()
)

print("\nTarget available:")
print(
    modeling["target_sales"]
    .notna()
    .value_counts()
)

print("\nReporting-break observations:")

print(
    modeling[
        modeling["potential_reporting_break"] == 1
    ][
        [
            "financial_year",
            "state",
            "fertilizer_type",
            "sales_current",
            "sales_lag_1",
            "target_sales"
        ]
    ].to_string(index=False)
)


# --------------------------------------------------
# 15. Save
# --------------------------------------------------

modeling = modeling.sort_values(
    ["financial_year", "state", "fertilizer_type"]
).reset_index(drop=True)

modeling.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\nSaved to:")
print(OUTPUT_PATH)