from typing import TYPE_CHECKING, Any, Dict, Optional, Union

import mlflow
from mlflow.data.dataset import Dataset
from mlflow.entities import Experiment, Run, RunStatus, ViewType
from mlflow.utils.async_logging.run_operations import RunOperations

if TYPE_CHECKING:
    import pandas

SEARCH_MAX_RESULTS_PANDAS = 100000


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
    return mlflow.create_experiment(
        name, artifact_location=artifact_location, tags=tags
    )


def set_experiment(
    experiment_name: Optional[str] = None, experiment_id: Optional[str] = None
) -> Experiment:
    """
    Set the given experiment as the active experiment. The experiment must either be specified by
    name via `experiment_name` or by ID via `experiment_id`. The experiment name and ID cannot
    both be specified.

    .. note::
        If the experiment being set by name does not exist, a new experiment will be
        created with the given name. After the experiment has been created, it will be set
        as the active experiment. On certain platforms, such as Databricks, the experiment name
        must be an absolute path, e.g. ``"/Users/<username>/my-experiment"``.

    Args:
        experiment_name: Case sensitive name of the experiment to be activated.
        experiment_id: ID of the experiment to be activated. If an experiment with this ID
            does not exist, an exception is thrown.

    Returns:
        An instance of :py:class:`mlflow.entities.Experiment` representing the new active
        experiment.

    .. code-block:: python
        :test:
        :caption: Example

        import mlflow

        # Set an experiment name, which must be unique and case-sensitive.
        experiment = mlflow.set_experiment("Social NLP Experiments")
        # Get Experiment Details
        print(f"Experiment_id: {experiment.experiment_id}")
        print(f"Artifact Location: {experiment.artifact_location}")
        print(f"Tags: {experiment.tags}")
        print(f"Lifecycle_stage: {experiment.lifecycle_stage}")

    .. code-block:: text
        :caption: Output

        Experiment_id: 1
        Artifact Location: file:///.../mlruns/1
        Tags: {}
        Lifecycle_stage: active
    """
    return mlflow.set_experiment(experiment_name, experiment_id=experiment_id)


def get_experiment(experiment_id: str) -> Experiment:
    """Retrieve an experiment by experiment_id from the backend store

    Args:
        experiment_id: The string-ified experiment ID returned from ``create_experiment``.

    Returns:
        :py:class:`mlflow.entities.Experiment`

    .. code-block:: python
        :test:
        :caption: Example

        import mlflow

        experiment = mlflow.get_experiment("0")
        print(f"Name: {experiment.name}")
        print(f"Artifact Location: {experiment.artifact_location}")
        print(f"Tags: {experiment.tags}")
        print(f"Lifecycle_stage: {experiment.lifecycle_stage}")
        print(f"Creation timestamp: {experiment.creation_time}")

    .. code-block:: text
        :caption: Output

        Name: Default
        Artifact Location: file:///.../mlruns/0
        Tags: {}
        Lifecycle_stage: active
        Creation timestamp: 1662004217511
    """
    return mlflow.get_experiment(experiment_id)


def get_experiment_by_name(name: str) -> Optional[Experiment]:
    """
    Retrieve an experiment by experiment name from the backend store

    Args:
        name: The case sensitive experiment name.

    Returns:
        An instance of :py:class:`mlflow.entities.Experiment`
        if an experiment with the specified name exists, otherwise None.

    .. code-block:: python
        :test:
        :caption: Example

        import mlflow

        # Case sensitive name
        experiment = mlflow.get_experiment_by_name("Default")
        print(f"Experiment_id: {experiment.experiment_id}")
        print(f"Artifact Location: {experiment.artifact_location}")
        print(f"Tags: {experiment.tags}")
        print(f"Lifecycle_stage: {experiment.lifecycle_stage}")
        print(f"Creation timestamp: {experiment.creation_time}")

    .. code-block:: text
        :caption: Output

        Experiment_id: 0
        Artifact Location: file:///.../mlruns/0
        Tags: {}
        Lifecycle_stage: active
        Creation timestamp: 1662004217511
    """
    return mlflow.get_experiment_by_name(name)


