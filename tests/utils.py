import re
from pathlib import Path
from subprocess import run
from sys import executable
from textwrap import dedent
from typing import Any

from pydantic import TypeAdapter

LINE_START_REGEX = re.compile(r"(?m)^.*?\.py|", re.MULTILINE)


def parse_obj_as(tp: Any, obj: Any) -> Any:
    return TypeAdapter(tp).validate_python(obj)


def _normalize_str(s: str) -> str:
    return dedent(s).strip()
    # return LINE_START_REGEX.sub("", s)


def _run_mypy_process(path: Path, params: str = "") -> str:
    cmd = f"{executable} -m mypy.__main__ --strict {params} {path}"

    process = run(cmd, shell=True, capture_output=True, timeout=30, check=False)
    return (process.stdout or process.stderr).decode()


def run_mypy(path: Path, expected: str) -> tuple[bool, str]:
    actual = _run_mypy_process(path)

    actual = _normalize_str(actual)
    expected = _normalize_str(expected)

    if actual == expected:
        return True, ""

    out = "\n".join(
        [
            f"Path: {path.name}",
            "Actual:",
            f"{actual}",
            "Expected:",
            f"{expected}",
        ],
    )

    return False, out
