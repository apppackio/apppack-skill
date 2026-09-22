#!/usr/bin/env python3
"""Render `apppack docgen` output into a compact CLI reference for the skill.

`apppack docgen` emits ~84 Markdown files (~70KB) — one per command, each repeating
the full inherited-flag block. That is far too much to load into a skill. This
condenses it to a single file of roughly 8KB that still carries every command,
every flag, and every default.

Usage:
    just cli-docs

or manually:
    apppack docgen --directory <tmpdir>
    python3 scripts/gen_cli_reference.py <tmpdir> --output skills/apppack/references/cli.md

The output is generated; do not hand-edit it. Curated knowledge that docgen cannot
know (version history, operational advice) belongs in SKILL.md instead.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

HEADING_RE = re.compile(r"^## (apppack.*)$", re.M)
USAGE_RE = re.compile(r"```\n(apppack[^\n]*)\n```")
EXAMPLES_RE = re.compile(r"### Examples\n+```\n(.*?)```", re.S)
OWN_OPTS_RE = re.compile(r"### Options\n+```\n(.*?)```", re.S)
INHERITED_OPTS_RE = re.compile(
    r"### Options inherited from parent commands\n+```\n(.*?)```", re.S
)
# "  -a, --app-name string   app name (required)" -> short, long, type, description
FLAG_RE = re.compile(
    r"^\s*(?:-(?P<short>\w), )?--(?P<long>[\w-]+)"
    r"(?: (?P<type>\w+))?\s{2,}(?P<desc>.*)$"
)


@dataclass
class Flag:
    long: str
    short: str | None
    type: str | None
    desc: str

    def render(self) -> str:
        name = f"-{self.short}, --{self.long}" if self.short else f"--{self.long}"
        if self.type and self.type != "bool":
            name += f" <{self.type}>"

        return f"`{name}` — {self.desc}"


@dataclass
class Command:
    name: str
    short: str
    usage: str
    examples: str
    own: list[Flag] = field(default_factory=list)
    inherited: list[Flag] = field(default_factory=list)

    @property
    def parts(self) -> list[str]:
        return self.name.split()

    @property
    def group(self) -> str:
        """Top-level command group, e.g. 'ps' for 'apppack ps scale'."""
        return self.parts[1] if len(self.parts) > 1 else ""

    @property
    def depth(self) -> int:
        return len(self.parts)


def parse_flags(block: re.Match[str] | None) -> list[Flag]:
    if not block:
        return []
    flags: list[Flag] = []
    for line in block.group(1).splitlines():
        m = FLAG_RE.match(line)
        if not m or m.group("long") == "help":
            continue
        flags.append(
            Flag(
                long=m.group("long"),
                short=m.group("short"),
                type=m.group("type"),
                desc=m.group("desc").strip(),
            )
        )
    return flags


def parse_file(path: Path) -> Command | None:
    text = path.read_text()
    heading = HEADING_RE.search(text)
    if not heading:
        return None
    name = heading.group(1).strip()

    rest = text[heading.end() :].lstrip("\n")
    short = rest.split("\n", 1)[0].strip()

    usage_m = USAGE_RE.search(text)
    examples_m = EXAMPLES_RE.search(text)

    return Command(
        name=name,
        short=short,
        usage=usage_m.group(1).strip() if usage_m else name,
        examples=examples_m.group(1).strip() if examples_m else "",
        own=parse_flags(OWN_OPTS_RE.search(text)),
        inherited=parse_flags(INHERITED_OPTS_RE.search(text)),
    )


def detect_version() -> str:
    try:
        out = subprocess.run(
            ["apppack", "version"], capture_output=True, text=True, timeout=30
        )
        v = out.stdout.strip().splitlines()
        if v:
            return v[0].strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return "unknown"


def render(commands: list[Command], version: str) -> str:
    by_name = {c.name: c for c in commands}
    root = by_name.get("apppack")
    root_flags = root.own if root else []

    # A flag is "near-global" if many command groups inherit it; list where it applies
    # so readers never again assume --region is global.
    groups = sorted({c.group for c in commands if c.group})
    # Scan every depth: a group's persistent flags usually sit on its depth-2 command,
    # but some (e.g. `modify app -c`) are registered on a subcommand instead.
    inherited_map: dict[str, set[str]] = {}
    for c in commands:
        if not c.group:
            continue
        for f in c.own + c.inherited:
            inherited_map.setdefault(f.long, set()).add(c.group)

    # Only flags spanning several groups get mistaken for global. A flag on one or two
    # groups (--cpu on ps/shell) reads as local already; listing it dilutes the warning.
    GLOBAL_CONFUSION_THRESHOLD = 3
    root_names = {f.long for f in root_flags}
    scoped = {
        name: sorted(gs)
        for name, gs in inherited_map.items()
        if name not in root_names and len(gs) >= GLOBAL_CONFUSION_THRESHOLD
    }

    out: list[str] = []
    w = out.append

    w("<!-- GENERATED FILE — DO NOT EDIT.")
    w("     Regenerate with `just cli-docs`.")
    w(f"     Source: apppack docgen ({version}). -->")
    w("")
    w("# AppPack CLI reference")
    w("")
    w(
        f"Every command and flag in the AppPack CLI, generated from `apppack docgen` "
        f"({version}). Operational guidance and version history that docgen cannot know "
        f"live in `SKILL.md`, not here."
    )
    w("")
    w(
        "**A shown default does not mean a flag is optional.** cobra allows a flag to have a "
        "default *and* be required, and docgen cannot express the difference — `ps resize` "
        "shows `--cpu` defaulting to 0.5 yet rejects the command if you omit it. Where "
        "`SKILL.md` marks a flag required, believe it over the default shown here."
    )
    w("")

    w("## Truly global flags")
    w("")
    w("Registered on the root command, valid everywhere:")
    w("")
    for f in sorted(root_flags, key=lambda f: f.long):
        w(f"- {f.render()}")
    w("- `-h, --help` — help for any command")
    w("")

    if scoped:
        w("## Scoped flags — NOT global")
        w("")
        w(
            "These look global but are registered per command group. Using one outside "
            "its group fails:"
        )
        w("")
        w("| Flag | Valid on |")
        w("|---|---|")
        for name in sorted(scoped):
            where = ", ".join(f"`{g}`" for g in scoped[name])
            w(f"| `--{name}` | {where} |")
        w("")

    w("## Commands")
    w("")

    for group in groups:
        members = sorted(
            (c for c in commands if c.group == group), key=lambda c: c.name
        )
        if not members:
            continue
        head = by_name.get(f"apppack {group}")
        w(f"### {group}")
        w("")
        if head and head.short:
            w(f"{head.short}")
            w("")

        for c in members:
            w(f"```")
            w(c.usage)
            w("```")
            w("")
            if c.short and c is not head:
                w(f"{c.short}")
                w("")
            if c.own:
                for f in c.own:
                    w(f"- {f.render()}")
                w("")
            if c.examples:
                w("Example:")
                w("")
                w("```bash")
                for line in c.examples.splitlines():
                    w(line)
                w("```")
                w("")

    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("docgen_dir", type=Path, help="directory containing docgen output")
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument(
        "--version",
        default=None,
        help="CLI version string to record (default: ask the apppack binary)",
    )
    args = ap.parse_args()

    files = sorted(args.docgen_dir.glob("apppack*.md"))
    if not files:
        print(f"error: no docgen output in {args.docgen_dir}", file=sys.stderr)
        return 1

    commands = [c for c in (parse_file(f) for f in files) if c]
    if not commands:
        print("error: parsed no commands — has docgen output changed shape?", file=sys.stderr)
        return 1

    version = args.version or detect_version()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(commands, version))

    size = args.output.stat().st_size
    print(f"wrote {args.output} — {len(commands)} commands, {size:,} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
