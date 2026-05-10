#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_PREFIXES = (
    "pages/templates/base/",
    "pages/templates/partials/",
    "pages/templates/widgets/",
    "pages/templates/email/",
    "organization/templates/organization/partials/",
    "facility/templates/widgets/",
    "faction/templates/widgets/",
)
ALLOWED_EXACT = {
    "pages/templates/admin/base_site.html",
    "pages/templates/admin/change_form.html",
}
ALLOWED_EXTENDS = (
    "base/layout.html",
    "base/list.html",
    "base/form.html",
    "base/show.html",
    "base/manage.html",
    "base/dashboard.html",
    "base/confirm_delete.html",
    "admin/base.html",
    "admin/change_form.html",
)
FORBIDDEN_PATTERNS = {
    "bodyHeader": "legacy bodyHeader layout is not allowed",
    "onclick=": "inline event handlers are not allowed",
    "data-toggle=": "Bootstrap 4 data-toggle is not allowed",
    "style=": "inline styles are not allowed",
    'href="#"': "placeholder links are not allowed",
    "href='#'": "placeholder links are not allowed",
}
ALLOWED_PATTERN_PATHS = {
    "$(": {
        "pages/templates/partials/datatable.html",
    },
    ".DataTable(": {
        "pages/templates/partials/datatable.html",
    },
}


def should_skip(path):
    rel = path.relative_to(ROOT).as_posix()
    return (
        rel in ALLOWED_EXACT
        or rel.startswith(ALLOWED_PREFIXES)
        or rel.startswith("venv/")
        or rel.startswith(".venv/")
        or rel.startswith("node_modules/")
        or rel.startswith("playwright-report/")
        or rel.startswith("test-results/")
        or "/venv/" in rel
        or "/.venv/" in rel
        or "/node_modules/" in rel
    )


def extract_extends(contents):
    marker = "{% extends"
    if marker not in contents:
        return None
    line = next(line for line in contents.splitlines() if marker in line)
    quote = '"' if '"' in line else "'"
    parts = line.split(quote)
    return parts[1] if len(parts) > 2 else ""


def main():
    failures = []
    for path in ROOT.rglob("*.html"):
        rel = path.relative_to(ROOT).as_posix()
        if should_skip(path):
            continue
        contents = path.read_text(encoding="utf-8")
        if "<!DOCTYPE" in contents.upper():
            failures.append(f"{rel}: raw document shell is not allowed")
            continue
        parent = extract_extends(contents)
        if not parent:
            failures.append(f"{rel}: missing shared template inheritance")
            continue
        if parent not in ALLOWED_EXTENDS:
            failures.append(f"{rel}: extends unsupported shell {parent!r}")
        if parent == "base/show.html" and "{% block cards" in contents:
            failures.append(f"{rel}: base/show.html pages must use card_body blocks")
        for pattern, message in FORBIDDEN_PATTERNS.items():
            if pattern in contents:
                failures.append(f"{rel}: {message}")
        for pattern, allowed_paths in ALLOWED_PATTERN_PATHS.items():
            if pattern in contents and rel not in allowed_paths:
                failures.append(f"{rel}: disallowed template script pattern {pattern!r}")

    if failures:
        print("Template shell audit failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Template shell audit passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
