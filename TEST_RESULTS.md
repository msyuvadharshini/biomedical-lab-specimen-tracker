# Standalone Verification Results

**Case study:** Biomedical-Laboratory-Specimen-Tracker  
**Verification date:** 2026-10-19  
**Platform tested:** Linux  
**Compiler:** `gcc (Debian 14.2.0-19) 14.2.0`  
**Python:** 3.13.16 (optional standard-library test runner)

## Observed results

| Check | Result |
|---|---|
| C11 build with `-Wall -Wextra -Wpedantic -Werror` | PASS; no diagnostics |
| This case study's integration suite | **51/51 test methods passed** |
| Same suite with UndefinedBehaviorSanitizer | **51/51 passed** |
| GCC `-fanalyzer -c` compilation with strict warnings | PASS; no diagnostics |
| Actual clean-start C demonstration | PASS; matches the included sample output |
| C-source comparison with the combined Drive ZIP | Identical, byte for byte |

The repository is independent: `main.c` is at its root, and the optional test runner compiles that file. It does not read or test the other case study. Several tests have additional subcases; the counts above count methods, not each subcase.

## Repeat the normal checks

From this repository's root:

```bash
python3 tests/run_tests.py -v
```

On Windows, `py tests/run_tests.py -v` is an alternative if Python and GCC are installed. Python is only needed for optional automated tests, not for running the C application.

## Repeat the sanitizer checks (Linux shell)

```bash
CFLAGS='-std=c11 -Wall -Wextra -Wpedantic -Werror -fsanitize=undefined -fno-sanitize-recover=all -g' python3 tests/run_tests.py -v
```

Tests compile in temporary folders and keep runtime data isolated from your active project records.

## Evidence

- [Named test cases and expected checks](TEST_CASES.md)
- [Actual normal test log](tests/LAST_TEST_RUN.txt)
- [Actual sanitizer test log](tests/UBSAN_TEST_RUN.txt)
- [Compilation summary](COMPILE_TEST.txt)
- [Actual demonstration output](SAMPLE_OUTPUT.md)

## Scope and limitations

Checks cover registration, search, exact menu/ID input, field limits, long lines, real Gregorian dates, CRLF, EOF, persistence, duplicates, invalid/corrupt/oversized/binary-null saved files, blocked saves, rollback, backups and this case study's specific rules. Malformed-file tests verify that original bytes remain unchanged. The tests do not simulate every possible disk or operating-system failure.

No Windows execution, clinical validation, real patient/equipment operation, concurrent-writer testing, exhaustive input testing or destructive power-loss testing was performed. The GitHub workflow has not been run remotely from this conversation.

Passing tests and compiler analysis do not prove the absence of all defects or suitability for real healthcare use. Use fictitious records only.
