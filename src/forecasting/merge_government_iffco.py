import pandas as pd
from pathlib import Path


# --------------------------------------------------
# 1. Define paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

GOVERNMENT_FILE = (
    PROJECT_ROOT / "processed" / "government_clean.csv"
)

IFFCO_FILE = (
    PROJECT_ROOT / "processed" / "iffco_urea_state_year.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT / "processed" / "government_iffco_merged.csv"
)


# --------------------------------------------------
# 2. Load datasets
# --------------------------------------------------

government = pd.read_csv(GOVERNMENT_FILE)
iffco = pd.read_csv(IFFCO_FILE)

print("Government shape:", government.shape)
print("IFFCO shape:", iffco.shape)


# --------------------------------------------------
# 3. Normalize join key
# --------------------------------------------------

# Government uses lowercase fertilizer names:
# urea, dap, mop, npks
#
# IFFCO currently has:
# Urea
#
# Convert both to lowercase so the join is consistent.

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
# 4. Validate Government business key
# --------------------------------------------------

key_columns = [
    "financial_year",
    "state",
    "fertilizer_type"
]

print("\nGovernment duplicate keys:")
print(
    government.duplicated(
        subset=key_columns
    ).sum()
)


# --------------------------------------------------
# 5. Validate IFFCO business key
# --------------------------------------------------

print("\nIFFCO duplicate keys:")
print(
    iffco.duplicated(
        subset=key_columns
    ).sum()
)


# --------------------------------------------------
# 6. Merge
# --------------------------------------------------

# LEFT JOIN:
#
# Keep every Government observation.
# Add IFFCO production wherever a matching
# year + state + fertilizer exists.

merged = government.merge(
    iffco[
        key_columns + ["iffco_production"]
    ],
    on=key_columns,
    how="left",
    validate="one_to_one"
)


# --------------------------------------------------
# 7. Validation
# --------------------------------------------------

print("\nMerged shape:")
print(merged.shape)

print("\nMerged columns:")
print(merged.columns.tolist())


print("\nIFFCO production availability:")
print(
    merged["iffco_production"]
    .notna()
    .value_counts()
    .to_string()
)


print("\nRows with IFFCO production:")
print(
    merged[
        merged["iffco_production"].notna()
    ].to_string(index=False)
)


print("\nMissing values:")
print(
    merged.isna().sum().to_string()
)


print("\nDuplicate business keys after merge:")
print(
    merged.duplicated(
        subset=key_columns
    ).sum()
)


# --------------------------------------------------
# 8. Save
# --------------------------------------------------

merged.to_csv(
    OUTPUT_FILE,
    index=False
)

print(f"\nSaved to: {OUTPUT_FILE}")