def start_run(
    run_id: Optional[str] = None,
    experiment_id: Optional[str] = None,
    run_name: Optional[str] = None,
    nested: bool = False,
    parent_run_id: Optional[str] = None,
    tags: Optional[dict[str, Any]] = None,
    description: Optional[str] = None,
    log_system_metrics: Optional[bool] = None,
) -> mlflow.ActiveRun:
    """
    Start a new MLflow run, setting it as the active run under which metrics and parameters
    will be logged. The return value can be used as a context manager within a ``with`` block;
    otherwise, you must call ``end_run()`` to terminate the current run.

    If you pass a ``run_id`` or the ``MLFLOW_RUN_ID`` environment variable is set,
    ``start_run`` attempts to resume a run with the specified run ID and
    other parameters are ignored. ``run_id`` takes precedence over ``MLFLOW_RUN_ID``.

    If resuming an existing run, the run status is set to ``RunStatus.RUNNING``.

    MLflow sets a variety of default tags on the run, as defined in
    `MLflow system tags <../../tracking/tracking-api.html#system_tags>`_.

    Args:
        run_id: If specified, get the run with the specified UUID and log parameters
            and metrics under that run. The run's end time is unset and its status
            is set to running, but the run's other attributes (``source_version``,
            ``source_type``, etc.) are not changed.
        experiment_id: ID of the experiment under which to create the current run (applicable
            only when ``run_id`` is not specified). If ``experiment_id`` argument
            is unspecified, will look for valid experiment in the following order:
            activated using ``set_experiment``, ``MLFLOW_EXPERIMENT_NAME``
            environment variable, ``MLFLOW_EXPERIMENT_ID`` environment variable,
            or the default experiment as defined by the tracking server.
        run_name: Name of new run, should be a non-empty string. Used only when ``run_id`` is
            unspecified. If a new run is created and ``run_name`` is not specified,
            a random name will be generated for the run.
        nested: Controls whether run is nested in parent run. ``True`` creates a nested run.
        parent_run_id: If specified, the current run will be nested under the the run with
            the specified UUID. The parent run must be in the ACTIVE state.
        tags: An optional dictionary of string keys and values to set as tags on the run.
            If a run is being resumed, these tags are set on the resumed run. If a new run is
            being created, these tags are set on the new run.
        description: An optional string that populates the description box of the run.
            If a run is being resumed, the description is set on the resumed run.
            If a new run is being created, the description is set on the new run.
        log_system_metrics: bool, defaults to None. If True, system metrics will be logged
            to MLflow, e.g., cpu/gpu utilization. If None, we will check environment variable
            `MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING` to determine whether to log system metrics.
            System metrics logging is an experimental feature in MLflow 2.8 and subject to change.

    Returns:
        :py:class:`mlflow.ActiveRun` object that acts as a context manager wrapping the
        run's state.

    .. code-block:: python
        :test:
        :caption: Example

        import mlflow

        # Create nested runs
        experiment_id = mlflow.create_experiment("experiment1")
        with mlflow.start_run(
            run_name="PARENT_RUN",
            experiment_id=experiment_id,
            tags={"version": "v1", "priority": "P1"},
            description="parent",
        ) as parent_run:
            mlflow.log_param("parent", "yes")
            with mlflow.start_run(
                run_name="CHILD_RUN",
                experiment_id=experiment_id,
                description="child",
                nested=True,
            ) as child_run:
                mlflow.log_param("child", "yes")
        print("parent run:")
        print(f"run_id: {parent_run.info.run_id}")
        print("description: {}".format(parent_run.data.tags.get("mlflow.note.content")))
        print("version tag value: {}".format(parent_run.data.tags.get("version")))
        print("priority tag value: {}".format(parent_run.data.tags.get("priority")))
        print("--")

        # Search all child runs with a parent id
        query = f"tags.mlflow.parentRunId = '{parent_run.info.run_id}'"
        results = mlflow.search_runs(experiment_ids=[experiment_id], filter_string=query)
        print("child runs:")
        print(results[["run_id", "params.child", "tags.mlflow.runName"]])

        # Create a nested run under the existing parent run
        with mlflow.start_run(
            run_name="NEW_CHILD_RUN",
            experiment_id=experiment_id,
            description="new child",
            parent_run_id=parent_run.info.run_id,
        ) as child_run:
            mlflow.log_param("new-child", "yes")

    .. code-block:: text
        :caption: Output

        parent run:
        run_id: 8979459433a24a52ab3be87a229a9cdf
        description: starting a parent for experiment 7
        version tag value: v1
        priority tag value: P1
        --
        child runs:
                                     run_id params.child tags.mlflow.runName
        0  7d175204675e40328e46d9a6a5a7ee6a          yes           CHILD_RUN
    """
    return mlflow.start_run(
        run_id=run_id,
        experiment_id=experiment_id,
        run_name=run_name,
        nested=nested,
        parent_run_id=parent_run_id,
        tags=tags,
        description=description,
        log_system_metrics=log_system_metrics,
    )


def end_run(status: str = RunStatus.to_string(RunStatus.FINISHED)) -> None:
    """
    End an active MLflow run (if there is one).

    .. code-block:: python
        :test:
        :caption: Example

        import mlflow

        # Start run and get status
        mlflow.start_run()
        run = mlflow.active_run()
        print(f"run_id: {run.info.run_id}; status: {run.info.status}")

        # End run and get status
        mlflow.end_run()
        run = mlflow.get_run(run.info.run_id)
        print(f"run_id: {run.info.run_id}; status: {run.info.status}")
        print("--")

        # Check for any active runs
        print(f"Active run: {mlflow.active_run()}")

    .. code-block:: text
        :caption: Output

        run_id: b47ee4563368419880b44ad8535f6371; status: RUNNING
        run_id: b47ee4563368419880b44ad8535f6371; status: FINISHED
        --
        Active run: None
    """
    return mlflow.end_run(status=status)


def active_run() -> Optional[mlflow.ActiveRun]:
    """
    Get the currently active ``Run``, or None if no such run exists.

    .. attention::
        This API is **thread-local** and returns only the active run in the current thread.
        If your application is multi-threaded and a run is started in a different thread,
        this API will not retrieve that run.

    **Note**: You cannot access currently-active run attributes
    (parameters, metrics, etc.) through the run returned by ``mlflow.active_run``. In order
    to access such attributes, use the :py:class:`mlflow.client.MlflowClient` as follows:

    .. code-block:: python
        :test:
        :caption: Example

        import mlflow

        mlflow.start_run()
        run = mlflow.active_run()
        print(f"Active run_id: {run.info.run_id}")
        mlflow.end_run()

    .. code-block:: text
        :caption: Output

        Active run_id: 6f252757005748708cd3aad75d1ff462
    """
    return mlflow.active_run()


