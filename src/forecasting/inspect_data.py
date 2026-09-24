import pandas as pd
from pathlib import Path


# ============================================================
# 1. PROJECT PATHS
# ============================================================

# Get the project root:
# D:\IFFCO_Data_Preprocessing
PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_ROOT / "raw"


# ============================================================
# 2. DATASET PATHS
# ============================================================

government_file = (
    RAW_DIR
    / "requirement_availability_sales_fertilisers_2014_to_2024.csv"
)

production_file = (
    RAW_DIR
    / "fertiliser_production_capacity_2014_to_2024.csv"
)

iffco_supply_file = (
    RAW_DIR
    / "RS_Session_270_AU_4173_B.i.csv"
)


# ============================================================
# 3. LOAD DATASETS
# ============================================================

government_df = pd.read_csv(government_file)
production_df = pd.read_csv(production_file)
iffco_supply_df = pd.read_csv(iffco_supply_file)


# ============================================================
# 4. GENERAL DATASET INSPECTION
# ============================================================

def inspect_dataset(name, df):
    print("\n" + "=" * 70)
    print(f"DATASET: {name}")
    print("=" * 70)

    # Shape
    print("\nShape:")
    print(f"Rows    : {df.shape[0]}")
    print(f"Columns : {df.shape[1]}")

    # Columns
    print("\nColumns:")
    for column in df.columns:
        print(f"  - {column}")

    # Data types
    print("\nData types:")
    print(df.dtypes)

    # First rows
    print("\nFirst 5 rows:")
    print(df.head().to_string(index=False))

    # Missing values
    print("\nMissing values:")
    missing = df.isnull().sum()
    print(missing[missing > 0] if missing.sum() > 0 else "No missing values")

    # Duplicate rows
    print("\nDuplicate rows:")
    print(df.duplicated().sum())

    # Numerical summary
    print("\nNumerical summary:")
    print(df.describe().to_string())


# ============================================================
# 5. INSPECT ALL DATASETS
# ============================================================

inspect_dataset(
    "Government Requirement / Availability / Sales",
    government_df
)

inspect_dataset(
    "Fertiliser Production / Capacity",
    production_df
)

inspect_dataset(
    "IFFCO Rajasthan District Supply",
    iffco_supply_df
)


# ============================================================
# 6. GOVERNMENT DATASET — IMPORTANT CHECKS
# ============================================================

print("\n" + "=" * 70)
print("GOVERNMENT DATASET — STRUCTURE CHECK")
print("=" * 70)

print("\nFinancial years:")
print(
    sorted(
        government_df["financial_year"]
        .dropna()
        .unique()
    )
)

print("\nNumber of states/regions:")
print(government_df["states"].nunique())

print("\nStates/regions:")
print(
    government_df["states"]
    .sort_values()
    .unique()
)


# ============================================================
# 7. GOVERNMENT DATASET — DUPLICATE STATE/YEAR CHECK
# ============================================================

duplicate_state_year = government_df[
    government_df.duplicated(
        subset=["financial_year", "states"],
        keep=False
    )
]

print("\nDuplicate state-year combinations:")

if duplicate_state_year.empty:
    print("None")
else:
    print(duplicate_state_year.to_string(index=False))


# ============================================================
# 8. PRODUCTION DATASET — STRUCTURE CHECK
# ============================================================

print("\n" + "=" * 70)
print("PRODUCTION DATASET — STRUCTURE CHECK")
print("=" * 70)

print("\nFertiliser types:")
print(
    production_df["fertiliser_type"]
    .dropna()
    .unique()
)

print("\nStates:")
print(
    production_df["state"]
    .dropna()
    .unique()
)

print("\nCompanies:")
print(
    production_df["company"]
    .dropna()
    .unique()
)


# ============================================================
# 9. IFFCO SUPPLY DATASET — STRUCTURE CHECK
# ============================================================

print("\n" + "=" * 70)
print("IFFCO SUPPLY DATASET — STRUCTURE CHECK")
print("=" * 70)

print("\nDistrict count:")
print(iffco_supply_df["District"].nunique())

print("\nDistricts:")
print(
    iffco_supply_df["District"]
    .dropna()
    .tolist()
)


# ============================================================
# 10. FINISHED
# ============================================================

print("\n" + "=" * 70)
print("INSPECTION COMPLETE")
print("=" * 70)