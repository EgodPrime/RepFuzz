#!/usr/bin/env python3
"""RQ1 follow-up: bucket parsed APIs by signature form.

Answers the reviewer's request (Section III-A-2 / RQ1) without re-running any
experiment. It reads the existing RQ1 SQLite results and emits ONE table:

    | bucket | #Public | #Parsed | #Gen | gen failure rate |

Buckets (mutually exclusive; a parsed API lands in exactly one):
    poskw        signature contains >=1 positional-or-keyword parameter
    varargs      contains *args/**kwargs but no positional-or-keyword parameter
    keyword_only only keyword-only parameters
    no_args      no parameters at all
    c_ext        stored api.source is empty (C-extension APIs, e.g. torch/numpy;
                 the signature only exists in .pyi stubs)
    unknown      source present but ast could not recover the signature
                 (defensive; 0 in the RQ1 run, so the row is omitted)
    unparsed     public APIs with no api row (parse failed, so no stored source
                 to bucket by; only these carry #Public > #Parsed)

Column semantics:
    #Public  -- the bucket's API count; equals #Parsed wherever #Parsed is
                shown (bucketing requires a successful parse). Parse failures
                appear as the `unparsed` row (#Public only), so the column
                sums to the full public API list.
    #Parsed  -- APIs with an api row (a successful parse); reported as n/a
              for `no_args` and the `unparsed` row.
    #Gen     -- APIs with an api_call row (generation succeeded); n/a for
              `no_args` and the `unparsed` row.
    gen failure rate = 1 - #Gen / #Parsed, strictly derived from the two
                columns shown (two decimal places). Reported as n/a for
                `no_args` and `unparsed`: the generation phase skips
                zero-parameter APIs by design, and parse failures store
                no call; the total row covers all parsed APIs.

Signature flags are extracted with ast from the STORED api.source, not from
the locally installed library, so the classification does not depend on the
pip environment. Failure classification is binary (call present / absent);
per-attempt failure causes are logged during the run, not stored in the DB.

Usage:
    python experiments/RQ1/rq1_bucket_analyze.py
    python experiments/RQ1/rq1_bucket_analyze.py \
        --data-dir data/library_qwen_2.5_7 --out-dir experiments/RQ1

Outputs (in --out-dir):
    rq1_bucket_summary.md    markdown: intro notes + the single table
    rq1_bucket_summary.csv   the same table as CSV
"""

from __future__ import annotations

import argparse
import ast
import csv
import sqlite3
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DATA_DIR = PROJECT_DIR / "data" / "library_qwen_2.5_7"
DEFAULT_OUT_DIR = PROJECT_DIR / "experiments" / "RQ1"

BUCKETS = ["poskw", "varargs", "keyword_only", "no_args", "c_ext", "unknown"]

LFS_POINTER_PREFIX = b"version https://git-lfs"


@dataclass
class ApiRow:
    lib: str
    full_name: str
    bucket: str
    has_call: bool
    n_params: int


@dataclass
class LibStat:
    lib: str
    n_public: int
    n_parsed: int