def delete_run(run_id: str) -> None:
    """
    Deletes a run with the given ID.

    Args:
        run_id: Unique identifier for the run to delete.

    .. code-block:: python
        :test:
        :caption: Example

        import mlflow

        with mlflow.start_run() as run:
            mlflow.log_param("p", 0)

        run_id = run.info.run_id
        mlflow.delete_run(run_id)

        lifecycle_stage = mlflow.get_run(run_id).info.lifecycle_stage
        print(f"run_id: {run_id}; lifecycle_stage: {lifecycle_stage}")

    .. code-block:: text
        :caption: Output

        run_id: 45f4af3e6fd349e58579b27fcb0b8277; lifecycle_stage: deleted

    """
    return mlflow.delete_run(run_id)


def log_param(key: str, value: Any, synchronous: Optional[bool] = None) -> Any:
    """
    Log a parameter (e.g. model hyperparameter) under the current run. If no run is active,
    this method will create a new active run.

    Args:
        key: Parameter name. This string may only contain alphanumerics, underscores (_), dashes
            (-), periods (.), spaces ( ), and slashes (/). All backend stores support keys up to
            length 250, but some may support larger keys.
        value: Parameter value, but will be string-ified if not. All built-in backend stores support
            values up to length 6000, but some may support larger values.
        synchronous: *Experimental* If True, blocks until the parameter is logged successfully. If
            False, logs the parameter asynchronously and returns a future representing the logging
            operation. If None, read from environment variable `MLFLOW_ENABLE_ASYNC_LOGGING`,
            which defaults to False if not set.

    Returns:
        When `synchronous=True`, returns parameter value. When `synchronous=False`, returns an
        :py:class:`mlflow.utils.async_logging.run_operations.RunOperations` instance that represents
        future for logging operation.

    .. code-block:: python
        :test:
        :caption: Example

        import mlflow

        with mlflow.start_run():
            value = mlflow.log_param("learning_rate", 0.01)
            assert value == 0.01
            value = mlflow.log_param("learning_rate", 0.02, synchronous=False)
    """
    return mlflow.log_param(key, value, synchronous=synchronous)


def log_params(
    params: dict[str, Any],
    synchronous: Optional[bool] = None,
    run_id: Optional[str] = None,
) -> Optional[RunOperations]:
    """
    Log a batch of params for the current run. If no run is active, this method will create a
    new active run.

    Args:
        params: Dictionary of param_name: String -> value: (String, but will be string-ified if
            not)
        synchronous: *Experimental* If True, blocks until the parameters are logged
            successfully. If False, logs the parameters asynchronously and
            returns a future representing the logging operation. If None, read from environment
            variable `MLFLOW_ENABLE_ASYNC_LOGGING`, which defaults to False if not set.
        run_id: Run ID. If specified, log params to the specified run. If not specified, log
            params to the currently active run.

    Returns:
        When `synchronous=True`, returns None. When `synchronous=False`, returns an
        :py:class:`mlflow.utils.async_logging.run_operations.RunOperations` instance that
        represents future for logging operation.

    .. code-block:: python
        :test:
        :caption: Example

        import mlflow

        params = {"learning_rate": 0.01, "n_estimators": 10}

        # Log a batch of parameters
        with mlflow.start_run():
            mlflow.log_params(params)

        # Log a batch of parameters in async fashion.
        with mlflow.start_run():
            mlflow.log_params(params, synchronous=False)
    """
    return mlflow.log_params(params, synchronous=synchronous, run_id=run_id)


def log_artifact(
    local_path: str, artifact_path: Optional[str] = None, run_id: Optional[str] = None
) -> None:
    """
    Log a local file or directory as an artifact of the currently active run. If no run is
    active, this method will create a new active run.

    Args:
        local_path: Path to the file to write.
        artifact_path: If provided, the directory in ``artifact_uri`` to write to.
        run_id: If specified, log the artifact to the specified run. If not specified, log the
            artifact to the currently active run.

    .. code-block:: python
        :test:
        :caption: Example

        import tempfile
        from pathlib import Path

        import mlflow

        # Create a features.txt artifact file
        features = "rooms, zipcode, median_price, school_rating, transport"
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir, "features.txt")
            path.write_text(features)
            # With artifact_path=None write features.txt under
            # root artifact_uri/artifacts directory
            with mlflow.start_run():
                mlflow.log_artifact(path)
    """
    return mlflow.log_artifact(local_path, artifact_path, run_id=run_id)


def log_artifacts(
    local_dir: str, artifact_path: Optional[str] = None, run_id: Optional[str] = None
) -> None:
    """
    Log all the contents of a local directory as artifacts of the run. If no run is active,
    this method will create a new active run.

    Args:
        local_dir: Path to the directory of files to write.
        artifact_path: If provided, the directory in ``artifact_uri`` to write to.
        run_id: If specified, log the artifacts to the specified run. If not specified, log the
            artifacts to the currently active run.

    .. code-block:: python
        :test:
        :caption: Example

        import json
        import tempfile
        from pathlib import Path

        import mlflow

        # Create some files to preserve as artifacts
        features = "rooms, zipcode, median_price, school_rating, transport"
        data = {"state": "TX", "Available": 25, "Type": "Detached"}
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir = Path(tmp_dir)
            with (tmp_dir / "data.json").open("w") as f:
                json.dump(data, f, indent=2)
            with (tmp_dir / "features.json").open("w") as f:
                f.write(features)
            # Write all files in `tmp_dir` to root artifact_uri/states
            with mlflow.start_run():
                mlflow.log_artifacts(tmp_dir, artifact_path="states")
    """
    return mlflow.log_artifacts(local_dir, artifact_path, run_id=run_id)


