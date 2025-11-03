# stdlib Docstring Enrichment Research

**Issue**: Research options to add more docstrings to stdlib stubs  
**Status**: ✅ Research Complete  
**Date**: 2025-11-03

## Quick Links

📋 **Start Here**: [`research_summary_stdlib_docstrings.md`](./research_summary_stdlib_docstrings.md)  
📚 **Full Details**: [`research_stdlib_docstrings.md`](./research_stdlib_docstrings.md)  
🔧 **Implementation**: [`implementation_guide_stdlib_docstrings.md`](./implementation_guide_stdlib_docstrings.md)

## What Was Researched

This research investigated three approaches to enrich MicroPython stdlib stubs with better type information and docstrings from CPython/typeshed sources:

1. **Option A**: Extract types from Pyright/BasedPyright typeshed (types only)
2. **Option B**: Generate stubs from CPython source (includes docstrings)
3. **Option C**: Hybrid approach combining both (RECOMMENDED)

## Key Findings

✅ **Technical Feasibility**: PROVEN - Working proof-of-concept scripts demonstrate both typeshed extraction and CPython docstring extraction  
✅ **Infrastructure Ready**: Existing `merge_docstub.py` can be enhanced for this purpose  
✅ **Preservation Possible**: MicroPython-specific docstrings can be preserved during merge  
⚠️ **Typeshed Caveat**: Intentionally excludes docstrings (maintenance policy)  
⭐ **Recommendation**: Hybrid approach for best results with acceptable risk

## Recommended Approach

**Hybrid Strategy** combining:
- Type information from pyright/basedpyright typeshed
- Docstrings from CPython runtime introspection
- Existing merge infrastructure with enhanced preservation rules

**Critical Preservation Rules**:
1. NEVER overwrite MicroPython-specific docstrings
2. ADD CPython docstrings only where none exist
3. FLAG conflicts for manual review
4. TRACK source versions in metadata

## Deliverables

### Documentation
- ✅ Executive summary (6KB) - For stakeholders
- ✅ Full research document (13KB) - Technical deep-dive
- ✅ Implementation guide (7KB) - For next developer

### Proof-of-Concept Code
- ✅ `extract_typeshed_poc.py` - Extracts from npm packages
- ✅ `extract_cpython_docstrings.py` - Extracts CPython docs
- ✅ Both tested and working on sample modules

### Test Results
```
✅ Extracted typeshed stubs can be located and copied
✅ CPython docstrings successfully extracted (json, sys)
✅ Output format suitable for merging
✅ 41 functions with docstrings from 2 test modules
```

## Implementation Phases

**Phase 1: PoC** ✅ (Complete - 1 week)
- Research and validation
- Working extraction scripts
- Approach recommendation

**Phase 2: Automation** (Pending Approval - 2-3 weeks)
- Move scripts to project
- Enhance merge logic
- Add tests

**Phase 3: Integration** (Pending - 1-2 weeks)
- CI/CD integration
- Documentation
- Make optional feature

**Phase 4: Maintenance** (Ongoing)
- Regular updates
- Review workflow
- Version tracking

## Decision Points

**Stakeholders need to decide:**

1. ✅ Approve hybrid approach?
2. ❓ Which modules to enrich first?
3. ❓ Make enrichment optional or default?
4. ❓ Update frequency?
5. ❓ Authorize Phase 2 implementation?

## Benefits

### For Users
- Better IDE experience (tooltips, autocomplete)
- More comprehensive documentation
- Clearer API compatibility

### For Project
- Leverages well-maintained sources
- Reduces documentation burden
- Improves professional appearance
- Enhances CPython parity

## Files in This Research

```
docs/
├── README_stdlib_docstrings.md          (this file)
├── research_summary_stdlib_docstrings.md (executive summary)
├── research_stdlib_docstrings.md         (full research)
└── implementation_guide_stdlib_docstrings.md (dev guide)

/tmp/
├── extract_typeshed_poc.py              (working PoC)
└── extract_cpython_docstrings.py        (working PoC)
```

## How to Use This Research

### For Stakeholders
1. Read [`research_summary_stdlib_docstrings.md`](./research_summary_stdlib_docstrings.md)
2. Review decision points
3. Provide feedback/approval

### For Implementers
1. Read summary and full research
2. Review PoC scripts
3. Follow [`implementation_guide_stdlib_docstrings.md`](./implementation_guide_stdlib_docstrings.md)
4. Start with Phase 2 checklist

### For Reviewers
1. Check technical feasibility claims against PoC scripts
2. Review preservation rules and risk mitigations
3. Validate approach against project goals

## Example Output

**Before** (MicroPython minimal):
```python
def dumps(obj) -> str: ...
```

**After** (enriched with types + docstrings):
```python
def dumps(obj: Any, separators: tuple[str, str] | None = ...) -> str:
    """
    Serialize ``obj`` to a JSON formatted ``str``.
    
    If ``separators`` is specified, it should be a tuple of 
    (item_separator, key_separator).
    
    Note: MicroPython has limited support for some JSON features.
    """
    ...
```

## Next Steps

1. **Review**: Stakeholders review documents
2. **Decide**: Approve approach and scope
3. **Authorize**: Green-light Phase 2
4. **Implement**: Follow implementation guide
5. **Test**: Validate on subset of modules
6. **Deploy**: Roll out to applicable modules

## References

- **BasedPyright**: https://docs.basedpyright.com/
- **Typeshed**: https://github.com/python/typeshed
- **Python Inspect**: https://docs.python.org/3/library/inspect.html
- **PEP 484** (Type Hints): https://www.python.org/dev/peps/pep-0484/
- **PEP 561** (Distributing Types): https://www.python.org/dev/peps/pep-0561/

## Questions?

- See full research for detailed technical answers
- Check implementation guide for how-to questions
- Review PoC scripts for code examples

---

**Research Status**: ✅ Complete  
**Recommendation**: Clear and actionable  
**Technical Risk**: Low (proven with PoCs)  
**Implementation Ready**: Yes (awaiting approval)