def is_lfs_pointer(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            return f.read(len(LFS_POINTER_PREFIX)) == LFS_POINTER_PREFIX
    except OSError:
        return False


def classify_signature(source: str) -> tuple[str, dict | None]:
    """Parse stored function source with ast; return (status, flags).

    status:
      "ok"        -- flags are valid;
      "no_source" -- source empty (C-extension API) -> c_ext bucket;
      "unparsed"  -- ast could not recover the signature -> unknown bucket.
    flags keys: poskw, varargs, kwonly, no_args (booleans).
    """
    if not source or not source.strip():
        return "no_source", None
    # inspect.getsource on nested/class methods yields indented source;
    # textwrap.dedent strips only the common leading whitespace.
    try:
        tree = ast.parse(textwrap.dedent(source))
    except SyntaxError:
        return "unparsed", None
    func = next(
        (
            n
            for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ),
        None,
    )
    if func is None:
        return "unparsed", None
    args = func.args
    flags = {
        "poskw": bool(args.posonlyargs or args.args),
        "varargs": args.vararg is not None or args.kwarg is not None,
        "kwonly": bool(args.kwonlyargs),
        "no_args": not (
            args.posonlyargs or args.args or args.vararg or args.kwarg or args.kwonlyargs
        ),
    }
    return "ok", flags


def exclusive_bucket(status: str, flags: dict | None) -> str:
    if status == "no_source":
        return "c_ext"
    if status != "ok" or flags is None:
        return "unknown"
    if flags["poskw"]:
        return "poskw"
    if flags["varargs"]:
        return "varargs"
    if flags["kwonly"]:
        return "keyword_only"
    if flags["no_args"]:
        return "no_args"
    return "unknown"  # unreachable


def load_library(db_path: Path) -> tuple[list[ApiRow], LibStat]:
    lib = db_path.stem
    if is_lfs_pointer(db_path):
        raise RuntimeError(
            f"{db_path} is a Git LFS pointer; run `git lfs pull` first."
        )
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        cur = conn.cursor()
        n_public = cur.execute("SELECT COUNT(*) FROM public_api").fetchone()[0]
        gen_names = {r[0] for r in cur.execute("SELECT full_name FROM api_call")}
        rows: list[ApiRow] = []
        for full_name, source, n_norm, n_kw in cur.execute(
            "SELECT full_name, source, num_normal_arg, num_kwonly_arg FROM api"
        ):
            status, flags = classify_signature(source or "")
            rows.append(
                ApiRow(
                    lib=lib,
                    full_name=full_name,
                    bucket=exclusive_bucket(status, flags),
                    has_call=full_name in gen_names,
                    n_params=(n_norm or 0) + (n_kw or 0),
                )
            )
        return rows, LibStat(lib=lib, n_public=n_public, n_parsed=len(rows))
    finally:
        conn.close()


def fmt_rate(rate: float | None) -> str:
    return "n/a" if rate is None else f"{rate * 100:.2f}%"


def fmt_n(value: int | None) -> str:
    return "n/a" if value is None else str(value)


def build_summary(rows: list[ApiRow], total_public: int) -> list[dict]:
    """Build the single summary table: bucket rows + unparsed + total."""
    out: list[dict] = []
    for bucket in BUCKETS:
        group = [r for r in rows if r.bucket == bucket]
        n_parsed = len(group)
        n_gen = sum(1 for r in group if r.has_call)
        if n_parsed:
            out.append(
                {
                    "bucket": bucket,
                    # bucketing requires a successful parse, so a bucket's
                    # public count equals its parsed count; the gap lives
                    # in the `unparsed` row.
                    "n_public": n_parsed,
                    # `no_args`: the generation phase skips zero-parameter
                    # APIs by design, so #Parsed/#Gen/rate report n/a
                    # instead of a misleading 100% failure.
                    "n_parsed": None if bucket == "no_args" else n_parsed,
                    "n_gen": None if bucket == "no_args" else n_gen,
                    # strict column consistency: rate = 1 - #Gen / #Parsed.
                    "gen_failure_rate": (
                        None if bucket == "no_args" else 1 - n_gen / n_parsed
                    ),
                }
            )
        # empty buckets (e.g. `unknown` in the RQ1 run) are omitted; they
        # contribute 0 to every column, so the sums stay consistent.
    out.append(
        {
            "bucket": "unparsed",
            "n_public": total_public - len(rows),
            # only #Public is known for parse failures: no stored source to
            # bucket by, no generated call.
            "n_parsed": None,
            "n_gen": None,
            "gen_failure_rate": None,
        }
    )
    # total row: rate = 1 - #Gen / #Parsed over ALL parsed APIs (the no_args
    # row alone reports n/a, since the gen phase never ran on those APIs).
    n_parsed = len(rows)
    n_gen = sum(1 for r in rows if r.has_call)
    out.append(
        {
            "bucket": "total",
            "n_public": total_public,
            "n_parsed": n_parsed,
            "n_gen": n_gen,
            "gen_failure_rate": (1 - n_gen / n_parsed if n_parsed else None),
        }
    )
    return out


def write_outputs(out_dir: Path, data_dir: Path, summary: list[dict]) -> None:
    # CSV: identical table
    csv_path = out_dir / "rq1_bucket_summary.csv"
    try:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(
                f,
                fieldnames=[
                    "bucket",
                    "n_public",
                    "n_parsed",
                    "n_gen",
                    "gen_failure_rate",
                ],
            )
            w.writeheader()
            for row in summary:
                out = dict(row)
                for key in ("n_public", "n_parsed", "n_gen"):
                    if out[key] is None:
                        out[key] = ""
                rate = out.pop("gen_failure_rate")
                out["gen_failure_rate"] = "" if rate is None else f"{rate:.4f}"
                w.writerow(out)
    except OSError as e:
        print(f"Failed to write {csv_path}: {e}", file=sys.stderr)

    # Markdown: intro notes + the single table
    lines = [
        "# RQ1 signature-form bucketing (follow-up for Section III-A-2)",
        "",
        f"- Data: `{data_dir}` (read-only; no experiment was re-run).",
        "- Buckets are mutually exclusive: `poskw` = contains positional-or-keyword",
        "  parameters; `varargs` = pure `*args`/`**kwargs` (no pos-or-kw);",
        "  `keyword_only`; `no_args`; `c_ext` = C-extension APIs with no stored",
        "  `.py` source (signature only in `.pyi` stubs; torch/numpy dominate);",
        "  `unparsed` = public APIs whose parse failed. Empty buckets (notably",
        "  `unknown`, 0 in this run) are omitted from the table.",
        "- `#Public` is the bucket's API count and equals `#Parsed` where both",
        "  are shown; parse failures appear as `unparsed` (#Public only), so the",
        "  column sums to the full public API list.",
        "- `gen failure rate = 1 - #Gen / #Parsed` (two decimals), strictly",
        "  derived from the two columns. `no_args` and `unparsed` report n/a for",
        "  #Parsed/#Gen/rate: generation skips zero-parameter APIs by design, and",
        "  parse failures store no source or call. Classification is binary",
        "  (call present/absent).",
        "- The `total` row's #Public (3859) counts every public API; its #Parsed",
        "  (3846) counts successful parses; the difference is the `unparsed` row.",
        "",
        "| bucket | #Public | #Parsed | #Gen | gen failure rate |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in summary:
        if row["bucket"] == "total":
            lines.append("|---|---|---|---|---|")
        lines.append(
            f"| {row['bucket']} | {fmt_n(row['n_public'])} "
            f"| {fmt_n(row['n_parsed'])} | {fmt_n(row['n_gen'])} "
            f"| {fmt_rate(row['gen_failure_rate'])} |"
        )
    lines.append("")
    md_path = out_dir / "rq1_bucket_summary.md"
    try:
        md_path.write_text("\n".join(lines), encoding="utf-8")
    except OSError as e:
        print(f"Failed to write {md_path}: {e}", file=sys.stderr)
        return
    print(f"wrote {csv_path}")
    print(f"wrote {md_path}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Bucket RQ1 parsed APIs by signature form and emit one table"
    )
    ap.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = ap.parse_args()

    data_dir: Path = args.data_dir
    if not data_dir.is_absolute():
        data_dir = PROJECT_DIR / data_dir
    out_dir: Path = args.out_dir
    if not out_dir.is_absolute():
        out_dir = PROJECT_DIR / out_dir

    db_paths = sorted(data_dir.glob("*.db"))
    if not db_paths:
        print(f"No .db files under {data_dir}", file=sys.stderr)
        return 1

    all_rows: list[ApiRow] = []
    total_public = 0
    for db_path in db_paths:
        rows, stat = load_library(db_path)
        all_rows.extend(rows)
        total_public += stat.n_public
        print(
            f"{stat.lib}: public={stat.n_public} parsed={stat.n_parsed}"
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    write_outputs(out_dir, data_dir, build_summary(all_rows, total_public))
    return 0


if __name__ == "__main__":
    sys.exit(main())