def set_tag(
    key: str, value: Any, synchronous: Optional[bool] = None
) -> Optional[RunOperations]:
    """
    Set a tag under the current run. If no run is active, this method will create a new active
    run.

    Args:
        key: Tag name. This string may only contain alphanumerics, underscores (_), dashes (-),
            periods (.), spaces ( ), and slashes (/). All backend stores will support keys up to
            length 250, but some may support larger keys.
        value: Tag value, but will be string-ified if not. All backend stores will support values
            up to length 5000, but some may support larger values.
        synchronous: *Experimental* If True, blocks until the tag is logged successfully. If False,
            logs the tag asynchronously and returns a future representing the logging operation.
            If None, read from environment variable `MLFLOW_ENABLE_ASYNC_LOGGING`, which
            defaults to False if not set.

    Returns:
        When `synchronous=True`, returns None. When `synchronous=False`, returns an
        :py:class:`mlflow.utils.async_logging.run_operations.RunOperations` instance that
        represents future for logging operation.

    .. code-block:: python
        :test:
        :caption: Example

        import mlflow

        # Set a tag.
        with mlflow.start_run():
            mlflow.set_tag("release.version", "2.2.0")

        # Set a tag in async fashion.
        with mlflow.start_run():
            mlflow.set_tag("release.version", "2.2.1", synchronous=False)
    """
    return mlflow.set_tag(key, value, synchronous=synchronous)


def set_experiment_tag(key: str, value: Any) -> None:
    """
    Set a tag on the current experiment. Value is converted to a string.

    Args:
        key: Tag name. This string may only contain alphanumerics, underscores (_), dashes (-),
            periods (.), spaces ( ), and slashes (/). All backend stores will support keys up to
            length 250, but some may support larger keys.
        value: Tag value, but will be string-ified if not. All backend stores will support values
            up to length 5000, but some may support larger values.

    .. code-block:: python
        :test:
        :caption: Example

        import mlflow

        with mlflow.start_run():
            mlflow.set_experiment_tag("release.version", "2.2.0")
    """
    return mlflow.set_experiment_tag(key=key, value=value)


def set_experiment_tags(tags: dict[str, Any]) -> None:
    """
    Set tags for the current active experiment.

    Args:
        tags: Dictionary containing tag names and corresponding values.

    .. code-block:: python
        :test:
        :caption: Example

        import mlflow

        tags = {
            "engineering": "ML Platform",
            "release.candidate": "RC1",
            "release.version": "2.2.0",
        }

        # Set a batch of tags
        with mlflow.start_run():
            mlflow.set_experiment_tags(tags)
    """
    return mlflow.set_tags(tags)


def log_metric(
    key: str,
    value: float,
    step: Optional[int] = None,
    synchronous: Optional[bool] = None,
    timestamp: Optional[int] = None,
    run_id: Optional[str] = None,
    model_id: Optional[str] = None,
    dataset: Optional["Dataset"] = None,
) -> Optional[RunOperations]:
    """
    Log a metric under the current run. If no run is active, this method will create
    a new active run.

    Args:
        key: Metric name. This string may only contain alphanumerics, underscores (_),
            dashes (-), periods (.), spaces ( ), and slashes (/).
            All backend stores will support keys up to length 250, but some may
            support larger keys.
        value: Metric value. Note that some special values such as +/- Infinity may be
            replaced by other values depending on the store. For example, the
            SQLAlchemy store replaces +/- Infinity with max / min float values.
            All backend stores will support values up to length 5000, but some
            may support larger values.
        step: Metric step. Defaults to zero if unspecified.
        synchronous: *Experimental* If True, blocks until the metric is logged
            successfully. If False, logs the metric asynchronously and
            returns a future representing the logging operation. If None, read from environment
            variable `MLFLOW_ENABLE_ASYNC_LOGGING`, which defaults to False if not set.
        timestamp: Time when this metric was calculated. Defaults to the current system time.
        run_id: If specified, log the metric to the specified run. If not specified, log the metric
            to the currently active run.
        model_id: The ID of the model associated with the metric. If not specified, use the current
            active model ID set by :py:func:`mlflow.set_active_model`. If no active model exists,
            the models IDs associated with the specified or active run will be used.
        dataset: The dataset associated with the metric.

    Returns:
        When `synchronous=True`, returns None.
        When `synchronous=False`, returns `RunOperations` that represents future for
        logging operation.

    .. code-block:: python
        :test:
        :caption: Example

        import mlflow

        # Log a metric
        with mlflow.start_run():
            mlflow.log_metric("mse", 2500.00)

        # Log a metric in async fashion.
        with mlflow.start_run():
            mlflow.log_metric("mse", 2500.00, synchronous=False)
    """
    return mlflow.log_metric(
        key, value, step, synchronous, timestamp, run_id, model_id, dataset
    )


