#!/usr/bin/env python3
"""
Kubeflow Tracking SDK Example

This example demonstrates how to use the Kubeflow Tracking SDK, which provides
a unified interface to MLflow + Model Registry plugin for experiment tracking.

Requirements:
    pip install kubeflow[tracking]
    # Or install the Model Registry plugin separately:
    pip install modelregistry_plugin
"""

import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score

# Import Kubeflow tracking components
from kubeflow.tracking import (
    get_tracking_store,
    list_tracking_stores,
    set_tracking_store,
    Tracker,
    launch_ui,
    stop_ui
)


def setup_tracking_stores():
    """Set up different tracking store configurations."""
    print("🔧 Setting up tracking stores...")
    
    # Option 1: Register Model Registry store
    # This assumes you have a Model Registry instance running
    model_registry_uri = os.getenv('MODEL_REGISTRY_TRACKING_URI', 'modelregistry://localhost:8080')
    artifact_uri = os.getenv('MODEL_REGISTRY_ARTIFACT_URI', 'file://./artifacts')
    
    try:
        set_tracking_store(
            name='model-registry',
            tracking_uri=model_registry_uri,
            artifact_uri=artifact_uri,
            description='Kubeflow Model Registry for production'
        )
        print(f"✅ Registered Model Registry store: {model_registry_uri}")
    except Exception as e:
        print(f"⚠️  Could not connect to Model Registry: {e}")
    
    # Option 2: Register local MLflow store (fallback)
    set_tracking_store(
        name='local',
        tracking_uri='file://./mlruns',
        artifact_uri='file://./artifacts',
        description='Local MLflow store for development'
    )
    print("✅ Registered local MLflow store")
    
    # List all available stores
    stores = list_tracking_stores()
    print(f"\n📊 Available tracking stores:")
    for store in stores:
        print(f"  - {store.name}: {store.tracking_uri}")
        if store.description:
            print(f"    Description: {store.description}")
    
    return stores


def train_model_with_tracking():
    """Train a model with experiment tracking."""
    print("\n🚀 Starting model training with tracking...")
    
    # Create a tracker instance
    tracker = Tracker(experiment_name='sklearn-classification-demo')
    
    # Enable autologging for scikit-learn
    tracker.enable_autolog('sklearn')
    
    # Generate sample data
    X, y = make_classification(
        n_samples=1000,
        n_features=20,
        n_informative=10,
        n_redundant=10,
        n_clusters_per_class=1,
        random_state=42
    )
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Training parameters
    params = {
        'n_estimators': 100,
        'max_depth': 6,
        'min_samples_split': 2,
        'min_samples_leaf': 1,
        'random_state': 42
    }
    
    # Start tracking run
    with tracker.start_run(
        run_name='random-forest-experiment',
        description='Random Forest classification with Kubeflow tracking'
    ) as run:
        print(f"🔬 Started run: {run.info.run_id}")
        
        # Log parameters
        tracker.log_params(params)
        
        # Log dataset info
        tracker.log_param('dataset_size', len(X))
        tracker.log_param('n_features', X.shape[1])
        tracker.log_param('test_size', 0.2)
        
        # Train model
        model = RandomForestClassifier(**params)
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        
        # Log metrics
        tracker.log_metric('accuracy', accuracy)
        tracker.log_metric('precision', precision)
        tracker.log_metric('recall', recall)
        
        # Log additional metrics for each epoch simulation
        for epoch in range(10):
            # Simulate training progress
            train_acc = 0.5 + (accuracy - 0.5) * (epoch + 1) / 10
            tracker.log_metric('train_accuracy', train_acc, step=epoch)
        
        # Set tags
        tracker.set_tags({
            'algorithm': 'RandomForest',
            'dataset': 'synthetic',
            'framework': 'scikit-learn',
            'environment': 'kubeflow-sdk',
            'model_type': 'classification'
        })
        
        # Log model
        tracker.log_model(
            artifact_path='model',
            model=model,
            flavor_module='sklearn'
        )
        
        print(f"📈 Model performance:")
        print(f"  - Accuracy: {accuracy:.4f}")
        print(f"  - Precision: {precision:.4f}")
        print(f"  - Recall: {recall:.4f}")
        
    print("✅ Training completed and logged")
    return run


