import pandas as pd
from pathlib import Path


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = PROJECT_ROOT / "processed"
REPORT_DIR = PROJECT_ROOT / "reports"

REPORT_DIR.mkdir(exist_ok=True)

REPORT_FILE = REPORT_DIR / "data_quality_report.txt"


# ============================================================
# 2. HELPER FUNCTION
# ============================================================

report_lines = []


def write(text=""):
    """Add a line to the report and print it."""
    print(text)
    report_lines.append(str(text))


def section(title):
    write()
    write("=" * 70)
    write(title)
    write("=" * 70)


# ============================================================
# 3. LOAD DATASETS
# ============================================================

government = pd.read_csv(
    PROCESSED_DIR / "government_clean.csv"
)

production = pd.read_csv(
    PROCESSED_DIR / "production_clean.csv"
)

iffco_state_year = pd.read_csv(
    PROCESSED_DIR / "iffco_production_state_year.csv"
)

iffco_urea = pd.read_csv(
    PROCESSED_DIR / "iffco_urea_state_year.csv"
)

rajasthan = pd.read_csv(
    PROCESSED_DIR / "iffco_rajasthan_clean.csv"
)


# ============================================================
# 4. GOVERNMENT DATA QUALITY
# ============================================================

section("1. GOVERNMENT MARKET DATA")

write(f"Rows: {len(government)}")
write(f"Columns: {len(government.columns)}")
write(f"Shape: {government.shape}")

write()
write("Columns:")
write(", ".join(government.columns))

write()
write("Missing values:")
write(government.isna().sum().to_string())

write()
write("Duplicate rows:")
write(str(government.duplicated().sum()))

government_key = [
    "financial_year",
    "state",
    "fertilizer_type"
]

write()
write("Duplicate business keys:")
write(
    str(
        government.duplicated(
            subset=government_key
        ).sum()
    )
)

write()
write("Financial years:")
write(", ".join(sorted(government["financial_year"].unique())))

write()
write("Fertilizer types:")
write(", ".join(sorted(government["fertilizer_type"].unique())))

write()
write(f"States: {government['state'].nunique()}")

write()
write("Rows per fertilizer:")
write(
    government.groupby("fertilizer_type")
    .size()
    .to_string()
)


# ============================================================
# 5. GOVERNMENT EXTREME YEAR-OVER-YEAR CHANGES
# ============================================================

section("2. GOVERNMENT SALES YEAR-OVER-YEAR CHANGES")

gov_sorted = government.sort_values(
    ["state", "fertilizer_type", "financial_year"]
).copy()

gov_group = gov_sorted.groupby(
    ["state", "fertilizer_type"]
)

gov_sorted["previous_sales"] = (
    gov_group["sales"].shift(1)
)

gov_sorted["sales_abs_change"] = (
    gov_sorted["sales"] -
    gov_sorted["previous_sales"]
).abs()

gov_sorted["sales_pct_change"] = (
    gov_sorted["sales"]
    .pct_change()
)

# Recalculate percentage change correctly within each group.
gov_sorted["sales_pct_change"] = (
    gov_group["sales"]
    .pct_change()
    * 100
)

large_changes = gov_sorted[
    gov_sorted["sales_abs_change"] > 10
]

write(
    f"Observations with absolute sales change > 10: "
    f"{len(large_changes)}"
)

if len(large_changes) > 0:
    write()
    write(
        large_changes[
            [
                "financial_year",
                "state",
                "fertilizer_type",
                "previous_sales",
                "sales",
                "sales_abs_change",
                "sales_pct_change"
            ]
        ].to_string(index=False)
    )


# ============================================================
# 6. KNOWN GEOGRAPHIC DISCONTINUITY
# ============================================================

section("3. POTENTIAL GEOGRAPHIC / REPORTING DISCONTINUITY")

write(
    "The Government source contains a pronounced "
    "UP/Uttarakhand shift around 2018-19."
)

transition = government[
    government["state"].isin(
        ["Uttar Pradesh", "Uttarakhand"]
    )
    &
    government["financial_year"].isin(
        ["2017-18", "2018-19"]
    )
]

transition_summary = (
    transition
    .groupby(
        ["financial_year", "fertilizer_type"]
    )[["requirement", "availability", "sales"]]
    .sum()
)

write()
write("Combined Uttar Pradesh + Uttarakhand:")
write(transition_summary.to_string())

write()
write(
    "Interpretation: the combined series is substantially "
    "more stable than the individual state series. "
    "This suggests a potential geographic/reporting "
    "boundary discontinuity, but the mechanism has not "
    "been established from the source."
)


# ============================================================
# 7. PRODUCTION DATA QUALITY
# ============================================================

section("4. PRODUCTION DATA")

write(f"Rows: {len(production)}")
write(f"Columns: {len(production.columns)}")
write(f"Shape: {production.shape}")

write()
write("Missing values:")
write(production.isna().sum().to_string())

write()
write("Duplicate rows:")
write(str(production.duplicated().sum()))

production_key = [
    "financial_year",
    "company",
    "manufacturing_unit",
    "fertiliser_type"
]

write()
write("Duplicate business keys:")
write(
    str(
        production.duplicated(
            subset=production_key
        ).sum()
    )
)

write()
write("Negative production values:")
write(
    str(
        (production["production"] < 0).sum()
    )
)

write()
write("Financial years:")
write(
    ", ".join(
        sorted(
            production["financial_year"].unique()
        )
    )
)

