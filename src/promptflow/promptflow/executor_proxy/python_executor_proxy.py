# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from promptflow.executor._result import LineResult
from promptflow.executor.flow_executor import FlowExecutor
from promptflow.executor_proxy.base_executor_proxy import AbsractExecutorProxy


class PythonExecutorProxy(AbsractExecutorProxy):
    @classmethod
    def create(
        cls,
        yaml_file,
        working_dir,
    ):
        """Create a new executor"""
        return cls(yaml_file, working_dir)

    def __init__(self, yaml_file, working_dir):
        self._yaml_file = yaml_file
        self._working_dir = working_dir
        self._executor = FlowExecutor.create(
            self._yaml_file,
            connections={},
            working_dir=self._working_dir,
        )

    def destroy(self):
        pass

    def exec_line(self, inputs, index, run_id) -> LineResult:
        return self._executor.exec_line(inputs, index, run_id=run_id)
