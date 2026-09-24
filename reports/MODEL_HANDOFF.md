# IFFCO Demand Forecasting — Model Handoff

## 1. Project Overview

This project prepares fertilizer demand data for forecasting and produces a
2025-26 demand forecast at State/UT/region × fertilizer level.

The forecasting target is fertilizer sales.

The forecasting scenario is:

> At the end of financial year t, use information available through t
> to forecast sales for financial year t+1.

---

## 2. Data Sources

### Government Fertilizer Dataset

Contains State/UT/region-level:

- Requirement
- Availability
- Sales

for:

- Urea
- DAP
- MOP
- NPKS

Financial years:

2014-15 to 2024-25.

The cleaned modeling data contains:

- 36 State/UT/region entities
- 4 fertilizer types
- 11 financial years

The State/UT/region level data is kept separate from the All India
aggregate to avoid mixing geographic levels.

---

### Fertilizer Production Dataset

Contains fertilizer production information by:

- State
- City
- Company
- Manufacturing unit
- Fertilizer type
- Financial year

IFFCO company names were normalized during preprocessing.

IFFCO production was aggregated at:

financial_year × state × fertilizer_type

level.

IFFCO production is treated as an auxiliary feature and is not required
by the final forecasting method.

---

### IFFCO Rajasthan Dataset

Contains IFFCO fertilizer supply by Rajasthan district.

It is maintained separately because its grain differs from the main
government demand dataset and it does not contain a fertilizer-type
dimension.

The 2025-26 Rajasthan values are partial-year values through
28-02-2026.

---

## 3. Main Modeling Dataset

File:

`processed/modeling/demand_forecasting.csv`

Shape:

1440 rows × 14 columns.

Columns:

- financial_year
- state
- fertilizer_type
- sales_current
- sales_lag_1
- requirement_current
- requirement_lag_1
- availability_current
- availability_lag_1
- iffco_production_current
- iffco_production_lag_1
- iffco_production_available
- potential_reporting_break
- target_sales

### Target

`target_sales` represents next financial year's sales.

For a row representing financial year t:

`target_sales = sales in t+1`

---

## 4. Train / Validation / Test Strategy

The split is chronological rather than random.

### Training

2015-16 to 2020-21

### Validation

2021-22 to 2022-23

### Test

2023-24

### Future Forecast

2024-25 observations are used to forecast 2025-26.

This prevents future information from being used to train the model.

---

## 5. Models Evaluated

The following approaches were evaluated:

1. Naive Persistence
2. Linear Regression
3. Random Forest
4. Random Forest with additional change/gap features
5. Drift baseline
6. Recent-change baseline

Rolling/expanding validation was also performed.

---

## 6. Final Forecasting Method

The final forecasting method is:

### Naive Persistence

For each State/UT/region and fertilizer:

`forecast(t+1) = sales(t)`

Therefore:

`2025-26 forecast = 2024-25 sales`

This method was selected as the primary forecasting approach based on
rolling/expanding historical evaluation.

It is intentionally simple and provides a strong baseline for this
dataset.

---

## 7. Rolling Evaluation

Forecast periods evaluated:

- 2019-20
- 2020-21
- 2021-22
- 2022-23
- 2023-24

Average rolling results:

| Model | MAE | RMSE | R² |
|---|---:|---:|---:|
| Naive Persistence | 0.4349 | 0.9254 | 0.9894 |
| Random Forest | 0.5203 | 1.3111 | 0.9760 |
| Linear Regression | 1.0312 | 1.8651 | 0.9389 |

Naive Persistence produced the lowest average MAE and RMSE and the
highest average R² among these evaluated approaches.

In the five rolling forecast periods, Naive Persistence had lower MAE
in four periods.

Random Forest performed better on MAE in the 2023-24 forecast period,
so it is retained as a benchmark rather than discarded.

---

## 8. Final Forecast

File:

`processed/modeling/final_forecast_2025_26.csv`

Expected dimensions:

144 rows

36 State/UT/region entities × 4 fertilizer types.

Columns:

- forecast_year
- state
- fertilizer_type
- sales_2024_25
- predicted_sales
- forecast_method
- forecast_basis

### Forecast validation

- Rows: 144
- Missing predictions: 0
- Negative predictions: 0
- Unique states/regions: 36
- Unique fertilizer types: 4

---

## 9. Important Data Quality Finding

The government dataset contains a potential reporting discontinuity
around 2018-19 involving Uttar Pradesh and Uttarakhand.

Affected observations include:

- Uttar Pradesh — DAP
- Uttar Pradesh — Urea
- Uttarakhand — DAP
- Uttarakhand — Urea

The source values were preserved.

They were not manually corrected or replaced.

The observations are flagged using:

`potential_reporting_break`

The mechanism behind the discontinuity has not been established from
the available source data, so it should not be interpreted as a confirmed
administrative change.

---

## 10. Important Modeling Limitations

### Historical reporting discontinuity

Some historical State/UT series contain abrupt changes that may represent
reporting or geographic allocation differences.

### IFFCO production coverage

IFFCO production is only available for certain states and fertilizer
categories.

Missing IFFCO production means unavailable data, not zero production.

### Rajasthan IFFCO dataset

The Rajasthan district supply dataset has a different data grain and is
not directly merged into the main State/UT × fertilizer forecasting
dataset.

### Annual/financial-year granularity

The current forecasting dataset is annual by financial year.

It should not be represented as a monthly forecasting system.

### 2025-26 forecast

The 2025-26 values in the final forecast are predictions based on
2024-25 sales. They are not actual 2025-26 observations.

---

## 11. Backend Integration Contract

The backend can consume:

`final_forecast_2025_26.csv`

Primary fields:

- state
- fertilizer_type
- forecast_year
- predicted_sales

Example:

```json
{
  "forecast_year": "2025-26",
  "state": "Uttarakhand",
  "fertilizer_type": "urea",
  "predicted_sales": 79.18
}