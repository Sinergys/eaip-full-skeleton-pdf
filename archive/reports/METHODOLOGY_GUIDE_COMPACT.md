# METHODOLOGY GUIDE (Compact)
## EAIP Audit Framework

**Date:** 2025-12-11 | **Analyzed:** 50/391 files

## 1. DEPENDENCY IDENTIFICATION
**Tools:** grep, find, manual inspection  
**Command:** `find . -name "*.py" -exec grep -l "module" {} \;`  
**Key Findings:**
- main.py → 18 imports
- schemas.py → imported by main.py  
- energy_aggregator.py → 6 functions used

## 2. CONFLICT DETECTION
**Type 1: Version** - Multiple files, different dates → Keep newest  
**Type 2: Duplication** - Same content → Keep best, delete others  
**Type 3: Contradictions** - Different facts → Keep source of truth  
**Type 4: Missing** - Listed but absent → Document absence

## 3. OPERATIONS
**KEEP** - Optimal as-is  
**UPDATE** - Needs revision  
**MERGE** - Combine files  
**MOVE** - Relocate/archive  
**DELETE** - Remove permanently

## 4. RISK ASSESSMENT
🔴 **CRITICAL** (16 files) - CI/CD, core code, security  
🟡 **MEDIUM** (20 files) - Services, configs  
🟢 **LOW** (14 files) - Documentation

## 5. QA CHECKLIST
- [ ] Dependencies mapped
- [ ] Conflicts identified  
- [ ] Operation specified
- [ ] Risk assessed
- [ ] Reasoning documented

## 6. LESSONS LEARNED
**Worked:** Dependency-first, concrete operations, risk levels  
**Challenges:** Large files, token limits, missing files  
**Improvements:** Automate scanning, use git history

See full docs: OPERATION_TEMPLATES.md, CRITICAL_FILES_LIST.md
