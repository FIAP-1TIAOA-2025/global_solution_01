# src/model_evaluation.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    precision_recall_curve,
    auc,
    RocCurveDisplay, # For plotting ROC curve
    PrecisionRecallDisplay # For plotting PR curve
)
import os

def evaluate_model(model, X_test: pd.DataFrame, y_test: pd.Series, feature_names: list):
    """
    Evaluates the performance of the trained Machine Learning model on the test set.

    This function calculates and displays:
    1. Classification Report (Precision, Recall, F1-score, Support for each class).
    2. Confusion Matrix (with visualization).
    3. ROC AUC Score and ROC Curve.
    4. Precision-Recall AUC and Precision-Recall Curve (crucial for imbalanced datasets).
    5. Feature Importances (for tree-based models like RandomForest, with visualization).
    6. Saves key performance metrics to a CSV file.

    Args:
        model: The trained Machine Learning model (e.g., RandomForestClassifier).
        X_test (pd.DataFrame): Features of the test set, ready for prediction (e.g., scaled).
        y_test (pd.Series): True target labels of the test set.
        feature_names (list): A list of feature names, used for displaying feature importances.
    """
    print("\n--- Starting Model Evaluation ---")

    # Generate predictions and probabilities for the test set
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1] # Probability of the positive class (flood)

    # Define directory for saving figures
    reports_figures_dir = 'reports/figures'
    os.makedirs(reports_figures_dir, exist_ok=True) # Ensure the directory exists

    # --- 1. Classification Report ---
    print("\n--- Classification Report ---")
    # The classification report provides precision, recall, f1-score, and support for each class.
    # For flood prediction, 'recall' for the positive class (flood) is often prioritized.
    print(classification_report(y_test, y_pred, target_names=['No Flood', 'Flood']))

    # --- 2. Confusion Matrix ---
    print("\n--- Confusion Matrix ---")
    cm = confusion_matrix(y_test, y_pred)
    print(cm) # Raw confusion matrix array

    # Visualize the Confusion Matrix for better understanding
    plt.figure(figsize=(7, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
                xticklabels=['Predicted No Flood', 'Predicted Flood'],
                yticklabels=['Actual No Flood', 'Actual Flood'])
    plt.title('Confusion Matrix for Flood Prediction', fontsize=16)
    plt.ylabel('Actual Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(reports_figures_dir, 'confusion_matrix.png'))
    plt.show()
    print(f"Confusion Matrix plot saved to: {os.path.join(reports_figures_dir, 'confusion_matrix.png')}")

    # --- 3. ROC AUC Score and ROC Curve ---
    # ROC AUC measures the model's ability to distinguish between classes.
    # It's less sensitive to class imbalance than accuracy but can still be misleading
    # for very skewed datasets.
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    print(f"\nROC AUC Score: {roc_auc:.4f}")

    # Plot the ROC Curve
    fig_roc, ax_roc = plt.subplots(figsize=(8, 7))
    RocCurveDisplay.from_estimator(model, X_test, y_test, name='Model ROC Curve', ax=ax_roc)
    ax_roc.plot([0, 1], [0, 1], linestyle='--', lw=2, color='r', label='Chance', alpha=.8) # Plot random guess line
    ax_roc.set_title('Receiver Operating Characteristic (ROC) Curve', fontsize=16)
    ax_roc.set_xlabel('False Positive Rate', fontsize=12)
    ax_roc.set_ylabel('True Positive Rate', fontsize=12)
    ax_roc.legend(loc='lower right')
    ax_roc.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(reports_figures_dir, 'roc_curve.png'))
    plt.show()
    print(f"ROC Curve plot saved to: {os.path.join(reports_figures_dir, 'roc_curve.png')}")

    # --- 4. Precision-Recall AUC and Precision-Recall Curve ---
    # The Precision-Recall curve is **crucial for imbalanced classification problems**.
    # It focuses on the performance of the positive class (floods).
    # A high PR AUC indicates good performance for the minority class.
    precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
    pr_auc = auc(recall, precision)
    print(f"\nPrecision-Recall AUC: {pr_auc:.4f}")

    # Plot the Precision-Recall Curve
    fig_pr, ax_pr = plt.subplots(figsize=(8, 7))
    PrecisionRecallDisplay.from_estimator(model, X_test, y_test, name='Model PR Curve', ax=ax_pr)
    ax_pr.set_title('Precision-Recall Curve', fontsize=16)
    ax_pr.set_xlabel('Recall (True Positive Rate)', fontsize=12)
    ax_pr.set_ylabel('Precision (Positive Predictive Value)', fontsize=12)
    ax_pr.legend(loc='lower left')
    ax_pr.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(reports_figures_dir, 'precision_recall_curve.png'))
    plt.show()
    print(f"Precision-Recall Curve plot saved to: {os.path.join(reports_figures_dir, 'precision_recall_curve.png')}")

    # --- 5. Feature Importances ---
    # For tree-based models, feature importance helps understand which features contributed most to predictions.
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        # Sort features by importance in descending order
        sorted_indices = np.argsort(importances)[::-1]
        sorted_features = [feature_names[i] for i in sorted_indices]
        sorted_importances = importances[sorted_indices]

        # Plot feature importances
        plt.figure(figsize=(10, 8))
        sns.barplot(x=sorted_importances, y=sorted_features, palette='viridis')
        plt.title("Feature Importances", fontsize=16)
        plt.xlabel("Relative Importance", fontsize=12)
        plt.ylabel("Feature", fontsize=12)
        plt.tight_layout()
        plt.savefig(os.path.join(reports_figures_dir, 'feature_importances.png'))
        plt.show()
        print(f"Feature Importances plot saved to: {os.path.join(reports_figures_dir, 'feature_importances.png')}")

        print("\nTop 10 Most Important Features:")
        for i in range(min(10, len(sorted_features))): # Show top 10 or all if less than 10
            print(f"- {sorted_features[i]}: {sorted_importances[i]:.4f}")
    else:
        print("\nFeature importances are not available for this model type.")

    # --- 6. Save Key Performance Metrics to CSV ---
    # Extract common metrics to save for easy tracking across experiments.
    accuracy = (cm[0,0] + cm[1,1]) / np.sum(cm) if np.sum(cm) > 0 else 0
    precision_flood = cm[1,1] / (cm[1,1] + cm[0,1]) if (cm[1,1] + cm[0,1]) > 0 else 0 # Precision for class 1 (Flood)
    recall_flood = cm[1,1] / (cm[1,1] + cm[1,0]) if (cm[1,1] + cm[1,0]) > 0 else 0     # Recall for class 1 (Flood)
    f1_flood = 2 * (precision_flood * recall_flood) / (precision_flood + recall_flood) if (precision_flood + recall_flood) > 0 else 0 # F1-score for class 1

    metrics_data = {
        'metric': ['Accuracy', 'Precision_Flood', 'Recall_Flood', 'F1_Flood', 'ROC_AUC', 'PR_AUC'],
        'value': [accuracy, precision_flood, recall_flood, f1_flood, roc_auc, pr_auc]
    }
    df_metrics = pd.DataFrame(metrics_data)

    metrics_file_path = 'reports/model_performance_metrics.csv'
    df_metrics.to_csv(metrics_file_path, index=False)
    print(f"\nKey performance metrics saved to: {metrics_file_path}")

    print("\n--- Model Evaluation Complete ---")


