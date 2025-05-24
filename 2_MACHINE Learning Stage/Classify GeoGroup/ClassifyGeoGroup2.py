import numpy as np
import pandas as pd
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import matplotlib.pyplot as plt

def load_mixed_samples():
    """Load the previously generated mixed samples"""
    try:
        # Read the Excel file
        df = pd.read_excel('mixed_samples.xlsx')
        
        # Extract components
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        data = df[numeric_cols].values
        labels = df['Ancestry_Label'].values
        sample_names = df['Sample_Name'].values
        original_ids = df['Original_HGDP_IDs'].values
        
        return data, labels, sample_names, original_ids
    except FileNotFoundError:
        print("Error: mixed_samples.xlsx not found. Please run 4_generate_mixed_samples.py first.")
        return None, None, None, None

def train_model(X, y, sample_names, original_ids):
    """Train a new LDA model with cross-validation"""
    # Split the data with stratification
    splits = train_test_split(X, y, sample_names, original_ids, test_size=0.2, stratify=y, random_state=42)
    X_train, X_test, y_train, y_test, names_test, ids_test = splits[0], splits[1], splits[2], splits[3], splits[5], splits[7]
    
    # Create a detailed tracking file for test samples
    test_samples_info = pd.DataFrame({
        'Sample_Name': names_test,
        'Original_HGDP_IDs': ids_test,
        'True_Ancestry': y_test,
    })
    test_samples_info.to_excel('test_samples_tracking.xlsx', index=False)
    print("\nTest samples tracking information saved to 'test_samples_tracking.xlsx'")
    
    # Print class distribution
    print("\nClass Distribution:")
    print("=" * 50)
    print("Training set:")
    print(pd.Series(y_train).value_counts().sort_index())
    print("\nTest set:")
    print(pd.Series(y_test).value_counts().sort_index())
    
    # Train the model
    lda = LinearDiscriminantAnalysis()
    lda.fit(X_train, y_train)
    
    # Perform cross-validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(lda, X, y, cv=cv)
    
    # Make classifications
    y_class = lda.predict(X_test)
    
    return lda, X_test, y_test, y_class, cv_scores, names_test, ids_test

def plot_confusion_matrix(cm, labels):
    """Plot the confusion matrix"""
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=labels,
                yticklabels=labels)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Classified Label')
    plt.tight_layout()
    plt.savefig('confusion_matrix.tif', dpi=600, format='tiff')
    plt.close()

