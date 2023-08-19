from pathlib import Path
from typing import Iterable, Any

from pytest import Collector, File, Item, ExceptionInfo

from ..utils import run_mypy


class _MypyFailure(Exception):
    pass


class _MypyItem(Item):
    def get_expected_result(self) -> str:
        code, _, expected = self.path.read_text().partition("# output:")
        return expected.strip().strip('"')

    def repr_failure(
        self,
        excinfo: ExceptionInfo[BaseException],
        style: Any = None,
    ) -> Any:
        if excinfo.errisinstance(_MypyFailure):
            return str(excinfo.value)

        return super().repr_failure(excinfo, style=style)

    def runtest(self) -> Any:
        expected = self.get_expected_result()
        passed, out = run_mypy(self.path, expected)

        if not passed:
            raise _MypyFailure(out)


class _MypyTest(File):
    def collect(self) -> Iterable[Item]:
        yield _MypyItem.from_parent(
            self,
            name=f"tests/mypy/{self.name}",
            path=self.path,
            nodeid=self.path.name,
        )


def pytest_collect_file(file_path: Path, parent: Collector):
    name = file_path.name

    if name in {"__init__.py", "conftest.py"}:
        return

    return _MypyTest.from_parent(
        parent,
        name=name,
        path=file_path,
        nodeid=name,
    )
