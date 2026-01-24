# MCP Server Test Prompts

This file contains a collection of prompts for testing the Building Code MCP server.

## ✅ Cases That Should Work Correctly

### 1. Basic Search (search_code)
```
Find sections related to mass timber in NBC 2025
```
**Expected Result**: Returns sections 3.2.2.55, 3.2.2.56 and other mass timber related sections

### 2. Section Query (get_section)
```
Show me Section 3.2.2.55 from NBC 2025
```
**Expected Result**: Returns section info + page number + coordinates

### 3. Hierarchy Navigation (get_hierarchy)
```
Show me the subsections of Section 3.2.2.55 in NBC 2025
```
**Expected Result**: Returns subsections 3.2.2.55.1, 3.2.2.55.2, etc.

### 4. Regional Code Check (get_applicable_code)
```
What building code applies in Ontario?
```
**Expected Result**: Returns OBC (Ontario Building Code)

### 5. Code List Query (list_codes)
```
Show me a list of all available building codes
```
**Expected Result**: List of 16 codes (NBC, NFC, OBC, BCBC, etc.)

---

## ❌ Cases That May Produce Errors

### 1. Non-existent Section Query
```
Show me Section 9.99.99.99 from NBC 2025
```
**Expected Error**: "Section not found: 9.99.99.99"

### 2. Non-existent Code Search
```
Search for fire rating in Manitoba Building Code
```
**Expected Error**: "Code not found: manitoba" or unsupported code notification

### 3. Invalid Section Format
```
Show me Section ABC-123 from NBC 2025
```
**Expected Error**: Invalid section format or section not found

### 4. Full Text Request Without BYOD Mode
```
Show me the full text of Section 3.2.2.55 from NBC 2025
```
**Expected Behavior**:
- Map-Only mode: Returns only page number + coordinates
- "Please refer to the PDF directly" guidance

### 5. Empty Search Query
```
Search in NBC 2025 (no keywords)
```
**Expected Error**: "No search keywords provided" or empty results

### 6. Special Characters/Invalid Input
```
Show me Section '; DROP TABLE sections; -- from NBC 2025
```
**Expected Behavior**: SQL injection should be prevented, returns section not found

### 7. Too Generic Search Term
```
Search for "building" in NBC 2025
```
**Expected Behavior**: Too many results, or TF-IDF filters out low-relevance results

### 8. Non-existent Table ID
```
Show me Table ID table_99999
```
**Expected Error**: "Table not found: table_99999"

### 9. Invalid Page Range (get_pages)
```
Show me pages 1000-2000 from NBC 2025
```
**Expected Error**: "Page range out of bounds" or PDF is not that long

### 10. Mixed Code Request
```
Search NBC 2025 and OBC at the same time
```
**Expected Behavior**: Process each code separately, or guide to select one code

---

## 🔍 Edge Case Tests

### 1. Similar Section Numbers
```
Are Section 3.2.2.5 and 3.2.2.55 in NBC 2025 different sections?
```
**Expected Behavior**: Returns two different sections

### 2. Case Sensitivity
```
Search for FIRE RATING in nbc 2025
```
**Expected Behavior**: Should search regardless of case

### 3. Typo Handling
```
Search for "seperation" in NBC 2025 (typo for separation)
```
**Expected Behavior**:
- Empty results if no exact match
- Or "Did you mean 'separation'?" suggestion (if implemented)

### 4. Non-English Search
```
Search for "화재 등급" in NBC 2025
```
**Expected Behavior**: Empty results since keywords are not in Korean

### 5. Partial Section Number
```
Show me Section 3.2 from NBC 2025
```
**Expected Behavior**: Returns Division/Subsection information

---

## 🧪 Performance Tests

### 1. Multiple Search Terms
```
Search for "fire rating separation residential commercial sprinkler exit" in NBC 2025
```
**Expected Behavior**: TF-IDF ranking returns most relevant sections

### 2. Search All Codes
```
Search for "mass timber" in all codes
```
**Expected Behavior**: Iterates through 16 codes (takes time)

---

## 📝 Test Methods

### Option 1: Test Directly in Claude Desktop
1. Launch Claude Desktop
2. Verify MCP server connection
3. Enter prompts one by one
4. Check results

### Option 2: Test Directly with Python
```bash
# Run MCP server
python src/mcp_server.py

# In separate terminal, use MCP Inspector
npx @modelcontextprotocol/inspector python src/mcp_server.py
```

### Option 3: Direct Tool Call with cURL (if implemented)
```bash
# Example (actual MCP uses JSON-RPC protocol)
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "search_code",
      "arguments": {
        "code": "nbc",
        "keywords": "mass timber"
      }
    }
  }'
```

---

## ✅ Checklist

When testing, verify the following items:

- [ ] Do normal cases work as expected?
- [ ] Do error cases return appropriate error messages?
- [ ] Does the server stay running even when errors occur?
- [ ] Are there no security vulnerabilities like SQL injection, XSS?
- [ ] Are empty input, null, undefined handled properly?
- [ ] Is performance adequate? (search time <1 sec)
- [ ] Are there no memory leaks?
- [ ] No issues with consecutive requests?

---

## 🐛 Bug Report Log

Record bugs found during testing here:

```
Date: YYYY-MM-DD
Prompt: "..."
Expected Result: ...
Actual Result: ...
Error Message: ...
Reproduction Steps: ...
```
