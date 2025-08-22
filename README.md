# Kubeflow SDK

<!-- TODO(kramaranya): update when release [![PyPI version](https://img.shields.io/pypi/v/kubeflow?color=%2334D058&label=pypi%20package)](https://pypi.org/project/kubeflow/) -->
[![Join Slack](https://img.shields.io/badge/Join_Slack-blue?logo=slack)](https://www.kubeflow.org/docs/about/community/#kubeflow-slack-channels)
[![Coverage Status](https://coveralls.io/repos/github/kubeflow/sdk/badge.svg?branch=main)](https://coveralls.io/github/kubeflow/sdk?branch=main)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue)](https://github.com/kubeflow/sdk/blob/main/LICENSE)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/kubeflow/sdk)
<!-- TODO(kramaranya): update when release [![Python Supported Versions](https://img.shields.io/pypi/pyversions/kubeflow.svg?color=%2334D058)](https://pypi.org/project/kubeflow/) -->

## Overview

Kubeflow SDK is a unified Python SDK that streamlines the user experience for AI Practitioners to interact with various
Kubeflow projects. It provides simple, consistent APIs across the Kubeflow ecosystem, enabling users to focus on building
ML applications rather than managing complex infrastrutcure.

> **Note**: The Kubeflow SDK is in active development. Currently, the SDK provides full support for **Kubeflow
Trainer** with other components planned for future releases.

### Kubeflow SDK Benefits

- **Unified Experience**: Single SDK to interact with multiple Kubeflow components through consistent Python APIs
- **Simplified ML Workflows**: Abstract away Kubernetes complexity, allowing ML practitioners to work in familiar Python environments
- **Seamless Integration**: Designed to work together with all Kubeflow projects for end-to-end ML pipelines
- **Local Development**: First-class support for local development requiring only `pip` installation

## Installation

Install the Kubeflow SDK using pip:

```bash
pip install git+https://github.com/kubeflow/sdk.git@main
```

## Supported Components

| Component                   | Status | Description                                                    |
|-----------------------------|--------|----------------------------------------------------------------|
| **Kubeflow Trainer**        | ✅ **Available** | Train and fine-tune models with various frameworks   |
| **Kubeflow Katib**          | 🚧 Planned | Hyperparameter optimization                                |
| **Kubeflow Pipelines**      | 🚧 Planned | Build, run, and track ML workflows                         |
| **Kubeflow Spark Operator** | 🚧 Planned | Run Apache Spark jobs on Kubernetes                        |
| **Kubeflow Model Registry** | 🚧 Planned | Manage model artifacts, versions and ML artifacts metadata |
| **Kubeflow Feast**          | 🚧 Planned | Feature store for ML feature management and serving        |
| **Kubeflow KServe**         | 🚧 Planned | Model deployment and serving infrastructure                |

## Community

### Getting Involved

- **Slack**: Join our [#kubeflow-trainer](https://www.kubeflow.org/docs/about/community/#kubeflow-slack-channels) Slack channel
  <!-- TODO(kramaranya): update to #ml-experience once we kick off -->
- **Meetings**: Attend the [AutoML and Training Working Group](https://bit.ly/2PWVCkV) bi-weekly meetings
  <!-- TODO(kramaranya): update with kubeflow sdk meetings once we kick off -->
- **GitHub**: Discussions, issues and contributions at [kubeflow/sdk](https://github.com/kubeflow/sdk)

### Contributing

Kubeflow SDK is a community project and is still under active development. We welcome contributions! Please see our
[CONTRIBUTING Guide](CONTRIBUTING.md) for details.

## Documentation

<!-- TODO(kramaranya): add kubeflow sdk docs -->
- **[Design Document](https://docs.google.com/document/d/1rX7ELAHRb_lvh0Y7BK1HBYAbA0zi9enB0F_358ZC58w/edit)**: Kubeflow SDK design proposal
- **[Component Guides](https://www.kubeflow.org/docs/components/)**: Individual component documentation
- **[DeepWiki](https://deepwiki.com/kubeflow/sdk)**: AI-powered repository documentation

## ✨ Contributors

We couldn't have done it without these incredible people:

<a href="https://github.com/kubeflow/sdk/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=kubeflow/sdk" />
</a>

## License

Licensed under the [Apache License 2.0](LICENSE).
