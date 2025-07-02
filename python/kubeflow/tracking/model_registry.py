# Copyright 2025 The Kubeflow Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dataclasses import dataclass
from typing import List
import os

from kubernetes import client, config
from kubernetes.client.models.v1_service import V1Service

TRACKING_URI_ANNOTATION_KEY = "routing.opendatahub.io/external-address-rest"

MODEL_REGISTRY_GROUP = "modelregistry.opendatahub.io"
MODEL_REGISTRY_VERSION = "v1alpha1"
MODEL_REGISTRY_KIND_PLURAL = "modelregistries"


# TODO: Add configurable k8s client, and add this method to fluent API
def get_tracking_store_uri(name: str, namespace: str) -> str:
    if is_running_in_k8s():
        config.load_incluster_config()
    else:
        config.load_kube_config()

    k8s_client = client.ApiClient()
    core_api = client.CoreV1Api(k8s_client)

    svc: V1Service = core_api.read_namespaced_service(name, namespace)
    # TODO: support non-https deployments
    return f"modelregistry+https://{svc.metadata.annotations[TRACKING_URI_ANNOTATION_KEY]}"


# TODO: discuss information a data scientist may want to see
@dataclass
class ModelRegistry:
    name: str
    available: bool

    def __str__(self) -> str:
        return f"Name: {self.name}, Available: {self.available})"


# TODO: implement list_all_model_regitries in all namespaces
# TODO: would the name "list_tracking_stores" be more useful?
def list_model_registries(namespace: str) -> List[ModelRegistry]:
    if is_running_in_k8s():
        config.load_incluster_config()
    else:
        config.load_kube_config()

    k8s_client = client.ApiClient()
    custom_api = client.CustomObjectsApi(k8s_client)

    model_registries = custom_api.list_namespaced_custom_object(
        group=MODEL_REGISTRY_GROUP,
        version=MODEL_REGISTRY_VERSION,
        namespace=namespace,
        plural=MODEL_REGISTRY_KIND_PLURAL,
    )

    model_registries_list: List[ModelRegistry] = []
    for model_registry in model_registries["items"]:
        is_available = False
        for condition in model_registry["status"]["conditions"]:
            if condition["type"] == "Available":
                is_available = bool(condition["status"])
        model_registries_list.append(ModelRegistry(model_registry["metadata"]["name"], is_available))

    return model_registries_list

def is_running_in_k8s() -> bool:
    return os.path.isdir("/var/run/secrets/kubernetes.io/")
