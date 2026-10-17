# Data Provenance and Preparation

Raw data is downloaded from the UCI Machine Learning Repository and stored under `data/raw/`. Raw files are excluded from Git; the tracked downloader makes acquisition reproducible.

## Reproduce the local data directory

From the repository root:

```bash
python data/download_datasets.py
```

Useful options:

```bash
python data/download_datasets.py --dataset regression
python data/download_datasets.py --dataset classification
python data/download_datasets.py --dataset clustering
python data/download_datasets.py --force
```

The script verifies the archive and extracted-file SHA-256 hashes before accepting the data. It also checks expected row counts.

## Regression dataset

### Source and license

- Name: Gas Turbine CO and NOx Emission Data Set
- UCI page: <https://archive.ics.uci.edu/dataset/551/gas+turbine+co+and+nox+emission+data+set>
- DOI: <https://doi.org/10.24432/C5WC95>
- License: Creative Commons Attribution 4.0
- Official archive SHA-256: `55fdb1acc25f05bd9c77aac285c424e9154ffb0dbf1bbadb56b69a1142231295`

### Local files

| File | Expected rows | SHA-256 |
|---|---:|---|
| `raw/gas_turbine/gt_2011.csv` | 7,411 | `d87ceef9aa59533cc7d924d10de241b1b06ecd11f9b26bab59191ea0f8a76b9a` |
| `raw/gas_turbine/gt_2012.csv` | 7,628 | `be54b9d0e1a7de40c55d32fa489e75de892b000c066b5a09f09a19124ee29100` |
| `raw/gas_turbine/gt_2013.csv` | 7,152 | `13c437bb440ec2045bd12057e6654c41dd4107a661eac16ba2e878e897a08f9e` |
| `raw/gas_turbine/gt_2014.csv` | 7,158 | `c2a03c92c9c3207aad0c6be7de8d9b5b4bfa4720ad0efb2c1f21b6cec4d3f3fa` |
| `raw/gas_turbine/gt_2015.csv` | 7,384 | `9b08f35fde0d4b138232a605db4093c2b8bf9d6757e6f1fbd9534ad616c13591` |

### Regression schema and modeling role

| Column | Meaning | Modeling role |
|---|---|---|
| `AT` | Ambient temperature | Predictor |
| `AP` | Ambient pressure | Predictor |
| `AH` | Ambient humidity | Predictor |
| `AFDP` | Air-filter difference pressure | Predictor |
| `GTEP` | Gas-turbine exhaust pressure | Predictor |
| `TIT` | Turbine inlet temperature | Predictor |
| `TAT` | Turbine after-temperature | Predictor |
| `TEY` | Turbine energy yield in MWh | **Regression target** |
| `CDP` | Compressor discharge pressure | Predictor |
| `CO` | Carbon-monoxide emission measurement | Excluded outcome measurement |
| `NOX` | Nitrogen-oxide emission measurement | Excluded outcome measurement |

The source year is derived from the filename and is used only for splitting.

### Regression split policy

- Training and cross-validation: 2011-2014
- Final held-out test: 2015
- Cross-validation: five-split `TimeSeriesSplit` within the training period
- Shuffle: no

This produces an approximately 80:20 chronological split and tests future-year generalization. All ten regression algorithms must use the same 2015 test observations.

### Regression cleaning and feature contract

- Missing values: none in the verified source files.
- Duplicates: seven extra, fully identical sensor records occur in two consecutive groups in 2014. Keep the first row in each group and remove the seven extras while preserving source order.
- Outliers: retain valid observations even when a univariate 1.5-IQR rule flags them. The bounded and concentrated operating regimes make automatic IQR deletion inappropriate.
- Rows after duplicate removal: 36,726.
- Training rows after duplicate removal: 29,342.
- Final test rows: 7,384.

The Phase 2 notebook creates three deterministic candidate features:

| Engineered feature | Definition | Rationale |
|---|---|---|
| `temperature_drop` | `TIT - TAT` | Represents the thermal change across the turbine |
| `exhaust_to_discharge_pressure` | `GTEP / CDP` | Normalises exhaust pressure by compressor discharge pressure |
| `ambient_heat_load` | `AT * AH` | Represents a temperature-humidity interaction |

These features use only approved same-row measurements. Phase 3 compared the eight raw predictors against the raw predictors plus all three engineered features using five-fold temporal CV with Linear Regression. The combined engineered set was retained because its mean CV R2 was 0.987017 versus 0.986681 for the raw set. The gain is small, so the notebook treats these as supporting features rather than the source of model performance.

## Classification dataset

### Source and license

- Name: Predict Students' Dropout and Academic Success
- UCI page: <https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success>
- DOI: <https://doi.org/10.24432/C5MC89>
- License: Creative Commons Attribution 4.0
- Official archive SHA-256: `e90e55fd65ec462ae283ebeb2cca409319e3460ed898d8754f62fb35cc83a65d`

### Local file

