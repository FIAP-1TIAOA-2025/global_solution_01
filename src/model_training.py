import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
import joblib
import os

def train_model(df_processed: pd.DataFrame):
    """
    Prepares the data, trains, and optimizes a Machine Learning model for flood prediction.

    This function performs:
    1. Time-series splitting of the data into training and testing sets.
    2. Feature scaling using StandardScaler.
    3. Hyperparameter tuning of a RandomForestClassifier using GridSearchCV
       with TimeSeriesSplit for robust cross-validation.
    4. Saves the best trained model and the scaler.

    Args:
        df_processed (pd.DataFrame): DataFrame containing the engineered features
                                     and the 'flood_event' target variable.
                                     Expected to have a DatetimeIndex.

    Returns:
        tuple: A tuple containing:
               - best_model (sklearn.ensemble.RandomForestClassifier): The best trained and tuned model.
               - scaler (sklearn.preprocessing.StandardScaler): The fitted StandardScaler object.
               - X_test_scaled (pd.DataFrame): The scaled features of the test set.
               - y_test (pd.Series): The target variable of the test set.
    """
    print("\n--- Starting Model Training ---")

    # Separate features (X) and target (y)
    X = df_processed.drop('flood_event', axis=1)
    y = df_processed['flood_event']

    # --- 1. Time-Series Data Splitting ---
    # Given data from 2023-04-30 to 2025-04-30 (2 years of data).
    # We'll use approximately the first 1.5 years for training and the last 0.5 year for testing.
    # This simulates predicting on unseen, future data.
    split_date = pd.to_datetime('2024-10-30') # Cut-off date for train/test split

    X_train = X[X.index < split_date]
    y_train = y[y.index < split_date]

    X_test = X[X.index >= split_date]
    y_test = y[y.index >= split_date]

    print(f"Data split into training and testing sets based on {split_date.strftime('%Y-%m-%d')}.")
    print(f"Training data range: {X_train.index.min().strftime('%Y-%m-%d')} to {X_train.index.max().strftime('%Y-%m-%d')}")
    print(f"Testing data range: {X_test.index.min().strftime('%Y-%m-%d')} to {X_test.index.max().strftime('%Y-%m-%d')}")
    print(f"Training data shape: {X_train.shape}, Target shape: {y_train.shape}")
    print(f"Testing data shape: {X_test.shape}, Target shape: {y_test.shape}")

    # Check for class imbalance in training set (crucial for flood prediction)
    flood_events_train_percentage = (y_train.sum() / len(y_train)) * 100 if len(y_train) > 0 else 0
    flood_events_test_percentage = (y_test.sum() / len(y_test)) * 100 if len(y_test) > 0 else 0
    print(f"Flood events in training set: {y_train.sum()} ({flood_events_train_percentage:.2f}%)")
    print(f"Flood events in testing set: {y_test.sum()} ({flood_events_test_percentage:.2f}%)")

    # --- 2. Feature Scaling ---
    # Initialize StandardScaler. It standardizes features by removing the mean and scaling to unit variance.
    scaler = StandardScaler()

    # Fit the scaler ONLY on the training data to avoid data leakage from the test set.
    X_train_scaled = scaler.fit_transform(X_train)
    # Transform both training and test data using the fitted scaler.
    X_test_scaled = scaler.transform(X_test)

    # Convert scaled arrays back to DataFrames, preserving column names and index.
    X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns, index=X_train.index)
    X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns, index=X_test.index)
    print("Features successfully scaled using StandardScaler.")

    # --- 3. Model Selection and Hyperparameter Tuning (Random Forest Classifier) ---
    # RandomForest is a robust choice for tabular data and handles non-linearity well.
    # We use GridSearchCV for exhaustive search over specified parameter values.
    # TimeSeriesSplit is crucial for cross-validation on time-series data.

    rf_model = RandomForestClassifier(random_state=42) # Initialize model with a random state for reproducibility

    # Define the parameter grid for GridSearchCV
    # These parameters can be adjusted based on computational resources and desired search depth.
    param_grid_rf = {
        'n_estimators': [50, 100, 150],       # Number of trees in the forest
        'max_depth': [None, 10, 20],          # Maximum depth of the tree (None means unlimited)
        'min_samples_split': [2, 5],          # Minimum number of samples required to split an internal node
        'min_samples_leaf': [1, 2],           # Minimum number of samples required to be at a leaf node
        'class_weight': ['balanced']          # Handles class imbalance by weighting samples inversely proportional to class frequency
    }

    # TimeSeriesSplit for cross-validation on time series data.
    # n_splits=3 means the data will be split into 3 folds, where each fold's test set
    # is a future segment relative to its training set.
    tscv = TimeSeriesSplit(n_splits=3)

    # Setup GridSearchCV
    grid_search_rf = GridSearchCV(
        estimator=rf_model,
        param_grid=param_grid_rf,
        cv=tscv,              # Use TimeSeriesSplit for cross-validation
        scoring='recall',     # Optimize for 'recall' to minimize False Negatives (missed floods)
        n_jobs=-1,            # Use all available CPU cores for faster computation
        verbose=1,            # Show progress during grid search
        error_score='raise'   # Raise errors explicitly for debugging
    )

    print("\nStarting GridSearchCV for RandomForestClassifier hyperparameter tuning...")
    # Fit GridSearchCV on the training data
    grid_search_rf.fit(X_train_scaled, y_train)

    best_rf_model = grid_search_rf.best_estimator_
    print(f"\nBest Hyperparameters found for RandomForest: {grid_search_rf.best_params_}")
    print(f"Best cross-validation score (Recall): {grid_search_rf.best_score_:.4f}")

    # --- 4. Saving the Trained Model and Scaler ---
    # It's crucial to save both the trained model and the fitted scaler.
    # The scaler is needed to preprocess new incoming data before making predictions.
    models_dir = 'models/trained_models'
    os.makedirs(models_dir, exist_ok=True) # Ensure the directory exists

    model_path = os.path.join(models_dir, 'RandomForestClassifier_v1.pkl')
    scaler_path = os.path.join(models_dir, 'StandardScaler_v1.pkl')

    joblib.dump(best_rf_model, model_path)
    joblib.dump(scaler, scaler_path)
    print(f"\nBest RandomForest model saved to: {model_path}")
    print(f"StandardScaler saved to: {scaler_path}")

    return best_rf_model, scaler, X_test_scaled, y_test

