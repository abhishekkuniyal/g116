import pandas as pd
from pathlib import Path


# --------------------------------------------------
# 1. Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "processed"
    / "iffco_production_state_year.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "processed"
    / "iffco_urea_state_year.csv"
)


# --------------------------------------------------
# 2. Load aggregated IFFCO production
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)

print("Loaded aggregated IFFCO production:")
print(f"Shape: {df.shape}")


# --------------------------------------------------
# 3. Keep only Urea
# --------------------------------------------------

urea = df[
    df["iffco_fertiliser_type"].eq("Urea")
].copy()


# --------------------------------------------------
# 4. Rename columns
# --------------------------------------------------

urea = urea.rename(
    columns={
        "iffco_fertiliser_type": "fertilizer_type"
    }
)


# --------------------------------------------------
# 5. Validation
# --------------------------------------------------

print("\nUrea dataset:")
print(urea.to_string(index=False))

print("\nShape:")
print(urea.shape)

print("\nMissing values:")
print(urea.isna().sum().to_string())

print("\nDuplicate business keys:")

key_columns = [
    "financial_year",
    "state",
    "fertilizer_type"
]

print(
    urea.duplicated(
        subset=key_columns
    ).sum()
)


# --------------------------------------------------
# 6. Save
# --------------------------------------------------

urea.to_csv(
    OUTPUT_FILE,
    index=False
)

print(f"\nSaved to: {OUTPUT_FILE}")