def log_metrics(
    metrics: dict[str, float],
    step: Optional[int] = None,
    synchronous: Optional[bool] = None,
    run_id: Optional[str] = None,
    timestamp: Optional[int] = None,
    model_id: Optional[str] = None,
    dataset: Optional["Dataset"] = None,
) -> Optional[RunOperations]:
    """
    Log multiple metrics for the current run. If no run is active, this method will create a new
    active run.

    Args:
        metrics: Dictionary of metric_name: String -> value: Float. Note that some special
            values such as +/- Infinity may be replaced by other values depending on
            the store. For example, sql based store may replace +/- Infinity with
            max / min float values.
        step: A single integer step at which to log the specified
            Metrics. If unspecified, each metric is logged at step zero.
        synchronous: *Experimental* If True, blocks until the metrics are logged
            successfully. If False, logs the metrics asynchronously and
            returns a future representing the logging operation. If None, read from environment
            variable `MLFLOW_ENABLE_ASYNC_LOGGING`, which defaults to False if not set.
        run_id: Run ID. If specified, log metrics to the specified run. If not specified, log
            metrics to the currently active run.
        timestamp: Time when these metrics were calculated. Defaults to the current system time.
        model_id: The ID of the model associated with the metric. If not specified, use the current
            active model ID set by :py:func:`mlflow.set_active_model`. If no active model
            exists, the models IDs associated with the specified or active run will be used.
        dataset: The dataset associated with the metrics.

    Returns:
        When `synchronous=True`, returns None. When `synchronous=False`, returns an
        :py:class:`mlflow.utils.async_logging.run_operations.RunOperations` instance that
        represents future for logging operation.

    .. code-block:: python
        :test:
        :caption: Example

        import mlflow

        metrics = {"mse": 2500.00, "rmse": 50.00}

        # Log a batch of metrics
        with mlflow.start_run():
            mlflow.log_metrics(metrics)

        # Log a batch of metrics in async fashion.
        with mlflow.start_run():
            mlflow.log_metrics(metrics, synchronous=False)
    """
    return mlflow.log_metrics(
        metrics, step, synchronous, run_id, timestamp, model_id, dataset
    )


def set_tags(
    tags: dict[str, Any], synchronous: Optional[bool] = None
) -> Optional[RunOperations]:
    """
    Log a batch of tags for the current run. If no run is active, this method will create a
    new active run.

    Args:
        tags: Dictionary of tag_name: String -> value: (String, but will be string-ified if
            not)
        synchronous: *Experimental* If True, blocks until tags are logged successfully. If False,
            logs tags asynchronously and returns a future representing the logging operation.
            If None, read from environment variable `MLFLOW_ENABLE_ASYNC_LOGGING`, which
            defaults to False if not set.

    Returns:
        When `synchronous=True`, returns None. When `synchronous=False`, returns an
        :py:class:`mlflow.utils.async_logging.run_operations.RunOperations` instance that
        represents future for logging operation.

    .. code-block:: python
        :test:
        :caption: Example

        import mlflow

        tags = {
            "engineering": "ML Platform",
            "release.candidate": "RC1",
            "release.version": "2.2.0",
        }

        # Set a batch of tags
        with mlflow.start_run():
            mlflow.set_tags(tags)

        # Set a batch of tags in async fashion.
        with mlflow.start_run():
            mlflow.set_tags(tags, synchronous=False)
    """
    return mlflow.set_tags(tags, synchronous)


def get_artifact_uri(artifact_path: Optional[str] = None) -> str:
    """
    Get the absolute URI of the specified artifact in the currently active run.

    If `path` is not specified, the artifact root URI of the currently active
    run will be returned; calls to ``log_artifact`` and ``log_artifacts`` write
    artifact(s) to subdirectories of the artifact root URI.

    If no run is active, this method will create a new active run.

    Args:
        artifact_path: The run-relative artifact path for which to obtain an absolute URI.
            For example, "path/to/artifact". If unspecified, the artifact root URI
            for the currently active run will be returned.

    Returns:
        An *absolute* URI referring to the specified artifact or the currently active run's
        artifact root. For example, if an artifact path is provided and the currently active
        run uses an S3-backed store, this may be a uri of the form
        ``s3://<bucket_name>/path/to/artifact/root/path/to/artifact``. If an artifact path
        is not provided and the currently active run uses an S3-backed store, this may be a
        URI of the form ``s3://<bucket_name>/path/to/artifact/root``.

    .. code-block:: python
        :test:
        :caption: Example

        import tempfile

        import mlflow

        features = "rooms, zipcode, median_price, school_rating, transport"
        with tempfile.NamedTemporaryFile("w") as tmp_file:
            tmp_file.write(features)
            tmp_file.flush()

            # Log the artifact in a directory "features" under the root artifact_uri/features
            with mlflow.start_run():
                mlflow.log_artifact(tmp_file.name, artifact_path="features")

                # Fetch the artifact uri root directory
                artifact_uri = mlflow.get_artifact_uri()
                print(f"Artifact uri: {artifact_uri}")

                # Fetch a specific artifact uri
                artifact_uri = mlflow.get_artifact_uri(artifact_path="features/features.txt")
                print(f"Artifact uri: {artifact_uri}")

    .. code-block:: text
        :caption: Output

        Artifact uri: file:///.../0/a46a80f1c9644bd8f4e5dd5553fffce/artifacts
        Artifact uri: file:///.../0/a46a80f1c9644bd8f4e5dd5553fffce/artifacts/features/features.txt
    """
    return mlflow.get_artifact_uri(artifact_path)


