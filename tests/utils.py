import re
from pathlib import Path
from subprocess import run, PIPE
from sys import executable
from textwrap import dedent
from typing import Any
from typing import Tuple

from pydantic import TypeAdapter

LINE_START_REGEX = re.compile(r"(?m)^.*?\.py|", re.MULTILINE)


def parse_obj_as(tp: Any, obj: Any) -> Any:
    return TypeAdapter(tp).validate_python(obj)


def _normalize_str(s: str) -> str:
    return LINE_START_REGEX.sub("", dedent(s).strip())


def _run_mypy_process(path: Path, params: str = "") -> str:
    cmd = f"{executable} -m mypy.__main__ --strict {params} {path}"

    process = run(cmd, shell=True, stdout=PIPE, stderr=PIPE, timeout=30)
    return (process.stdout or process.stderr).decode()


def run_mypy(path: Path, expected: str) -> Tuple[bool, str]:
    actual = _run_mypy_process(path)

    actual = _normalize_str(actual)
    expected = _normalize_str(expected)

    if actual == expected:
        return True, ""

    out = f"Actual:\n{actual}\nExpected:\n{expected}"
    return False, out
