# Implementation Progress: stdlib Docstring Enrichment (`--ai-enhance`)

**Branch:** `copilot/fix-981654-177823007-25fa9065-6b74-4979-9d6e-e05423667c4c`  
**Status:** ✅ Implementation Complete

---

## Summary

Implemented the `stubber get-typeshed` command with an `--ai-enhance` flag that:
1. Extracts typeshed `.pyi` stubs for MicroPython-compatible stdlib modules from the bundled `pyright` package
2. When `--ai-enhance` is provided, injects CPython docstrings (extracted via runtime introspection) into the copied stubs without overwriting any existing docstrings

---

## Changes Made

### New Files

| File | Description |
|------|-------------|
| `src/stubber/get_typeshed.py` | Core module: locate typeshed, extract CPython docstrings, inject via LibCST transformer |
| `src/stubber/commands/get_typeshed_cmd.py` | CLI command: `stubber get-typeshed [--ai-enhance]` |
| `tests/test_get_typeshed.py` | 22 tests covering all key functionality |
| `docs/implementation_progress_stdlib_docstrings.md` | This document |

### Modified Files

| File | Change |
|------|--------|
| `src/stubber/stubber.py` | Import and register `cli_get_typeshed` command |

---

## Phase-by-Phase Progress

### Phase 1: Research ✅ (Previous Work)
- Researched BasedPyright/Pyright bundled typeshed stubs
- Confirmed stubs are accessible via the `pyright` pip package
  - Location: `pyright/dist/dist/typeshed-fallback/stdlib/`
- Confirmed CPython docstrings are extractable via `inspect` module
- Documented hybrid approach recommendations

### Phase 2: Core Implementation ✅

#### 2.1 Typeshed Stub Location
**Finding:** The `pyright` pip package (already a project dependency) bundles
typeshed at a predictable path: `<pyright_pkg>/dist/dist/typeshed-fallback/stdlib/`

**Solution:** `_pyright_typeshed_path()` function that locates the stdlib directory
without requiring npm or any new dependencies.

#### 2.2 Module List
Defined `MICROPYTHON_STDLIB_MODULES` – the 20 modules that exist in both
MicroPython and CPython stdlib:
`array`, `binascii`, `cmath`, `collections`, `errno`, `gc`, `hashlib`, `io`,
`json`, `math`, `os`, `random`, `re`, `select`, `socket`, `ssl`, `struct`,
`sys`, `time`, `zlib`

#### 2.3 CPython Docstring Extraction
**Implementation:** `_get_module_docstrings(module_name)` uses Python's `inspect`
module to extract:
- Module-level docstring (key: `""`)
- Function/built-in function docstrings (key: `"function_name"`)
- Class docstrings (key: `"ClassName"`)
- Method docstrings (key: `"ClassName.method_name"`)

**Issue Found:** Some functions/methods may not have inspectable signatures
(built-in C functions). **Resolution:** Wrapped in `try/except` to gracefully
skip un-inspectable objects.

#### 2.4 LibCST Docstring Injector
**Implementation:** `_DocstringInjector` – a LibCST `CSTTransformer` that:
- Injects module-level docstrings if not present
- Injects function docstrings if not present
- Injects class docstrings if not present  
- Injects method docstrings if not present
- **Never overwrites existing docstrings** (MicroPython-specific docs preserved)

**Issue Found:** Typeshed stub functions use `SimpleStatementSuite` (single-line
`def f(): ...`) not `IndentedBlock`. The initial implementation only handled
`IndentedBlock`.

**Resolution:** Added branch for `SimpleStatementSuite` – converts single-line
stubs to indented blocks when injecting docstrings:
```python
elif isinstance(old_body, cst.SimpleStatementSuite):
    new_body = cst.IndentedBlock(body=[ds_node, cst.SimpleStatementLine(...)])
    updated_node = updated_node.with_changes(body=new_body)
```

#### 2.5 CLI Command
**Implementation:** `stubber get-typeshed` with options:
- `--stub-path` / `--stub-folder` – destination (default: `<config.stub_path>/typeshed-stdlib`)
- `--module` / `-m` – specific module(s) to copy (repeatable)
- `--ai-enhance` / `--no-ai-enhance` – enable CPython docstring injection
- `--format` / `--no-format` – run ruff formatter after extraction
- `--list-modules` – list available modules and exit

### Phase 3: Testing ✅

#### Tests Written (22 total)

