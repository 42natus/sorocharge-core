#!/usr/bin/env python3
"""Generates docs/WAVE<N>_BACKLOG.md from docs/WAVE<N>_BACKLOG.json.

This file is generated, not hand-maintained. Re-run after any edit to the
JSON:

    python3 scripts/render_wave_backlog_md.py docs/WAVE3_BACKLOG.json
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def render(items: list[dict]) -> str:
    for it in items:
        it.setdefault("repo", "sorocharge-core")  # Wave 2's format predates multi-repo
    tally = Counter(it["complexity"] for it in items)
    points = sum(it["points"] for it in items)
    by_area = Counter(it["area"] for it in items)
    by_repo = Counter(it["repo"] for it in items)
    complexities = [c for c in ["high", "medium", "low", "trivial"] if c in tally]
    points_per = {"high": 200, "medium": 150, "low": 100, "trivial": 100}

    lines = []
    lines.append("<!-- GENERATED FILE — do not hand-edit.")
    lines.append("     Source of truth is the matching docs/WAVE<N>_BACKLOG.json.")
    lines.append("     Regenerate with: python3 scripts/render_wave_backlog_md.py <path-to-json> -->")
    lines.append("")
    lines.append("# Wave backlog")
    lines.append("")
    tally_str = ", ".join(f"{tally[c]} {c} ({points_per[c]} pts each)" for c in complexities)
    lines.append(f"**{len(items)} issues, {points} points** — {tally_str}.")
    lines.append("")
    lines.append("By repo: " + ", ".join(f"`{r}` ({n})" for r, n in sorted(by_repo.items())))
    lines.append("")
    lines.append("By area: " + ", ".join(f"`{a}` ({n})" for a, n in sorted(by_area.items())))
    lines.append("")
    lines.append(
        "Every item below cites a specific file and gap found by reading the "
        "repositories during this wave's survey, not a generic roadmap item. "
        "Complexity labels were assigned to hit an exact point quota per "
        "explicit maintainer instruction — they do not all correspond to "
        "real relative effort size."
    )
    lines.append("")

    labels = {"high": "High — 200 points", "medium": "Medium — 150 points", "low": "Low — 100 points", "trivial": "Trivial — 100 points"}
    for complexity in complexities:
        group = [it for it in items if it["complexity"] == complexity]
        lines.append(f"## {labels[complexity]} ({len(group)})")
        lines.append("")
        for it in group:
            gfi = " `good first issue`" if it["good_first_issue"] else ""
            lines.append(f"### {it['title']}")
            lines.append("")
            lines.append(f"`repo:{it['repo']}` `area:{it['area']}`{gfi}")
            lines.append("")
            lines.append(f"**Description.** {it['description']}")
            lines.append("")
            lines.append(f"**Why.** {it['why']}")
            lines.append("")
            lines.append("**Acceptance criteria.**")
            for c in it["criteria"]:
                lines.append(f"- [ ] {c}")
            lines.append("")
            lines.append("**Guidance.**")
            for g in it["guidance"]:
                lines.append(f"- {g}")
            if it["entry_point"]:
                lines.append("")
                lines.append(f"**Entry point.** `{it['entry_point']}`")
            lines.append("")
    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: render_wave_backlog_md.py <path-to-json>", file=sys.stderr)
        return 1
    json_path = Path(sys.argv[1])
    md_path = json_path.with_suffix(".md")
    items = json.loads(json_path.read_text())
    md_path.write_text(render(items))
    print(f"wrote {md_path} from {len(items)} issues in {json_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
