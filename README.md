# Biomedical Laboratory Specimen Tracking System

## Case study

A simplified laboratory coordinator needs a unique ID for each specimen and a consistent way to track its processing stage. This C console program demonstrates those record-keeping tasks using fictitious patient codes, without collecting names or clinical results.

## Aim

Use core C programming to register, search, persist and summarise specimen records, while checking a stated processing workflow.

## Features

- Register a specimen ID, fictitious patient code, sample type and collection date.
- Start at `Collected`, list records and search by unique specimen ID.
- Update only through the allowed teaching transitions.
- Count specimens in Collected, InProcess, Completed and Rejected stages.
- Reject duplicate IDs, invalid dates, unsupported transitions and bad input.
- Save/reload records with checked temporary-file/backup replacement.
- Refuse invalid/corrupt/oversized saved files without rewriting them.

## C concepts

Structures, arrays, strings, functions, pointer parameters, conditions, `switch`, loops, linear search, counters, bounded parsing and text-file handling. These are concept mappings, not an official Unit 1–5 mapping.

## Files

`main.c`, `README.md`, `ALGORITHM.md`, `TEST_CASES.md` and `COMPILE_TEST.txt` preserve the reference layout. `CODE_EXPLANATION.md`, `SAMPLE_OUTPUT.md` and fictitious `examples/` add study and demonstration material.

Runtime files are `specimen_records.txt`, `specimen_records.txt.tmp`, and `specimen_records.txt.bak`. They are excluded by the repository's `.gitignore`.

## Compile and run

From this project folder:

```bash
gcc main.c -std=c11 -Wall -Wextra -Wpedantic -o specimen_tracker
./specimen_tracker
```

Windows with GCC/MinGW:

```powershell
gcc main.c -std=c11 -Wall -Wextra -Wpedantic -o specimen_tracker.exe
.\specimen_tracker.exe
```

Requires a C11-capable compiler, not legacy Turbo C. Linux GCC execution was verified; Windows commands were not executed here.

## Menu

1. Register specimen
2. List specimens
3. Search by ID
4. Update processing status
5. Status summary
6. Exit

## Data model and input rules

| Field | Limit / rule |
|---|---|
| Specimen ID | 1–23 characters; letters/digits/`-`/`_`; unique and case-sensitive |
| Fictitious patient code | 1–23 characters, using the same ID characters; may repeat on different specimens |
| Sample type | 1–39 printable characters, with spaces inside allowed |
| Collection date | Real, fixed-width `YYYY-MM-DD`, years 2000–9999 |
| Status | `Collected`, `InProcess`, `Completed` or `Rejected` |

Capacity: 500 specimens. Console-input whitespace at the ends is trimmed. Empty fields, `|` and control characters are rejected. Long sample types are shortened only in the list view; Search displays the full value.

### File format

```text
specimenID|patientCode|sampleType|collectionDate|status
SP1001|PT042|Blood|2026-10-18|Collected
```

## Allowed workflow — classroom model only

| Current stage | Allowed next stage |
|---|---|
| Collected | InProcess or Rejected |
| InProcess | Completed or Rejected |
| Completed | None; final |
| Rejected | None; final |

During menu option 4, choose `1` for InProcess, `2` for Completed, or `3` for Rejected. A direct Collected-to-Completed update is rejected, as are repeated or final-stage changes. These rules illustrate validation; they are not a validated real-laboratory procedure.

## Try a demonstration safely

Use a separate copied project folder with no runtime data or backup. Follow `SAMPLE_OUTPUT.md`, or on a compatible shell run `./specimen_tracker < examples/demo_input.txt` after compilation.

For a report-only demo, while closed and in a separate clean demo folder, copy `examples/specimen_records.demo.txt` to `specimen_records.txt`, run the program and choose option 5. It contains one fictitious record in each status. Do not also run the clean-start registration script on seeded data.

## Storage and recovery

The file is validated completely at startup; a bad row, duplicate ID or too many rows stops the program without editing it. Each change is written and checked in a temporary file before the old main file is backed up and replaced. Failed updates restore the previous in-memory status. A missing main file with an existing `.bak` triggers a manual recovery warning.

Run only one copy per folder; do not externally edit a running program's data. Backups are not encrypted. The rename sequence is not an atomic/power-failure-safe database transaction.

## Privacy and limitations

Use **entirely fictitious** patient codes and records. Codes do not provide authentication, encryption, anonymity guarantees or compliance. This prototype does not verify identity, specimen suitability, diagnostic results or clinical protocols, and it keeps no complete change/audit history.


## Standalone repository

This repository contains **only this case study**. Its C source, examples, documentation and optional tests do not depend on the other case study or on a parent folder.

Suggested repository name: `biomedical-laboratory-specimen-tracker`.

### Supporting documents

- [Case-study report](COURSEWORK_REPORT.md)
- [Algorithm and flowchart](ALGORITHM.md)
- [Code explanation](CODE_EXPLANATION.md)
- [Sample input and actual output](SAMPLE_OUTPUT.md)
- [Test cases](TEST_CASES.md)
- [Verification results](TEST_RESULTS.md)
- [Compilation summary](COMPILE_TEST.txt)
- [Viva preparation](VIVA_GUIDE.md)
- [Upload instructions for this repository](GITHUB_UPLOAD_GUIDE.md)

### Verification and optional tests

Standalone local verification on **19 October 2026**: **51/51 integration tests passed** with strict GCC warnings; the same 51 tests also passed with UndefinedBehaviorSanitizer. See the verification report for scope and actual logs.

To repeat this project's checks from this repository's root:

```bash
python3 tests/run_tests.py -v
```

On Windows, `py tests/run_tests.py -v` is an alternative when Python and GCC are installed. Python is only for optional tests; it is not needed to run `main.c`. Tests use temporary folders rather than active project records.

A GitHub Actions workflow is included. It runs only this case study's tests after publication; no remote workflow run is claimed here.