def plot_classification_probabilities(lda, X_test, y_test, labels, sample_names, original_ids):
    """Plot and analyze classification probabilities"""
    # Get classification probabilities
    probabilities = lda.predict_proba(X_test)
    
    # Create figure for probability matrix
    plt.figure(figsize=(15, 12))
    
    # Create matrix for annotations
    prob_matrix = np.zeros((len(labels), len(labels)))
    annotations = np.empty((len(labels), len(labels)), dtype=object)
    
    for i, true_label in enumerate(labels):
        for j, class_label in enumerate(labels):
            mask = (y_test == true_label) & (lda.predict(X_test) == class_label)
            if np.any(mask):
                # Get probabilities for these samples
                sample_probs = probabilities[mask]
                
                # Get top 1 probability and label
                top1_prob = np.mean(np.max(sample_probs, axis=1))
                prob_matrix[i, j] = top1_prob
                
                # Only get top 2 if top 1 is not 1.0
                if top1_prob < 1.0:
                    # Get top 2 probability and label
                    sorted_indices = np.argsort(sample_probs, axis=1)
                    top2_indices = sorted_indices[:, -2]  # Indices of second highest probabilities
                    top2_probs = np.array([sample_probs[k, top2_indices[k]] for k in range(len(sample_probs))])
                    top2_prob = np.mean(top2_probs)
                    annotations[i, j] = f"{top1_prob:.2f}\n{top2_prob:.2f}"
                else:
                    annotations[i, j] = f"{top1_prob:.2f}"
            else:
                prob_matrix[i, j] = 0
                annotations[i, j] = "0.00"
    
    # Plot heatmap with annotations
    sns.heatmap(prob_matrix, annot=annotations, fmt='', cmap='Blues',
                xticklabels=labels, yticklabels=labels)
    plt.title('Classification Probabilities\n(Top 1 and Top 2 Probabilities)')
    plt.xlabel('Classified Label')
    plt.ylabel('True Label')
    plt.tight_layout()
    plt.savefig('classification_probabilities.tif', dpi=600, format='tiff')
    plt.close()
    
    # Print detailed probability information for each sample
    print("\nDetailed Probability Information for Each Sample:")
    print("=" * 80)
    
    # Create a list to store all sample information
    sample_info = []
    
    for i in range(len(X_test)):
        probs = probabilities[i]
        sorted_indices = np.argsort(probs)[::-1]
        top1_label = labels[sorted_indices[0]]
        top1_prob = probs[sorted_indices[0]]
        top2_label = labels[sorted_indices[1]]
        top2_prob = probs[sorted_indices[1]]
        
        # Store sample information
        sample_info.append({
            'Sample_Name': sample_names[i],
            'Original_HGDP_IDs': original_ids[i],
            'True_Ancestry': y_test[i],
            'Classified_Ancestry': lda.predict(X_test)[i],
            'Top1_Classification': top1_label,
            'Top1_Probability': top1_prob,
            'Top2_Classification': top2_label,
            'Top2_Probability': top2_prob
        })
        
        print(f"Sample {sample_names[i]}:")
        print(f"Original HGDP IDs: {original_ids[i]}")
        print(f"True Ancestry: {y_test[i]}")
        print(f"Top 1 Classification: {top1_label} (Probability: {top1_prob:.4f})")
        print(f"Top 2 Classification: {top2_label} (Probability: {top2_prob:.4f})")
        print("-" * 80)
    
    # Save sample information to Excel
    pd.DataFrame(sample_info).to_excel('test_samples_classifications.xlsx', index=False)
    print("\nTest samples classifications saved to 'test_samples_classifications.xlsx'")

def print_detailed_classifications(names_test, ids_test, y_test, y_class, limit=20):
    """Print detailed classifications for the first n samples"""
    print(f"\nDetailed Classifications (first {limit} samples):")
    print("=" * 50)
    for name, orig_id, true, class_label in zip(names_test[:limit], ids_test[:limit], y_test[:limit], y_class[:limit]):
        print(f"Sample {name}:")
        print(f"Original HGDP IDs: {orig_id}")
        print(f"True: {true:<30} Classified: {class_label}")
        print("-" * 50)

def main():
    # Load the mixed samples
    X, y, sample_names, original_ids = load_mixed_samples()
    if X is None:
        return
        
    # Train model and get results
    lda, X_test, y_test, y_class, cv_scores, names_test, ids_test = train_model(
        X, y, sample_names, original_ids
    )
    
    # Print model performance
    print("\nModel Training Results:")
    print(f"Training Accuracy: {lda.score(X, y):.2%}")
    print(f"Testing Accuracy: {lda.score(X_test, y_test):.2%}")
    print(f"Cross-validation scores: {cv_scores}")
    print(f"Mean CV accuracy: {cv_scores.mean():.2%} (+/- {cv_scores.std() * 2:.2%})")
    
    # Plot confusion matrix
    cm = confusion_matrix(y_test, y_class)
    plot_confusion_matrix(cm, np.unique(y))
    
    # Plot and analyze classification probabilities
    plot_classification_probabilities(lda, X_test, y_test, np.unique(y), names_test, ids_test)
    
    # Print classification report
    print("\nClassification Report:")
    print(classification_report(y_test, y_class))
    
    # Print detailed classifications
    print_detailed_classifications(names_test, ids_test, y_test, y_class)

if __name__ == "__main__":
    main() 