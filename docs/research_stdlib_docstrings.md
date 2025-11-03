# Research: Adding More Docstrings to stdlib Stubs

**Date:** 2025-11-03  
**Issue:** Add more docstrings to stdlib stubs  
**Status:** Research Complete - Implementation Pending

## Executive Summary

This document presents research findings on options to enrich MicroPython stdlib stubs with docstrings from CPython/typeshed sources. The goal is to improve IDE support by providing better documentation for standard library modules that are compatible between MicroPython and CPython.

## Background

### Current State
- MicroPython-stubber generates stubs from MicroPython RST documentation
- CPython compatibility modules are downloaded from PyPI
- Existing merge infrastructure (`merge_docstub.py`) can merge type information between stubs
- Test case `typeshed_incomplete_pyi` demonstrates merging from CPython-like stubs

### Problem Statement
MicroPython stubs for stdlib-compatible modules lack comprehensive docstrings that could be sourced from CPython's well-documented standard library. This affects IDE experience when developers work with modules that exist in both ecosystems.

## Research Areas

### 1. BasedPyright/Pyright Documentation

**Source:** https://docs.basedpyright.com/dev/development/internals/

#### Key Findings:
- BasedPyright is a fork of Pyright with additional features
- Both bundle typeshed stubs in their npm packages
- Stubs located at: `node_modules/[basedpyright|pyright]/dist/typeshed/`
- Contains stdlib stubs in `typeshed/stdlib/` directory
- Can be extracted programmatically using Node.js/npm

#### Technical Details:
```javascript
// Example extraction approach
const typeshedPath = 'node_modules/basedpyright/dist/typeshed/stdlib/';
// Copy .pyi files from this location
```

### 2. Typeshed Project and Docstring Policy

**Sources:**
- https://github.com/python/typeshed
- https://github.com/python/typeshed/issues/4881
- https://github.com/python/typeshed/issues/12085

#### Key Findings:

**Docstring Policy:**
- Typeshed stubs **intentionally exclude docstrings**
- Primary reason: maintenance burden
- Keeping docstrings in sync with CPython source is difficult
- Risk of documentation drift

**Rationale:**
1. **For Python modules:** IDEs can extract docstrings from runtime source
2. **For C modules:** Runtime docstring extraction is harder, but still preferred over stub docstrings
3. **Type information is the priority:** Stubs focus on accurate type annotations

**Community Discussion:**
- Active debate about C-module docstrings (math, datetime, etc.)
- Some proposals for tool-generated docstrings
- Consensus: maintenance concerns trump convenience

**Related Tools:**
- `stubgen` (mypy): Can generate stubs with `--include-docstrings` flag
- `docify`: Mentioned as tool to enrich stubs with docstrings
- Runtime introspection: Pyright/Pylance use this for builtins

### 3. Extracting Stubs from npm Packages

#### Approach 1: Direct Node.js Extraction

```javascript
const fs = require('fs');
const path = require('path');

function extractTypeshedStubs(destDir) {
    const typeshedPath = path.resolve(
        __dirname, 
        'node_modules/basedpyright/dist/typeshed/stdlib'
    );
    
    // Recursively copy .pyi files
    // Filter for stdlib modules of interest
}
```

#### Approach 2: Python Script After npm Install

```bash
# Install basedpyright
npm install basedpyright

# Extract with Python
python extract_typeshed.py --source node_modules/basedpyright/dist/typeshed
```

### 4. CPython Docstring Sources

#### Option A: Runtime Introspection
```python
import inspect
import json

# Extract docstrings from imported modules
doc = inspect.getdoc(module.function)
```

**Pros:**
- Authoritative source
- Always up-to-date with installed Python
- Can be automated

**Cons:**
- Requires CPython runtime
- Some modules may not be available on all platforms

#### Option B: CPython Source Parsing
- Parse CPython source `.rst` or `.py` files
- Extract docstrings directly
- More complex but comprehensive

#### Option C: Use Existing Tools
- `pydoc`: Can extract documentation
- `sphinx-doc`: Can generate documentation
- May be able to output in structured format

## Proposed Approaches

### Option A: Extract Types from Pyright, Keep MicroPython Docs

**Description:**
Extract type information (parameters, return types) from pyright/basedpyright typeshed stubs and merge into MicroPython stubs while preserving MicroPython-specific docstrings.

**Workflow:**
```
1. npm install basedpyright
2. Extract typeshed stdlib .pyi files
3. Use merge_docstub.py codemod:
   - Copy type annotations from typeshed
   - Preserve MicroPython docstrings
   - Only update where MicroPython lacks types
```

