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

import os
import signal
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from kubeflow.trainer.constants import constants
from kubeflow.trainer.job_runners.job_runner import JobRunner
from kubeflow.trainer.types import types
from kubeflow.trainer.utils import utils


def is_process_runner_available() -> bool:
    try:
        import subprocess
        import threading
        return True
    except ImportError:
        return False


class ProcessJobRunner(JobRunner):

    def __init__(
        self,
        working_dir: Optional[Union[str, Path]] = None,
        python_executable: Optional[str] = None,
    ):
        if working_dir is None:
            self.working_dir = Path.cwd() / "kubeflow_trainer_jobs"
        else:
            self.working_dir = Path(working_dir)
        
        self.working_dir.mkdir(parents=True, exist_ok=True)
        
        if python_executable is None:
            self.python_executable = "python"
        else:
            self.python_executable = python_executable

        self._active_jobs: Dict[str, Dict] = {}
        self._job_logs: Dict[str, Dict[str, str]] = {}

    def create_job(
        self,
        image: str,
        entrypoint: List[str],
        command: List[str],
        num_nodes: int,
        framework: types.Framework,
        runtime_name: str,
    ) -> str:
        if framework not in [types.Framework.TORCH, types.Framework.TORCHTUNE]:
            raise RuntimeError(f"Framework '{framework}' is not currently supported in ProcessJobRunner.")

        train_job_name = (
            f"{constants.LOCAL_TRAIN_JOB_NAME_PREFIX}{utils.generate_train_job_name()}"
        )

        job_dir = self.working_dir / train_job_name
        job_dir.mkdir(parents=True, exist_ok=True)

        self._active_jobs[train_job_name] = {
            "creation_timestamp": datetime.now(),
            "runtime_name": runtime_name,
            "image": image,
            "processes": [],
            "num_nodes": num_nodes,
            "framework": framework,
            "job_dir": job_dir,
            "status": "Starting",
        }
        
        self._job_logs[train_job_name] = {}

        for node_rank in range(num_nodes):
            process_info = self._start_node_process(
                train_job_name=train_job_name,
                node_rank=node_rank,
                num_nodes=num_nodes,
                entrypoint=entrypoint,
                command=command,
                framework=framework,
                job_dir=job_dir,
            )
            self._active_jobs[train_job_name]["processes"].append(process_info)

        self._active_jobs[train_job_name]["status"] = "Running"
        return train_job_name

    def _start_node_process(
        self,
        train_job_name: str,
        node_rank: int,
        num_nodes: int,
        entrypoint: List[str],
        command: List[str],
        framework: types.Framework,
        job_dir: Path,
    ) -> Dict:
        env = os.environ.copy()
        env.update(
            self._get_process_environment(
                framework=framework,
                head_node_address="localhost",
                num_nodes=num_nodes,
                node_rank=node_rank,
                train_job_name=train_job_name,
            )
        )

        if (entrypoint and entrypoint == ["bash", "-c"] and command and len(command) > 0 and 
            command[0].strip().startswith("read -r -d") and "torchrun" in command[0]):
            original_script = command[0]
            modified_script = original_script.replace('torchrun "', f'{self.python_executable} -m torch.distributed.run "')
            full_command = ["bash", "-c", modified_script]
        elif entrypoint and entrypoint[0] == "torchrun" and command and len(command) > 0:
            full_command = self._build_torchrun_command(
                entrypoint=entrypoint,
                command=command,
                num_nodes=num_nodes,
                node_rank=node_rank,
            )
        elif (entrypoint and command and 
              len(command) > 0 and command[0].endswith('.py')):
            full_command = [self.python_executable] + command
        else:
            full_command = entrypoint + command

        stdout_file = job_dir / f"node-{node_rank}-stdout.log"
        stderr_file = job_dir / f"node-{node_rank}-stderr.log"

        print(f"Starting process for node {node_rank} with command: {' '.join(full_command[:3])}...")

        with open(stdout_file, 'w') as stdout_f, open(stderr_file, 'w') as stderr_f:
            process = subprocess.Popen(
                full_command,
                env=env,
                stdout=stdout_f,
                stderr=stderr_f,
                cwd=job_dir,
                preexec_fn=os.setsid,
            )

        return {
            "process": process,
            "node_rank": node_rank,
            "stdout_file": stdout_file,
            "stderr_file": stderr_file,
            "status": "Running",
        }

    def _build_torchrun_command(
        self,
        entrypoint: List[str],
        command: List[str],
        num_nodes: int,
        node_rank: int,
    ) -> List[str]:
        
        torchrun_args = [
            self.python_executable, "-m", "torch.distributed.run",
            "--nproc_per_node=1",
            f"--nnodes={num_nodes}",
            f"--node_rank={node_rank}",
            "--master_addr=localhost",
            "--master_port=29500",
        ]

        torchrun_args.extend(command)
        
        return torchrun_args

    def get_job(self, job_name: str) -> types.ContainerJob:
        if job_name not in self._active_jobs:
            raise RuntimeError(f"Job '{job_name}' not found")

        job_info = self._active_jobs[job_name]

        containers = []
        for i, process_info in enumerate(job_info["processes"]):
            process = process_info["process"]
            status = self._get_process_status(process)
            process_info["status"] = status
            
            containers.append(
                types.Container(
                    name=f"{job_name}-{i}",
                    status=status,
                )
            )

        job_status = self._get_job_status(containers)
        job_info["status"] = job_status

        return types.ContainerJob(
            name=job_name,
            creation_timestamp=job_info["creation_timestamp"],
            runtime_name=job_info["runtime_name"],
            containers=containers,
            status=job_status,
        )

    def get_job_logs(
        self,
        job_name: str,
        follow: bool = False,
        step: str = constants.NODE,
        node_rank: int = 0,
    ) -> Dict[str, str]:
        if job_name not in self._active_jobs:
            raise RuntimeError(f"Job '{job_name}' not found")

        job_info = self._active_jobs[job_name]
        
        if node_rank >= len(job_info["processes"]):
            raise RuntimeError(f"Node rank {node_rank} not found for job '{job_name}'")

        process_info = job_info["processes"][node_rank]
        stdout_file = process_info["stdout_file"]
        stderr_file = process_info["stderr_file"]

        logs = {}
        
        if follow:
            # For following logs, we'll read and print in real-time
            self._follow_logs(job_name, node_rank, stdout_file, stderr_file, step, logs)
        else:
            # Read all available logs
            try:
                if stdout_file.exists():
                    with open(stdout_file, 'r') as f:
                        stdout_content = f.read()
                else:
                    stdout_content = ""
                
                if stderr_file.exists():
                    with open(stderr_file, 'r') as f:
                        stderr_content = f.read()
                else:
                    stderr_content = ""
                
                # Combine stdout and stderr
                combined_logs = stdout_content
                if stderr_content:
                    combined_logs += f"\n--- STDERR ---\n{stderr_content}"
                
                logs[f"{step}-{node_rank}"] = combined_logs
                
            except Exception as e:
                logs[f"{step}-{node_rank}"] = f"Error reading logs: {str(e)}"

        return logs

    def _follow_logs(
        self,
        job_name: str,
        node_rank: int,
        stdout_file: Path,
        stderr_file: Path,
        step: str,
        logs: Dict[str, str],
    ):
        def tail_file(file_path: Path, prefix: str = ""):
            if not file_path.exists():
                return
            
            with open(file_path, 'r') as f:
                # Read existing content
                content = f.read()
                if content:
                    for line in content.splitlines():
                        print(f"[{step}-{node_rank}]{prefix}: {line}")
                        logs[f"{step}-{node_rank}"] = (
                            logs.get(f"{step}-{node_rank}", "") + line + "\n"
                        )
                
                # Follow new content
                while True:
                    line = f.readline()
                    if line:
                        line = line.rstrip('\n')
                        print(f"[{step}-{node_rank}]{prefix}: {line}")
                        logs[f"{step}-{node_rank}"] = (
                            logs.get(f"{step}-{node_rank}", "") + line + "\n"
                        )
                    else:
                        # Check if process is still running
                        job_info = self._active_jobs.get(job_name)
                        if not job_info or node_rank >= len(job_info["processes"]):
                            break
                        process = job_info["processes"][node_rank]["process"]
                        if process.poll() is not None
                            break
                        time.sleep(0.1)

        stdout_thread = threading.Thread(target=tail_file, args=(stdout_file, ""))
        stderr_thread = threading.Thread(target=tail_file, args=(stderr_file, "[STDERR]"))
        
        stdout_thread.start()
        stderr_thread.start()

        stdout_thread.join()
        stderr_thread.join()

    def list_jobs(
        self,
        runtime_name: Optional[str] = None,
    ) -> List[types.ContainerJob]:
        jobs = []
        for job_name in self._active_jobs.keys():
            job_info = self._active_jobs[job_name]
            if runtime_name is None or job_info["runtime_name"] == runtime_name:
                jobs.append(self.get_job(job_name))
        return jobs

    def delete_job(self, job_name: str) -> None:
        if job_name not in self._active_jobs:
            raise RuntimeError(f"Job '{job_name}' not found")

        job_info = self._active_jobs[job_name]

        for process_info in job_info["processes"]:
            process = process_info["process"]
            if process.poll() is None:
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)

                    time.sleep(2)

                    if process.poll() is None:
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                        
                except (ProcessLookupError, OSError):
                    pass

        del self._active_jobs[job_name]
        if job_name in self._job_logs:
            del self._job_logs[job_name]

    @staticmethod
    def _get_process_environment(
        framework: types.Framework,
        head_node_address: str,
        num_nodes: int,
        node_rank: int,
        train_job_name: str,
    ) -> Dict[str, str]:
        env = {}
        
        if framework == types.Framework.TORCH:
            env.update({
                "NNODES": str(num_nodes),
                "NPROC_PER_NODE": "1",
                "NODE_RANK": str(node_rank),
                "MASTER_ADDR": head_node_address,
                "MASTER_PORT": "29500",
                "RANK": str(node_rank),
                "LOCAL_RANK": "0",
                "WORLD_SIZE": str(num_nodes),
            })
        
        # Add job-specific environment variables
        env[constants.CONTAINER_TRAIN_JOB_NAME_LABEL] = train_job_name
        env[constants.LOCAL_NODE_RANK_LABEL] = str(node_rank)
        
        return env

    @staticmethod
    def _get_process_status(process: subprocess.Popen) -> str:
        if process.poll() is None:
            return "running"
        elif process.returncode == 0:
            return "exited"
        else:
            return "failed"

    @staticmethod
    def _get_job_status(containers: List[types.Container]) -> str:
        if not containers:
            return "pending"
        
        statuses = [c.status for c in containers]
        
        if all(status == "exited" for status in statuses):
            return "succeeded"
        elif any(status == "failed" for status in statuses):
            return "failed"
        elif any(status == "running" for status in statuses):
            return "running"
        else:
            return "pending" 