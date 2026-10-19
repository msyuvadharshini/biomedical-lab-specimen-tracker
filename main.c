/* Educational C11 console application. Use fictitious records only.
 * No dynamic memory, database, or non-standard C library is required.
 */
#include <ctype.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>

#define READ_END (-1)
#define READ_BAD 0
#define READ_OK 1
#define DATE_LEN 11
#define LINE_LEN 256

#define MAX_RECORDS 500
#define ID_LEN 24
#define PATIENT_LEN 24
#define TYPE_LEN 40
#define STATUS_LEN 20
#define DATA_FILE "specimen_records.txt"
#define TEMP_FILE "specimen_records.txt.tmp"
#define BACKUP_FILE "specimen_records.txt.bak"

typedef struct {
    char id[ID_LEN];
    char patientCode[PATIENT_LEN]; /* Fictitious code, never a real name. */
    char sampleType[TYPE_LEN];
    char collectionDate[DATE_LEN];
    char status[STATUS_LEN];
} Specimen;

static const char *const statuses[] = {
    "Collected", "InProcess", "Completed", "Rejected"
};

/* Read and consume a WHOLE line, even if it is too long for the buffer.
 * Return 1 for a line, 0 for end-of-file, -1 for an invalid line/read error.
 * CRLF and a final line without a newline are supported. */
static int readRawLine(FILE *stream, char *out, size_t capacity) {
    size_t used = 0;
    int ch, bad = 0;
    while ((ch = fgetc(stream)) != '\n' && ch != EOF) {
        if (ch == '\0') bad = 1;
        if (used + 1 < capacity) out[used++] = (char)ch;
        else bad = 1;
    }
    out[used] = '\0';
    if (ferror(stream)) return -1;
    if (ch == EOF && used == 0 && !bad) return 0;
    if (used > 0 && out[used - 1] == '\r') out[--used] = '\0';
    return bad ? -1 : 1;
}

/* Spaces inside names are allowed; empty fields, control characters,
 * leading/trailing whitespace, and the file separator '|' are not. */
static int validText(const char *text, size_t capacity) {
    size_t length = strlen(text);
    if (length == 0 || length >= capacity) return 0;
    if (isspace((unsigned char)text[0]) ||
        isspace((unsigned char)text[length - 1])) return 0;
    for (size_t i = 0; i < length; i++)
        if (!isprint((unsigned char)text[i]) || text[i] == '|') return 0;
    return 1;
}

static int readText(const char *prompt, char *out, size_t capacity) {
    char line[LINE_LEN];
    size_t start = 0, length;
    int result;
    fputs(prompt, stdout);
    fflush(stdout);
    result = readRawLine(stdin, line, sizeof line);
    if (result == 0 || ferror(stdin)) return READ_END;
    if (result < 0) {
        puts("Invalid input: line too long or contains a null character.");
        return READ_BAD;
    }
    length = strlen(line);
    while (length > 0 && isspace((unsigned char)line[length - 1]))
        line[--length] = '\0';
    while (isspace((unsigned char)line[start])) start++;
    if (start > 0) memmove(line, line + start, length - start + 1);
    if (!validText(line, capacity)) {
        printf("Invalid input: use 1 to %zu printable characters; no '|'.\n",
               capacity - 1);
        return READ_BAD;
    }
    strcpy(out, line); /* Length was checked before copying. */
    return READ_OK;
}

static int validId(const char *id) {
    if (id[0] == '\0') return 0;
    for (size_t i = 0; id[i] != '\0'; i++)
        if (!isalnum((unsigned char)id[i]) && id[i] != '-' && id[i] != '_')
            return 0;
    return 1;
}

static int readId(const char *prompt, char *out, size_t capacity) {
    int result = readText(prompt, out, capacity);
    if (result != READ_OK) return result;
    if (!validId(out)) {
        puts("Invalid ID: use letters, digits, '-' or '_' only.");
        return READ_BAD;
    }
    return READ_OK;
}

