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
    / "requirement_availability_sales_fertilisers_2014_to_2024.csv"
)

df = pd.read_csv(INPUT_FILE)

print("=" * 70)
print("GOVERNMENT DATA CLEANING")
print("=" * 70)

print(f"\nRaw shape: {df.shape}")


# ============================================================
# 3. STANDARDIZE COLUMN NAMES
# ============================================================

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

print("\nStandardized columns:")
print(df.columns.tolist())


# ============================================================
# 4. CLEAN TEXT COLUMNS
# ============================================================

text_columns = ["financial_year", "states"]

for column in text_columns:
    df[column] = (
        df[column]
        .astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )


# ============================================================
# 5. STANDARDIZE STATE NAMES
# ============================================================

state_mapping = {
    "Chattisgarh": "Chhattisgarh",
    "Harayana": "Haryana",
    "Orissa": "Odisha",
    "Pondicherry": "Puducherry",
    "GOA": "Goa",
}


df["states"] = df["states"].replace(state_mapping)


# ============================================================
# 6. SEPARATE ALL INDIA AGGREGATE
# ============================================================

all_india_df = df[df["states"] == "All India"].copy()

state_df = df[df["states"] != "All India"].copy()

print(f"\nState-level rows : {len(state_df)}")
print(f"All India rows   : {len(all_india_df)}")


# ============================================================
# 7. REMOVE STATE CODE FROM MODEL DATA
# ============================================================

# State code is an identifier, not a meaningful numerical
# feature for forecasting.

state_df = state_df.drop(columns=["state_code"])

all_india_df = all_india_df.drop(columns=["state_code"])


# ============================================================
# 8. IDENTIFY FERTILIZER MEASURES
# ============================================================

fertilizers = {
    "urea": {
        "requirement": "requirement_urea",
        "availability": "availability_urea",
        "sales": "sales_urea",
    },
    "dap": {
        "requirement": "requirement_dap",
        "availability": "availability_dap",
        "sales": "sales_dap",
    },
    "mop": {
        "requirement": "requirement_mop",
        "availability": "availability_mop",
        "sales": "sales_mop",
    },
    "npks": {
        "requirement": "requirement_npks",
        "availability": "availability_npks",
        "sales": "sales_npks",
    },
}


# ============================================================
# 9. CONVERT WIDE FORMAT → LONG FORMAT
# ============================================================

long_data = []

for fertilizer, columns in fertilizers.items():

    temp = state_df[
        [
            "financial_year",
            "states",
            columns["requirement"],
            columns["availability"],
            columns["sales"],
        ]
    ].copy()

    temp = temp.rename(
        columns={
            "states": "state",
            columns["requirement"]: "requirement",
            columns["availability"]: "availability",
            columns["sales"]: "sales",
        }
    )

    temp["fertilizer_type"] = fertilizer

    long_data.append(temp)


clean_df = pd.concat(long_data, ignore_index=True)


# ============================================================
# 10. REORDER COLUMNS
# ============================================================

clean_df = clean_df[
    [
        "financial_year",
        "state",
        "fertilizer_type",
        "requirement",
        "availability",
        "sales",
    ]
]


# ============================================================
# 11. SORT DATA
# ============================================================

clean_df = clean_df.sort_values(
    by=[
        "financial_year",
        "state",
        "fertilizer_type",
    ]
).reset_index(drop=True)


# ============================================================
# 12. VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("POST-CLEANING VALIDATION")
print("=" * 70)

print("\nCleaned shape:")
print(clean_df.shape)

print("\nMissing values:")
print(clean_df.isnull().sum())

print("\nDuplicate rows:")
print(clean_df.duplicated().sum())

print("\nUnique fertilizer types:")
print(clean_df["fertilizer_type"].unique())

print("\nUnique states:")
print(clean_df["state"].nunique())

print("\nFinancial years:")
print(clean_df["financial_year"].unique())


# ============================================================
# 13. CHECK FOR NEGATIVE VALUES
# ============================================================

numeric_columns = [
    "requirement",
    "availability",
    "sales",
]

negative_values = (
    clean_df[numeric_columns] < 0
).sum()

print("\nNegative values:")
print(negative_values)


# ============================================================
# 14. SAVE CLEAN DATASET
# ============================================================

output_file = (
    PROCESSED_DIR
    / "government_clean.csv"
)

clean_df.to_csv(
    output_file,
    index=False
)


# ============================================================
# 15. SAVE ALL INDIA DATA SEPARATELY
# ============================================================

all_india_output = (
    PROCESSED_DIR
    / "government_all_india.csv"
)

all_india_df.to_csv(
    all_india_output,
    index=False
)


print("\nFiles created:")
print(f"  {output_file}")
print(f"  {all_india_output}")

print("\n" + "=" * 70)
print("CLEANING COMPLETE")
print("=" * 70)