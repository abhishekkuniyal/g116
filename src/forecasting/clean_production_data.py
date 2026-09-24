import pandas as pd
from pathlib import Path


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_ROOT / "raw"
PROCESSED_DIR = PROJECT_ROOT / "processed"

PROCESSED_DIR.mkdir(exist_ok=True)


# ============================================================
# 2. LOAD RAW DATA
# ============================================================

INPUT_FILE = (
    RAW_DIR
    / "fertiliser_production_capacity_2014_to_2024.csv"
)

df = pd.read_csv(INPUT_FILE)

print("=" * 70)
print("FERTILISER PRODUCTION DATA CLEANING")
print("=" * 70)

print(f"\nRaw shape: {df.shape}")


# ============================================================
# 3. STANDARDIZE TEXT WHITESPACE
# ============================================================
#
# Some text fields contain newline characters such as:
#
# Tamil\nNadu
# Indian Farmers Fertilizers Co-\nOperative Ltd.
# Urea\n&Complexes
#
# We convert these into normal spaces first.
# ============================================================

text_columns = [
    "sector",
    "state",
    "city",
    "company",
    "manufacturing_unit",
    "fertiliser_type",
]

for column in text_columns:

    df[column] = (
        df[column]
        .astype("string")
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )


# ============================================================
# 4. STANDARDIZE COMPANY NAMES
# ============================================================

company_mapping = {

    "Indian Farmers Fertilizers Co- Operative Ltd.":
        "Indian Farmers Fertilizers Cooperative Ltd.",

    "Indian Farmers Fertilizers Co-Operative Ltd.":
        "Indian Farmers Fertilizers Cooperative Ltd.",

    "Indian Farmers Fertilizers Co - Operative Ltd.":
        "Indian Farmers Fertilizers Cooperative Ltd.",

    "Indian Farmers Fertilizers Co- Operative Ltd":
        "Indian Farmers Fertilizers Cooperative Ltd.",

    "Indian Farmers Fertilizers Co-Operative Ltd":
        "Indian Farmers Fertilizers Cooperative Ltd.",
}

df["company"] = df["company"].replace(company_mapping)


# ============================================================
# 5. STANDARDIZE FERTILISER CATEGORY FORMATTING
# ============================================================

fertilizer_mapping = {

    "Urea &Complexes":
        "Urea & Complexes",

    "Urea, DAP &Complexes":
        "Urea, DAP & Complexes",

    "Urea,DAP &Complexes":
        "Urea, DAP & Complexes",

    "Urea/ Complexes":
        "Urea / Complexes",

    "TSP & Complex":
        "TSP & Complexes",
}

df["fertiliser_type"] = (
    df["fertiliser_type"]
    .replace(fertilizer_mapping)
)


# ============================================================
# 6. STANDARDIZE STATE NAMES
# ============================================================

state_mapping = {
    "Karnttaka":
        "Karnataka",
}

df["state"] = df["state"].replace(state_mapping)


# ============================================================
# 7. CHECK FERTILISER TYPES
# ============================================================

print("\nFertiliser types after text cleaning:")

for value in sorted(
    df["fertiliser_type"]
    .dropna()
    .unique()
):

    print(f"  - {value}")


# ============================================================
# 8. IDENTIFY FINANCIAL YEAR COLUMNS
# ============================================================

year_columns = [
    column
    for column in df.columns
    if column.startswith("fy_")
]

print("\nYear columns:")
print(year_columns)


# ============================================================
# 9. CONVERT PRODUCTION VALUES TO NUMERIC
# ============================================================

for column in year_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# ============================================================
# 10. MISSING VALUE REPORT
# ============================================================

print("\nMissing values by year:")

missing_values = (
    df[year_columns]
    .isnull()
    .sum()
)

print(missing_values)


# ============================================================
# 11. DO NOT IMPUTE MISSING VALUES
# ============================================================

print("\nMissing values have NOT been replaced.")

