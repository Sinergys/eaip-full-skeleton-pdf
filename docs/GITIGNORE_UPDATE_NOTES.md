# .gitignore UPDATE - 12 Dec 2025

## NEW RULES ADDED

### Temporary Analysis Files
```
*_analysis_temp.md
*_scratch.md
wave*_draft*.json
audit_temp/
```
**Purpose:** Exclude temporary analysis files during audit process

### Intermediate Group Analysis
```
group_*_analysis.md
intermediate_*.json
```
**Purpose:** Keep only final reports, exclude intermediate group analyses

### One-Time Operation Scripts
```
cleanup_*.sh
analyze_*.sh
temp_*.py
```
**Purpose:** Exclude temporary automation scripts

### Personal Notes
```
NOTES_*.md
TODO_personal.md
scratch/
```
**Purpose:** Exclude personal notes that aren't project documentation

## FILES TO KEEP (NOT IGNORED)

✅ WAVE1_*.json - Final audit reports
✅ WAVE1_*.md - Final documentation
✅ ANALYZED_FILES_REPORT.json
✅ CRITICAL_FILES_LIST.md
✅ METHODOLOGY_GUIDE_COMPACT.md

## RATIONALE

These rules prevent pollution of git history with:
- Temporary files from audit process
- Personal working notes
- One-off scripts
- Intermediate analysis stages

While keeping all final deliverables tracked.