/* Check EXACTLY YYYY-MM-DD, including leap years. No sscanf signs or
 * shortened month/day fields are accepted. Supported years: 2000-9999. */
static int validDate(const char *date) {
    int year, month, day;
    int days[] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    if (strlen(date) != 10 || date[4] != '-' || date[7] != '-') return 0;
    for (int i = 0; i < 10; i++)
        if (i != 4 && i != 7 && !isdigit((unsigned char)date[i])) return 0;
    year = (date[0] - '0') * 1000 + (date[1] - '0') * 100 +
           (date[2] - '0') * 10 + date[3] - '0';
    month = (date[5] - '0') * 10 + date[6] - '0';
    day = (date[8] - '0') * 10 + date[9] - '0';
    if (year < 2000 || month < 1 || month > 12) return 0;
    if (year % 400 == 0 || (year % 4 == 0 && year % 100 != 0)) days[1] = 29;
    return day >= 1 && day <= days[month - 1];
}

static int readDate(const char *prompt, char *out) {
    int result = readText(prompt, out, DATE_LEN);
    if (result != READ_OK) return result;
    if (!validDate(out)) {
        puts("Invalid date: use a real YYYY-MM-DD date (years 2000-9999).");
        return READ_BAD;
    }
    return READ_OK;
}

/* Missing data means a fresh project, NOT an unreadable data file.
 * A backup without a main file is treated as a recovery situation. */
static FILE *openDataFile(int *ok) {
    FILE *fp = fopen(DATA_FILE, "r");
    *ok = 1;
    if (fp != NULL) return fp;
    if (errno != ENOENT) {
        fprintf(stderr, "Cannot read %s. No changes made.\n", DATA_FILE);
        *ok = 0;
        return NULL;
    }
    fp = fopen(BACKUP_FILE, "r");
    if (fp != NULL) {
        fclose(fp);
        fprintf(stderr, "Main data file missing, but %s exists.\n"
                "Restore the backup as %s before running again.\n",
                BACKUP_FILE, DATA_FILE);
        *ok = 0;
    } else if (errno != ENOENT) {
        fprintf(stderr, "Cannot check backup file. No changes made.\n");
        *ok = 0;
    }
    return NULL;
}

/* Called ONLY after every record was written and the temporary file
 * closed successfully. Keep the previous main file as a .bak file.
 * Standard C rename steps are used, so this also works with Windows GCC.
 * This is not a power-failure-safe database transaction. */
static int commitFile(void) {
    int hadOldFile;
    if (remove(BACKUP_FILE) != 0 && errno != ENOENT) {
        puts("Save failed: cannot replace the backup. No changes saved.");
        remove(TEMP_FILE);
        return 0;
    }
    hadOldFile = rename(DATA_FILE, BACKUP_FILE) == 0;
    if (!hadOldFile && errno != ENOENT) {
        puts("Save failed: cannot back up the data file. No changes saved.");
        remove(TEMP_FILE);
        return 0;
    }
    if (rename(TEMP_FILE, DATA_FILE) != 0) {
        puts("Save failed: cannot install the new data file.");
        if (hadOldFile && rename(BACKUP_FILE, DATA_FILE) != 0)
            printf("Restore %s as %s before running again.\n",
                   BACKUP_FILE, DATA_FILE);
        remove(TEMP_FILE);
        return 0;
    }
    return 1;
}

static int statusIndex(const char *status) {
    for (int i = 0; i < 4; i++)
        if (strcmp(statuses[i], status) == 0) return i;
    return -1;
}

static int findById(const Specimen records[], int count, const char *id) {
    for (int i = 0; i < count; i++)
        if (strcmp(records[i].id, id) == 0) return i;
    return -1;
}