print(
    "Reason: a missing production value may represent "
    "unreported or unavailable data rather than zero production."
)


# ============================================================
# 12. CONVERT WIDE FORMAT → LONG FORMAT
# ============================================================

id_columns = [
    "sector",
    "state",
    "city",
    "company",
    "manufacturing_unit",
    "fertiliser_type",
]

production_long = df.melt(
    id_vars=id_columns,
    value_vars=year_columns,
    var_name="financial_year",
    value_name="production"
)


# ============================================================
# 13. CLEAN FINANCIAL YEAR
# ============================================================

production_long["financial_year"] = (
    production_long["financial_year"]
    .str.replace(
        "fy_",
        "",
        regex=False
    )
    .str.replace(
        "_",
        "-",
        regex=False
    )
)


# ============================================================
# 14. REORDER COLUMNS
# ============================================================

production_long = production_long[
    [
        "financial_year",
        "state",
        "city",
        "company",
        "manufacturing_unit",
        "fertiliser_type",
        "sector",
        "production",
    ]
]


# ============================================================
# 15. SORT DATA
# ============================================================

production_long = production_long.sort_values(
    by=[
        "financial_year",
        "state",
        "company",
        "manufacturing_unit",
    ]
).reset_index(drop=True)


# ============================================================
# 16. VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("POST-CLEANING VALIDATION")
print("=" * 70)


# ------------------------------------------------------------
# Shape
# ------------------------------------------------------------

print("\nCleaned shape:")
print(production_long.shape)


# ------------------------------------------------------------
# Missing values
# ------------------------------------------------------------

print("\nMissing values:")

print(
    production_long.isnull().sum()
)


# ------------------------------------------------------------
# Duplicate rows
# ------------------------------------------------------------

print("\nDuplicate rows:")

print(
    production_long.duplicated().sum()
)


# ------------------------------------------------------------
# Financial years
# ------------------------------------------------------------

print("\nFinancial years:")

print(
    production_long["financial_year"]
    .unique()
)


# ------------------------------------------------------------
# States
# ------------------------------------------------------------

print("\nStates:")

print(
    sorted(
        production_long["state"]
        .dropna()
        .unique()
    )
)


# ------------------------------------------------------------
# Companies
# ------------------------------------------------------------

print("\nCompanies:")

print(
    sorted(
        production_long["company"]
        .dropna()
        .unique()
    )
)


# ------------------------------------------------------------
# Fertiliser categories
# ------------------------------------------------------------

print("\nFinal fertilizer categories:")

print(
    sorted(
        production_long["fertiliser_type"]
        .dropna()
        .unique()
    )
)


# ------------------------------------------------------------
# Missing production values
# ------------------------------------------------------------

print("\nMissing production values:")

print(
    production_long["production"]
    .isna()
    .sum()
)


# ============================================================
# 17. NEGATIVE PRODUCTION CHECK
# ============================================================

negative_production = (
    production_long["production"] < 0
).sum()

print("\nNegative production values:")

print(negative_production)


# ============================================================
# 18. DUPLICATE BUSINESS KEY CHECK
# ============================================================
#
# A record is expected to represent a particular:
#
# financial_year
# + company
# + manufacturing_unit
# + fertiliser_type
#
# We check this combination for duplicates.
# ============================================================

business_key = [
    "financial_year",
    "company",
    "manufacturing_unit",
    "fertiliser_type",
]

duplicate_business_keys = (
    production_long
    .duplicated(
        subset=business_key,
        keep=False
    )
)

print("\nDuplicate business keys:")

print(
    duplicate_business_keys.sum()
)


# ============================================================
# 19. SAVE CLEAN DATASET
# ============================================================

OUTPUT_FILE = (
    PROCESSED_DIR
    / "production_clean.csv"
)

production_long.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 20. FINAL MESSAGE
# ============================================================

print("\nOutput file:")
print(OUTPUT_FILE)

print("\n" + "=" * 70)
print("PRODUCTION CLEANING COMPLETE")
print("=" * 70)