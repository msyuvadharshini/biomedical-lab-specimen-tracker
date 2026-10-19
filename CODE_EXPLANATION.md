# Understanding `main.c` — Specimen project

## Data structure

```c
typedef struct {
    char id[ID_LEN];
    char patientCode[PATIENT_LEN];
    char sampleType[TYPE_LEN];
    char collectionDate[DATE_LEN];
    char status[STATUS_LEN];
} Specimen;
```

The ID identifies one specimen. The patient code is fictitious and need not be unique. An array holds up to 500 specimens; `count` tracks used slots.

## Function map — read in this order

| Function | Purpose |
|---|---|
| `main` | Load validated records, repeat the menu and dispatch operations |
| `findById` | Linear search by specimen ID |
| `addSpecimen` | Validate details, start at Collected, save before increasing the count |
| `listSpecimens` / `searchSpecimen` | Display a table or full details |
| `updateStatus` | Reject final records and invalid transitions; save or restore the old status |
| `statusIndex` | Convert a known status string to counter index 0–3 |
| `statusSummary` | Initialise an integer array and count records by status |
| `readRawLine`, `readText`, `readId`, `readDate` | Consume whole lines and validate console input |
| `validText`, `validId`, `validDate` | Check contents, limits and real dates |
| `openDataFile`, `loadRecords` | Handle a clean start/recovery case and validate every saved row |
| `saveRecords`, `commitFile` | Write/check a temporary file and preserve the previous main as backup |

## Main case-study rule

```text
Collected -> InProcess -> Completed
     |            |
     +-> Rejected <-+
```

Collected may move to InProcess or Rejected. InProcess may move to Completed or Rejected. The final stages cannot be changed. The actual source uses string comparisons and a Boolean `allowed` expression; no complex state-machine library is required.

These are classroom rules, not a universal laboratory protocol.

## Important details

### Initial status

`strcpy(item.status, "Collected")` gives a predictable starting stage. The known literal fits the 20-byte status array.

### Count update

`addSpecimen` receives `int *count` because it must change the caller's count. It increases `(*count)` only after the candidate file was saved successfully.

### Summary array

```c
int totals[4] = {0, 0, 0, 0};
```

`statusIndex` returns 0 for Collected, 1 for InProcess, 2 for Completed and 3 for Rejected. A loop increments the corresponding counter. Loading validates status names before they enter the active array.

### Failed-save rollback

Before a proposed update, the old status is copied to `oldStatus`. If `saveRecords` fails, the old string is copied back. This keeps search/summary output consistent with the unchanged main file during normal write failures.

### File validation

Bounded scans prevent field overflow; an extra `%c` detects unexpected remaining text. Empty fields, invalid codes/dates/statuses, duplicate IDs and excess rows stop startup before any editing.

## Complexity

Search, listing, summary and saving are O(n), where n <= 500. Loading's repeated duplicate-ID checks are O(n²) in the worst case. A fixed-size array avoids dynamic-memory management.

## Be clear about limits

The files are plain text with no login, encryption or full status-change history. Collection dates are user-supplied and are not checked against a computer clock. The application does not verify identities, handle diagnostic results or guarantee clinical/privacy compliance.