def autolog(
    log_input_examples: bool = False,
    log_model_signatures: bool = True,
    log_models: bool = True,
    log_datasets: bool = True,
    log_traces: bool = True,
    disable: bool = False,
    exclusive: bool = False,
    disable_for_unsupported_versions: bool = False,
    silent: bool = False,
    extra_tags: Optional[dict[str, str]] = None,
    exclude_flavors: Optional[list[str]] = None,
) -> None:
    """
    Enables (or disables) and configures autologging for all supported integrations.

    The parameters are passed to any autologging integrations that support them.

    See the `tracking docs <../../tracking/autolog.html>`_ for a list of supported autologging
    integrations.

    Note that framework-specific configurations set at any point will take precedence over
    any configurations set by this function. For example:

    .. code-block:: python
        :test:

        import mlflow

        mlflow.autolog(log_models=False, exclusive=True)
        import sklearn

    would enable autologging for `sklearn` with `log_models=False` and `exclusive=True`,
    but

    .. code-block:: python
        :test:

        import mlflow

        mlflow.autolog(log_models=False, exclusive=True)

        import sklearn

        mlflow.sklearn.autolog(log_models=True)

    would enable autologging for `sklearn` with `log_models=True` and `exclusive=False`,
    the latter resulting from the default value for `exclusive` in `mlflow.sklearn.autolog`;
    other framework autolog functions (e.g. `mlflow.tensorflow.autolog`) would use the
    configurations set by `mlflow.autolog` (in this instance, `log_models=False`, `exclusive=True`),
    until they are explicitly called by the user.

    Args:
        log_input_examples: If ``True``, input examples from training datasets are collected and
            logged along with model artifacts during training. If ``False``,
            input examples are not logged.
            Note: Input examples are MLflow model attributes
            and are only collected if ``log_models`` is also ``True``.
        log_model_signatures: If ``True``,
            :py:class:`ModelSignatures <mlflow.models.ModelSignature>`
            describing model inputs and outputs are collected and logged along
            with model artifacts during training. If ``False``, signatures are
            not logged. Note: Model signatures are MLflow model attributes
            and are only collected if ``log_models`` is also ``True``.
        log_models: If ``True``, trained models are logged as MLflow model artifacts.
            If ``False``, trained models are not logged.
            Input examples and model signatures, which are attributes of MLflow models,
            are also omitted when ``log_models`` is ``False``.
        log_datasets: If ``True``, dataset information is logged to MLflow Tracking.
            If ``False``, dataset information is not logged.
        log_traces: If ``True``, traces are collected for integrations.
            If ``False``, no trace is collected.
        disable: If ``True``, disables all supported autologging integrations. If ``False``,
            enables all supported autologging integrations.
        exclusive: If ``True``, autologged content is not logged to user-created fluent runs.
            If ``False``, autologged content is logged to the active fluent run,
            which may be user-created.
        disable_for_unsupported_versions: If ``True``, disable autologging for versions of
            all integration libraries that have not been tested against this version
            of the MLflow client or are incompatible.
        silent: If ``True``, suppress all event logs and warnings from MLflow during autologging
            setup and training execution. If ``False``, show all events and warnings during
            autologging setup and training execution.
        extra_tags: A dictionary of extra tags to set on each managed run created by autologging.
        exclude_flavors: A list of flavor names that are excluded from the auto-logging.
            e.g. tensorflow, pyspark.ml

    .. code-block:: python
        :test:
        :caption: Example

        import numpy as np
        import mlflow.sklearn
        from mlflow import MlflowClient
        from sklearn.linear_model import LinearRegression


        def print_auto_logged_info(r):
            tags = {k: v for k, v in r.data.tags.items() if not k.startswith("mlflow.")}
            artifacts = [f.path for f in MlflowClient().list_artifacts(r.info.run_id, "model")]
            print(f"run_id: {r.info.run_id}")
            print(f"artifacts: {artifacts}")
            print(f"params: {r.data.params}")
            print(f"metrics: {r.data.metrics}")
            print(f"tags: {tags}")


        # prepare training data
        X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
        y = np.dot(X, np.array([1, 2])) + 3

        # Auto log all the parameters, metrics, and artifacts
        mlflow.autolog()
        model = LinearRegression()
        with mlflow.start_run() as run:
            model.fit(X, y)

        # fetch the auto logged parameters and metrics for ended run
        print_auto_logged_info(mlflow.get_run(run_id=run.info.run_id))

    .. code-block:: text
        :caption: Output

        run_id: fd10a17d028c47399a55ab8741721ef7
        artifacts: ['model/MLmodel', 'model/conda.yaml', 'model/model.pkl']
        params: {'copy_X': 'True',
                 'normalize': 'False',
                 'fit_intercept': 'True',
                 'n_jobs': 'None'}
        metrics: {'training_score': 1.0,
                  'training_root_mean_squared_error': 4.440892098500626e-16,
                  'training_r2_score': 1.0,
                  'training_mean_absolute_error': 2.220446049250313e-16,
                  'training_mean_squared_error': 1.9721522630525295e-31}
        tags: {'estimator_class': 'sklearn.linear_model._base.LinearRegression',
               'estimator_name': 'LinearRegression'}
    """
    return mlflow.autolog(
        log_input_examples=log_input_examples,
        log_model_signatures=log_model_signatures,
        log_models=log_models,
        log_datasets=log_datasets,
        log_traces=log_traces,
        disable=disable,
        exclusive=exclusive,
        disable_for_unsupported_versions=disable_for_unsupported_versions,
        silent=silent,
        extra_tags=extra_tags,
        exclude_flavors=exclude_flavors,
    )