static int loadRecords(Specimen records[]) {
    int ok, count = 0, lineNumber = 0, result;
    FILE *fp = openDataFile(&ok);
    char line[LINE_LEN], extra;
    Specimen item;
    if (fp == NULL) return ok ? 0 : -1;
    while ((result = readRawLine(fp, line, sizeof line)) != 0) {
        lineNumber++;
        if (result < 0 || count >= MAX_RECORDS ||
            sscanf(line, "%23[^|]|%23[^|]|%39[^|]|%10[^|]|%19[^|]%c",
                   item.id, item.patientCode, item.sampleType,
                   item.collectionDate, item.status, &extra) != 5 ||
            !validText(item.id, sizeof item.id) || !validId(item.id) ||
            !validText(item.patientCode, sizeof item.patientCode) ||
            !validId(item.patientCode) ||
            !validText(item.sampleType, sizeof item.sampleType) ||
            !validDate(item.collectionDate) || statusIndex(item.status) < 0 ||
            findById(records, count, item.id) >= 0) {
            fprintf(stderr, "Cannot load %s at line %d: invalid, duplicate, "
                    "or excess record. No changes made.\n", DATA_FILE, lineNumber);
            fclose(fp);
            return -1;
        }
        records[count++] = item;
    }
    if (fclose(fp) != 0) {
        fprintf(stderr, "Cannot finish reading %s. No changes made.\n", DATA_FILE);
        return -1;
    }
    return count;
}

static int saveRecords(const Specimen records[], int count) {
    FILE *fp = fopen(TEMP_FILE, "w");
    int ok = 1;
    if (fp == NULL) {
        puts("Save failed: cannot create temporary file. No changes saved.");
        return 0;
    }
    for (int i = 0; i < count; i++) {
        if (fprintf(fp, "%s|%s|%s|%s|%s\n", records[i].id,
                    records[i].patientCode, records[i].sampleType,
                    records[i].collectionDate, records[i].status) < 0) {
            ok = 0;
            break;
        }
    }
    if (fclose(fp) != 0) ok = 0;
    if (!ok) {
        puts("Save failed while writing. No changes saved.");
        remove(TEMP_FILE);
        return 0;
    }
    return commitFile();
}

static int addSpecimen(Specimen records[], int *count) {
    Specimen item;
    int result;
    if (*count >= MAX_RECORDS) {
        puts("Record limit reached (500). No changes made.");
        return READ_OK;
    }
    result = readId("Specimen ID: ", item.id, sizeof item.id);
    if (result != READ_OK) return result;
    if (findById(records, *count, item.id) >= 0) {
        puts("Duplicate specimen ID. No changes made.");
        return READ_OK;
    }
    result = readId("Fictitious patient code: ", item.patientCode, sizeof item.patientCode);
    if (result != READ_OK) return result;
    result = readText("Sample type: ", item.sampleType, sizeof item.sampleType);
    if (result != READ_OK) return result;
    result = readDate("Collection date (YYYY-MM-DD): ", item.collectionDate);
    if (result != READ_OK) return result;
    strcpy(item.status, "Collected");
    records[*count] = item;
    if (saveRecords(records, *count + 1)) {
        (*count)++;
        puts("Specimen saved with status: Collected.");
    }
    return READ_OK;
}

static void listSpecimens(const Specimen records[], int count) {
    if (count == 0) {
        puts("No specimen records found.");
        return;
    }
    puts("\nSample types are shortened here; Search shows full details.");
    printf("%-23s %-23s %-20s %-10s %-10s\n",
           "Specimen ID", "Patient code", "Sample type", "Collected", "Status");
    for (int i = 0; i < count; i++)
        printf("%-23s %-23s %-20.20s %-10s %-10s\n", records[i].id,
               records[i].patientCode, records[i].sampleType,
               records[i].collectionDate, records[i].status);
}

static int searchSpecimen(const Specimen records[], int count) {
    char id[ID_LEN];
    int index, result = readId("Specimen ID to search: ", id, sizeof id);
    if (result != READ_OK) return result;
    index = findById(records, count, id);
    if (index < 0) puts("Specimen ID not found.");
    else printf("\nSpecimen ID: %s\nPatient code: %s\nSample type: %s\n"
                "Collection date: %s\nStatus: %s\n", records[index].id,
                records[index].patientCode, records[index].sampleType,
                records[index].collectionDate, records[index].status);
    return READ_OK;
}

