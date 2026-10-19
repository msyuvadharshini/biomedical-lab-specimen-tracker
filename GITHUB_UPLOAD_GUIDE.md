# Upload this case study as its own GitHub repository

This package contains only **Biomedical Laboratory Specimen Tracker**. It has not been published to GitHub for you.

1. Extract **Biomedical-Laboratory-Specimen-Tracker.zip** using Windows **Extract All**. No C compiler is needed to extract or upload it.
2. Sign in to GitHub and create a new repository named **`biomedical-laboratory-specimen-tracker`** (or another name you prefer).
3. Choose Public only if you are comfortable sharing this fictitious coursework. For a private repository, invite your teacher as a collaborator; a private link alone does not grant access.
4. Leave automatic README/ignore/license creation unchecked for this new empty repository. This package already supplies a README and `.gitignore`; a license is your own decision.
5. Choose **uploading an existing file** or **Add file -> Upload files**.
6. Open the extracted **Biomedical-Laboratory-Specimen-Tracker** folder. Upload the **files and folders inside it**, so `README.md` and `main.c` appear at the repository root. Preserve `examples/`, `tests/` and the optional `.github/` paths. Do not upload only the ZIP.
7. Commit with a message such as `Add specimen C case study`.
8. Check that `main.c` is visible, the README displays and documentation links open. If your browser omits dot-files/folders, add `.gitignore` or the optional `.github/workflows/c-tests.yml` using GitHub's Create new file feature and the supplied contents.
9. Copy this repository's actual URL. For a public repository, check it in an incognito/private browser window before sharing.

Repeat the process using the **other case study's separate ZIP** and a different repository name. Then send your teacher the two actual repository URLs.

GitHub displays C source; it does not run this console application in the repository page. A compiler is not required simply to upload these prepared files.

## Do not upload generated/private files

Do not upload executables, object files, runtime `specimen_records.txt`, `.tmp`/`.bak` files, caches, real hospital records, patient information or secrets. Fictitious examples in `examples/` are intended to be included.

If you use Git commands, the supplied `.gitignore` helps exclude generated files. When uploading through the website, select files carefully; do not rely on `.gitignore` to filter your browser's upload selection.

The optional GitHub Actions workflow can compile this one C program and run its 51 tests once uploaded. Check its actual result in the repository's Actions tab; local test logs are not a claim that a remote run has occurred.
