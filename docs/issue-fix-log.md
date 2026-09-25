# v3.2.4 issue and fix log

This log records the repository audit performed on 2026-09-24, the observed
failure, its root cause, the selected repair, and its current status.

| ID | Area | Observed failure | Root cause | Correct fix | Status |
|---|---|---|---|---|---|
| DAT-001 | Non-ISO time replacement | Component or timezone changes raised `NameError: get_pattern` | `_timeutils.py` referenced a removed regex accessor | Use the compiled regex objects already imported by the module and validate timezone inputs centrally | Fixed and tested |
| DAT-002 | ISO time replacement | `hour`, `minute`, `second`, `microsecond`, and `tzinfo` were silently ignored | The inner vectorized processor used default arguments instead of the outer API arguments | Close over the public arguments and normalize named zones, offsets, and `tzinfo` objects | Fixed and tested |
| DAT-003 | Date replacement with time | Inputs containing a time raised `NameError: cleanstr`; ISO `T` separators also failed detection | Missing import and loss of separator state | Import the compiled cleaner, isolate the date before validation, and preserve the original separator | Fixed and tested |
| DAT-004 | Formatted sequences | `sequence(..., to_format=...)` subtracted strings | Endpoints were formatted before date arithmetic | Convert endpoints to date objects first and format only generated results | Fixed and tested |
| DAT-005 | Relative weekdays/weekends | `next Friday` and repeated weekends skipped an extra week | Direction helpers added seven days twice and recurrence cursors advanced past a full period | Apply strict next/last semantics once and advance recurrence cursors from the prior occurrence | Fixed and tested |
| DAT-006 | NLP validation | Valid documented forms such as `5 days ago`, `Q2 2026`, and `middle of this year` returned `None` | The structural classifier rejected resolver-supported forms even when semantic checks passed | Retain semantic bounds, allow a semantic fallback, then continue through vocabulary validation and the resolver | Fixed and tested |
| DAT-007 | Explicit periods and anchors | Explicit years were ignored; half-year, boundary, and anchored-ago forms were unresolved | Missing resolver branches and incorrect anchoring order | Add explicit period/year, positional half, generic boundary, and anchored-ago resolution | Fixed and tested |
| DAT-008 | Week-start API | Documented numeric values `0` and `6` raised `AttributeError` | Integer lookup was attempted against a string-keyed weekday map | Normalize numeric indices with `calendar.day_name` before enforcing supported week starts | Fixed and tested |
| DAT-009 | Temporal helper names | Static analysis found missing `calendar`, `timedelta`, `date`, `datetime`, period helpers, and `parsed` | Incomplete refactor from full datetime names to aliases and unfinished helper extraction | Use consistent aliases and supply the missing scoped/nth-period helpers | Fixed; covered through public NLP tests |
| DAT-010 | Source-data package | `import dately.sources` imported nonexistent `sources.core` | A duplicate, unused data package remained from the old repository layout | Remove `sources`; runtime datasets live exclusively in `dately.files` | Fixed |
| DAT-011 | Version metadata | Runtime version said `3.2.0` on the `v3.2.4` release | Stale `_version.py` | Set and publicly export `3.2.4` | Fixed and tested |
| DAT-012 | Repository packaging | `pip install .` failed and the PyPI wheel was falsely tagged `py3-none-any` while containing CPython 3.8 Windows `.pyd` files | Build metadata was absent; prebuilt native files were treated as pure package data | Add a PEP 517 build entry, compile all seven extensions from their authoritative Cython sources, and build interpreter-specific Windows wheels | Fixed; CPython 3.8–3.14 wheels built, installed, and fully tested locally, with automated rebuilds configured |
| DAT-013 | `TimeZoner` transport | Methods returned `None`; API-key bootstrap failed parsing an undecoded Brotli response | A shared client advertised optional encodings unconditionally, always required keys, used mutable global endpoint state, and hid transport errors | Let `requests` negotiate encodings, load the temporary Netlify key source lazily, scope each key type to its owning API host, use explicit HTTPS endpoints, restore shared-client state after requests, and add request timeouts | Fixed, re-enabled, and tested without live-network dependencies |
| DAT-014 | `Holidate` transport | Valid holiday requests returned `None` | It shared the keyed client, mutated its global URL, and scrapes external HTML | Keep credentials scoped away from the holiday host, restore the previous endpoint after each request, validate missing country URLs, and cover the parser/manager with fixture-backed tests | Re-enabled with isolated request state and offline tests |
| DAT-015 | Static correctness | Repository-wide analysis reported undefined names, wildcard imports, duplicate dictionary keys, bare `except` clauses, and dead assignments/imports | Several incomplete refactors and generated alias tables had accumulated without a static-analysis gate | Repair runtime correctness findings and enforce Ruff's syntax/undefined-name checks during verification | Critical checks pass; broader style findings remain recorded technical debt |
| DAT-016 | Python 3.15 readiness | Python 3.13/3.14 report a deprecation warning when the format detector probes day/month strings without a year | CPython will change ambiguous yearless `strptime` behavior in 3.15 | Supply a deterministic leap-safe reference year during format probing, then remove it from the parsed result; add dedicated leap-day tests before enabling 3.15 | Recorded; package support is explicitly capped below 3.15 for now |

## Network-backed feature policy

`dately.TimeZoner` and `dately.Holidate` are lazy-loaded. Importing `dately` does
not fetch API keys or call third-party services. Local catalog properties load
packaged data, while explicitly network-backed methods perform bounded requests
and restore the shared client's endpoint after completion.

## Verification policy

Every fixed public behavior above has a regression test in
`tests/test_regressions.py`. Invalid semantic bounds and unknown vocabulary are
also tested so the NLP validation fallback does not turn malformed phrases into
dates.

The latest verification run uses Python 3.13 and includes:

- `python -m pytest -q`: 18 tests passed.
- `python -m ruff check . --select E9,F63,F7,F82`: passed.
- Direct syntax compilation of all 63 repository Python files: passed.
- Clean CPython 3.13 wheel and source builds: passed `twine check`.
- The wheel was installed into a fresh environment and passed all 18 tests. It
  contains seven native extensions and exactly the three runtime JSON datasets.

Distribution builds are documented in `docs/distribution-builds.md`. The build
workflow creates separate Windows x64 wheels for CPython 3.8 through 3.14 and a
source archive; binary wheels are never relabeled across Python ABIs.
