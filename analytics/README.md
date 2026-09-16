# Module 2 — Analytics

This module implements the required end-to-end analytics and predictive-modeling workflow using the Titanic dataset.

## Files

* `eda.ipynb` — Data loading, profiling, cleaning, EDA, survival analysis, correlation analysis, visualizations, and standardization
* `modeling.ipynb` — Classification, imbalance analysis, hyperparameter tuning, regression, and model persistence
* `titanic.csv` — Committed offline fallback dataset
* `titanic_best_pipeline.joblib` — Saved complete classification pipeline

## Dataset

The Titanic dataset was loaded once using `sns.load_dataset("titanic")` as required by the capstone.

Original dataset:

* 891 rows
* 15 columns

The loaded dataset was saved as `titanic.csv`. The modeling notebook reads this committed CSV instead of loading the dataset again.

## Data Cleaning

Missing-value handling followed the required percentage-based rule.

| Column        | Missing % | Handling          |
| ------------- | --------: | ----------------- |
| `deck`        |  77.2166% | Dropped           |
| `age`         |  19.8653% | Median imputation |
| `embarked`    |   0.2245% | Rows dropped      |
| `embark_town` |   0.2245% | Rows dropped      |

Median age used for imputation: `28.00`.

After cleaning:

* 889 rows
* 14 columns
* 0 missing values

## Exploratory Analysis

The EDA notebook includes the required:

* `df.info()`, `df.describe()`, and shape
* Missing-value analysis
* Age and fare histograms and box plots
* IQR-based outlier analysis
* Fare mean, median, mode, and skewness
* Survival rates by sex, passenger class, and sex + passenger class
* Required 6-column correlation matrix and heatmap
* Four multivariate charts with written interpretations
* Exploratory z-score standardization of age and fare

The detailed numerical outputs and chart interpretations are contained in `eda.ipynb`.

### Strongest Correlations

| Variable Pair      | Correlation |
| ------------------ | ----------: |
| `fare` vs `pclass` |     -0.5482 |
| `parch` vs `sibsp` |      0.4145 |

The negative `pclass`–`fare` correlation is consistent with the coding of passenger class, where higher class numbers represent lower passenger classes. The positive `parch`–`sibsp` correlation indicates an association between the number of parents/children and siblings/spouses aboard.

### Standardization Check

Age and fare were standardized using the z-score formula.

| Variable | Mean Before | Std Before | Mean After | Std After |
| -------- | ----------: | ---------: | ---------: | --------: |
| Age      |     29.3152 |    12.9849 |        ≈ 0 |       ≈ 1 |
| Fare     |     32.0967 |    49.6975 |        ≈ 0 |       ≈ 1 |

This exploratory standardization was not used in the final modeling pipeline.

## Predictive Modeling

A stratified 80/20 train-test split was used before preprocessing.

Preprocessing was implemented with `ColumnTransformer` and `Pipeline`:

* Numeric: median imputation + `StandardScaler`
* Categorical: most-frequent imputation + `OneHotEncoder`

All preprocessing steps were fitted on the training split only.

The three required classifiers were:

1. Logistic Regression
2. Decision Tree
3. Random Forest

## Classification Results

| Model               | Accuracy | Precision | Recall |     F1 | ROC-AUC |
| ------------------- | -------: | --------: | -----: | -----: | ------: |
| Logistic Regression |   0.7809 |    0.7544 | 0.6324 | 0.6880 |  0.8265 |
| Decision Tree       |   0.8146 |    0.7869 | 0.7059 | 0.7442 |  0.8207 |
| Random Forest       |   0.7978 |    0.7759 | 0.6618 | 0.7143 |  0.8211 |

The Decision Tree achieved the highest observed accuracy and F1-score, while Logistic Regression achieved the highest ROC-AUC.

## Class Imbalance

Logistic Regression was compared using:

* Baseline
* `class_weight="balanced"`
* SMOTE applied only to the training data

Precision, recall, and F1-score were compared across the three approaches. The detailed numerical comparison and conclusion are provided in `modeling.ipynb`.

## Random Forest Tuning

`GridSearchCV` was used to tune:

* `n_estimators`
* `max_depth`
* `max_features`

Best parameters:

* `n_estimators = 200`
* `max_depth = 5`
* `max_features = sqrt`

Best cross-validation ROC-AUC: `0.8586`

OOB score: `0.8073`

## Regression

A multivariate Linear Regression model was used to predict `fare`.

| Metric      |   Value |
| ----------- | ------: |
| MAE         | 21.2234 |
| RMSE        | 42.4276 |
| R²          |  0.3253 |
| Adjusted R² |  0.2295 |

A residual plot was generated and the heteroscedasticity conclusion is documented in `modeling.ipynb`.

## Final Model

The Decision Tree was selected as the final classification model based on the observed classification results, particularly its highest accuracy (`0.8146`) and F1-score (`0.7442`).

The complete preprocessing + classifier pipeline was saved as:

`titanic_best_pipeline.joblib`

The saved pipeline was reloaded successfully and verified using raw input data.

## Reproducibility

Run the notebooks in this order:

1. `eda.ipynb`
2. `modeling.ipynb`

The EDA notebook performs the single Seaborn dataset load and creates `titanic.csv`. The modeling notebook uses the committed CSV as the offline input.
