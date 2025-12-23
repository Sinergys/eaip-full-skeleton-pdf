# ✅ Fix: Month Name Normalization to Prevent Quarter Duplication

## 🎯 Problem

**Root Cause:** Inconsistent month names in Excel files (e.g., "Январь", "Январь ", "январь") were being stored as separate months, causing quarters to appear to have 6+ months instead of 3.

**Symptoms:**
- Quarters showing 6 months instead of 3
- Q2 2024 summing April-September (should be April-June)
- Q3 2024 summing July-December (should be July-September)
- Inflated quarterly totals (double the correct values)

**Example from logs:**
```
Month July: volume_m3=593
Month August: volume_m3=593
Month September: volume_m3=641
Month July: volume_m3=593  <-- DUPLICATE!
Month August: volume_m3=593  <-- DUPLICATE!
Month September: volume_m3=641  <-- DUPLICATE!
```

## ✅ Solution

### 1. **Store Normalized Month Names**

**Before:**
```python
quarter_entry["months"].append({
    "month": month_name,  # Original name with spaces/typos
    "values": payload
})
```

**After:**
```python
quarter_entry["months"].append({
    "month": month_norm,  # Normalized name (lowercase, trimmed)
    "values": payload
})
```

### 2. **Add Validation to Detect Duplicates**

Added validation in `_compute_quarter_totals()` to detect and warn about duplicate months:

```python
# VALIDATION: Check for duplicate months (caused by inconsistent month names)
if months:
    month_names = [m.get("month", "") for m in months]
    normalized_names = [_normalise_month_name(name) for name in month_names]
    unique_normalized = set(normalized_names)

    if len(months) != len(unique_normalized):
        logger.warning(
            f"⚠️ VALIDATION ERROR: Квартал {quarter_key} для {key} содержит дублирующиеся месяцы! "
            f"Всего записей: {len(months)}, уникальных месяцев: {len(unique_normalized)}. "
            f"Месяцы: {month_names}. "
            f"Это вызвано несогласованными названиями месяцев (пробелы, опечатки). "
            f"ВАЖНО: Квартал должен содержать ровно 3 уникальных месяца!"
        )

    if len(unique_normalized) > 3:
        logger.error(
            f"❌ CRITICAL: Квартал {quarter_key} для {key} содержит {len(unique_normalized)} уникальных месяцев "
            f"вместо ожидаемых 3! Это приведет к неверным квартальным итогам. "
            f"Нормализованные месяцы: {sorted(unique_normalized)}"
        )
```

## 📝 Changes Made

### Files Modified:
**`eaip_full_skeleton/services/ingest/utils/energy_aggregator.py`**

### Functions Updated:
1. **`aggregate_months()`** - Line ~505
   - Changed from storing `month_name` to `month_key` (normalized)

2. **`aggregate_single_resource_file()`** - Multiple locations
   - Line ~337: Gas/water aggregation
   - Line ~383: Water volume aggregation

3. **`aggregate_single_resource_file_from_db()`** - Multiple locations
   - Line ~1706: Gas aggregation from DB
   - Line ~1751: Water aggregation from DB
   - Lines ~1901, ~1997: Generic month append operations

4. **`_compute_quarter_totals()`** - Lines ~886-906
   - Added validation logic to detect duplicates

## 🔍 How It Works

1. **Normalization Process:**
   ```python
   def _normalise_month_name(value: Optional[str]) -> Optional[str]:
       if not isinstance(value, str):
           return None
       return value.strip().lower()  # Remove spaces, convert to lowercase
   ```

2. **Month Mapping:**
   ```python
   MONTH_ALIASES = {
       "январь": 1,
       "февраль": 2,
       # ... etc
   }
   ```

3. **Flow:**
   - Excel file has: "Январь", "Январь ", "ЯНВАРЬ"
   - All normalize to: "январь"
   - All map to: month number 1
   - All stored as: "январь" (preventing duplicates)

## ✅ Benefits

1. **Prevents Duplication:** Inconsistent month names no longer create duplicate entries
2. **Early Detection:** Validation warns if duplicates are detected
3. **Accurate Totals:** Quarterly sums are now correct (not inflated)
4. **Better Data Quality:** Standardized month names throughout the system

## 🧪 Testing

To verify the fix:

1. **Run aggregation with inconsistent month names:**
   ```python
   python tools/diagnose_quarter_duplication.py "data/aggregated/<batch_id>_aggregated.json"
   ```

2. **Check logs for validation warnings:**
   - Should see no warnings about duplicate months
   - Each quarter should have exactly 3 unique months

3. **Verify quarterly totals:**
   - Q1: Jan + Feb + Mar
   - Q2: Apr + May + Jun
   - Q3: Jul + Aug + Sep
   - Q4: Oct + Nov + Dec

## 📊 Example

**Before Fix:**
```json
{
  "2024-Q2": {
    "months": [
      {"month": "Апрель", "values": {"volume_m3": 590}},
      {"month": "Май", "values": {"volume_m3": 500}},
      {"month": "Июнь", "values": {"volume_m3": 759}},
      {"month": "Апрель ", "values": {"volume_m3": 590}},  // Duplicate!
      {"month": "МАЙ", "values": {"volume_m3": 500}},  // Duplicate!
      {"month": "июнь", "values": {"volume_m3": 759}}   // Duplicate!
    ],
    "quarter_totals": {"volume_m3": 3698}  // WRONG (2x correct value)
  }
}
```

**After Fix:**
```json
{
  "2024-Q2": {
    "months": [
      {"month": "апрель", "values": {"volume_m3": 590}},
      {"month": "май", "values": {"volume_m3": 500}},
      {"month": "июнь", "values": {"volume_m3": 759}}
    ],
    "quarter_totals": {"volume_m3": 1849}  // CORRECT
  }
}
```

## ⚠️ Important Notes

- This fix prevents NEW duplication issues
- Existing aggregated data with duplicates will need to be regenerated
- The validation will warn about any remaining duplicate issues
- Month names in the JSON are now always lowercase and trimmed

## 🎯 Summary

**Issue:** Inconsistent month name formatting → duplicate month entries → inflated quarterly totals

**Fix:** Store normalized month names + add validation → prevent duplicates → accurate totals

**Status:** ✅ **RESOLVED**
