# Algorithm — Laboratory Specimen Tracker

## Main algorithm

1. Start and load all saved specimens with field, date, status, duplicate and capacity validation.
2. If there is no data and no recovery backup, start empty. On unreadable/invalid data or a required backup recovery, stop without changing files.
3. Display the menu and read a whole line.
4. On end-of-input, cancel any incomplete operation and stop.
5. Perform the selected operation:
   - **Register:** check capacity; read a unique ID, fictitious patient code, sample type and valid collection date; set status to Collected; save; increase count only if saving succeeds.
   - **List:** display saved records or a no-records message.
   - **Search:** perform linear search by specimen ID and display full details or not-found.
   - **Update:** find the record; if final, refuse changes; otherwise read an exact status option and check it against the transition rules; save the new status or restore the previous in-memory status if saving fails.
   - **Summary:** initialise four counters to zero, scan the records, increment the corresponding status counter, and display totals.
   - **Exit:** stop.
6. Show an error for invalid input/choice and return to the menu.
7. Repeat until Exit or end-of-input.

## Transition subroutine

- Collected accepts InProcess or Rejected.
- InProcess accepts Completed or Rejected.
- Completed and Rejected have no outgoing transition.
- Refuse all other updates without saving.

These are explicitly simplified coursework rules, not a clinical protocol.

## Save subroutine

Write and check a temporary file, close it successfully, preserve the old main as `.bak`, and install the new file. Attempt to restore the backup if installation fails. The calling function accepts the new in-memory status only on success. Standard C rename steps do not guarantee power-failure-safe or multi-user storage.

## Flowchart

```mermaid
flowchart TD
    A([Start]) --> B[Load and validate all saved specimens]
    B --> C{Valid data or clean empty start?}
    C -->|No| X[Display error without changing file]
    X --> Z([Stop])
    C -->|Yes| M[Show menu and read whole line]
    M --> E{Exit or end of input?}
    E -->|Yes| Z
    E -->|No| O{Selected operation}
    O -->|Register| R[Read fields; validate date, ID and capacity]
    R --> V{Valid and unique?}
    V -->|No| ERR[Show error]
    V -->|Yes| S[Set Collected; save and accept on success]
    O -->|List or search| L[Display rows or ID search result]
    O -->|Update| F[Find specimen]
    F --> G{Found and non-final?}
    G -->|No| ERR
    G -->|Yes| H[Read proposed next status]
    H --> I{Allowed transition?}
    I -->|No| ERR
    I -->|Yes| U[Save new status; restore old status on failure]
    O -->|Summary| Q[Count each status and display total]
    O -->|Invalid| ERR
    S --> M
    L --> M
    U --> M
    Q --> M
    ERR --> M
```

End-of-input during any prompt exits cleanly without accepting an incomplete operation.
