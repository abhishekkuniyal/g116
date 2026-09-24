import pandas as pd
from pathlib import Path


# --------------------------------------------------
# 1. Define project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = PROJECT_ROOT / "processed" / "production_clean.csv"
OUTPUT_FILE = PROJECT_ROOT / "processed" / "iffco_production_state_year.csv"


# --------------------------------------------------
# 2. Load cleaned production data
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)

print("Loaded production data:")
print(f"Shape: {df.shape}")


# --------------------------------------------------
# 3. Keep only IFFCO records
# --------------------------------------------------

iffco = df[
    df["company"].eq("Indian Farmers Fertilizers Cooperative Ltd.")
].copy()

print(f"IFFCO records: {len(iffco)}")


# --------------------------------------------------
# 4. Check IFFCO fertilizer categories
# --------------------------------------------------

print("\nIFFCO fertilizer categories:")
print(iffco["fertiliser_type"].value_counts().to_string())


# --------------------------------------------------
# 5. Aggregate manufacturing units
# --------------------------------------------------

# We aggregate plant-level production into:
#
# financial_year + state + fertiliser_type
#
# This removes the manufacturing-unit level because
# our Government dataset does not have a plant dimension.

aggregated = (
    iffco
    .groupby(
        ["financial_year", "state", "fertiliser_type"],
        as_index=False
    )["production"]
    .sum()
)


# --------------------------------------------------
# 6. Rename fertilizer column
# --------------------------------------------------

aggregated = aggregated.rename(
    columns={
        "fertiliser_type": "iffco_fertiliser_type",
        "production": "iffco_production"
    }
)


# --------------------------------------------------
# 7. Sort the dataset
# --------------------------------------------------

aggregated = aggregated.sort_values(
    ["financial_year", "state", "iffco_fertiliser_type"]
).reset_index(drop=True)


# --------------------------------------------------
# 8. Validation
# --------------------------------------------------

print("\nAggregated shape:")
print(aggregated.shape)

print("\nAggregated data:")
print(aggregated.to_string(index=False))


print("\nMissing values:")
print(aggregated.isna().sum().to_string())


print("\nDuplicate rows:")
print(aggregated.duplicated().sum())


print("\nDuplicate business keys:")
key_columns = [
    "financial_year",
    "state",
    "iffco_fertiliser_type"
]

print(
    aggregated.duplicated(
        subset=key_columns
    ).sum()
)


# --------------------------------------------------
# 9. Save
# --------------------------------------------------

aggregated.to_csv(
    OUTPUT_FILE,
    index=False
)

print(f"\nSaved to: {OUTPUT_FILE}")