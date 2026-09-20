# 23CSE301 Machine Learning Capstone

End-to-end machine-learning study for the 2026-27 `23CSE301 Machine Learning` capstone.

## Team

| Team member | Registration number | Review 1 responsibility |
|---|---|---|
| Hasini Kancharapu | CB.SC.U4CSE24123 | Classification Part A |
| Kolan Shruhath Reddy | CB.SC.U4CSE24124 | Regression algorithms 6-10 and regression integration |
| Dharani B | CB.SC.U4CSE24161 | Regression algorithms 1-5 |

Implementation is divided for efficiency, but every member reviews the complete work and prepares to explain any submitted section during the viva.

## Review 1 problems

### Regression: gas-turbine energy-yield estimation

Estimate hourly turbine energy yield (`TEY`, MWh) using ambient conditions and turbine operating measurements. The study uses a chronological evaluation: observations from 2011-2014 form the training and cross-validation period, while 2015 remains the final unseen test year.

The emission measurements `CO` and `NOX` are excluded from the predictors. The model is treated as a contemporaneous soft sensor rather than a long-range forecast.

Source: [UCI Gas Turbine CO and NOx Emission Data Set](https://archive.ics.uci.edu/dataset/551/gas+turbine+co+and+nox+emission+data+set), DOI [10.24432/C5WC95](https://doi.org/10.24432/C5WC95).

### Classification: three-way academic outcome early warning

Classify the eventual student outcome as `Dropout`, `Enrolled`, or `Graduate` using information available through the end of the second semester. The intended use is human-led academic support, not automated academic decision-making.

Source: [UCI Predict Students' Dropout and Academic Success](https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success), DOI [10.24432/C5MC89](https://doi.org/10.24432/C5MC89).

Both datasets are distributed under the Creative Commons Attribution 4.0 license.

## Current Review 1 progress

- Phase 0: problem framing, source audit, target selection, leakage review, and evaluation protocols completed.
- Phase 1: repository structure, verified dataset acquisition, provenance documentation, and reproducible environment completed.
- Phase 2: dataset audit, EDA, cleaning decisions, deterministic feature engineering, fixed splits, and leakage-safe preprocessing implemented in both notebooks.
- Phase 3: all ten regression algorithms and all five Classification Part-A algorithms implemented, tuned, evaluated, and documented.

Both Review 1 notebooks have been executed from top to bottom with visible outputs and no saved execution errors. Team verification of every interpretation and instructor confirmation of the selected datasets and split protocols remain required before evaluation.

## Repository structure

```text
app/                       Optional GUI and deployment code
data/
  README.md                Data provenance, schema, and split policy
  download_datasets.py     Verified dataset downloader
  raw/                     Local raw files; excluded from Git
figures/                   Essential exported visualizations
models/                    Optional saved final pipelines
notebooks/
  regression.ipynb         Review 1 regression track
  classification.ipynb     Review 1 classification Part A
results/                   Essential exported comparison tables
requirements.txt           Pinned Python dependencies
```

## Environment setup

Python 3.13 is used for the reproducible environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Download and verify the datasets

```bash
python data/download_datasets.py
```

The downloader retrieves the official UCI archives, verifies their SHA-256 hashes, extracts only the expected CSV files, validates file hashes and row counts, and writes them under `data/raw/`.

Dataset files are deliberately excluded from Git. See [data/README.md](data/README.md) for provenance, checksums, features, targets, and split rules.

## Run the notebooks

```bash
jupyter lab
```

Run each notebook from the first cell to the last with the working directory set to the repository root. All random operations use `random_state=42` where applicable.

To reproduce the saved Phase 2 outputs non-interactively:

```bash
python -m jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=600 notebooks/regression.ipynb
python -m jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=600 notebooks/classification.ipynb
```

## Evaluation principles

- Every algorithm within a track uses the same held-out test observations.
- Preprocessing is fitted on training data only through scikit-learn pipelines.
- Hyperparameters are selected only through training-set cross-validation.
- Regression uses R2, RMSE, MAE, and time-aware cross-validation.
- Classification reports Accuracy, Precision, Recall, weighted F1, confusion matrices, and multiclass One-vs-Rest ROC-AUC.
- Macro F1 and per-class recall supplement the mandatory metrics for the imbalanced classification target.
- The held-out test set is not used for feature selection or hyperparameter tuning.

## Review 1 results

### Regression comparison

All models use 2011-2014 for training and time-aware validation and the same untouched 2015 test year.

| Model | Test R2 | RMSE (MWh) | MAE (MWh) | Mean CV R2 |
|---|---:|---:|---:|---:|
| Random Forest Regressor | 0.9951 | 1.1318 | 0.8536 | 0.9858 |
| Gradient Boosting Regressor | 0.9933 | 1.3273 | 1.0387 | 0.9860 |
| Decision Tree Regressor | 0.9906 | 1.5690 | 1.2080 | 0.9824 |
| Lasso Regression | 0.9866 | 1.8748 | 1.3323 | 0.9911 |
| Polynomial Regression | 0.9857 | 1.9374 | 1.3694 | 0.9870 |
| Linear Regression | 0.9857 | 1.9374 | 1.3694 | 0.9870 |
| Ridge Regression | 0.9799 | 2.2936 | 1.6377 | 0.9925 |
| Support Vector Regressor | 0.9768 | 2.4657 | 1.6511 | 0.9880 |
| ElasticNet Regression | 0.9686 | 2.8688 | 2.0224 | 0.9933 |
| K-Nearest Neighbors Regressor | 0.9603 | 3.2225 | 2.2300 | 0.9864 |

ElasticNet was preselected by the highest mean temporal-CV R2. Random Forest subsequently produced the strongest descriptive 2015 result. The disagreement is reported rather than using 2015 to retroactively change hyperparameters; it indicates that model rankings vary across operating years. The notebook includes diagnostics for both models.

### Classification Part A comparison

All models use the same stratified 80:20 split. Hyperparameters were selected by five-fold training macro F1.

| Model | Accuracy | Weighted F1 | Macro F1 | Weighted OvR ROC-AUC | Mean CV Macro F1 |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 0.7356 | 0.7485 | 0.6983 | 0.9010 | 0.7144 |
| Support Vector Classifier | 0.7243 | 0.7353 | 0.6839 | 0.8902 | 0.7157 |
| Decision Tree Classifier | 0.7243 | 0.7169 | 0.6488 | 0.8655 | 0.6679 |
| K-Nearest Neighbors | 0.7153 | 0.6989 | 0.6278 | 0.8392 | 0.6267 |
| Gaussian Naive Bayes | 0.2531 | 0.1792 | 0.2296 | 0.7218 | 0.2296 |

SVC was preselected by training macro F1 and achieved `Enrolled` recall of 0.6038. Logistic Regression produced the highest descriptive held-out weighted F1. Gaussian Naive Bayes reached very high `Enrolled` recall by severely over-predicting that class, producing only 0.1992 precision and 0.2531 overall accuracy; this is not a useful trade-off.

Detailed best parameters, per-class classification metrics, top-two fold results, tuning comparisons, and subgroup checks are exported under `results/` from the same notebook executions.

## Review 1 conclusions and limitations

- The turbine measurements support highly accurate contemporaneous energy-yield estimation, but the work must not be presented as long-range forecasting.
- Temporal-CV and 2015 model rankings differ, showing why an honest future-year holdout matters.
- Student outcome accuracy alone is insufficient because `Enrolled` remains the hardest class.
- Student predictions are associations from one Portuguese institution and are suitable only for human-reviewed support analysis.
- Coefficients, tree importance, subgroup error differences, and correlations do not establish causation.
- Instructor approval and independent team verification remain required before presentation.

## Responsible-use statement

The student-outcome model is an educational analysis and decision-support exercise. Its predictions must not be treated as causal explanations or used to make automated decisions about a student. Results are specific to the source institution and require validation before any use in a different educational setting.

## AI-assistance disclosure

Generative-AI tools assisted with planning, dataset-audit support, code scaffolding, documentation, reproducibility utilities, initial notebook construction, and draft observation text. The team must independently rerun the notebooks, verify every displayed result, revise interpretations in its own words, validate all modeling decisions, and be able to explain every submitted line during the viva. AI-generated scaffolding does not replace the team's required analysis or interpretation.
