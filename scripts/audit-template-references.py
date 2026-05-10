#!/usr/bin/env python3
"""Verify hard-coded Django template references exist in this workspace."""

import ast
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "playwright-report",
    "test-results",
    "__pycache__",
}
IGNORED_PREFIXES = ("admin/", "django_tables2/")
IGNORED_EXACT = {"", "base/show.html"}


def skipped(path):
    return bool(SKIP_PARTS.intersection(path.parts))


def template_inventory():
    templates = set()
    for path in ROOT.rglob("*.html"):
        if skipped(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        if "/templates/" in rel:
            templates.add(rel.split("/templates/", 1)[1])
        elif rel.startswith("templates/"):
            templates.add(rel.removeprefix("templates/"))
    return templates


def literal_string(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def iter_template_refs():
    for path in ROOT.rglob("*.py"):
        if skipped(path):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    target_name = None
                    if isinstance(target, ast.Name):
                        target_name = target.id
                    elif isinstance(target, ast.Attribute):
                        target_name = target.attr
                    if target_name == "template_name":
                        value = literal_string(node.value)
                        if value is not None:
                            yield path, node.lineno, value
            elif isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "render":
                    if len(node.args) >= 2:
                        value = literal_string(node.args[1])
                        if value is not None:
                            yield path, node.lineno, value
                elif isinstance(func, ast.Attribute) and func.attr == "as_view":
                    for keyword in node.keywords:
                        if keyword.arg == "template_name":
                            value = literal_string(keyword.value)
                            if value is not None:
                                yield path, node.lineno, value


def ignored(template):
    return template in IGNORED_EXACT or template.startswith(IGNORED_PREFIXES)


def main():
    templates = template_inventory()
    failures = []
    for path, line, template in iter_template_refs():
        if ignored(template):
            continue
        if template not in templates:
            rel = path.relative_to(ROOT).as_posix()
            failures.append(f"{rel}:{line}: {template}")

    if failures:
        print("Template reference audit failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Template reference audit passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
