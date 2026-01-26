# GPT App Files

Files for the ChatGPT GPTs app

## File Structure

```
gpt/
├── README.md                    # This file
├── GPT_INSTRUCTIONS_v2.6.md     # Latest! (Thorough + Tables)
├── GPT_INSTRUCTIONS_v2.5.md     # Previous version
├── GPT_INSTRUCTIONS_v2.4.md     # Previous version
├── GPT_SYSTEM_PROMPT.md         # Detailed documentation (reference)
└── extractor.py                 # Python helper (v2.6 - table extraction!)
```

## v2.6 Setup (Latest - Thorough + Tables)

### 1. Knowledge Upload Files
```
extractor.py          # Python helper (required!)
maps/OBC_Vol1.json
maps/OBC_Vol2.json
maps/NBC2025.json
... (required JSON files)
```

### 2. GPT Configuration Steps
1. ChatGPT → Explore GPTs → Create
2. Configure tab
3. Name: `Canadian Building Code Navigator`
4. Knowledge: Upload `extractor.py` + JSON files (**Re-upload v2.6 extractor.py required!**)
5. Code Interpreter: ✅ Check
6. Instructions: Copy-paste contents of `GPT_INSTRUCTIONS_v2.6.md`
7. Save → Anyone with link

## Version Comparison

| Version | Time Budget | Search | Tables | Speed | Accuracy |
|---------|-------------|--------|--------|-------|----------|
| v2.0-2.1 | None | Unlimited | ❌ | Slow | Frequent errors |
| v2.2-2.3 | None | Unlimited | ❌ | Medium | High |
| v2.4 | None | Unlimited | ❌ | 3min+ | Medium |
| v2.5 | 90s | 1x | ❌ | 56s | High (some misses) |
| **v2.6** | **120s** | **2x** | **✅** | **1-2min** | **Very High** |

## v2.6 Key Improvements (Latest)

### 1. Relaxed Time Budget + 2-Phase Search

**Problem (v2.5):**
- 90s Time Budget too tight → Unable to search accurately
- 1x search limit → Missing important sections (e.g., W360x41 steel section)

**Solution:**
- Time Budget: 90s → **120s (2 min)**
- **2-Phase Search Strategy**:
  - Phase 1: Specific keyword search
  - Phase 2: If insufficient results, re-search with broader keywords
  - "Better 2 min + accurate than 1 min + missing info"

```python
# Phase 1: Specific
results = search_json(data, "foundation column design")[:4]

# Phase 2: If < 3 good results
if len(results) < 3:
    results2 = search_json(data, "structural Part 4")[:4]
    results = results + results2
```

### 2. Table Data Support

**Why:** AEC professionals frequently need table data
- Live load tables, fire ratings, span tables, material properties

**Implementation:**
```python
# Extract table from JSON (fast!)
from extractor import extract_table

table = extract_table(data, "4.1.5.3")
print(table["markdown"])  # Formatted table

# Batch tables
from extractor import extract_tables_batch
tables = extract_tables_batch(data, ["4.1.5.3", "9.10.14.4"])
```

**Output Example:**
```
**NBC Table 4.1.5.3** - Live Loads on Floors (p.452)

| Load Type | Residential | Office | Storage |
|-----------|-------------|--------|---------|
| Uniform   | 1.9 kPa     | 2.4 kPa | 4.8 kPa |

Source: JSON (pre-indexed)
```

**Expected Results:**
- Speed: 56s (v2.5 simple) → 1-2min (v2.6 complex)
- Accuracy: High → **Very High** (fewer missed sections)
- Tables: ❌ → ✅ (1,200+ tables supported)

## Testing

```
Question 1 (Simple - baseline):
"What is the guard height for stairs in OBC?"
→ Within 60s, Section ID + page + PDF citation

Question 2 (Complex - time budget test):
"New Brunswick 20-storey residential foundation, column sizing requirements?"
→ Within 120s, 4-6 sections + PDF citation
→ Verify 2-phase search operation

Question 3 (Follow-up - context retention):
"Can I use W360x41 for column sizing?"
→ Within 60s
→ Verify "W360x41 not standard, suggest W360x39/44"
→ Reuse previous answer context

Question 4 (Table - new feature):
"Show me NBC live load table for residential buildings"
→ Within 60s
→ Display Table 4.1.5.3 in markdown
→ Show Source: JSON

Question 5 (Multi-table - batch test):
"Compare fire resistance ratings for different construction types"
→ Within 90s
→ 2-3 tables in markdown
→ Verify extract_tables_batch() usage

Checklist:
✅ 2-phase search working (when needed)
✅ Batch extraction used (extract_sections_batch / extract_tables_batch)
✅ > "..." citation format
✅ Table markdown display
✅ Follow-up question prompt at the end
```

## Reference

- Latest Instructions: `GPT_INSTRUCTIONS_v2.6.md`
- Detailed Documentation: `GPT_SYSTEM_PROMPT.md`
- Version History: v2.0 (bbox) → v2.3 (Section ID) → v2.5 (Batch) → v2.6 (Thorough + Tables)
- Table Infrastructure: 1,200+ tables indexed (NBC, OBC, and all codes)