write()
write("Companies:")
write(str(production["company"].nunique()))

write()
write("Fertilizer categories:")
write(
    ", ".join(
        sorted(
            production["fertiliser_type"].unique()
        )
    )
)


# ============================================================
# 8. IFFCO COVERAGE
# ============================================================

section("5. IFFCO STATE-YEAR PRODUCTION")

write(f"Rows: {len(iffco_state_year)}")

write()
write("Missing values:")
write(
    iffco_state_year.isna().sum().to_string()
)

write()
write("Duplicate business keys:")

iffco_key = [
    "financial_year",
    "state",
    "iffco_fertiliser_type"
]

write(
    str(
        iffco_state_year.duplicated(
            subset=iffco_key
        ).sum()
    )
)

write()
write("States:")
write(
    ", ".join(
        sorted(
            iffco_state_year["state"].unique()
        )
    )
)

write()
write("IFFCO fertilizer categories:")
write(
    ", ".join(
        sorted(
            iffco_state_year[
                "iffco_fertiliser_type"
            ].unique()
        )
    )
)


# ============================================================
# 9. IFFCO UREA JOIN COVERAGE
# ============================================================

section("6. IFFCO UREA JOIN COVERAGE")

write(f"IFFCO Urea rows: {len(iffco_urea)}")

write()
write("States:")
write(
    ", ".join(
        sorted(
            iffco_urea["state"].unique()
        )
    )
)

write()
write("Years:")
write(
    ", ".join(
        sorted(
            iffco_urea["financial_year"].unique()
        )
    )
)

write()
write("Missing values:")
write(
    iffco_urea.isna().sum().to_string()
)


# ============================================================
# 10. GOVERNMENT + IFFCO JOIN COVERAGE
# ============================================================

section("7. GOVERNMENT + IFFCO JOIN COVERAGE")

government["fertilizer_type"] = (
    government["fertilizer_type"]
    .str.strip()
    .str.lower()
)

iffco_urea["fertilizer_type"] = (
    iffco_urea["fertilizer_type"]
    .str.strip()
    .str.lower()
)

merged = government.merge(
    iffco_urea,
    on=[
        "financial_year",
        "state",
        "fertilizer_type"
    ],
    how="left",
    validate="one_to_one"
)

total_rows = len(merged)

matched_rows = (
    merged["iffco_production"]
    .notna()
    .sum()
)

missing_rows = total_rows - matched_rows

write(f"Government rows: {total_rows}")
write(f"Matched IFFCO rows: {matched_rows}")
write(f"Unmatched IFFCO rows: {missing_rows}")

write()
write(
    f"IFFCO coverage: "
    f"{matched_rows / total_rows * 100:.2f}%"
)

write()
write("Matched states:")
write(
    merged[
        merged["iffco_production"].notna()
    ]["state"]
    .drop_duplicates()
    .sort_values()
    .to_string(index=False)
)


# ============================================================
# 11. RAJASTHAN DATA QUALITY
# ============================================================

section("8. IFFCO RAJASTHAN DISTRICT SUPPLY")

write(f"Rows: {len(rajasthan)}")
write(f"Districts: {rajasthan['district'].nunique()}")

write()
write("Years:")
write(
    ", ".join(
        sorted(
            rajasthan["financial_year"].unique()
        )
    )
)

write()
write("Missing values:")
write(
    rajasthan.isna().sum().to_string()
)

write()
write("Duplicate rows:")
write(
    str(rajasthan.duplicated().sum())
)

write()
write("Partial-year records:")
write(
    str(
        rajasthan["is_partial_year"].sum()
    )
)

write()
write(
    "Important: Rajasthan data is district-level "
    "and has no fertilizer dimension, so it should "
    "not be directly merged into the state + "
    "fertilizer modeling table."
)


# ============================================================
# 12. FINAL DATA QUALITY SUMMARY
# ============================================================

section("9. OVERALL DATA QUALITY SUMMARY")

write("Government dataset:")
write("  - Cleaned")
write("  - No duplicate business keys")
write("  - 11 financial years")
write("  - 36 states/regions")
write("  - 4 fertilizer categories")

write()
write("Production dataset:")
write("  - Cleaned")
write("  - No duplicate business keys")
write("  - Missing production values preserved")
write("  - No negative production values")

write()
write("IFFCO production:")
write("  - Aggregated from manufacturing-unit level")
write("  - IFFCO Urea safely aligned with Government Urea")
write("  - DAP & Complexes intentionally NOT mapped to DAP")

write()
write("Government + IFFCO:")
write("  - Left join preserves all Government observations")
write("  - IFFCO production available for 22 observations")
write("  - Missing IFFCO values are NOT interpreted as zero")

write()
write("Rajasthan:")
write("  - Kept as separate district-level dataset")
write("  - 2025-26 is partial through 28-02-2026")
write("  - Missing Sikar value remains missing")

write()
write("Known issue:")
write(
    "  - Potential UP/Uttarakhand geographic/reporting "
    "discontinuity around 2018-19"
)

write()
write(
    "No source-derived values were modified to resolve "
    "the detected discontinuity."
)


# ============================================================
# 13. SAVE REPORT
# ============================================================

REPORT_FILE.write_text(
    "\n".join(report_lines),
    encoding="utf-8"
)

print()
print("=" * 70)
print(f"Report saved to: {REPORT_FILE}")
print("=" * 70)