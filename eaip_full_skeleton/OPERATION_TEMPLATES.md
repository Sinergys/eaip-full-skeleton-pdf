# OPERATION TEMPLATES
## Standard Procedures for File Operations

**Version:** 1.0  
**Date:** 11 December 2025

---

## TEMPLATE 1: MERGE

### When to Use:
- Multiple files cover same topic
- Content duplication detected
- Consolidation improves clarity

### Pre-Merge Checklist:
- [ ] Identify primary file (most complete/recent)
- [ ] List all files to merge
- [ ] Extract unique content from each
- [ ] Identify conflicts in content
- [ ] Plan merged structure

### Execution Steps:
```bash
# 1. Backup all files
cp file1.md file1.md.backup
cp file2.md file2.md.backup

# 2. Create merged file
cat > merged_file.md << 'EOF'
# [Title from primary file]
[Content from primary]
## [Unique sections from file2]
[Content from file2]
EOF

# 3. Update cross-references
grep -r "file1.md" docs/ | # find references
sed -i 's/file1.md/merged_file.md/g' [files with references]

# 4. Move old files to archive
mkdir -p archive/merged_$(date +%Y%m%d)
mv file1.md archive/merged_$(date +%Y%m%d)/
mv file2.md archive/merged_$(date +%Y%m%d)/
```

### Real Example (AI Config Files):
```bash
# MERGE: AI_QUICK_START.md + AI_SETUP_QUICK_GUIDE.md + AI_CONFIGURATION_GUIDE.md
# → AI_SETUP_MASTER.md

# Extract:
# - Quick start steps from AI_QUICK_START
# - Detailed procedures from AI_SETUP_QUICK_GUIDE  
# - Full variable tables from AI_CONFIGURATION_GUIDE

# Result: Single comprehensive AI setup document
```

---

## TEMPLATE 2: DELETE

### When to Use:
- True duplicate (exact copy)
- Obsolete/superseded
- No unique value

### Pre-Delete Checklist:
- [ ] Confirm NOT imported by code
- [ ] Confirm NOT referenced in docs
- [ ] Verify newer version exists
- [ ] Check git history value
- [ ] Team approval (if CRITICAL)

### Execution Steps:
```bash
# 1. Final verification
grep -r "filename.ext" . | grep -v ".git"

# 2. Git check
git log --follow filename.ext  # check history value

# 3. Backup (just in case)
mkdir -p deleted_$(date +%Y%m%d)
cp filename.ext deleted_$(date +%Y%m%d)/

# 4. Delete
git rm filename.ext
git commit -m "docs: remove obsolete filename.ext (superseded by new_file.ext)"
```

### Real Example (TZ duplicate):
```bash
# DELETE: docs/EAIP_TZ_for_Cursor.txt
# REASON: Exact duplicate of EAIP_TZ_for_Cursor.md

# Verification:
diff EAIP_TZ_for_Cursor.txt EAIP_TZ_for_Cursor.md
# Result: Files identical

# Safe to delete
git rm docs/EAIP_TZ_for_Cursor.txt
```

---

## TEMPLATE 3: MOVE (Archive)

### When to Use:
- Outdated but historical value
- Intermediate versions
- Old reports/status docs

### Pre-Move Checklist:
- [ ] Confirm outdated
- [ ] Identify historical value
- [ ] Plan archive location
- [ ] Update any references

### Execution Steps:
```bash
# 1. Create archive structure
mkdir -p docs/archive/[category]/YYYY-MM/

# 2. Move with date suffix
mv old_file.md docs/archive/[category]/YYYY-MM/old_file_YYYYMMDD.md

# 3. Update references (if any)
find . -name "*.md" -exec sed -i 's|old_file.md|archive/[category]/YYYY-MM/old_file_YYYYMMDD.md|g' {} \;

# 4. Create README in archive
cat > docs/archive/[category]/README.md << 'EOF'
# Archived [Category] Files
## [Month Year]
- old_file_YYYYMMDD.md - [Reason for archiving]
EOF
```

### Real Example (Status Reports):
```bash
# MOVE: docs/PROJECT_FULL_STATUS_REPORT.md
# TO: docs/archive/status_reports/2025-11/PROJECT_FULL_STATUS_REPORT_20251113.md

mkdir -p docs/archive/status_reports/2025-11
mv docs/PROJECT_FULL_STATUS_REPORT.md \
   docs/archive/status_reports/2025-11/PROJECT_FULL_STATUS_REPORT_20251113.md
```

---

## TEMPLATE 4: UPDATE

### When to Use:
- Content needs revision
- Sync with current state
- Fix errors/outdated info

### Pre-Update Checklist:
- [ ] Identify what needs updating
- [ ] Check current state (code/config)
- [ ] Plan changes
- [ ] Backup original

### Execution Steps:
```bash
# 1. Backup
cp file.md file.md.before_update

# 2. Make changes
vim file.md  # or your editor

# 3. Track changes
git diff file.md  # review changes

# 4. Commit with clear message
git add file.md
git commit -m "docs: update file.md - [specific changes]"
```

### Real Example (API Docs):
```bash
# UPDATE: docs/API_DOCUMENTATION.md
# REASON: Sync with actual endpoints

# Steps:
1. Review all services/*/main.py for current endpoints
2. Update endpoint list in API_DOCUMENTATION.md
3. Add new endpoints
4. Remove deprecated endpoints
5. Update request/response examples
```

---

## CONFLICT RESOLUTION

### Version Conflicts:
```bash
# When: file_v1.md, file_v2.md, file_v3.md exist
# Action: Keep newest, archive rest

# Identify newest
ls -lt file*.md | head -1

# Archive old versions
mkdir -p archive/versions/
mv file_v1.md archive/versions/file_v1_YYYYMMDD.md
mv file_v2.md archive/versions/file_v2_YYYYMMDD.md
```

### Content Contradictions:
```bash
# When: Two files have different facts on same topic
# Action: Verify source of truth, update/delete wrong one

# 1. Identify correct information (check code, tests, data)
# 2. Update correct file if needed
# 3. Delete or archive incorrect file
# 4. Add note explaining resolution
```

---

## ROLLBACK PROCEDURES

### If operation causes problems:

**MERGE rollback:**
```bash
cp archive/merged_[date]/file1.md docs/
cp archive/merged_[date]/file2.md docs/
git rm merged_file.md
```

**DELETE rollback:**
```bash
cp deleted_[date]/filename.ext docs/
git add docs/filename.ext
git commit -m "restore: rollback deletion of filename.ext"
```

**MOVE rollback:**
```bash
mv docs/archive/[path]/file.md docs/
# Update any references back
```

---

**Template Version:** 1.0  
**Last Updated:** 11 December 2025
