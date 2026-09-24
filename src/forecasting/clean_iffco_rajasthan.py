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
    / "RS_Session_270_AU_4173_B.i.csv"
)

df = pd.read_csv(INPUT_FILE)

print("=" * 70)
print("IFFCO RAJASTHAN DISTRICT SUPPLY DATA CLEANING")
print("=" * 70)

print(f"\nRaw shape: {df.shape}")


# ============================================================
# 3. STANDARDIZE COLUMN NAMES
# ============================================================

df = df.rename(
    columns={
        "Sl. No.": "sl_no",
        "District": "district",
        "2022-23": "2022-23",
        "2023-24": "2023-24",
        "2024-25": "2024-25",
        "2025-26 (Till 28-02-2026)": "2025-26_partial",
    }
)

print("\nColumns after standardization:")
print(df.columns.tolist())


# ============================================================
# 4. CLEAN TEXT COLUMNS
# ============================================================

df["district"] = (
    df["district"]
    .astype("string")
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)


# ============================================================
# 5. IDENTIFY GRAND TOTAL
# ============================================================

grand_total = df[
    df["district"].str.casefold() == "grand total"
].copy()

district_df = df[
    df["district"].str.casefold() != "grand total"
].copy()

print("\nGrand Total rows:")
print(len(grand_total))

print("\nActual district rows:")
print(len(district_df))


# ============================================================
# 6. CHECK DISTRICTS
# ============================================================

print("\nDistricts:")

print(
    sorted(
        district_df["district"]
        .dropna()
        .unique()
    )
)


# ============================================================
# 7. CONVERT SUPPLY VALUES TO NUMERIC
# ============================================================

year_columns = [
    "2022-23",
    "2023-24",
    "2024-25",
    "2025-26_partial",
]

for column in year_columns:

    district_df[column] = pd.to_numeric(
        district_df[column],
        errors="coerce"
    )


# ============================================================
# 8. MISSING VALUE CHECK
# ============================================================

print("\nMissing values before reshaping:")

print(
    district_df[
        year_columns
    ].isnull().sum()
)


# ============================================================
# 9. NEGATIVE VALUE CHECK
# ============================================================

negative_values = (
    district_df[year_columns] < 0
).sum().sum()

print("\nNegative supply values:")
print(negative_values)


# ============================================================
# 10. CONVERT WIDE FORMAT → LONG FORMAT
# ============================================================

supply_long = district_df.melt(
    id_vars=["district"],
    value_vars=year_columns,
    var_name="financial_year",
    value_name="iffco_supply"
)


# ============================================================
# 11. MARK PARTIAL YEAR
# ============================================================

supply_long["is_partial_year"] = (
    supply_long["financial_year"]
    == "2025-26_partial"
)


# ============================================================
# 12. CLEAN FINANCIAL YEAR
# ============================================================

supply_long["financial_year"] = (
    supply_long["financial_year"]
    .str.replace(
        "_partial",
        "",
        regex=False
    )
)


# ============================================================
# 13. ADD SOURCE / MEASUREMENT INFORMATION
# ============================================================

supply_long["supply_unit"] = "not specified in source"


# ============================================================
# 14. REORDER COLUMNS
# ============================================================

supply_long = supply_long[
    [
        "financial_year",
        "district",
        "iffco_supply",
        "is_partial_year",
        "supply_unit",
    ]
]


# ============================================================
# 15. SORT DATA
# ============================================================

supply_long = supply_long.sort_values(
    by=[
        "financial_year",
        "district",
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
print(supply_long.shape)


# ------------------------------------------------------------
# Missing values
# ------------------------------------------------------------

print("\nMissing values:")

print(
    supply_long.isnull().sum()
)


# ------------------------------------------------------------
# Duplicate rows
# ------------------------------------------------------------

print("\nDuplicate rows:")

print(
    supply_long.duplicated().sum()
)


# ------------------------------------------------------------
# Financial years
# ------------------------------------------------------------

print("\nFinancial years:")

print(
    supply_long["financial_year"]
    .unique()
)


# ------------------------------------------------------------
# Partial-year records
# ------------------------------------------------------------

print("\nPartial-year records:")

print(
    supply_long[
        supply_long["is_partial_year"]
    ].shape[0]
)


# ------------------------------------------------------------
# District count
# ------------------------------------------------------------

print("\nDistrict count:")

print(
    supply_long["district"]
    .nunique()
)


# ------------------------------------------------------------
# Supply summary
# ------------------------------------------------------------

print("\nSupply summary:")

print(
    supply_long.groupby(
        "financial_year"
    )["iffco_supply"]
    .agg(
        [
            "count",
            "sum",
            "min",
            "max",
        ]
    )
)


# ============================================================
# 17. GRAND TOTAL VALIDATION
# ============================================================
#
# We keep the original Grand Total separate.
# This allows us to check whether the sum of district
# values matches the source's reported total.
# ============================================================

if len(grand_total) == 1:

    print("\n" + "=" * 70)
    print("GRAND TOTAL VALIDATION")
    print("=" * 70)

    grand_total_values = grand_total.copy()

    for column in year_columns:

        grand_total_values[column] = pd.to_numeric(
            grand_total_values[column],
            errors="coerce"
        )

    district_totals = (
        district_df[year_columns]
        .sum()
    )

    source_totals = (
        grand_total_values[
            year_columns
        ]
        .iloc[0]
    )

    comparison = pd.DataFrame(
        {
            "district_sum": district_totals,
            "source_grand_total": source_totals,
            "difference": (
                district_totals
                - source_totals
            ),
        }
    )

    print(comparison)

else:

    print(
        "\nWARNING: Expected exactly one "
        "Grand Total row."
    )


# ============================================================
# 18. SAVE CLEAN DATASET
# ============================================================

OUTPUT_FILE = (
    PROCESSED_DIR
    / "iffco_rajasthan_clean.csv"
)

supply_long.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 19. SAVE GRAND TOTAL FOR REFERENCE
# ============================================================

GRAND_TOTAL_FILE = (
    PROCESSED_DIR
    / "iffco_rajasthan_grand_total.csv"
)

grand_total.to_csv(
    GRAND_TOTAL_FILE,
    index=False
)


# ============================================================
# 20. FINAL MESSAGE
# ============================================================

print("\nClean district dataset:")
print(OUTPUT_FILE)

print("\nGrand Total reference dataset:")
print(GRAND_TOTAL_FILE)

print("\n" + "=" * 70)
print("IFFCO RAJASTHAN CLEANING COMPLETE")
print("=" * 70)