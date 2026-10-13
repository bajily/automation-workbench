# Automation Workbench · File Organizer

A Python CLI that previews a file-organization plan and, when explicitly requested, copies files into clear categories. It demonstrates filesystem automation, reusable functions, JSON reports, and conservative defaults.

**Python 3.11+ · Standard library only · Dry run by default**

## Quick start

```bash
git clone https://github.com/bajily/automation-workbench.git
cd automation-workbench
mkdir inbox
python -c "from pathlib import Path; Path('inbox/notes.txt').write_text('demo'); Path('inbox/events.csv').write_text('event,count\nlogin,3\n')"
python organize.py inbox organized
python organize.py inbox organized --apply
```

The first command prints a JSON plan without creating directories or copying files. With `--apply`, `notes.txt` is copied to `organized/documents/` and `events.csv` to `organized/data/`. Originals remain in `inbox/`.

## Categories

| Category | Examples |
|---|---|
| Documents | `.pdf`, `.docx`, `.txt`, `.md` |
| Images | `.png`, `.jpg`, `.svg`, `.webp` |
| Data | `.csv`, `.json`, `.xlsx`, `.yaml` |
| Archives | `.zip`, `.tar`, `.gz`, `.7z` |
| Code | `.py`, `.js`, `.ts`, `.sh` |
| Other | Unrecognized extensions |

Extensions are case-insensitive. Only top-level regular files are included; subdirectories and symbolic links are skipped. Source and destination must be separate, non-nested directories.

## Reliability

- Existing destination files cause an error; files are never intentionally overwritten.
- Exclusive file creation checks for collisions again during copying.
- Exit `0` means success; exit `2` means invalid input or a filesystem error.
- A multi-file copy is not transactional: completed copies remain if a later copy fails. Review the output directory before retrying.
- Copies preserve bytes, not timestamps or filesystem permissions. This is an organizer, not a backup system.

Use a fresh destination for each run. Treat real file paths in JSON reports as private information. This tool is intended for directories under your control, not filesystems being modified by untrusted processes during the operation.

## Validate

```bash
python -m unittest discover -s tests -v
```

Tests cover dry runs, byte preservation, category selection, collisions, nested paths, and symlinks.

## بالعربية

أداة أتمتة لتنظيم الملفات حسب الامتداد. تعرض خطة أولًا، وعند استخدام `--apply` تنسخ الملفات إلى مجلدات مصنّفة مع الاحتفاظ بالأصول ورفض استبدال الملفات الموجودة.