| File | Expected rows | SHA-256 |
|---|---:|---|
| `raw/student_outcomes/data.csv` | 4,424 | `3ef126de5cefff26eb11fbb4237f1a1401cb64b488e2f1d598c23cedeb4c45ae` |

The file uses a semicolon delimiter.

### Classification target

`Target` contains three classes:

| Class | Rows | Share |
|---|---:|---:|
| Dropout | 1,421 | 32.12% |
| Enrolled | 794 | 17.95% |
| Graduate | 2,209 | 49.93% |

The 36 predictors combine enrollment information, integer-coded categories, financial indicators, first- and second-semester performance counts, grades, and macroeconomic context.

The prediction time is after completion of the second semester. This is essential because both first- and second-semester performance variables are used.

### Classification split policy

- Train/test ratio: 80:20
- Stratification target: `Target`
- Random state: 42
- Cross-validation: five-fold `StratifiedKFold` with shuffling and `random_state=42`

Every Part-A classification algorithm must use the same held-out test observations.

### Classification cleaning and feature contract

- Missing values: none in the verified source file.
- Exact duplicates: none.
- Outliers: retain legitimate rare ages, grades, and study histories; do not remove records solely because they cross a univariate IQR fence.
- Categorical integer codes: one-hot encode rather than treating their numeric codes as continuous quantities.
- Numeric features: median-impute and standardise inside the model pipeline.
- Categorical features: most-frequent impute and one-hot encode inside the model pipeline, with unknown categories ignored safely.

The Phase 2 notebook creates four deterministic academic-progress features:

| Engineered feature | Definition | Rationale |
|---|---|---|
| `approval_ratio_1st` | First-semester approved units divided by enrolled units | Normalises achievement for course load |
| `approval_ratio_2nd` | Second-semester approved units divided by enrolled units | Normalises achievement for course load |
| `approval_ratio_change` | Second-semester ratio minus first-semester ratio | Captures improvement or decline |
| `semester_grade_change` | Second-semester grade minus first-semester grade | Captures grade direction |

Zero enrolled units produce an approval ratio of zero. All engineered features use only information available at the declared end-of-second-semester prediction point. Training-only Logistic Regression CV retained only `approval_ratio_change`: mean macro F1 was 0.703238 versus 0.702053 for the raw feature set. The other engineered variables remain documented but are not passed to the Phase 3 classifiers because they did not improve the training-only check.

## Clustering dataset

### Source and license

- Name: Raisin Dataset
- UCI page: <https://archive.ics.uci.edu/dataset/850/raisin>
- DOI: <https://doi.org/10.24432/C5660T>
- License: Creative Commons Attribution 4.0
- Official download: <https://archive.ics.uci.edu/static/public/850/raisin.zip>
- Locally verified outer-archive SHA-256: `5d516c040923fd154ecf85e31b6e1b5a096724fa0e68d588c33fb5a2f0c3e5db`

The UCI outer archive contains the nested `Raisin_Dataset.zip`. The downloader validates the outer archive, extracts only `Raisin_Dataset/Raisin_Dataset.arff` from the nested archive, validates the extracted-file hash and row count, then stores it locally. The outer-archive hash above is measured from the official download on 2026-10-17; it is not presented as a publisher-issued checksum.

### Local file and audited schema

| File | Expected rows | SHA-256 |
|---|---:|---|
| `raw/raisin/Raisin_Dataset.arff` | 900 | `8a33803b5961650225150740fa09fa31ee8875266277c7ac3291e2a3ee351814` |

The verified ARFF release has seven numeric image-derived morphology features: `Area`, `MajorAxisLength`, `MinorAxisLength`, `Eccentricity`, `ConvexArea`, `Extent`, and `Perimeter`. It has zero missing values and zero exact duplicate rows.

`Class` is a separate source reference field with 450 `Besni` and 450 `Kecimen` rows. It is excluded from scaling, K-Means, Agglomerative Hierarchical Clustering, k selection, linkage selection, PCA, and t-SNE. It is used only after those choices are frozen, to describe post-hoc reference agreement.

### Clustering protocol

- Standardize all seven numeric features with `StandardScaler`.
- Evaluate K-Means candidates from k=2 through k=8 using `random_state=42` and `n_init=20`.
- Select k with the highest label-free silhouette score; retain inertia, Davies-Bouldin, and Calinski-Harabasz results for the complete comparison.
- Compare Ward, complete, and average hierarchical linkage at the selected k.
- Exclude a hierarchical candidate if its smallest cluster has fewer than 5% of the records, then choose the eligible candidate with the strongest silhouette score. This prevents a tiny outlier-like group from being presented as a meaningful two-cluster solution.
- Compute the hierarchy from all records and truncate only the dendrogram display for readability.
- Use PCA plots for both required algorithms and t-SNE for K-Means. These are explanatory views, not model-selection metrics.

The dataset is a team-proposed Review 2 direction. The course guideline says datasets are assigned by the instructor, so instructor confirmation remains required before treating it as the official submission source.

## Attribution

When redistributing or publishing derived work, retain the dataset names, UCI links, DOI citations, and Creative Commons Attribution 4.0 credit above.
