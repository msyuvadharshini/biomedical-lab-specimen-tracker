# Viva Guide — Biomedical Laboratory Specimen Tracker

Use this to understand the source rather than memorise answers. Describe your own work accurately and follow your college's rules on acknowledging assistance.

## Introduction to adapt

> This C case study registers fictitious laboratory specimens and follows a simplified processing workflow. It uses structures, arrays, functions, strings, menus, counters and text files. It validates the requested next status before saving a change.

## Core C questions

### 1. Why use a structure?

One record has related fields. A `struct` groups them into a record, rather than keeping separate arrays that could get out of step.

### 2. Why use an array of structures?

It holds several records of the same type. A loop can list, search or count them. The program uses a fixed limit to avoid dynamic-memory complexity.

### 3. Why divide the program into functions?

Each function handles a task such as input, date validation, searching or saving. This makes the logic easier to read, explain, test and change.

### 4. Why does registration receive `int *count`?

The function must update the caller's record count after a successful save. `*count` accesses the integer at that pointer; `(*count)++` increases it.

### 5. What does `strcmp` return?

A value less than zero, zero, or greater than zero according to string order. Do not assume it returns exactly -1 or 1. IDs match when the result is zero.

### 6. Why not compare strings with `==`?

For character arrays/pointers, `==` does not compare the contents as a string. `strcmp` compares the characters.

### 7. What search algorithm is used?

Linear search: examine records in order and return the matching index, or -1 if no ID matches. It is O(n), appropriate for 500 small records.

### 8. What is the purpose of `static` on a function here?

It gives the function internal linkage: it is private to this source file. These are standalone single-source programs.

### 9. Why are character checks cast to `unsigned char`?

Functions such as `isdigit`, `isspace` and `isprint` require EOF or a value representable as unsigned char. The cast avoids invalid negative-character arguments.

### 10. Why not use `gets` or an unbounded `%s`?

They cannot safely enforce the destination size. `gets` was removed from modern C. Here a whole-line reader enforces a buffer limit, consumes the rest of an overlong line and rejects it.

### 11. What is EOF?

End-of-file/end-of-input. The program recognises it and exits instead of displaying the menu forever. A partial record missing required fields is not saved.

### 12. Why use text files?

They are simple to inspect and sufficient for an educational example. Files persist after the process exits, unlike ordinary in-memory variables. They are not a replacement for a secure database.

### 13. How are records separated?

Each record is one line. Fields are separated by `|`, so that character is not allowed inside an input field. The loader checks field lengths and rejects extra fields.

### 14. What do the scan widths do?

For example, `%23[^|]` reads at most 23 non-pipe characters into a 24-byte ID array, leaving space for `\0`. The additional `%c` in a record scan detects unexpected remaining characters.

### 15. Why check `fprintf` and `fclose`?

A file opening successfully does not mean every write or buffered flush will succeed. The program installs the new data file only after writing and closing the temporary file successfully.

### 16. Does the backup make saving completely crash-safe?

No. It preserves the previous main file during normal replacement and supports some manual recovery cases. Standard C rename steps do not provide a power-failure-safe database transaction or multi-user locking.

### 17. Why is `strcpy` safe at its call sites here?

Input length is checked before copying to its destination; known status literals fit their arrays; loaded fields use bounded scans. `strcpy` is not automatically safe without those preconditions.

## Case-specific questions

### 18. Which transitions are allowed?

`Collected -> InProcess`, `Collected -> Rejected`, `InProcess -> Completed`, and `InProcess -> Rejected`. Completed and Rejected are final in this classroom model.

### 19. Why reject a direct Collected-to-Completed change?

It demonstrates checking an allowed workflow rather than merely accepting any status word. This is a teaching rule, not a claim about every real laboratory.

### 20. Can a patient code repeat?

Yes. Several specimens may share a fictitious patient code. The specimen ID, not the patient code, must be unique.

### 21. Do patient codes make the system private or compliant?

No. The files are plain text without authentication or encryption. The assignment must use entirely fictitious codes and records.

## Short live demonstration

1. Register `SP1001`, `PT042`, `Blood`, `2026-10-18`.
2. Explain why the initial status is Collected.
3. Explain why a direct change to Completed is refused.
4. Change to InProcess, then Completed.
5. Show the status summary and explain why Completed is final.
6. Exit/restart and search to show persistence.

## Limitations to explain honestly

This does not verify identities, specimen suitability, clinical results or regulatory compliance. Its workflow is a classroom model, not a validated laboratory procedure. It has no complete status-change history, authentication or encryption; patient codes do not provide a privacy guarantee.

Text-file backups do not provide encryption, authentication, multi-user locking, a complete audit history or crash-atomic storage. Any future improvements must be labelled as future work, not features already implemented.
