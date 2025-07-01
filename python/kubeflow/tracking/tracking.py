from typing import Optional, Dict, Any

import mlflow

def create_experiment(
    name: str,
    artifact_location: Optional[str] = None,
    tags: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create an experiment.

    Args:
        name: The experiment name, must be a non-empty unique string.
        artifact_location: The location to store run artifacts. If not provided, the server picks
            an appropriate default.
        tags: An optional dictionary of string keys and values to set as tags on the experiment.

    Returns:
        String ID of the created experiment.

     .. code-block:: python
        :test:
        :caption: Example

        import mlflow
        from pathlib import Path

        # Create an experiment name, which must be unique and case sensitive
        experiment_id = mlflow.create_experiment(
            "Social NLP Experiments",
            artifact_location=Path.cwd().joinpath("mlruns").as_uri(),
            tags={"version": "v1", "priority": "P1"},
        )
        experiment = mlflow.get_experiment(experiment_id)
        print(f"Name: {experiment.name}")
        print(f"Experiment_id: {experiment.experiment_id}")
        print(f"Artifact Location: {experiment.artifact_location}")
        print(f"Tags: {experiment.tags}")
        print(f"Lifecycle_stage: {experiment.lifecycle_stage}")
        print(f"Creation timestamp: {experiment.creation_time}")

    .. code-block:: text
        :caption: Output

        Name: Social NLP Experiments
        Experiment_id: 1
        Artifact Location: file:///.../mlruns
        Tags: {'version': 'v1', 'priority': 'P1'}
        Lifecycle_stage: active
        Creation timestamp: 1662004217511
        """
    return mlflow.create_experiment(name, artifact_location=artifact_location, tags=tags)