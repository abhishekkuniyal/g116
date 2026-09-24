import pandas as pd
from pathlib import Path


# --------------------------------------------------
# 1. Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = (
    BASE_DIR
    / "processed"
    / "government_clean.csv"
)


# --------------------------------------------------
# 2. Load government data
# --------------------------------------------------

df = pd.read_csv(DATA_PATH)

print("Dataset shape:", df.shape)


# --------------------------------------------------
# 3. Normalize fertilizer names
# --------------------------------------------------

df["fertilizer_type"] = (
    df["fertilizer_type"]
    .str.strip()
    .str.lower()
)


# --------------------------------------------------
# 4. Cases we want to investigate
# --------------------------------------------------

cases = [
    ("Uttarakhand", "urea"),
    ("Madhya Pradesh", "urea"),
    ("Maharashtra", "npks"),
    ("Karnataka", "npks"),
]


# --------------------------------------------------
# 5. Analyze each series
# --------------------------------------------------

for state, fertilizer in cases:

    print("\n")
    print("=" * 70)
    print(f"{state} | {fertilizer.upper()}")
    print("=" * 70)

    series = df[
        (df["state"] == state)
        & (df["fertilizer_type"] == fertilizer)
    ].copy()

    series = series.sort_values(
        "financial_year"
    )

    # Calculate year-to-year sales change
    series["sales_change"] = (
        series["sales"]
        - series["sales"].shift(1)
    )

    # Calculate requirement change
    series["requirement_change"] = (
        series["requirement"]
        - series["requirement"].shift(1)
    )

    # Calculate availability change
    series["availability_change"] = (
        series["availability"]
        - series["availability"].shift(1)
    )

    print(
        series[
            [
                "financial_year",
                "sales",
                "requirement",
                "availability",
                "sales_change",
                "requirement_change",
                "availability_change",
            ]
        ].to_string(index=False)
    )


# --------------------------------------------------
# 6. Check the reporting-break observations
# --------------------------------------------------

print("\n")
print("=" * 70)
print("REPORTING-BREAK OBSERVATIONS")
print("=" * 70)

reporting_breaks = df[
    (
        (df["financial_year"] == "2018-19")
        & (
            df["state"].isin(
                [
                    "Uttar Pradesh",
                    "Uttarakhand",
                ]
            )
        )
        & (
            df["fertilizer_type"].isin(
                [
                    "urea",
                    "dap",
                ]
            )
        )
    )
]

print(
    reporting_breaks[
        [
            "financial_year",
            "state",
            "fertilizer_type",
            "sales",
            "requirement",
            "availability",
        ]
    ].to_string(index=False)
)