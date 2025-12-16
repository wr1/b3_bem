import subprocess
import pytest
from pathlib import Path


def test_ex1():
    """Test running ex1.py example."""
    ex1_path = Path(__file__).parent.parent / "examples" / "ex1.py"
    if not ex1_path.exists():
        pytest.skip("ex1.py not found")
    result = subprocess.run(["python", str(ex1_path)], capture_output=True, text=True)
    assert result.returncode == 0, f"ex1.py failed: {result.stderr}"


def test_ex2():
    """Test running ex2.py example."""
    ex2_path = Path(__file__).parent.parent / "examples" / "ex2.py"
    if not ex2_path.exists():
        pytest.skip("ex2.py not found")
    result = subprocess.run(["python", str(ex2_path)], capture_output=True, text=True)
    assert result.returncode == 0, f"ex2.py failed: {result.stderr}"
