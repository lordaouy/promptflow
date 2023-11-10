# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from promptflow.executor._result import LineResult


class AbsractExecutorProxy:
    @classmethod
    def create(
        cls,
        yaml_file,
        working_dir,
    ):
        """Create a new executor"""
        raise NotImplementedError()

    @classmethod
    def destroy(self):
        pass

    def exec_line(self, inputs, index, run_id) -> LineResult:
        raise NotImplementedError()


class APIBasedExecutorProxy(AbsractExecutorProxy):
    @property
    def api_endpoint(self) -> str:
        raise NotImplementedError()

    def exec_line(self, inputs, index, run_id) -> LineResult:
        import requests

        timeout = 600
        payload = {"run_id": run_id, "line_number": index, "inputs": inputs}
        resp = requests.post(self.api_endpoint, json=payload, timeout=timeout)
        return LineResult.from_dict(resp.json())
