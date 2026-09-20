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

## Evaluation principles

- Every algorithm within a track uses the same held-out test observations.
- Preprocessing is fitted on training data only through scikit-learn pipelines.
- Hyperparameters are selected only through training-set cross-validation.
- Regression uses R2, RMSE, MAE, and time-aware cross-validation.
- Classification reports Accuracy, Precision, Recall, weighted F1, confusion matrices, and multiclass One-vs-Rest ROC-AUC.
- Macro F1 and per-class recall supplement the mandatory metrics for the imbalanced classification target.
- The held-out test set is not used for feature selection or hyperparameter tuning.

## Responsible-use statement

The student-outcome model is an educational analysis and decision-support exercise. Its predictions must not be treated as causal explanations or used to make automated decisions about a student. Results are specific to the source institution and require validation before any use in a different educational setting.

## AI-assistance disclosure

Generative-AI tools were used for code scaffolding, documentation support, and reproducibility utilities. All dataset decisions, feature engineering, analysis, experimental validation, and interpretations were independently performed and verified by the team. Every team member is responsible for understanding and explaining the submitted work during the viva.
