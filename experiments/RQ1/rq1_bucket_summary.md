# RQ1 signature-form bucketing (follow-up for Section III-A-2)

- Data: `/home/lisy/Projects/RepFuzz/data/library_qwen_2.5_7` (read-only; no experiment was re-run).
- Buckets are mutually exclusive: `poskw` = contains positional-or-keyword
  parameters; `varargs` = pure `*args`/`**kwargs` (no pos-or-kw);
  `keyword_only`; `no_args`; `c_ext` = C-extension APIs with no stored
  `.py` source (signature only in `.pyi` stubs; torch/numpy dominate);
  `unparsed` = public APIs whose parse failed. Empty buckets (notably
  `unknown`, 0 in this run) are omitted from the table.
- `#Public` is the bucket's API count and equals `#Parsed` where both
  are shown; parse failures appear as `unparsed` (#Public only), so the
  column sums to the full public API list.
- `gen failure rate = 1 - #Gen / #Parsed` (two decimals), strictly
  derived from the two columns. `no_args` and `unparsed` report n/a for
  #Parsed/#Gen/rate: generation skips zero-parameter APIs by design, and
  parse failures store no source or call. Classification is binary
  (call present/absent).
- The `total` row's #Public (3859) counts every public API; its #Parsed
  (3846) counts successful parses; the difference is the `unparsed` row.

| bucket | #Public | #Parsed | #Gen | gen failure rate |
|---|---:|---:|---:|---:|
| poskw | 2758 | 2758 | 1878 | 31.91% |
| varargs | 83 | 83 | 11 | 86.75% |
| keyword_only | 3 | 3 | 2 | 33.33% |
| no_args | 330 | n/a | n/a | n/a |
| c_ext | 672 | 672 | 526 | 21.73% |
| unparsed | 13 | n/a | n/a | n/a |
|---|---|---|---|---|
| total | 3859 | 3846 | 2417 | 37.16% |
