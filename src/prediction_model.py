import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# --- Data Loading/Creation (Adjusted for your date range) ---
# Replace this with your actual data loading if you have a CSV or similar:
# df = pd.read_csv('your_climate_and_flood_data.csv', parse_dates=['timestamp'])
# df = df.set_index('timestamp').sort_index()

# Dummy Data Creation (ADJUSTED for 2023-04-30 to 2025-04-30)
np.random.seed(42) # for reproducibility

dates = pd.date_range(start='2023-04-30', end='2025-04-30', freq='D')
n_days = len(dates)

# Base climate variables
temperature_2m_mean = 25 + 5 * np.sin(np.arange(n_days) / 365 * 2 * np.pi) + np.random.randn(n_days) * 2
temperature_2m_max = temperature_2m_mean + np.random.randn(n_days) * 3 + 2
wind_direction_10m_dominant = np.random.randint(0, 360, n_days) # Degrees

# Rainfall (simulate periods of heavy rain)
precipitation_sum = np.zeros(n_days)
# Simulate some heavy rain periods
for _ in range(30): # Fewer events for shorter duration
    start_idx = np.random.randint(0, n_days - 15) # Adjust range
    duration = np.random.randint(3, 7) # Adjust duration
    intensity = np.random.rand() * 100 + 50 # mm/day
    precipitation_sum[start_idx : start_idx + duration] = np.random.rand(duration) * intensity

rain_sum = precipitation_sum # As per your correlation matrix, they are identical

df = pd.DataFrame({
    'temperature_2m_mean': temperature_2m_mean,
    'temperature_2m_max': temperature_2m_max,
    'wind_direction_10m_dominant': wind_direction_10m_dominant,
    'precipitation_sum': precipitation_sum,
    'rain_sum': rain_sum,
}, index=dates)

# Simulate flood events based on lagged high rainfall and accumulated rainfall
df['flood_event'] = 0 # Initialize to no flood

# A flood might occur if precipitation_sum was high yesterday and day before
# Or if accumulated rain over 3 days is high
df['precipitation_sum_lag1'] = df['precipitation_sum'].shift(1)
df['precipitation_sum_lag2'] = df['precipitation_sum'].shift(2)
df['precipitation_sum_3day_sum'] = df['precipitation_sum'].rolling(window=3).sum().shift(1) # Sum of previous 3 days

# Define flood conditions (example logic)
# A flood event (1) if:
# - Daily precipitation was > 80mm yesterday OR
# - Accumulated 3-day precipitation was > 150mm
df.loc[
    (df['precipitation_sum_lag1'] > 80) |
    (df['precipitation_sum_3day_sum'] > 150)
    , 'flood_event'
] = 1

# Reduce number of floods to make it more realistic (imbalanced)
flood_indices = df[df['flood_event'] == 1].index
num_to_keep = int(len(flood_indices) * 0.15) # Keep slightly more for shorter dataset
indices_to_remove = np.random.choice(flood_indices, size=len(flood_indices) - num_to_keep, replace=False)
df.loc[indices_to_remove, 'flood_event'] = 0

# Ensure flood_event is int type
df['flood_event'] = df['flood_event'].astype(int)

# Drop helper columns and NaNs from shifts
df.drop(columns=['precipitation_sum_lag1', 'precipitation_sum_lag2', 'precipitation_sum_3day_sum'], inplace=True)
df.dropna(inplace=True)

print("DataFrame head with dummy data:")
print(df.head())
print("\nFlood events count:")
print(df['flood_event'].value_counts())
print(f"Dataset range: {df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}")

# Training Model
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE # If you choose to use SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline # Use imblearn's pipeline for SMOTE

# Define features (X) and target (y)
# Ensure all your engineered features (like lagged ones) are in X
X = df_correlated.drop('flood_event', axis=1) # df_correlated is from the previous step
y = df_correlated['flood_event']

# --- Time-Series Split (ADJUSTED for your specific date range) ---
# Your data ranges from 2023-04-30 to 2025-04-30 (2 years).
# A good split for training (older data) and testing (newer data) would be:
# Train: 2023-04-30 to 2024-10-29 (approx. 1.5 years)
# Test:  2024-10-30 to 2025-04-30 (approx. 0.5 years)

split_date = pd.to_datetime('2024-10-30') # Set the cutoff date for your split

X_train = X[X.index < split_date]
y_train = y[y.index < split_date]

X_test = X[X.index >= split_date]
y_test = y[y.index >= split_date]

print(f"Training data range: {X_train.index.min().strftime('%Y-%m-%d')} to {X_train.index.max().strftime('%Y-%m-%d')}")
print(f"Testing data range: {X_test.index.min().strftime('%Y-%m-%d')} to {X_test.index.max().strftime('%Y-%m-%d')}")
print(f"Training data shape: {X_train.shape}, Target shape: {y_train.shape}")
print(f"Testing data shape: {X_test.shape}, Target shape: {y_test.shape}")
print(f"Flood events in training: {y_train.sum()} ({y_train.sum()/len(y_train)*100:.2f}%)")
print(f"Flood events in testing: {y_test.sum()} ({y_test.sum()/len(y_test)*100:.2f}%)")

