# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from pathlib import Path
from typing import Dict, Union

from promptflow._utils.load_data import load_data
from promptflow._utils.logger_utils import bulk_logger
from promptflow._utils.multimedia_utils import resolve_multimedia_data_recursively


class DataResolver:
    def __init__(self, base_dir: Path, max_lines_count: int = None):
        self._base_dir = base_dir
        self._max_lines_count = max_lines_count

    def resolve_data(self, input_dirs: Dict[str, str]):
        """Resolve input data from input dirs"""
        result = {}
        for input_key, input_dir in input_dirs.items():
            input_dir = self.resolve_dir(input_dir)
            result[input_key] = self._resolve_data_from_input_path(input_dir)
        return result

    def resolve_dir(self, dir: Union[str, Path]) -> Path:
        """Resolve input dir to absolute path"""
        path = dir if isinstance(dir, Path) else Path(dir)
        if not path.is_absolute():
            path = self._base_dir / path
        return path

    def _resolve_data_from_input_path(self, input_path: Path):
        """Resolve input data from directory"""
        result = []
        if input_path.is_file():
            result.extend(resolve_multimedia_data_recursively(input_path.parent, load_data(input_path)))
        else:
            for input_file in input_path.rglob("*"):
                if input_file.is_file():
                    result.extend(resolve_multimedia_data_recursively(input_file.parent, load_data(input_file)))
                    if self._max_lines_count and len(result) >= self._max_lines_count:
                        break
        if self._max_lines_count and len(result) > self._max_lines_count:
            bulk_logger.warning(
                (
                    "The data provided exceeds the maximum lines limit. Currently, only the first "
                    f"{self._max_lines_count} lines are processed."
                )
            )
            return result[: self._max_lines_count]
        return result
