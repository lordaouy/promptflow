# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

from promptflow._utils.context_utils import _change_working_dir
from promptflow._utils.utils import dump_list_to_jsonl
from promptflow.batch_engine._data_resolver import DataResolver
from promptflow.executor._result import BulkResult
from promptflow.executor_proxy.base_executor_proxy import AbsractExecutorProxy
from promptflow.storage import AbstractRunStorage

OUTPUT_FILE_NAME = "output.jsonl"


class BatchEngine:
    executor_proxy_classes = {}

    @classmethod
    def register_executor(cls, type, executor_cls: AbsractExecutorProxy):
        cls.executor_proxy_classes[type] = executor_cls

    def __init__(self, flow_yaml, storage: AbstractRunStorage, working_dir: Path = None):
        if not working_dir:
            working_dir = Path(flow_yaml).parent
        working_dir = Path(working_dir).resolve()
        executor_type = "python"
        self._executor_cls = self.executor_proxy_classes[executor_type]
        with _change_working_dir(working_dir):
            self._executor: AbsractExecutorProxy = self._executor_cls.create(flow_yaml, working_dir)
        self._storage = storage
        self._working_dir = working_dir
        self._flow_yaml = flow_yaml

    def run(
        self,
        input_dirs: Dict[str, str],
        inputs_mapping: Dict[str, str],
        output_dir: Path,
        run_id: Optional[str] = None,
        max_lines_count: Optional[int] = None,
    ) -> BulkResult:
        # resolve input data from input dirs and apply inputs mapping
        data_resolver = DataResolver(self.flow_executor._working_dir, max_lines_count)
        input_dicts = data_resolver.resolve_data(input_dirs)
        mapped_inputs = self.flow_executor.validate_and_apply_inputs_mapping(input_dicts, inputs_mapping)
        # run flow in batch mode
        output_dir = data_resolver.resolve_dir(output_dir)
        with _change_working_dir(self.flow_executor._working_dir):
            batch_result = self.flow_executor.exec_bulk(mapped_inputs, run_id, output_dir=output_dir)
        # persist outputs to output dir
        self._persist_outputs(batch_result.outputs, output_dir)
        return batch_result

    def _persist_outputs(self, outputs: List[Mapping[str, Any]], output_dir: Path):
        """Persist outputs to json line file in output directory"""
        output_file = output_dir / OUTPUT_FILE_NAME
        dump_list_to_jsonl(output_file, outputs)
