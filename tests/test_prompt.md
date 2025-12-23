# Word Document Validator - Testing & Validation Phase

## Context
Architecture fixes have been implemented in previous session. Now we need to test the fixes with real document to verify they work correctly.

## Test File
**File:** `C:\Users\DELL\Desktop\Navoiy IES\test full.docm`
**Expected:** Complete object preservation and proper restoration

## Testing Tasks

### Task 1: Verify Service is Running
```bash
# Check if validate service is running
curl http://localhost:8003/health
```

### Task 2: Process Test Document
```bash
# Send document for processing
curl -X POST "http://localhost:8003/api/v1/check-report/" \
  -F "file=@C:\Users\DELL\Desktop\Navoiy IES\test full.docm" \
  --max-time 1800  # 30 minutes timeout
```

### Task 3: Analyze Results
```bash
# Check output file
dir \tmp\test full_Проверенный.docx
# Verify file size (should be close to input size)
```

### Task 4: Validation Checks
**Check these critical metrics:**
1. **File Size:** Input ≈ Output (no 10x reduction)
2. **Processing Time:** Reasonable (not too fast/long)
3. **No Errors:** Clean processing without failures
4. **Object Restoration:** All images/tables/diagrams present

### Task 5: Compare with Previous Results
**If previous test showed:**
- File size: 3.7MB (was 30MB input)
- Objects: Partial restoration
- Order: Mixed up

**Expected now:**
- File size: Close to original (within 20% margin)
- Objects: Complete restoration (all objects)
- Order: Proper sequence maintained

## Success Criteria
✅ File size not dramatically reduced
✅ Processing completes successfully  
✅ All objects visible in output
✅ No critical errors in logs

## If Issues Found
Document specific problems:
- File size still reduced dramatically?
- Objects still missing?
- Processing errors?
- Performance issues?

## Commands to Run
Execute these commands in order and report results:

1. **Health Check:**
```bash
curl http://localhost:8003/health
```

2. **Document Processing:**
```bash
curl -X POST "http://localhost:8003/api/v1/check-report/" -F "file=@C:\Users\DELL\Desktop\Navoiy IES\test full.docm"
```

3. **Result Verification:**
```bash
dir \tmp\test full_Проверенный.docx
```

4. **File Comparison:**
- Check input file size vs output file size
- Calculate size ratio (should be close to 1.0, not 0.1)

## Report Format
Provide results in this format:
- **Input File:** [size] 
- **Output File:** [size]
- **Size Ratio:** [output/input]
- **Processing Time:** [seconds]
- **Status:** [Success/Failed]
- **Objects Visible:** [Yes/No]
- **Issues Found:** [List any problems]

## Language
Respond in Russian, but technical terms can remain in English.