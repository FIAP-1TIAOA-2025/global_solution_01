# Example run_pipeline.py
import pandas as pd
from src.data_ingestion import load_raw_data
from src.data_preprocessing import clean_and_engineer_features
from src.model_training import train_model
from src.model_evaluation import evaluate_model
import joblib

def main():
    # 1. Load Data
    print("Loading raw data...")
    # Assume load_raw_data returns a dictionary of dataframes or merges them
    raw_df = load_raw_data()
    print("Raw data loaded.")

    # 2. Preprocess and Feature Engineer
    print("Preprocessing and engineering features...")
    processed_df = clean_and_engineer_features(raw_df)
    print("Features engineered.")

    # 3. Train Model
    print("Training model...")
    best_model, scaler, X_test_scaled, y_test = train_model(processed_df) # train_model returns the trained model, scaler, and test sets
    print("Model trained and evaluated on cross-validation.")

    # 4. Evaluate Model on Test Set
    print("Evaluating model on unseen test set...")
    evaluate_model(best_model, X_test_scaled, y_test, X_test_scaled.columns) # Pass feature names for importance plot
    print("Model evaluation complete.")

    # 5. Save Model and Scaler
    print("Saving model and scaler...")
    joblib.dump(best_model, 'models/trained_models/flood_prediction_model_v1.pkl')
    joblib.dump(scaler, 'models/trained_models/feature_scaler_v1.pkl')
    print("Model and scaler saved.")

if __name__ == "__main__":
    main()