# Quick Start: Implementing stdlib Docstring Enrichment

**For the developer who implements this research**

## Before You Start

✅ Read `docs/research_summary_stdlib_docstrings.md` (5 min)  
✅ Skim `docs/research_stdlib_docstrings.md` (15 min)  
✅ Review PoC scripts in `/tmp/extract_*.py` (10 min)

## Implementation Checklist

### Phase 1: Setup (Already Complete ✅)
- [x] Research completed
- [x] Approach selected (Hybrid)
- [x] PoC scripts created and tested

### Phase 2: Build Automation (Next Steps)

#### 2.1 Setup npm Integration
```bash
# Add to project root
npm init -y
npm install basedpyright --save-dev
```

#### 2.2 Move PoC Scripts to Project
```bash
# Move from /tmp to permanent location
mkdir -p scripts/enrichment
cp /tmp/extract_typeshed_poc.py scripts/enrichment/
cp /tmp/extract_cpython_docstrings.py scripts/enrichment/
```

#### 2.3 Create Master Enrichment Script
```bash
# Create: scripts/enrichment/enrich_stdlib.py
# This should:
# 1. Run extract_typeshed_poc.py
# 2. Run extract_cpython_docstrings.py  
# 3. Call merge_docstub.py with proper flags
# 4. Validate results
```

#### 2.4 Enhance merge_docstub.py
Add these features if not present:
- [ ] `--preserve-micropython-docs` flag
- [ ] `--add-missing-docstrings` flag
- [ ] Conflict detection and logging
- [ ] Module filtering (allowlist)

#### 2.5 Create Module Allowlist
```python
# In scripts/enrichment/module_allowlist.py
SAFE_MODULES = [
    "json",    # Start with these
    "os",      # Well-tested modules
    "sys",
    # Add more after validation
]
```

### Phase 3: Testing

#### 3.1 Unit Tests
```bash
# Create: tests/enrichment/test_extraction.py
# Test:
# - Typeshed extraction
# - CPython docstring extraction
# - Merge logic
```

#### 3.2 Integration Tests
```bash
# Create: tests/enrichment/test_merge.py
# Test:
# - MicroPython docs preserved
# - CPython docs added where missing
# - No unintended overwrites
```

#### 3.3 Validation Tests
```bash
# Create: tests/enrichment/test_validation.py
# Test:
# - Stubs are valid Python syntax
# - No type check errors
# - Docstrings properly formatted
```

### Phase 4: CI/CD Integration

#### 4.1 Add GitHub Workflow
```yaml
# .github/workflows/enrich-stubs.yml
name: Enrich stdlib stubs
on:
  workflow_dispatch:  # Manual trigger initially
  
jobs:
  enrich:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - uses: actions/setup-python@v4
      - name: Install dependencies
        run: |
          npm install basedpyright
          poetry install
      - name: Run enrichment
        run: |
          python scripts/enrichment/enrich_stdlib.py
      - name: Run tests
        run: |
          poetry run pytest tests/enrichment/
```

#### 4.2 Add to Main Stub Generation
```python
# In src/stubber/commands/docs_stubs.py
# Add option: --enrich-with-cpython
```

## Command Line Usage (After Implementation)

### Extract typeshed stubs
```bash
python scripts/enrichment/extract_typeshed_poc.py \
    --output ./extracted_typeshed \
    --modules json os sys
```

### Extract CPython docstrings
```bash
python scripts/enrichment/extract_cpython_docstrings.py \
    --output ./cpython_docs.json \
    --modules json os sys
```

### Merge into MicroPython stubs
```bash
python -m libcst.tool codemod merge_docstub.MergeCommand \
    --doc-stub ./extracted_typeshed/json.pyi \
    --preserve-micropython-docs \
    ./micropython_stubs/json.pyi
```

### Full enrichment pipeline
```bash
python scripts/enrichment/enrich_stdlib.py \
    --modules json os sys \
    --output ./enriched_stubs/
```

## Key Preservation Rules

**CRITICAL - Never Violate These**:

1. ✅ **Preserve MicroPython docstrings**
   ```python
   # If MicroPython stub has docstring, KEEP IT
   ```

2. ✅ **Add CPython docs only where missing**
   ```python
   # Only add if MicroPython stub has no docstring
   ```

3. ✅ **Flag conflicts for manual review**
   ```python
   # Log: "Conflict: function X has different docs"
   ```

4. ✅ **Preserve MicroPython-specific notes**
   ```python
   # Keep: "Note: MicroPython-specific behavior..."
   ```

## Module Priority List

**Start with (safest):**
1. `json` - Well-defined, stable API
2. `sys` - Mostly compatible
3. `os` - Similar but check for differences

**Then add:**
4. `re` - Regex module
5. `struct` - Binary data
6. `binascii` - Binary/ASCII conversions

**Later (more differences):**
7. `socket` - Check platform differences
8. `ssl` - Limited MicroPython support
9. `io` - Some differences in classes

## Testing Strategy

### Before Each Module
```bash
# 1. Backup current stub
cp stubs/json.pyi stubs/json.pyi.backup

# 2. Run enrichment
python scripts/enrichment/enrich_stdlib.py --modules json

# 3. Diff and review
diff stubs/json.pyi.backup stubs/json.pyi

# 4. Run tests
poetry run pytest tests/ -k json

# 5. Manual verification
poetry run stubber show-config  # Should work
poetry run pyright stubs/json.pyi  # No errors
```

### Validation Checks
```python
# scripts/enrichment/validate.py
def validate_enriched_stub(stub_path):
    checks = [
        check_syntax_valid(),
        check_no_type_errors(),
        check_micropython_docs_preserved(),
        check_docstrings_added(),
    ]
    return all(checks)
```

## Debugging Common Issues

### Issue: "Module not found in typeshed"
```bash
# Check available modules
python scripts/enrichment/extract_typeshed_poc.py --list
```

### Issue: "CPython import failed"
```bash
# Check if module available
python -c "import MODULE_NAME; print('OK')"
```

### Issue: "MicroPython docs overwritten"
```bash
# Check preservation logic in merge_docstub.py
# Look for: copy_docstr flag and condition checks
```

### Issue: "Type errors in enriched stub"
```bash
# Run pyright on output
poetry run pyright stubs/MODULE.pyi --verbose
```

## Success Criteria

✅ All tests pass  
✅ No MicroPython docs lost  
✅ CPython docstrings added where missing  
✅ No syntax or type errors  
✅ Manual spot-check confirms quality  
✅ Documentation updated  

## Resources

### Documentation
- Full research: `docs/research_stdlib_docstrings.md`
- Summary: `docs/research_summary_stdlib_docstrings.md`
- This guide: `docs/implementation_guide_stdlib_docstrings.md`

### Code
- PoC scripts: `/tmp/extract_*.py`
- Existing merge: `src/stubber/codemod/merge_docstub.py`
- Test examples: `tests/codemods/codemod_test_cases/`

### External
- Typeshed: https://github.com/python/typeshed
- BasedPyright: https://docs.basedpyright.com/
- Python inspect: https://docs.python.org/3/library/inspect.html

## Questions?

If stuck, review:
1. The full research document
2. Existing `merge_docstub.py` code
3. Test cases in `tests/codemods/`
4. Similar work in `src/stubber/rst/` (MicroPython doc processing)

Good luck! 🚀