def search_experiments(
    view_type: int = ViewType.ACTIVE_ONLY,
    max_results: Optional[int] = None,
    filter_string: Optional[str] = None,
    order_by: Optional[list[str]] = None,
) -> list[Experiment]:
    """
    Search for experiments that match the specified search query.

    Args:
        view_type: One of enum values ``ACTIVE_ONLY``, ``DELETED_ONLY``, or ``ALL``
            defined in :py:class:`mlflow.entities.ViewType`.
        max_results: If passed, specifies the maximum number of experiments desired. If not
            passed, all experiments will be returned.
        filter_string: Filter query string (e.g., ``"name = 'my_experiment'"``), defaults to
            searching for all experiments. The following identifiers, comparators, and logical
            operators are supported.

            Identifiers
              - ``name``: Experiment name
              - ``creation_time``: Experiment creation time
              - ``last_update_time``: Experiment last update time
              - ``tags.<tag_key>``: Experiment tag. If ``tag_key`` contains
                spaces, it must be wrapped with backticks (e.g., ``"tags.`extra key`"``).

            Comparators for string attributes and tags
                - ``=``: Equal to
                - ``!=``: Not equal to
                - ``LIKE``: Case-sensitive pattern match
                - ``ILIKE``: Case-insensitive pattern match

            Comparators for numeric attributes
                - ``=``: Equal to
                - ``!=``: Not equal to
                - ``<``: Less than
                - ``<=``: Less than or equal to
                - ``>``: Greater than
                - ``>=``: Greater than or equal to

            Logical operators
              - ``AND``: Combines two sub-queries and returns True if both of them are True.

        order_by: List of columns to order by. The ``order_by`` column can contain an optional
            ``DESC`` or ``ASC`` value (e.g., ``"name DESC"``). The default ordering is ``ASC``,
            so ``"name"`` is equivalent to ``"name ASC"``. If unspecified, defaults to
            ``["last_update_time DESC"]``, which lists experiments updated most recently first.
            The following fields are supported:

                - ``experiment_id``: Experiment ID
                - ``name``: Experiment name
                - ``creation_time``: Experiment creation time
                - ``last_update_time``: Experiment last update time

    Returns:
        A list of :py:class:`Experiment <mlflow.entities.Experiment>` objects.

    .. code-block:: python
        :test:
        :caption: Example

        import mlflow


        def assert_experiment_names_equal(experiments, expected_names):
            actual_names = [e.name for e in experiments if e.name != "Default"]
            assert actual_names == expected_names, (actual_names, expected_names)


        mlflow.set_tracking_uri("sqlite:///:memory:")
        # Create experiments
        for name, tags in [
            ("a", None),
            ("b", None),
            ("ab", {"k": "v"}),
            ("bb", {"k": "V"}),
        ]:
            mlflow.create_experiment(name, tags=tags)

        # Search for experiments with name "a"
        experiments = mlflow.search_experiments(filter_string="name = 'a'")
        assert_experiment_names_equal(experiments, ["a"])
        # Search for experiments with name starting with "a"
        experiments = mlflow.search_experiments(filter_string="name LIKE 'a%'")
        assert_experiment_names_equal(experiments, ["ab", "a"])
        # Search for experiments with tag key "k" and value ending with "v" or "V"
        experiments = mlflow.search_experiments(filter_string="tags.k ILIKE '%v'")
        assert_experiment_names_equal(experiments, ["bb", "ab"])
        # Search for experiments with name ending with "b" and tag {"k": "v"}
        experiments = mlflow.search_experiments(filter_string="name LIKE '%b' AND tags.k = 'v'")
        assert_experiment_names_equal(experiments, ["ab"])
        # Sort experiments by name in ascending order
        experiments = mlflow.search_experiments(order_by=["name"])
        assert_experiment_names_equal(experiments, ["a", "ab", "b", "bb"])
        # Sort experiments by ID in descending order
        experiments = mlflow.search_experiments(order_by=["experiment_id DESC"])
        assert_experiment_names_equal(experiments, ["bb", "ab", "b", "a"])
    """
    return mlflow.search_experiments(
        view_type=view_type,
        max_results=max_results,
        filter_string=filter_string,
        order_by=order_by,
    )


