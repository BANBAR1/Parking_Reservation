import pkgutil
import subprocess
import sys

import pytest

import parking_reservation

MODULES = sorted(
    module.name
    for module in pkgutil.walk_packages(parking_reservation.__path__, prefix="parking_reservation.")
)


@pytest.mark.parametrize("module", MODULES)
def test_module_imports_on_its_own(module):
    result = subprocess.run(
        [sys.executable, "-c", f"import {module}"], capture_output=True, text=True
    )

    assert result.returncode == 0, result.stderr
