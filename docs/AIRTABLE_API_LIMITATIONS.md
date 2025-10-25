# Airtable API Limitations - Important Findings

## Summary

During implementation of integration tests for the Airtable schema setup, we discovered a critical limitation of Airtable's Meta API: **table deletion is not supported via API**.

## Investigation Results

### What Works ✅

| Operation | HTTP Method | Endpoint | Status |
|-----------|-------------|----------|--------|
| List bases | GET | `/v0/meta/bases` | ✅ Works (200) |
| Read schema | GET | `/v0/meta/bases/{baseId}/tables` | ✅ Works (200) |
| Create table | POST | `/v0/meta/bases/{baseId}/tables` | ✅ Works (200) |
| Update table | PATCH | `/v0/meta/bases/{baseId}/tables/{tableId}` | ✅ Works (200) |

### What Doesn't Work ❌

| Operation | HTTP Method | Endpoint | Status |
|-----------|-------------|----------|--------|
| Delete table | DELETE | `/v0/meta/bases/{baseId}/tables/{tableId}` | ❌ Returns 404 |

## Test Evidence

```bash
# Attempting to delete a table that EXISTS in the base
URL: https://api.airtable.com/v0/meta/bases/app5go7iUaSsc0uKs/tables/tbl7M6SXhhNExc5vS
Method: DELETE
Response: 404 {"error":"NOT_FOUND"}

# Yet the table clearly exists:
GET /v0/meta/bases/app5go7iUaSsc0uKs/tables
Returns: Table with ID tbl7M6SXhhNExc5vS exists in list
```

## Why This Matters

### For Testing
- **Cannot** automatically clean up test tables
- **Must** manually delete test tables through web interface
- Test framework updated to print cleanup instructions

### For Automation
- Any scripts that create temporary tables need manual cleanup
- Cannot implement "create-process-delete" workflows programmatically
- Need to consider table proliferation in automation design

## Workarounds

### 1. Manual Deletion (Current Approach)
- Create tables with identifiable suffixes (e.g., "_TEST")
- Print list of tables to delete after operations
- User manually deletes through Airtable web interface

### 2. Reuse Tables
- Instead of creating new tables, reuse existing ones
- Clear data instead of deleting tables
- Maintain a pool of reusable test tables

### 3. Separate Test Base
- Use a dedicated Airtable base for testing
- Periodically recreate the entire base manually
- Keeps production base clean

## Impact on Our Project

### Test Suite
✅ **Updated** - Tests now print cleanup instructions:
```
============================================================
⚠️  MANUAL CLEANUP REQUIRED
============================================================
The following test tables were created and must be
manually deleted through the Airtable web interface:

  • Work Experience_TEST (ID: tblVyv8hZiNzTg95A)
  • Personal Details_TEST (ID: tblEennFRGEb8EHel)

Visit: https://airtable.com/app5go7iUaSsc0uKs
============================================================
```

### Schema Setup Script
✅ **No Impact** - The `setup_airtable_schema.py` script creates permanent tables that are meant to stay, so deletion is not needed.

### Future Automation
⚠️ **Consider** - If future scripts need temporary tables:
- Document manual cleanup requirements
- Use descriptive names for easy identification
- Consider data clearing instead of table deletion

## Verification

You can verify this limitation yourself:

```bash
# 1. Create a test table
curl -X POST "https://api.airtable.com/v0/meta/bases/YOUR_BASE_ID/tables" \
  -H "Authorization: Bearer YOUR_PAT" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "API_TEST",
    "fields": [{"name": "Field1", "type": "singleLineText"}]
  }'

# Returns: 200 OK with table ID

# 2. Try to delete it
curl -X DELETE "https://api.airtable.com/v0/meta/bases/YOUR_BASE_ID/tables/TABLE_ID" \
  -H "Authorization: Bearer YOUR_PAT"

# Returns: 404 {"error":"NOT_FOUND"}
```

## References

- **Airtable Meta API Documentation**: https://airtable.com/developers/web/api/introduction
- **Our Investigation**: See diagnostic scripts (now removed) that confirmed this behavior
- **Test Framework**: Updated `tests/conftest.py` to handle this limitation

## Conclusion

This is a **known limitation of Airtable's public API**, not a bug in our code or insufficient permissions. Table deletion must be performed through the Airtable web interface. Our test framework and documentation have been updated accordingly.

---

**Date Discovered**: October 25, 2025  
**Investigated By**: AI Assistant during test suite implementation  
**Confirmed With**: Multiple API endpoint tests with valid PAT

