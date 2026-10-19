# Test cases and verified test catalogue

**Local result on 2026-10-19: 51 / 51 tests passed for this project.**

Run this project's suite from the repository root with `python3 tests/run_tests.py -v`.
The runner compiles this repository's main.c with strict warnings and uses isolated temporary data folders.
No existing project records are deleted or edited by these tests.

## Main manual scenarios

| Scenario | Expected behaviour | Observed in automated tests |
|---|---|---|
| Valid registration | Exactly one record saved; no false menu error | PASS |
| Duplicate ID | Refused before further fields; old data unchanged | PASS |
| Search and restart | Full details available after restarting | PASS |
| Bad date `2026-01-+1` / impossible day | Rejected; no record saved | PASS |
| Date plus `junk` / overlong line | Whole line consumed; not truncated into a valid field | PASS |
| EOF at menu or during entry | Clean exit; incomplete record not saved | PASS |
| Invalid/corrupt/duplicate/oversized saved file | Startup refused; original bytes unchanged | PASS |
| Temporary-file write/open failure | No false success; old disk/in-memory state retained | PASS |
| Successful replacement | Previous main data retained in `.bak` | PASS |

Use a copied demo folder with fictitious data for manual testing. For a clean registration demo, start without runtime data **and** backups; do not delete files containing work you need.

## Automated test catalogue

Each row below is an actual named integration test in `tests/run_tests.py`. Several tests also contain subcases (for example multiple invalid dates). The pass count counts test methods, not each subcase.

| Test method | Expected behaviour checked | Actual result |
|---|---|---|
| `test_backup_without_main_file` | A lone backup causes an explicit recovery warning, not an empty restart. | PASS |
| `test_bad_text_fields` | Blank, pipe-containing and control-character name/type fields are rejected. | PASS |
| `test_blank_line_in_file` | Unexpected blank saved rows trigger a clear error, not silent data loss. | PASS |
| `test_blocked_backup_preserves_main` | A backup replacement error leaves the original main data unchanged. | PASS |
| `test_cannot_skip_processing` | Collected -> Completed is rejected by the stated teaching workflow. | PASS |
| `test_century_leap_rule` | 2100 is not a leap year; 2000 is a leap year. | PASS |
| `test_crlf_and_no_final_newline_data` | Both CRLF data and a last saved row without a newline load correctly. | PASS |
| `test_crlf_input` | CRLF console input does not leave stray carriage returns/newlines. | PASS |
| `test_duplicate_id` | An existing ID is rejected before asking for more record fields. | PASS |
| `test_duplicate_ids_in_file` | Duplicate IDs already present on disk are detected before editing. | PASS |
| `test_empty_data_file` | An existing empty data file is a valid empty project. | PASS |
| `test_empty_list` | An empty project displays a clear no-records message. | PASS |
| `test_empty_summary` | The status summary reports zero for every stage when there are no records. | PASS |
| `test_eof_at_menu` | End-of-input exits instead of repeating the menu forever. | PASS |
| `test_eof_mid_entry` | An incomplete registration is cancelled without creating a record. | PASS |
| `test_exact_menu_choice` | 2junk, 02 and arbitrary text are not accepted as menu option 2. | PASS |
| `test_excess_capacity_file` | An oversized data file is refused instead of silently truncating records. | PASS |
| `test_extra_field_in_file` | An unexpected extra saved field is rejected. | PASS |
| `test_final_statuses_immutable` | Completed and Rejected are final; no new-status prompt is displayed. | PASS |
| `test_forward_workflow` | Collected -> InProcess -> Completed updates one record and survives restart. | PASS |
| `test_full_capacity` | At the record limit, a new add is refused without modifying saved records. | PASS |
| `test_id_characters` | IDs allow letters/digits/hyphen/underscore but reject spaces and slashes. | PASS |
| `test_impossible_date` | April 31 is rejected. | PASS |
| `test_invalid_date_in_file` | Invalid saved dates are not trusted. | PASS |
| `test_invalid_saved_status` | An unrecognised status already saved on disk blocks startup. | PASS |
| `test_invalid_status_choice` | An unsupported status menu choice does not change the record. | PASS |
| `test_last_input_without_newline` | A final exit choice without a newline is handled correctly. | PASS |
| `test_leap_day` | 2028-02-29 is accepted as a valid leap day. | PASS |
| `test_long_line_drained` | A 400-character ID is rejected without leaking into the next menu input. | PASS |
| `test_long_or_binary_file_line` | Oversized and null-containing saved rows are refused. | PASS |
| `test_malformed_record_file` | A malformed middle row blocks startup and preserves all original bytes. | PASS |
| `test_maximum_id_length` | An ID exactly at the documented maximum length is accepted. | PASS |
| `test_maximum_sample_type_length` | A 39-character sample type is saved and searchable without truncation. | PASS |
| `test_missing_specimen_update` | An unknown specimen ID does not prompt for a status change. | PASS |
| `test_non_leap_day` | 2027-02-29 is rejected and nothing is saved. | PASS |
| `test_outer_whitespace_trimmed` | Surrounding input whitespace is trimmed; spaces inside names remain. | PASS |
| `test_patient_code_validation` | Patient codes use ID characters rather than spaces or real-name-style text. | PASS |
| `test_persistence_after_restart` | Saved records are still available after the program restarts. | PASS |
| `test_previous_data_backed_up` | A successful save keeps the previous main file as a .bak file. | PASS |
| `test_reject_from_collected` | A Collected specimen can be marked Rejected. | PASS |
| `test_reject_from_inprocess` | An InProcess specimen can be marked Rejected. | PASS |
| `test_repeat_status_rejected` | InProcess -> InProcess is rejected without a redundant save. | PASS |
| `test_save_failure_add` | A blocked temporary file prevents a false save and leaves memory empty. | PASS |
| `test_save_failure_update_rolls_back` | If an update cannot be saved, disk AND in-memory details remain unchanged. | PASS |
| `test_search_existing` | Searching an existing ID shows its full details. | PASS |
| `test_search_missing` | Searching an unknown ID gives a not-found message. | PASS |
| `test_short_date_and_year_range` | Short dates and years below 2000 are rejected; 9999-12-31 is accepted. | PASS |
| `test_signed_date_component` | The reference bug 2026-01-+1 is rejected. | PASS |
| `test_summary_totals` | A mixed-status file produces correct counts for all four stages. | PASS |
| `test_trailing_date_junk` | A date with trailing junk is rejected, not silently truncated. | PASS |
| `test_valid_add_no_spurious_menu_error` | A normal valid registration saves exactly one record, with no false menu error. | PASS |

## Scope

Passing these cases does not prove the absence of every defect. No Windows execution, real healthcare validation, concurrent-writer behaviour or destructive power-loss testing was performed.
See `TEST_RESULTS.md`, `tests/LAST_TEST_RUN.txt` and `COMPILE_TEST.txt` for the actual local verification details.
