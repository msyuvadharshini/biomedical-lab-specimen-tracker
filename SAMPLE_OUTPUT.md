# Actual sample run

Captured on Linux with GCC on 2026-10-19, starting from an empty temporary data folder. All IDs and records are fictitious. This is actual program stdout, not a screenshot or a claimed production result.

## Input sequence

Enter one line at a time when prompted. The same sequence is in `examples/demo_input.txt`.

```text
1
SP1001
PT042
Blood
2026-10-18
4
SP1001
1
4
SP1001
2
5
3
SP1001
6
```

## Captured output

Keyboard input is supplied separately above and is not echoed by the automated capture, so consecutive prompts can appear on one line. An interactive terminal normally echoes what you type.

```text
Educational simulation. Use fictitious patient codes only.

BIOMEDICAL LABORATORY SPECIMEN TRACKER
1. Register specimen
2. List specimens
3. Search by ID
4. Update processing status
5. Status summary
6. Exit
Choose an option: Specimen ID: Fictitious patient code: Sample type: Collection date (YYYY-MM-DD): Specimen saved with status: Collected.

BIOMEDICAL LABORATORY SPECIMEN TRACKER
1. Register specimen
2. List specimens
3. Search by ID
4. Update processing status
5. Status summary
6. Exit
Choose an option: Specimen ID: Current status: Collected
1. InProcess
2. Completed
3. Rejected
Choose new status: Status updated successfully: InProcess.

BIOMEDICAL LABORATORY SPECIMEN TRACKER
1. Register specimen
2. List specimens
3. Search by ID
4. Update processing status
5. Status summary
6. Exit
Choose an option: Specimen ID: Current status: InProcess
1. InProcess
2. Completed
3. Rejected
Choose new status: Status updated successfully: Completed.

BIOMEDICAL LABORATORY SPECIMEN TRACKER
1. Register specimen
2. List specimens
3. Search by ID
4. Update processing status
5. Status summary
6. Exit
Choose an option: 
SPECIMEN STATUS SUMMARY
Collected: 0
InProcess: 0
Completed: 1
Rejected: 0
Total specimens: 1

BIOMEDICAL LABORATORY SPECIMEN TRACKER
1. Register specimen
2. List specimens
3. Search by ID
4. Update processing status
5. Status summary
6. Exit
Choose an option: Specimen ID to search: 
Specimen ID: SP1001
Patient code: PT042
Sample type: Blood
Collection date: 2026-10-18
Status: Completed

BIOMEDICAL LABORATORY SPECIMEN TRACKER
1. Register specimen
2. List specimens
3. Search by ID
4. Update processing status
5. Status summary
6. Exit
Choose an option: Exiting tracker. Thank you.
```

## Saved data after the run

```text
SP1001|PT042|Blood|2026-10-18|Completed
```

The demonstration was run in an isolated folder. It did not create active runtime data in the supplied project.