def demonstrate_tracking_features():
    """Demonstrate various tracking features."""
    print("\n🔍 Demonstrating tracking features...")
    
    tracker = Tracker()
    
    # Search experiments
    experiments = tracker.search_experiments()
    print(f"📋 Found {len(experiments)} experiments:")
    for exp in experiments[:5]:  # Show first 5
        print(f"  - {exp.name} (ID: {exp.experiment_id})")
    
    # Search runs
    if experiments:
        runs = tracker.search_runs(
            experiment_ids=[experiments[0].experiment_id],
            max_results=5
        )
        print(f"\n🏃 Found {len(runs)} runs in '{experiments[0].name}':")
        for run in runs.itertuples():
            print(f"  - Run {run.run_id[:8]}... Status: {run.status}")
    
    # Get current tracking URI
    uri = tracker.get_tracking_uri()
    print(f"\n📍 Current tracking URI: {uri}")


def launch_tracking_ui():
    """Launch the tracking UI for visualization."""
    print("\n🖥️  Launching tracking UI...")
    
    try:
        # Launch UI based on current tracking store
        url = launch_ui(
            ui_type='mlflow',
            port=5000,
            open_browser=False  # Set to True to open browser automatically
        )
        print(f"🌐 Tracking UI available at: {url}")
        print("   You can view your experiments and runs in the web interface")
        
        # Keep UI running for a bit
        print("   UI will run for 30 seconds for demonstration...")
        import time
        time.sleep(5)  # Reduced for demo
        
        # Stop UI
        stop_ui()
        print("🛑 Stopped tracking UI")
        
    except Exception as e:
        print(f"⚠️  Could not launch UI: {e}")
        print("   Make sure MLflow is installed: pip install mlflow")


def integration_with_trainer():
    """Demonstrate integration with Kubeflow Trainer."""
    print("\n⚙️  Integration with Kubeflow Trainer:")
    
    # Example of how this would integrate with Kubeflow Trainer
    print("""
    # This is how you would use tracking with Kubeflow Trainer:
    
    from kubeflow.trainer import Client
    from kubeflow.tracking import get_tracking_store
    
    def train_pytorch_with_kubeflow():
        import torch
        import torch.nn as nn
        from kubeflow.tracking import Tracker
        
        # Setup tracking
        tracker = Tracker()
        tracker.enable_autolog('pytorch')
        
        with tracker.start_run():
            # Your training code here
            model = nn.Linear(10, 1)
            tracker.log_param("learning_rate", 0.01)
            
            # Training loop
            for epoch in range(10):
                loss = train_step(model)
                tracker.log_metric("loss", loss, step=epoch)
            
            # Log model
            tracker.log_model("model", model, flavor_module='pytorch')
    
    # Use with Kubeflow Trainer
    client = Client()
    client.train(
        func=train_pytorch_with_kubeflow,
        tracking_store=get_tracking_store("model-registry"),
        artifact_store="s3://my-bucket/artifacts"
    )
    """)


def main():
    """Main example execution."""
    print("🎯 Kubeflow Tracking SDK Example")
    print("=" * 50)
    
    # Setup tracking stores
    stores = setup_tracking_stores()
    
    # Train model with tracking
    run = train_model_with_tracking()
    
    # Demonstrate tracking features
    demonstrate_tracking_features()
    
    # Launch UI (optional)
    # Uncomment to launch UI
    # launch_tracking_ui()
    
    # Show integration example
    integration_with_trainer()
    
    print("\n🎉 Example completed!")
    print("\nNext steps:")
    print("1. Install Model Registry plugin: pip install modelregistry_plugin")
    print("2. Set up Model Registry server")
    print("3. Configure environment variables:")
    print("   export MODEL_REGISTRY_TRACKING_URI='modelregistry://your-host:8080'")
    print("   export MODEL_REGISTRY_ARTIFACT_URI='s3://your-bucket/artifacts'")
    print("4. Use the Kubeflow Tracking SDK in your ML projects!")


if __name__ == "__main__":
    main() 