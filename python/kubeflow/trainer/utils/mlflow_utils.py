import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

try:
    import mlflow
    import mlflow.pytorch
    import mlflow.sklearn
    import mlflow.tensorflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    mlflow = None


def is_mlflow_available() -> bool:
    return MLFLOW_AVAILABLE


def setup_mlflow_tracking(
    experiment_name: Optional[str] = None,
    tracking_uri: Optional[str] = None,
    run_name: Optional[str] = None,
    tags: Optional[Dict[str, Any]] = None,
    auto_log: bool = True,
    framework: Optional[str] = None,
) -> Optional[Any]:
    if not MLFLOW_AVAILABLE:
        logger.warning(
            "MLflow is not available, install with: pip install kubeflow[mlflow]"
        )
        return None
    
    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        elif "MLFLOW_TRACKING_URI" not in os.environ:
            mlflow.set_tracking_uri("file:./mlruns")

        if experiment_name:
            mlflow.set_experiment(experiment_name)

        run = mlflow.start_run(run_name=run_name, tags=tags)

        if auto_log and framework:
            enable_auto_logging(framework)
        
        logger.info(f"MLflow tracking started. Run ID: {run.info.run_id}")
        return run
        
    except Exception as e:
        logger.warning(f"Failed to setup MLflow tracking: {e}")
        return None


def enable_auto_logging(framework: str):
    if not MLFLOW_AVAILABLE:
        return
    
    try:
        if framework.lower() == 'pytorch' or framework.lower() == 'torch':
            mlflow.pytorch.autolog()
            logger.info("MLflow PyTorch auto-logging enabled")
        elif framework.lower() == 'tensorflow' or framework.lower() == 'tf':
            mlflow.tensorflow.autolog()
            logger.info("MLflow TensorFlow auto-logging enabled")
        elif framework.lower() == 'sklearn':
            mlflow.sklearn.autolog()
            logger.info("MLflow scikit-learn auto-logging enabled")
        else:
            mlflow.autolog()
            logger.info(f"MLflow generic auto-logging enabled for {framework}")
    except Exception as e:
        logger.warning(f"Failed to enable auto-logging for {framework}: {e}")


def log_kubeflow_context(
    job_name: str,
    runtime_name: str,
    framework: str,
    num_nodes: Optional[int] = None,
    resources_per_node: Optional[Dict] = None,
):
    if not MLFLOW_AVAILABLE or not mlflow.active_run():
        return
    
    try:
        mlflow.log_param("kubeflow.job_name", job_name)
        mlflow.log_param("kubeflow.runtime", runtime_name)
        mlflow.log_param("kubeflow.framework", framework)
        
        if num_nodes:
            mlflow.log_param("kubeflow.num_nodes", num_nodes)
        
        if resources_per_node:
            for key, value in resources_per_node.items():
                mlflow.log_param(f"kubeflow.resources.{key}", value)

        mlflow.set_tag("kubeflow.source", "kubeflow-trainer")
        mlflow.set_tag("kubeflow.framework", framework)
        
        logger.info("Kubeflow context logged to MLflow")
        
    except Exception as e:
        logger.warning(f"Failed to log Kubeflow context: {e}")


def finalize_mlflow():
    if not MLFLOW_AVAILABLE:
        return
    
    try:
        if mlflow.active_run():
            mlflow.end_run()
            logger.info("MLflow run ended successfully")
    except Exception as e:
        logger.warning(f"Failed to end MLflow run: {e}")


class MLflowContextManager:
    
    def __init__(
        self,
        experiment_name: Optional[str] = None,
        tracking_uri: Optional[str] = None,
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        auto_log: bool = True,
        framework: Optional[str] = None,
        job_name: Optional[str] = None,
        runtime_name: Optional[str] = None,
        num_nodes: Optional[int] = None,
        resources_per_node: Optional[Dict] = None,
    ):
        self.experiment_name = experiment_name
        self.tracking_uri = tracking_uri
        self.run_name = run_name
        self.tags = tags or {}
        self.auto_log = auto_log
        self.framework = framework
        self.job_name = job_name
        self.runtime_name = runtime_name
        self.num_nodes = num_nodes
        self.resources_per_node = resources_per_node
        self.run = None
    
    def __enter__(self):
        self.run = setup_mlflow_tracking(
            experiment_name=self.experiment_name,
            tracking_uri=self.tracking_uri,
            run_name=self.run_name,
            tags=self.tags,
            auto_log=self.auto_log,
            framework=self.framework,
        )

        if self.run and self.job_name and self.runtime_name and self.framework:
            log_kubeflow_context(
                job_name=self.job_name,
                runtime_name=self.runtime_name,
                framework=self.framework,
                num_nodes=self.num_nodes,
                resources_per_node=self.resources_per_node,
            )
        
        return self.run
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        finalize_mlflow()


def create_mlflow_wrapper(training_func):
    def wrapper(*args, **kwargs):
        enable_mlflow = os.getenv("KUBEFLOW_ENABLE_MLFLOW", "false").lower() == "true"
        
        if enable_mlflow and MLFLOW_AVAILABLE:
            experiment_name = os.getenv("KUBEFLOW_MLFLOW_EXPERIMENT", "kubeflow-training")
            tracking_uri = os.getenv("KUBEFLOW_MLFLOW_TRACKING_URI")
            
            with MLflowContextManager(
                experiment_name=experiment_name,
                tracking_uri=tracking_uri,
                framework="auto-detect",
                auto_log=True,
            ):
                return training_func(*args, **kwargs)
        else:
            return training_func(*args, **kwargs)
    
    return wrapper 