if __name__ == '__main__':
    # --- This block is for testing the 'evaluate_model' function independently ---
    # To run this, ensure you have a trained model, scaler, and processed data.
    # This typically involves running data_ingestion, data_preprocessing, and model_training first.

    print("--- Running model_evaluation.py as main for testing purposes ---")

    # Import necessary modules and functions
    from src.data_ingestion import load_raw_data
    from src.data_preprocessing import clean_and_engineer_features
    from src.model_training import train_model
    import joblib

    try:
        # Simulate the full pipeline up to getting the trained model and test data
        print("Simulating data loading, preprocessing, and model training for evaluation test...")
        raw_data_for_test = load_raw_data()
        processed_data_for_test = clean_and_engineer_features(raw_data_for_test)

        # Check if processed data is valid before training
        if 'flood_event' not in processed_data_for_test.columns or processed_data_for_test.empty or processed_data_for_test.shape[0] < 100:
            print("Skipping evaluation test: Processed data is invalid or too small.")
        else:
            # train_model also returns the test set (X_test_scaled, y_test)
            trained_model, feature_scaler, test_X_scaled, test_y = train_model(processed_data_for_test)

            # Get feature names from the scaled test set
            feature_names_for_eval = test_X_scaled.columns.tolist()

            # Call the evaluation function
            evaluate_model(trained_model, test_X_scaled, test_y, feature_names_for_eval)
            print("\n--- Model evaluation function test complete ---")

    except Exception as e:
        print(f"An error occurred during evaluation test: {e}")
        print("Please ensure all previous pipeline steps (data loading, preprocessing, training) run successfully.")