if __name__ == '__main__':
    # --- This block is for testing the 'train_model' function independently ---
    # To run this, ensure you have dummy data or actual processed data available.
    # This typically involves calling data_ingestion and data_preprocessing first.

    print("--- Running model_training.py as main for testing purposes ---")

    # Import necessary functions from other modules for testing
    from src.data_ingestion import load_raw_data
    from src.data_preprocessing import clean_and_engineer_features

    # Load and preprocess dummy data for testing
    print("Loading raw dummy data for testing...")
    raw_data_for_test = load_raw_data()
    print("Cleaning and engineering features for testing...")
    processed_data_for_test = clean_and_engineer_features(raw_data_for_test)

    # Ensure the processed data has enough rows after dropping NaNs for lags
    # and has a 'flood_event' column.
    if 'flood_event' not in processed_data_for_test.columns:
        print("Error: 'flood_event' column not found in processed data. Cannot proceed with training test.")
    elif processed_data_for_test.empty or processed_data_for_test.shape[0] < 100: # Arbitrary minimum rows
        print("Error: Processed data is too small or empty after engineering. Cannot proceed with training test.")
    else:
        # Call the main training function
        trained_model, feature_scaler, test_X, test_y = train_model(processed_data_for_test)

        print("\n--- Model training function test complete ---")
        print(f"Type of trained model: {type(trained_model)}")
        print(f"Shape of test features (scaled): {test_X.shape}")
        print(f"Shape of test target: {test_y.shape}")