# --- Feature Scaling ---
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test) # IMPORTANT: Only transform test set, do not fit again!

# Convert back to DataFrame with original column names (optional, but good for debugging)
X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns, index=X_train.index)
X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns, index=X_test.index)

# Remaining training code is the same
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, precision_recall_curve, auc
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV # For hyperparameter tuning

print("\n--- 4. Training the Model ---")

# --- Option 1: Simple RandomForest with class_weight ---
print("\nTraining RandomForestClassifier with class_weight='balanced'...")
model_rf = RandomForestClassifier(
    n_estimators=100,      # Number of trees in the forest
    random_state=42,       # For reproducibility
    class_weight='balanced' # Crucial for imbalanced datasets
)

model_rf.fit(X_train_scaled, y_train)
print("Model trained!")

# --- Option 2: RandomForest with SMOTE (if using imbalanced-learn) ---
# You can uncomment and use this block if you want to test SMOTE
# smote = SMOTE(random_state=42)
# X_train_resampled, y_train_resampled = smote.fit_resample(X_train_scaled, y_train)
# print(f"Training data after SMOTE: {X_train_resampled.shape}")
# print(f"Flood events after SMOTE: {y_train_resampled.sum()} ({y_train_resampled.sum()/len(y_train_resampled)*100:.2f}%)")
# model_rf_smote = RandomForestClassifier(n_estimators=100, random_state=42)
# model_rf_smote.fit(X_train_resampled, y_train_resampled)
# print("Model trained with SMOTE!")


# --- Option 3: Hyperparameter Tuning with GridSearchCV (Recommended for better performance) ---
# For a 2-year dataset, 5 splits for TimeSeriesSplit might be a bit tight, but still feasible.
# Each fold will train on ~1.5 years and test on a subsequent ~0.5 year.
print("\nPerforming Hyperparameter Tuning with GridSearchCV (using TimeSeriesSplit for CV)...")

# Define a more robust time-series cross-validator for GridSearchCV
tscv = TimeSeriesSplit(n_splits=3) # Reduced to 3 splits for shorter data range to ensure enough data per fold

# Define the parameter grid to search
param_grid = {
    'n_estimators': [50, 100, 150],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'class_weight': ['balanced']
}

grid_search = GridSearchCV(
    estimator=RandomForestClassifier(random_state=42),
    param_grid=param_grid,
    cv=tscv,
    scoring='recall',
    n_jobs=-1,
    verbose=1
)

grid_search.fit(X_train_scaled, y_train) # Fit only on the training portion

best_model = grid_search.best_estimator_
print(f"\nBest Hyperparameters found: {grid_search.best_params_}")
print(f"Best cross-validation score (Recall): {grid_search.best_score_:.4f}")

# Now, use the best_model for evaluation on the unseen X_test_scaled
print("\nUsing the best model found by GridSearchCV for final evaluation.")

# --- 5. Model Evaluation ---

print("\n--- 5. Model Evaluation on Test Set ---")

# Use the best model from GridSearchCV, or model_rf if you skipped tuning
final_model = best_model # or model_rf

y_pred = final_model.predict(X_test_scaled)
y_pred_proba = final_model.predict_proba(X_test_scaled)[:, 1] # Probability of flood (class 1)

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
print(cm)
# Visualize Confusion Matrix
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Predicted No Flood', 'Predicted Flood'],
            yticklabels=['Actual No Flood', 'Actual Flood'])
plt.title('Confusion Matrix')
plt.ylabel('Actual Label')
plt.xlabel('Predicted Label')
plt.show()

print(f"\nROC AUC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")

# Precision-Recall Curve (Very important for imbalanced classification)
# ROC AUC can be misleading on highly imbalanced datasets.
# PR AUC focuses on the positive class.
precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
pr_auc = auc(recall, precision)
print(f"Precision-Recall AUC: {pr_auc:.4f}")

plt.figure(figsize=(8, 6))
plt.plot(recall, precision, label=f'Precision-Recall curve (AUC = {pr_auc:.2f})')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve')
plt.legend(loc='lower left')
plt.grid(True)
plt.show()


# --- Feature Importance (for tree-based models) ---
if hasattr(final_model, 'feature_importances_'):
    importances = final_model.feature_importances_
    feature_names = X_train.columns
    sorted_indices = np.argsort(importances)[::-1]

    plt.figure(figsize=(10, 6))
    sns.barplot(x=importances[sorted_indices], y=feature_names[sorted_indices])
    plt.title("Feature Importances (from trained model)")
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.show()

    print("\nTop 5 Most Important Features:")
    for i in sorted_indices[:5]:
        print(f"- {feature_names[i]}: {importances[i]:.4f}")