**Pros:**
- Leverages well-maintained type information
- Preserves MicroPython-specific documentation
- Uses existing infrastructure
- No docstring conflicts

**Cons:**
- No new docstrings added (only types)
- May not fully solve the "more docstrings" request

**Recommendation:** Good for type accuracy, but limited docstring improvement.

### Option B: Generate Docstring-Rich Stubs from CPython

**Description:**
Generate stubs directly from CPython standard library with both types and docstrings.

**Workflow:**
```
1. Use stubgen --include-docstrings on CPython stdlib
2. Filter for modules also in MicroPython
3. Merge with existing MicroPython stubs
4. Preserve MicroPython-specific info
```

**Pros:**
- Would include actual docstrings
- Single authoritative source
- Comprehensive coverage

**Cons:**
- stubgen quality varies
- CPython docstrings may not match MicroPython behavior
- Maintenance burden (need to re-generate for each Python version)
- Risk of overwriting important MicroPython documentation

**Recommendation:** Higher risk of documentation conflicts.

### Option C: Hybrid - Types from Pyright + Docstrings from CPython (RECOMMENDED)

**Description:**
Combine the best of both worlds:
1. Extract type information from pyright/basedpyright
2. Extract docstrings from CPython runtime/source
3. Merge both into MicroPython stubs with careful preservation of MicroPython-specific information

**Workflow:**
```
Phase 1: Type Information
1. npm install basedpyright
2. Extract stdlib .pyi files from typeshed
3. Create intermediate "typed but undocumented" stubs

Phase 2: Docstring Enrichment
4. Extract docstrings from CPython runtime (inspect module)
5. Add docstrings to intermediate stubs
6. Create "CPython-enriched" stubs

Phase 3: Merge with MicroPython
7. Use enhanced merge_docstub.py:
   - Copy types and docstrings from CPython-enriched stubs
   - NEVER overwrite existing MicroPython docstrings
   - Add docstrings only where MicroPython stub has none
   - Flag mismatches for manual review
```

**Pros:**
- Best type information (from typeshed)
- Rich docstrings (from CPython)
- Preserves MicroPython-specific documentation
- Flexible merge rules

**Cons:**
- Most complex implementation
- Requires both npm and CPython tools
- Need careful merge logic

**Recommendation:** Best long-term solution if implemented carefully.

## Implementation Recommendations

### Phase 1: Proof of Concept (1-2 weeks)
1. **Select Test Modules**: Choose 2-3 modules (e.g., `json`, `os`, `sys`)
2. **Manual Extraction**: Manually extract from pyright typeshed
3. **Test Merge**: Use existing merge_docstub on test modules
4. **Validate**: Ensure no MicroPython docs are lost

### Phase 2: Automation (2-3 weeks)
1. **npm Extraction Script**: Automate typeshed extraction
2. **Docstring Extraction**: Script to get CPython docstrings
3. **Enhanced Merge Logic**: Update merge_docstub.py if needed:
   - Add `--preserve-micropython-docs` flag
   - Add conflict detection/reporting
   - Add selective module filtering

### Phase 3: Integration (1-2 weeks)
1. **CI/CD Integration**: Add to stub generation workflow
2. **Testing**: Comprehensive tests for merge scenarios
3. **Documentation**: Update developer docs
4. **Configuration**: Allow users to enable/disable enrichment

### Phase 4: Maintenance
1. **Regular Updates**: Script to update from latest pyright/CPython
2. **Review Process**: Manual review of conflicts
3. **Version Tracking**: Track which CPython version docs came from

## Technical Considerations

### 1. Docstring Preservation Rules

**Priority Order (highest to lowest):**
1. MicroPython-specific docstrings (NEVER overwrite)
2. MicroPython-generated docstrings from RST (preserve)
3. CPython docstrings (add only if none exists)
4. Auto-generated placeholders (can replace)

### 2. Module Selection

**Include:**
- Modules in both CPython and MicroPython
- Core stdlib (os, sys, json, re, etc.)
- Well-documented CPython modules

**Exclude:**
- MicroPython-only modules (machine, etc.)
- Modules with significant API differences
- Deprecated CPython modules

### 3. Version Compatibility

**Considerations:**
- MicroPython may target different CPython versions
- Need to specify which CPython version to use
- Document version compatibility in stubs

**Recommendation:**
- Default to CPython 3.11 or 3.12 (current stable)
- Allow configuration for different versions
- Add version markers in comments

### 4. Quality Assurance