/* Teaching workflow, not a clinical protocol:
 * Collected -> InProcess/Rejected; InProcess -> Completed/Rejected.
 * Completed and Rejected are final in this simplified model. */
static int updateStatus(Specimen records[], int count) {
    char id[ID_LEN], choice[8], oldStatus[STATUS_LEN];
    const char *nextStatus;
    int index, allowed, result = readId("Specimen ID: ", id, sizeof id);
    if (result != READ_OK) return result;
    index = findById(records, count, id);
    if (index < 0) {
        puts("Specimen ID not found.");
        return READ_OK;
    }
    if (strcmp(records[index].status, "Completed") == 0 ||
        strcmp(records[index].status, "Rejected") == 0) {
        puts("Completed/Rejected is final in this model. No change made.");
        return READ_OK;
    }
    printf("Current status: %s\n1. InProcess\n2. Completed\n3. Rejected\n",
           records[index].status);
    result = readText("Choose new status: ", choice, sizeof choice);
    if (result != READ_OK) return result;
    if (strcmp(choice, "1") == 0) nextStatus = "InProcess";
    else if (strcmp(choice, "2") == 0) nextStatus = "Completed";
    else if (strcmp(choice, "3") == 0) nextStatus = "Rejected";
    else {
        puts("Invalid status option. No change made.");
        return READ_OK;
    }
    allowed = (strcmp(records[index].status, "Collected") == 0 &&
               (strcmp(nextStatus, "InProcess") == 0 || strcmp(nextStatus, "Rejected") == 0)) ||
              (strcmp(records[index].status, "InProcess") == 0 &&
               (strcmp(nextStatus, "Completed") == 0 || strcmp(nextStatus, "Rejected") == 0));
    if (!allowed) {
        puts("Invalid transition. Follow Collected -> InProcess -> Completed, "
             "or reject a non-final specimen. No change made.");
        return READ_OK;
    }
    strcpy(oldStatus, records[index].status);
    strcpy(records[index].status, nextStatus);
    if (saveRecords(records, count))
        printf("Status updated successfully: %s.\n", nextStatus);
    else strcpy(records[index].status, oldStatus);
    return READ_OK;
}

static void statusSummary(const Specimen records[], int count) {
    int totals[4] = {0, 0, 0, 0};
    for (int i = 0; i < count; i++) {
        int index = statusIndex(records[i].status);
        if (index >= 0) totals[index]++;
    }
    puts("\nSPECIMEN STATUS SUMMARY");
    for (int i = 0; i < 4; i++) printf("%s: %d\n", statuses[i], totals[i]);
    printf("Total specimens: %d\n", count);
}

int main(void) {
    Specimen records[MAX_RECORDS];
    char choice[8];
    int count = loadRecords(records), result = READ_OK;
    if (count < 0) return 1;
    puts("Educational simulation. Use fictitious patient codes only.");
    while (result != READ_END) {
        puts("\nBIOMEDICAL LABORATORY SPECIMEN TRACKER\n"
             "1. Register specimen\n2. List specimens\n3. Search by ID\n"
             "4. Update processing status\n5. Status summary\n6. Exit");
        result = readText("Choose an option: ", choice, sizeof choice);
        if (result != READ_OK) continue;
        switch (strlen(choice) == 1 ? choice[0] : '?') {
            case '1': result = addSpecimen(records, &count); break;
            case '2': listSpecimens(records, count); break;
            case '3': result = searchSpecimen(records, count); break;
            case '4': result = updateStatus(records, count); break;
            case '5': statusSummary(records, count); break;
            case '6': puts("Exiting tracker. Thank you."); return 0;
            default: puts("Invalid option. Choose 1 to 6."); break;
        }
    }
    puts("\nInput ended. Any incomplete entry was cancelled.");
    return ferror(stdin) ? 1 : 0;
}
