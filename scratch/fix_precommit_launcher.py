from pathlib import Path

root = Path(r"C:\Users\rkhol\OneDrive\Documents\Anthropic\Introduction to MCP")
py = root / ".git" / "hooks" / "pre-commit.py"
# Prefer Git Bash path form
py_bash = "/cygdrive/c/Users/rkhol/OneDrive/Documents/Anthropic/Introduction to MCP/.git/hooks/pre-commit.py"
launcher = (
    b'#!/bin/sh\n'
    b'export PYTHONIOENCODING=utf-8\n'
    + f'exec "/cygdrive/c/Python314/python.exe" "{py_bash}" "$@"\n'.encode("ascii")
)
(root / ".git" / "hooks" / "pre-commit").write_bytes(launcher)
print((root / ".git" / "hooks" / "pre-commit").read_text(encoding="ascii"))