**Testing Strategy:**
1. **Unit Tests**: Test merge logic with known inputs
2. **Integration Tests**: Test full workflow
3. **Validation Tests**: 
   - Check no MicroPython docs lost
   - Verify type information correct
   - Ensure stubs are valid Python syntax
4. **Manual Review**: Sample review of merged stubs

### 5. Performance

**Considerations:**
- Stub generation already time-consuming
- Adding this step should be optional
- Cache intermediate results

**Optimization:**
- Only process changed modules
- Parallel processing where possible
- Cache CPython docstring extraction

## Example: Merging `json` Module

### Before (MicroPython stub - minimal):
```python
"""JSON encoding and decoding."""

def dumps(obj) -> str: ...
def loads(s: str): ...
```

### CPython Typeshed (types only):
```python
from typing import Any

def dumps(obj: Any, separators: tuple[str, str] | None = ...) -> str: ...
def loads(s: str) -> Any: ...
```

### CPython Runtime (docstrings):
```python
def dumps(obj):
    """
    Serialize ``obj`` to a JSON formatted ``str``.
    
    If ``separators`` is specified, it should be a tuple of (item_separator, key_separator).
    """
    ...
```

### After Merge (enriched):
```python
"""JSON encoding and decoding.

MicroPython module: https://docs.micropython.org/en/latest/library/json.html
CPython module: https://docs.python.org/3/library/json.html
"""

from typing import Any

def dumps(obj: Any, separators: tuple[str, str] | None = ...) -> str:
    """
    Serialize ``obj`` to a JSON formatted ``str``.
    
    If ``separators`` is specified, it should be a tuple of (item_separator, key_separator).
    
    Note: MicroPython has limited support for some JSON features compared to CPython.
    """
    ...

def loads(s: str) -> Any:
    """
    Deserialize ``s`` (a ``str`` instance containing a JSON document) to a Python object.
    """
    ...
```

## Risks and Mitigations

### Risk 1: Overwriting MicroPython Documentation
**Mitigation:** 
- Strict preservation rules in merge logic
- Automated tests to detect overwrites
- Manual review of changes

### Risk 2: CPython/MicroPython API Differences
**Mitigation:**
- Maintain allowlist of safe-to-merge modules
- Add warnings in docstrings about differences
- Version-specific notes

### Risk 3: Maintenance Burden
**Mitigation:**
- Automate as much as possible
- Clear documentation for maintainers
- Make enrichment optional, not required

### Risk 4: Stale Documentation
**Mitigation:**
- Regular update cadence
- Track source versions in metadata
- Deprecation warnings when appropriate

## Alternative Approaches Considered

### Alternative 1: Link to Online Documentation
Instead of embedding docstrings, provide links to CPython docs.

**Rejected because:** 
- Less useful in IDE
- Requires internet
- Doesn't improve offline development

### Alternative 2: Manual Curation
Manually write/curate docstrings for stdlib modules.

**Rejected because:**
- Too time-consuming
- Doesn't scale
- Duplicates CPython effort

### Alternative 3: Use Type Comments Instead
Focus on type comments rather than docstrings.

**Rejected because:**
- Type comments deprecated in favor of annotations
- Doesn't solve docstring request

## Conclusion

The hybrid approach (Option C) is recommended:
1. Extract well-maintained type information from pyright/basedpyright
2. Enrich with CPython docstrings from runtime introspection
3. Carefully merge into MicroPython stubs with preservation rules
4. Provide as optional enhancement to stub generation workflow

This approach:
- Improves IDE experience with better type hints and documentation
- Preserves MicroPython-specific information
- Leverages existing, well-maintained sources
- Can be automated and integrated into CI/CD
- Provides flexibility for future enhancements

## Next Steps

1. **Get Stakeholder Approval**: Present this research to project maintainers
2. **Prioritize Approach**: Confirm hybrid approach or select alternative
3. **Define Scope**: Select initial set of modules for Phase 1
4. **Implement Proof of Concept**: Test on 2-3 modules
5. **Iterate**: Refine based on PoC results
6. **Full Implementation**: Roll out to all applicable modules

## References

- BasedPyright Documentation: https://docs.basedpyright.com/
- Typeshed Repository: https://github.com/python/typeshed
- Typeshed Docstring Discussion: https://github.com/python/typeshed/issues/4881
- PEP 484 (Type Hints): https://www.python.org/dev/peps/pep-0484/
- PEP 561 (Distributing Type Information): https://www.python.org/dev/peps/pep-0561/
- MicroPython Documentation: https://docs.micropython.org/
