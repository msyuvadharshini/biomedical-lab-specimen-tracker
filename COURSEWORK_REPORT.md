# Case Study — Biomedical Laboratory Specimen Tracker

**Submission:** One independent C11 console application. Add student details only if your teacher requires them; avoid unnecessary personal information in a public repository.

## Aim

Apply introductory C programming concepts to a small real-life biomedical record-keeping problem using fictitious data.

## Problem statement

A coordinator in a simplified laboratory needs a unique ID for each specimen and a consistent way to follow its processing stage, without storing patient names or clinical results.

## Objectives

1. Register a unique specimen ID, fictitious patient code, sample type and collection date.
2. Start each new specimen at Collected.
3. List records and find a specimen by ID.
4. Permit only the stated processing-stage transitions.
5. Summarise the number of specimens in each stage.
6. Reject invalid inputs and preserve fictitious records between runs.

## Proposed solution

An array of `Specimen` structures is loaded from a local text file and completely validated before the menu permits editing. Separate functions perform registration, listing, ID search, validation, case-specific operations and checked saving. Capacity is 500 records.

## Data model

| Field | Rule |
|---|---|
| Specimen ID | 1–23 ID characters; unique and case-sensitive |
| Fictitious patient code | 1–23 ID characters; may repeat on different specimens |
| Sample type | 1–39 printable characters |
| Collection date | Real YYYY-MM-DD date |
| Status | Collected, InProcess, Completed or Rejected |

ID characters are letters, digits, hyphens and underscores. Console-input whitespace at the ends is trimmed; empty fields, the separator `|` and control characters are refused. Dates use exactly `YYYY-MM-DD`, years 2000–9999, with Gregorian leap-year checks.

## Main case-study logic

The deliberately simplified classroom workflow is:

- `Collected -> InProcess` or `Collected -> Rejected`.
- `InProcess -> Completed` or `InProcess -> Rejected`.
- Completed and Rejected are final.

A direct Collected-to-Completed change, repeated stage assignment or change to a final stage is refused. These are teaching rules, not a universal laboratory protocol. A counter array produces the per-stage summary.

## C concept mapping

| Concept | Use |
|---|---|
| Variables, constants and input/output | Menu choices, field buffers, `#define`, console/file output |
| Conditions and `switch` | Menu selection and case-study validation rules |
| Loops | Repeating the menu, traversing records and counting |
| Arrays and strings | Fixed-size records and text fields |
| Structures | Grouping related data into a record |
| User-defined functions | Separating input, search, reports and saving |
| Pointer parameters | Updating `count` through `int *count`; using `FILE *` streams |
| File handling | Loading, bounded parsing, checked writing, closing, backup and rename |

The college's Unit 1–5 syllabus was not supplied. This is a concept mapping, not an invented official unit-number mapping. Confirm any required syllabus alignment with your teacher.

## Storage and error handling

New registrations become active only after saving succeeds. Updates keep an old copy so memory can be restored if saving fails. The program writes/checks/closes a temporary file before backing up the previous main file and installing the new one. Invalid/duplicate/excess rows stop startup without editing the original file.

The previous main file is kept as `.bak` after a successful replacement. A lone backup without the main file triggers a manual recovery warning. Use one running copy per folder and do not externally edit its files while it is running. This storage is not crash-atomic, power-failure-safe, encrypted or designed for multiple writers.

## Testing

Standalone verification on 19 October 2026 passed **51/51 integration tests** with strict GCC warnings, and the same suite passed with UndefinedBehaviorSanitizer. See [TEST_RESULTS.md](TEST_RESULTS.md) and [TEST_CASES.md](TEST_CASES.md) for evidence and scope. No Windows execution or real healthcare validation is claimed.

## Limitations

This does not verify identities, specimen suitability, clinical results or regulatory compliance. Its workflow is a classroom model, not a validated laboratory procedure. It has no complete status-change history, authentication or encryption; patient codes do not provide a privacy guarantee.

Use entirely fictitious records. Passing tests is not proof of correctness for every input or suitability for healthcare operation.

## Conclusion

The application demonstrates the connection between a clear real-life problem, C data structures, readable functions, explicit validation and repeatable tests. It is an educational prototype rather than a production system.

## Before presenting

Read [CODE_EXPLANATION.md](CODE_EXPLANATION.md), try [SAMPLE_OUTPUT.md](SAMPLE_OUTPUT.md), and practise the questions in [VIVA_GUIDE.md](VIVA_GUIDE.md). Understand the code, describe your own contribution accurately, and acknowledge external or AI assistance according to your college's rules.
