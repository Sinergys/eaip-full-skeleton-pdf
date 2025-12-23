@echo off
cd /d C:\eaip

echo === GIT STATUS ===
git status --short

echo.
echo === ADDING FILES ===
git add ANALYZED_FILES_REPORT.json
git add CRITICAL_FILES_LIST.md
git add METHODOLOGY_GUIDE_COMPACT.md
git add OPERATION_TEMPLATES.md
git add CONTINUATION_PLAN.md
git add WAVE1_ANALYSIS_22_FILES.md
git add WAVE1_REMAINING_18_FILES.json
git add WAVE1_COMPLETION_STATUS.md
git add WAVE1_COMBINED_SUMMARY.md

echo.
echo === COMMITTING ===
git commit -m "docs: Complete Wave 1 audit (80/80 files)" -m "" -m "- Claude: 48+18=66 files analyzed" -m "- Koda: 14 files analyzed" -m "- Created handover documentation" -m "- Identified 20 critical files" -m "- Detected 5 conflicts" -m "- Wave 1 complete: 80/80 (100%%)" -m "" -m "Deliverables:" -m "- ANALYZED_FILES_REPORT.json (48 files)" -m "- WAVE1_REMAINING_18_FILES.json (18 files)" -m "- CRITICAL_FILES_LIST.md (16 protected files)" -m "- METHODOLOGY_GUIDE_COMPACT.md" -m "- OPERATION_TEMPLATES.md" -m "- CONTINUATION_PLAN.md" -m "- WAVE1_COMPLETION_STATUS.md"

echo.
echo === PUSHING ===
git push

echo.
echo === DONE ===
pause