| Test | Coverage |
|------|----------|
| `test_pyright_typeshed_path_returns_existing_path` | Typeshed path discovery |
| `test_pyright_typeshed_path_without_pyright` | Graceful missing-package handling |
| `test_get_module_docstrings_json` | CPython docstring extraction for `json` |
| `test_get_module_docstrings_sys` | CPython docstring extraction for `sys` |
| `test_get_module_docstrings_nonexistent` | Non-existent module → empty dict |
| `TestDocstringInjector.test_injects_module_docstring` | Module docstring injection |
| `TestDocstringInjector.test_does_not_overwrite_existing_module_docstring` | Preservation |
| `TestDocstringInjector.test_injects_function_docstring_single_line` | Single-line stub |
| `TestDocstringInjector.test_does_not_overwrite_existing_function_docstring` | Preservation |
| `TestDocstringInjector.test_injects_function_docstring_indented_block` | Indented block |
| `TestDocstringInjector.test_injects_class_docstring` | Class docstring injection |
| `TestDocstringInjector.test_does_not_overwrite_existing_class_docstring` | Preservation |
| `TestDocstringInjector.test_injects_method_docstring` | Method docstring injection |
| `TestDocstringInjector.test_no_docstring_missing_key` | No change when no key match |
| `test_get_typeshed_stubs_copies_modules` | Integration: copy json + sys + cmath |
| `test_get_typeshed_stubs_skips_missing` | Integration: skipped list |
| `test_get_typeshed_stubs_ai_enhance` | Integration: docstrings injected |
| `test_get_typeshed_stubs_default_modules` | All default modules covered |
| `test_get_typeshed_stubs_no_pyright` | RuntimeError when pyright absent |
| `test_cli_get_typeshed` | CLI invocation |
| `test_cli_get_typeshed_list_modules` | `--list-modules` flag |
| `test_cli_get_typeshed_ai_enhance` | CLI with `--ai-enhance` |

**Results:** 22/22 passed ✅

### Phase 4: Integration & Formatting ✅

- Registered `cli_get_typeshed` command in `src/stubber/stubber.py`
- Ran `ruff format` on all new files
- Ran `ruff check --fix` to remove unused imports
- Ran broader test suite: 275 passed, 7 pre-existing failures (GitHub API rate
  limiting + missing MicroPython repos – unrelated to this feature)

---

## Usage

### Basic: copy typeshed stubs (type annotations only)
```bash
stubber get-typeshed --stub-path ./all-stubs/typeshed-stdlib
```

### With AI enhancement (add CPython docstrings)
```bash
stubber get-typeshed --stub-path ./all-stubs/typeshed-stdlib --ai-enhance
```

### Copy specific modules only
```bash
stubber get-typeshed -m json -m os -m sys --ai-enhance
```

### List available modules
```bash
stubber get-typeshed --list-modules
```

### Example output (json with ai-enhance)
```python
# Before (typeshed only)
def dumps(obj: Any, *, skipkeys: bool = ...) -> str: ...

# After (--ai-enhance)
def dumps(obj: Any, *, skipkeys: bool = ...) -> str:
    """Serialize ``obj`` to a JSON formatted ``str``.

    If ``skipkeys`` is true then ``dict`` keys that are not basic types
    ...
    """
    ...
```

---

## Design Decisions

### 1. Use pyright (not npm) for typeshed
The `pyright` Python package is already a project dependency and bundles the
typeshed stubs internally.  Using it avoids any npm/Node.js dependency.

**Trade-off:** Tied to the pyright package's internal layout.  If pyright
restructures its package, the path needs updating.  The fallback is a clear
error message.

### 2. Runtime introspection for docstrings
CPython docstrings are extracted at runtime using `inspect.getdoc()`.  This is
simpler and more reliable than parsing CPython source files or `.rst`
documentation.

**Trade-off:** Requires the module to be importable in the current Python
environment.  All `MICROPYTHON_STDLIB_MODULES` are in the CPython stdlib so
this is always satisfied.

### 3. LibCST for docstring injection
Using LibCST (already a project dependency) preserves all formatting,
whitespace, and comments in the stub files.

**Issue encountered:** Stub files use single-line bodies (`def f(): ...`)
which are `SimpleStatementSuite` nodes, not `IndentedBlock`.  Fixed by
explicitly handling both cases.

### 4. Never overwrite existing docstrings
The `_DocstringInjector` checks `_has_docstring()` before injecting.  This
ensures MicroPython-specific documentation is never replaced with CPython docs.

---

## Known Limitations

1. **Typeshed has no docstrings for most C modules** (e.g. `math`, `struct`).
   The `--ai-enhance` flag compensates by injecting CPython runtime docstrings,
   but these may differ from MicroPython behavior.

2. **Sub-module stubs** (e.g. `json/encoder.pyi`) only get module-level
   enrichment from `json.encoder`.  The current implementation only enriches
   `__init__.pyi` with the top-level module's docstrings.

3. **Some MicroPython modules are missing from typeshed** (e.g. `gc` in some
   versions).  These are logged as warnings and added to the `skipped` list.

---

## Next Steps (Suggested)

1. **Integrate into `docs-stubs` workflow**: Consider calling `get-typeshed`
   as a step in the overall stub generation pipeline.

2. **Extend to sub-modules**: Enhance `_copy_and_enrich` to look up
   sub-module docstrings (e.g. `json.encoder.JSONEncoder`).

3. **Add VERSIONS file handling**: Copy the typeshed `VERSIONS` file to
   document minimum Python version for each module.

4. **CI integration**: Add a workflow step to run `get-typeshed --ai-enhance`
   as part of the release process.