def search_runs(
    experiment_ids: Optional[list[str]] = None,
    filter_string: str = "",
    run_view_type: int = ViewType.ACTIVE_ONLY,
    max_results: int = SEARCH_MAX_RESULTS_PANDAS,
    order_by: Optional[list[str]] = None,
    output_format: str = "pandas",
    search_all_experiments: bool = False,
    experiment_names: Optional[list[str]] = None,
) -> Union[list[Run], "pandas.DataFrame"]:
    """
    Search for Runs that fit the specified criteria.

    Args:
        experiment_ids: List of experiment IDs. Search can work with experiment IDs or
            experiment names, but not both in the same call. Values other than
            ``None`` or ``[]`` will result in error if ``experiment_names`` is
            also not ``None`` or ``[]``. ``None`` will default to the active
            experiment if ``experiment_names`` is ``None`` or ``[]``.
        filter_string: Filter query string, defaults to searching all runs.
        run_view_type: one of enum values ``ACTIVE_ONLY``, ``DELETED_ONLY``, or ``ALL`` runs
            defined in :py:class:`mlflow.entities.ViewType`.
        max_results: The maximum number of runs to put in the dataframe. Default is 100,000
            to avoid causing out-of-memory issues on the user's machine.
        order_by: List of columns to order by (e.g., "metrics.rmse"). The ``order_by`` column
            can contain an optional ``DESC`` or ``ASC`` value. The default is ``ASC``.
            The default ordering is to sort by ``start_time DESC``, then ``run_id``.
        output_format: The output format to be returned. If ``pandas``, a ``pandas.DataFrame``
            is returned and, if ``list``, a list of :py:class:`mlflow.entities.Run`
            is returned.
        search_all_experiments: Boolean specifying whether all experiments should be searched.
            Only honored if ``experiment_ids`` is ``[]`` or ``None``.
        experiment_names: List of experiment names. Search can work with experiment IDs or
            experiment names, but not both in the same call. Values other
            than ``None`` or ``[]`` will result in error if ``experiment_ids``
            is also not ``None`` or ``[]``. ``None`` will default to the active
            experiment if ``experiment_ids`` is ``None`` or ``[]``.

    Returns:
        If output_format is ``list``: a list of :py:class:`mlflow.entities.Run`. If
        output_format is ``pandas``: ``pandas.DataFrame`` of runs, where each metric,
        parameter, and tag is expanded into its own column named metrics.*, params.*, or
        tags.* respectively. For runs that don't have a particular metric, parameter, or tag,
        the value for the corresponding column is (NumPy) ``Nan``, ``None``, or ``None``
        respectively.

     .. code-block:: python
        :test:
        :caption: Example

        import mlflow

        # Create an experiment and log two runs under it
        experiment_name = "Social NLP Experiments"
        experiment_id = mlflow.create_experiment(experiment_name)
        with mlflow.start_run(experiment_id=experiment_id):
            mlflow.log_metric("m", 1.55)
            mlflow.set_tag("s.release", "1.1.0-RC")
        with mlflow.start_run(experiment_id=experiment_id):
            mlflow.log_metric("m", 2.50)
            mlflow.set_tag("s.release", "1.2.0-GA")
        # Search for all the runs in the experiment with the given experiment ID
        df = mlflow.search_runs([experiment_id], order_by=["metrics.m DESC"])
        print(df[["metrics.m", "tags.s.release", "run_id"]])
        print("--")
        # Search the experiment_id using a filter_string with tag
        # that has a case insensitive pattern
        filter_string = "tags.s.release ILIKE '%rc%'"
        df = mlflow.search_runs([experiment_id], filter_string=filter_string)
        print(df[["metrics.m", "tags.s.release", "run_id"]])
        print("--")
        # Search for all the runs in the experiment with the given experiment name
        df = mlflow.search_runs(experiment_names=[experiment_name], order_by=["metrics.m DESC"])
        print(df[["metrics.m", "tags.s.release", "run_id"]])

    .. code-block:: text
        :caption: Output

           metrics.m tags.s.release                            run_id
        0       2.50       1.2.0-GA  147eed886ab44633902cc8e19b2267e2
        1       1.55       1.1.0-RC  5cc7feaf532f496f885ad7750809c4d4
        --
           metrics.m tags.s.release                            run_id
        0       1.55       1.1.0-RC  5cc7feaf532f496f885ad7750809c4d4
        --
           metrics.m tags.s.release                            run_id
        0       2.50       1.2.0-GA  147eed886ab44633902cc8e19b2267e2
        1       1.55       1.1.0-RC  5cc7feaf532f496f885ad7750809c4d4
    """
    return mlflow.search_runs(
        experiment_ids=experiment_ids,
        filter_string=filter_string,
        run_view_type=run_view_type,
        max_results=max_results,
        order_by=order_by,
        output_format=output_format,
        search_all_experiments=search_all_experiments,
        experiment_names=experiment_names,
    )


def delete_experiment(experiment_id: str) -> None:
    """
    Delete an experiment from the backend store.

    Args:
        experiment_id: The string-ified experiment ID returned from ``create_experiment``.

    .. code-block:: python
        :test:
        :caption: Example

        import mlflow

        experiment_id = mlflow.create_experiment("New Experiment")
        mlflow.delete_experiment(experiment_id)

        # Examine the deleted experiment details.
        experiment = mlflow.get_experiment(experiment_id)
        print(f"Name: {experiment.name}")
        print(f"Artifact Location: {experiment.artifact_location}")
        print(f"Lifecycle_stage: {experiment.lifecycle_stage}")
        print(f"Last Updated timestamp: {experiment.last_update_time}")

    .. code-block:: text
        :caption: Output

        Name: New Experiment
        Artifact Location: file:///.../mlruns/2
        Lifecycle_stage: deleted
        Last Updated timestamp: 1662004217511

    """
    mlflow.delete_experiment(experiment_id)
