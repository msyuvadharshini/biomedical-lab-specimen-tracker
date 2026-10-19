#!/usr/bin/env python3
"""Compile and integration-test this standalone C program; Python is only for tests.

Run from the repository root: python3 tests/run_tests.py -v
Uses only Python's standard library. All runtime data stays in temporary folders.
Override CC/CFLAGS if needed. CFLAGS must include any desired standard/warnings.
"""
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FLAGS = '-std=c11 -Wall -Wextra -Wpedantic -Werror'


class CommonChecks:
    """Input/storage regression checks for this standalone C program."""

    @classmethod
    def setUpClass(cls):
        cls.build_dir = tempfile.TemporaryDirectory(prefix='biomedical-c-compile-')
        cls.addClassCleanup(cls.build_dir.cleanup)
        cls.executable = Path(cls.build_dir.name) / ('program.exe' if os.name == 'nt' else 'program')
        cls.compile_command = [os.environ.get('CC', 'gcc')]
        cls.compile_command += shlex.split(os.environ.get('CFLAGS', DEFAULT_FLAGS))
        cls.compile_command += [str(ROOT / 'main.c'), '-o', str(cls.executable)]
        result = subprocess.run(cls.compile_command, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            raise AssertionError('Compilation failed:\n' + result.stdout + result.stderr)

    def setUp(self):
        self.sandbox = tempfile.TemporaryDirectory(prefix='biomedical-c-data-')
        self.addCleanup(self.sandbox.cleanup)
        self.work = Path(self.sandbox.name)
        self.data = self.work / self.data_name

    def run_app(self, script=''):
        return subprocess.run([str(self.executable)], input=script, text=True,
                              capture_output=True, cwd=self.work, timeout=3)

    def seed(self, content=None):
        self.data.write_bytes((self.row() if content is None else content).encode('ascii'))

    def saved(self):
        return self.data.read_text() if self.data.exists() else ''

    def assert_bad_file_preserved(self, content):
        self.seed(content)
        before = self.data.read_bytes()
        result = self.run_app('6\n')
        self.assertEqual(result.returncode, 1)
        self.assertIn('Cannot load', result.stderr)
        self.assertEqual(self.data.read_bytes(), before)
        self.assertNotIn('Choose an option:', result.stdout)

    def test_empty_list(self):
        """An empty project displays a clear no-records message."""
        result = self.run_app('2\n6\n')
        self.assertEqual(result.returncode, 0)
        self.assertIn(self.no_records, result.stdout)
        self.assertFalse(self.data.exists())

    def test_eof_at_menu(self):
        """End-of-input exits instead of repeating the menu forever."""
        result = self.run_app('')
        self.assertEqual(result.returncode, 0)
        self.assertIn('Input ended.', result.stdout)

    def test_eof_mid_entry(self):
        """An incomplete registration is cancelled without creating a record."""
        result = self.run_app('1\n' + self.sample_id + '\n')
        self.assertEqual(result.returncode, 0)
        self.assertIn('Input ended.', result.stdout)
        self.assertFalse(self.data.exists())

    def test_valid_add_no_spurious_menu_error(self):
        """A normal valid registration saves exactly one record, with no false menu error."""
        result = self.run_app(self.add() + '6\n')
        self.assertEqual(result.returncode, 0)
        self.assertIn(self.save_message, result.stdout)
        self.assertNotIn('Invalid option.', result.stdout)
        self.assertEqual(self.saved(), self.row())

    def test_duplicate_id(self):
        """An existing ID is rejected before asking for more record fields."""
        self.seed()
        before = self.data.read_bytes()
        result = self.run_app('1\n' + self.sample_id + '\n6\n')
        self.assertIn('Duplicate', result.stdout)
        self.assertEqual(self.data.read_bytes(), before)

    def test_search_existing(self):
        """Searching an existing ID shows its full details."""
        self.seed()
        result = self.run_app('3\n' + self.sample_id + '\n6\n')
        self.assertIn(self.sample_id, result.stdout)
        self.assertIn(self.sample_name, result.stdout)
        self.assertIn('2026-10-18', result.stdout)

    def test_search_missing(self):
        """Searching an unknown ID gives a not-found message."""
        self.seed()
        result = self.run_app('3\nMISSING999\n6\n')
        self.assertIn('ID not found.', result.stdout)

    def test_persistence_after_restart(self):
        """Saved records are still available after the program restarts."""
        self.run_app(self.add() + '6\n')
        result = self.run_app('3\n' + self.sample_id + '\n6\n')
        self.assertEqual(result.returncode, 0)
        self.assertIn(self.sample_id, result.stdout)
        self.assertIn(self.sample_name, result.stdout)
        self.assertNotIn('ID not found.', result.stdout)

    def test_leap_day(self):
        """2028-02-29 is accepted as a valid leap day."""
        self.run_app(self.add(date='2028-02-29') + '6\n')
        self.assertIn('2028-02-29', self.saved())

    def test_non_leap_day(self):
        """2027-02-29 is rejected and nothing is saved."""
        result = self.run_app(self.add(date='2027-02-29') + '6\n')
        self.assertIn('Invalid date:', result.stdout)
        self.assertFalse(self.data.exists())

    def test_century_leap_rule(self):
        """2100 is not a leap year; 2000 is a leap year."""
        result = self.run_app(self.add(date='2100-02-29') + '6\n')
        self.assertIn('Invalid date:', result.stdout)
        self.assertFalse(self.data.exists())
        self.run_app(self.add(date='2000-02-29') + '6\n')
        self.assertIn('2000-02-29', self.saved())

    def test_impossible_date(self):
        """April 31 is rejected."""
        result = self.run_app(self.add(date='2026-04-31') + '6\n')
        self.assertIn('Invalid date:', result.stdout)
        self.assertFalse(self.data.exists())

    def test_signed_date_component(self):
        """The reference bug 2026-01-+1 is rejected."""
        result = self.run_app(self.add(date='2026-01-+1') + '6\n')
        self.assertIn('Invalid date:', result.stdout)
        self.assertFalse(self.data.exists())

    def test_trailing_date_junk(self):
        """A date with trailing junk is rejected, not silently truncated."""
        result = self.run_app(self.add(date='2026-10-18junk') + '6\n')
        self.assertIn('Invalid input:', result.stdout)
        self.assertNotIn('Invalid option.', result.stdout)
        self.assertFalse(self.data.exists())

    def test_short_date_and_year_range(self):
        """Short dates and years below 2000 are rejected; 9999-12-31 is accepted."""
        for date in ('2026-1-01', '1999-12-31', '2026-00-10', '2026-10-00'):
            with self.subTest(date=date):
                result = self.run_app(self.add(date=date) + '6\n')
                self.assertIn('Invalid date:', result.stdout)
                self.assertFalse(self.data.exists())
        self.run_app(self.add(date='9999-12-31') + '6\n')
        self.assertIn('9999-12-31', self.saved())

    def test_outer_whitespace_trimmed(self):
        """Surrounding input whitespace is trimmed; spaces inside names remain."""
        script = '\n'.join('  ' + line + '  ' for line in self.add().splitlines()) + '\n6\n'
        self.run_app(script)
        self.assertEqual(self.saved(), self.row())

    def test_long_line_drained(self):
        """A 400-character ID is rejected without leaking into the next menu input."""
        result = self.run_app('1\n' + 'A' * 400 + '\n2\n6\n')
        self.assertIn('Invalid input:', result.stdout)
        self.assertIn(self.no_records, result.stdout)
        self.assertNotIn('Invalid option.', result.stdout)
        self.assertFalse(self.data.exists())

    def test_maximum_id_length(self):
        """An ID exactly at the documented maximum length is accepted."""
        record_id = 'A' * self.id_max
        self.run_app(self.add(record_id=record_id) + '6\n')
        self.assertTrue(self.saved().startswith(record_id + '|'))

    def test_id_characters(self):
        """IDs allow letters/digits/hyphen/underscore but reject spaces and slashes."""
        for bad in ('BAD ID', 'BAD/ID'):
            result = self.run_app('1\n' + bad + '\n6\n')
            self.assertIn('Invalid ID:', result.stdout)
            self.assertFalse(self.data.exists())
        self.run_app(self.add(record_id='TEST_01-A') + '6\n')
        self.assertTrue(self.saved().startswith('TEST_01-A|'))

    def test_bad_text_fields(self):
        """Blank, pipe-containing and control-character name/type fields are rejected."""
        for bad in ('   ', 'Bad|Field', 'Bad\tField'):
            with self.subTest(value=repr(bad)):
                result = self.run_app(self.add_until_name() + bad + '\n6\n')
                self.assertIn('Invalid input:', result.stdout)
                self.assertFalse(self.data.exists())

    def test_exact_menu_choice(self):
        """2junk, 02 and arbitrary text are not accepted as menu option 2."""
        result = self.run_app('2junk\n02\nhello\n6\n')
        self.assertEqual(result.stdout.count('Invalid option.'), 3)
        self.assertNotIn(self.no_records, result.stdout)

    def test_crlf_input(self):
        """CRLF console input does not leave stray carriage returns/newlines."""
        result = self.run_app((self.add() + '6\n').replace('\n', '\r\n'))
        self.assertIn(self.save_message, result.stdout)
        self.assertNotIn('Invalid option.', result.stdout)
        self.assertEqual(self.saved(), self.row())

    def test_last_input_without_newline(self):
        """A final exit choice without a newline is handled correctly."""
        result = self.run_app(self.add() + '6')
        self.assertEqual(result.returncode, 0)
        self.assertIn('Exiting tracker.', result.stdout)
        self.assertEqual(self.saved(), self.row())

    def test_full_capacity(self):
        """At the record limit, a new add is refused without modifying saved records."""
        content = ''.join(self.row(record_id='ID' + str(i)) for i in range(self.capacity))
        self.seed(content)
        result = self.run_app('1\n6\n')
        self.assertEqual(result.returncode, 0)
        self.assertIn('Record limit reached', result.stdout)
        self.assertEqual(self.saved(), content)

    def test_excess_capacity_file(self):
        """An oversized data file is refused instead of silently truncating records."""
        content = ''.join(self.row(record_id='ID' + str(i)) for i in range(self.capacity + 1))
        self.assert_bad_file_preserved(content)

    def test_malformed_record_file(self):
        """A malformed middle row blocks startup and preserves all original bytes."""
        content = self.row() + 'BROKEN\n' + self.row(record_id='OTHER')
        self.assert_bad_file_preserved(content)

    def test_duplicate_ids_in_file(self):
        """Duplicate IDs already present on disk are detected before editing."""
        self.assert_bad_file_preserved(self.row() + self.row())

    def test_invalid_date_in_file(self):
        """Invalid saved dates are not trusted."""
        self.assert_bad_file_preserved(self.row(date='2026-02-30'))

    def test_extra_field_in_file(self):
        """An unexpected extra saved field is rejected."""
        self.assert_bad_file_preserved(self.row().rstrip('\n') + '|EXTRA\n')

    def test_blank_line_in_file(self):
        """Unexpected blank saved rows trigger a clear error, not silent data loss."""
        self.assert_bad_file_preserved(self.row() + '\n')

    def test_long_or_binary_file_line(self):
        """Oversized and null-containing saved rows are refused."""
        for bad in ('X' * 400 + '\n', self.row().rstrip('\n') + '\x00JUNK\n'):
            with self.subTest(value=repr(bad[:30])):
                self.assert_bad_file_preserved(bad)

    def test_save_failure_add(self):
        """A blocked temporary file prevents a false save and leaves memory empty."""
        blocked = self.work / (self.data_name + '.tmp')
        blocked.mkdir()
        (blocked / 'keep.txt').write_text('block writing')
        result = self.run_app(self.add() + '2\n6\n')
        self.assertIn('Save failed:', result.stdout)
        self.assertNotIn(self.save_message, result.stdout)
        self.assertIn(self.no_records, result.stdout)
        self.assertFalse(self.data.exists())

    def test_save_failure_update_rolls_back(self):
        """If an update cannot be saved, disk AND in-memory details remain unchanged."""
        self.seed()
        blocked = self.work / (self.data_name + '.tmp')
        blocked.mkdir()
        (blocked / 'keep.txt').write_text('block writing')
        result = self.run_app(self.update_input() + '3\n' + self.sample_id + '\n6\n')
        self.assertIn('Save failed:', result.stdout)
        self.assertEqual(self.saved(), self.row())
        self.assertIn(self.original_search_value, result.stdout)
        self.assertNotIn(self.changed_search_value, result.stdout)

    def test_previous_data_backed_up(self):
        """A successful save keeps the previous main file as a .bak file."""
        self.seed()
        result = self.run_app(self.add(record_id='OTHER') + '6\n')
        self.assertIn(self.save_message, result.stdout)
        backup = self.work / (self.data_name + '.bak')
        self.assertEqual(backup.read_text(), self.row())
        self.assertEqual(len(self.saved().splitlines()), 2)

    def test_backup_without_main_file(self):
        """A lone backup causes an explicit recovery warning, not an empty restart."""
        backup = self.work / (self.data_name + '.bak')
        backup.write_text(self.row())
        result = self.run_app('6\n')
        self.assertEqual(result.returncode, 1)
        self.assertIn('Restore the backup', result.stderr)
        self.assertFalse(self.data.exists())
        self.assertEqual(backup.read_text(), self.row())

    def test_blocked_backup_preserves_main(self):
        """A backup replacement error leaves the original main data unchanged."""
        self.seed()
        blocked = self.work / (self.data_name + '.bak')
        blocked.mkdir()
        (blocked / 'keep.txt').write_text('block replacement')
        result = self.run_app(self.add(record_id='OTHER') + '6\n')
        self.assertIn('Save failed:', result.stdout)
        self.assertEqual(self.saved(), self.row())
        self.assertFalse((self.work / (self.data_name + '.tmp')).exists())

    def test_crlf_and_no_final_newline_data(self):
        """Both CRLF data and a last saved row without a newline load correctly."""
        for content in (self.row().replace('\n', '\r\n'), self.row().rstrip('\n')):
            with self.subTest(content=repr(content)):
                self.seed(content)
                result = self.run_app('3\n' + self.sample_id + '\n6\n')
                self.assertEqual(result.returncode, 0)
                self.assertIn(self.sample_name, result.stdout)

    def test_empty_data_file(self):
        """An existing empty data file is a valid empty project."""
        self.seed('')
        result = self.run_app('2\n6\n')
        self.assertEqual(result.returncode, 0)
        self.assertIn(self.no_records, result.stdout)




class SpecimenTests(CommonChecks, unittest.TestCase):
    data_name = 'specimen_records.txt'
    sample_id = 'SP1001'
    sample_name = 'Blood'
    save_message = 'Specimen saved with status: Collected.'
    no_records = 'No specimen records found.'
    original_search_value = 'Status: Collected'
    changed_search_value = 'Status: InProcess'
    id_max = 23
    capacity = 500

    def row(self, record_id='SP1001', date='2026-10-18', status='Collected', sample_type='Blood'):
        return f'{record_id}|PT042|{sample_type}|{date}|{status}\n'

    def add(self, record_id='SP1001', date='2026-10-18'):
        return f'1\n{record_id}\nPT042\nBlood\n{date}\n'

    def add_until_name(self):
        return '1\nSP1001\nPT042\n'

    def update_input(self):
        return '4\nSP1001\n1\n'

    def test_forward_workflow(self):
        """Collected -> InProcess -> Completed updates one record and survives restart."""
        self.seed()
        result = self.run_app('4\nSP1001\n1\n4\nSP1001\n2\n5\n6\n')
        self.assertIn('Status updated successfully: InProcess.', result.stdout)
        self.assertIn('Status updated successfully: Completed.', result.stdout)
        self.assertEqual(self.saved(), self.row(status='Completed'))
        self.assertIn('Completed: 1', result.stdout)
        self.assertIn('Total specimens: 1', result.stdout)
        result = self.run_app('3\nSP1001\n6\n')
        self.assertIn('Status: Completed', result.stdout)

    def test_cannot_skip_processing(self):
        """Collected -> Completed is rejected by the stated teaching workflow."""
        self.seed()
        result = self.run_app('4\nSP1001\n2\n6\n')
        self.assertIn('Invalid transition.', result.stdout)
        self.assertEqual(self.saved(), self.row())

    def test_reject_from_collected(self):
        """A Collected specimen can be marked Rejected."""
        self.seed()
        result = self.run_app('4\nSP1001\n3\n6\n')
        self.assertIn('Status updated successfully: Rejected.', result.stdout)
        self.assertEqual(self.saved(), self.row(status='Rejected'))

    def test_reject_from_inprocess(self):
        """An InProcess specimen can be marked Rejected."""
        self.seed(self.row(status='InProcess'))
        result = self.run_app('4\nSP1001\n3\n6\n')
        self.assertIn('Status updated successfully: Rejected.', result.stdout)
        self.assertEqual(self.saved(), self.row(status='Rejected'))

    def test_final_statuses_immutable(self):
        """Completed and Rejected are final; no new-status prompt is displayed."""
        for status in ('Completed', 'Rejected'):
            self.seed(self.row(status=status))
            result = self.run_app('4\nSP1001\n6\n')
            self.assertIn('Completed/Rejected is final', result.stdout)
            self.assertNotIn('Choose new status:', result.stdout)
            self.assertEqual(self.saved(), self.row(status=status))

    def test_repeat_status_rejected(self):
        """InProcess -> InProcess is rejected without a redundant save."""
        self.seed(self.row(status='InProcess'))
        result = self.run_app('4\nSP1001\n1\n6\n')
        self.assertIn('Invalid transition.', result.stdout)
        self.assertEqual(self.saved(), self.row(status='InProcess'))

    def test_invalid_status_choice(self):
        """An unsupported status menu choice does not change the record."""
        self.seed()
        result = self.run_app('4\nSP1001\n9\n6\n')
        self.assertIn('Invalid status option.', result.stdout)
        self.assertEqual(self.saved(), self.row())

    def test_missing_specimen_update(self):
        """An unknown specimen ID does not prompt for a status change."""
        self.seed()
        result = self.run_app('4\nUNKNOWN\n6\n')
        self.assertIn('Specimen ID not found.', result.stdout)
        self.assertNotIn('Choose new status:', result.stdout)

    def test_summary_totals(self):
        """A mixed-status file produces correct counts for all four stages."""
        stages = ('Collected', 'InProcess', 'Completed', 'Rejected')
        self.seed(''.join(self.row(record_id='SP' + str(i), status=status)
                          for i, status in enumerate(stages)))
        result = self.run_app('5\n6\n')
        for status in stages:
            self.assertIn(status + ': 1', result.stdout)
        self.assertIn('Total specimens: 4', result.stdout)

    def test_empty_summary(self):
        """The status summary reports zero for every stage when there are no records."""
        result = self.run_app('5\n6\n')
        for status in ('Collected', 'InProcess', 'Completed', 'Rejected'):
            self.assertIn(status + ': 0', result.stdout)
        self.assertIn('Total specimens: 0', result.stdout)

    def test_invalid_saved_status(self):
        """An unrecognised status already saved on disk blocks startup."""
        self.assert_bad_file_preserved(self.row(status='ProcessingNow'))

    def test_patient_code_validation(self):
        """Patient codes use ID characters rather than spaces or real-name-style text."""
        result = self.run_app('1\nSP1001\nPatient Name\n6\n')
        self.assertIn('Invalid ID:', result.stdout)
        self.assertFalse(self.data.exists())
        self.assert_bad_file_preserved('SP1001|Patient Name|Blood|2026-10-18|Collected\n')

    def test_maximum_sample_type_length(self):
        """A 39-character sample type is saved and searchable without truncation."""
        sample_type = 'T' * 39
        result = self.run_app(f'1\nSP1001\nPT042\n{sample_type}\n2026-10-18\n3\nSP1001\n6\n')
        self.assertIn('Sample type: ' + sample_type, result.stdout)
        self.assertEqual(self.saved(), self.row(sample_type=sample_type))


if __name__ == '__main__':
    unittest.main(verbosity=2)
