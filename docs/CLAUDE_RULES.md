# Claude Desktop Configuration for Token Efficiency

> Copy these rules to your `~/.claude/CLAUDE.md` for optimal MCP token usage

---

## Location

Add this section to your global Claude configuration file:

**Windows:** `C:\Users\[YourName]\.claude\CLAUDE.md`
**macOS/Linux:** `~/.claude/CLAUDE.md`

If the file doesn't exist, create it.

---

## Rules to Copy

```markdown
### MCP Token Efficiency (Building Code MCP)

#### ⚠️ 3-Strike Rule (Important!)
- **Same topic: Maximum 3 searches**
- After 3 tries with no results → clearly state "not specified in code"
- Different approaches/topics count separately
- Exception: User explicitly requests ("search more")

#### Pre-Search Planning Required
1. **Clarify goal:** "What exactly am I looking for?"
2. **Select keywords:** 1-2 only (too many causes confusion)
3. **Estimate location:** Part? Division? Section?
4. **Execute → Evaluate → Decide:** Next step or stop

#### Parameter Optimization
- `limit`: 5-10 (use default, increase only if needed)
- `verbose`: **false** (99% of cases, this is default)
- `verbose=true`: Only when metadata truly needed
  - Need keywords context
  - Need bbox coordinates
  - Need match_type confirmation

#### Token Budget (Enforce!)
- **Simple questions:** 100-300 tokens (1-3 searches)
  - Example: "guard height?", "which code?"
- **Complex questions:** 500-1000 tokens (3-5 searches)
  - Example: "fire separation requirements?"
- **⚠️ 1500+ usage:** Must review strategy
  - Search method is inefficient
  - Should break question into parts

#### Decision Criteria: When to Stop?
- ✅ **Same results after 2 searches** → Stop
- ✅ **"0 results" twice** → Try different approach or give up
- ✅ **Found target section** → Verify with get_section, then stop
- ❌ **Infinite repetition with different keywords** → Forbidden!

#### Real Case Study (Learning from Mistakes)

**❌ Bad Example: Balcony dimension search**
```
1. search("balcony width residential") → 15 results
2. search("balcony dimension") → 15 results
3. search("balcony residential") → 15 results
4. search("exit balcony") → 10 results
... (29 total searches)
Result: 5,100 tokens wasted, answer was "not specified in OBC"
```

**✅ Good Example: Improved search**
```
1. search("balcony residential", limit=5) → 5 results, found B-3.2.2.11
2. get_section("B-3.2.2.11") → structural requirements only, no dimensions
3. Conclusion: "Dimensions not specified in OBC. Check municipal bylaws."
Result: 150 tokens (97% reduction), same or clearer answer
```

#### Handling Complex Questions
When question requires multiple requirements:
1. **Notify user first**
   - "This question requires checking multiple sections (10-15 searches, ~1000 tokens)"
   - "Continue?"
2. **If approved:** Budget can be expanded
3. **If declined:** Break question into parts
```

---

## Why This Matters

### Before Optimization
- Average: 5,100 tokens per question
- 29 MCP calls
- 10-15 second response time

### After Optimization
- Average: 150-300 tokens per question
- 3-5 MCP calls
- 2-3 second response time
- **97% token reduction**

---

## Testing Your Setup

After adding the rules, test with simple questions:

1. **Simple test:** "What is the guard height in OBC?"
   - Target: 1-2 searches, ~100 tokens

2. **Medium test:** "Fire separation requirements for 5-storey residential?"
   - Target: 3-5 searches, ~400 tokens

3. **Complex test:** "All egress requirements for Toronto commercial building?"
   - Target: 5-8 searches, ~800 tokens (after user approval)

---

## Troubleshooting

### Claude still using too many tokens?

1. **Check if file is being read**
   - Restart Claude Desktop after editing
   - Verify file location is correct

2. **Make rules more explicit**
   - Add "⚠️ CRITICAL:" prefix
   - Emphasize token budget

3. **Provide immediate feedback**
   - When you see excessive searches, say "Let's review the 3-Strike Rule"

### Answer quality decreased?

Don't worry! Token reduction ≠ quality loss
- Actually more concise and clear
- Can always use `verbose=true` when needed
- Focus prevents information overload

---

## Version History

- **v1.1.1 (2026-01-23):** Initial token efficiency rules
- **Future (v1.2.0):** Server-side hints will complement these rules

---

## Additional Resources

- [Full Token Efficiency Guide](TOKEN_EFFICIENCY.md)
- [PyPI Package](https://pypi.org/project/building-code-mcp/)
- [GitHub Repository](https://github.com/DavidCho1999/Canada_building_code_mcp)

---

_These rules help Claude use the MCP server more efficiently while maintaining answer quality._
