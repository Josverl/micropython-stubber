# MicroPython Stubber Development Instructions

**ALWAYS follow these instructions first and fallback to additional search and context gathering only if the information in these instructions is incomplete or found to be in error.**

## Working Effectively
This is a Python project that creates type stubs for MicroPython development in editors like VSCode. The project uses [uv](https://docs.astral.sh/uv/) for dependency management (with the hatchling build backend) and has both CPython and MicroPython components.

### Bootstrap and Setup
Follow these exact commands in order:

1. **Install uv** (if not available):
   ```bash
   pipx install uv
   ```
   - Takes: ~1-2 minutes. NEVER CANCEL. Set timeout to 5+ minutes.

2. **Install all dependencies**:
   ```bash
   uv sync --group dev --group docs --group test
   ```
   - Takes: ~17 seconds normally, up to 2 minutes on slow connections. NEVER CANCEL. Set timeout to 5+ minutes.

3. **Verify installation**:
   ```bash
   uv run stubber --help
   ```
   - Takes: ~1 second. Should show the stubber command help.

### Testing
**ALWAYS run tests to validate your changes:**

1. **Run core tests** (fast validation):
   ```bash
   uv run pytest tests/rst/test_constants.py tests/common/ -v
   ```
   - Takes: ~3-5 seconds. NEVER CANCEL. Set timeout to 2+ minutes.

2. **Run broader test suite**:
   ```bash
   uv run pytest tests/rst/ tests/utils/ -v --tb=short --maxfail=5
   ```
   - Takes: ~3-4 seconds. NEVER CANCEL. Set timeout to 5+ minutes.
   - Expect: 150+ tests to pass, some may fail due to GitHub API rate limiting (this is normal).

3. **Run full test suite** (when needed):
   ```bash
   uv run pytest --cov --cov-branch --cov-report=xml
   ```
   - Takes: ~30-60 seconds. NEVER CANCEL. Set timeout to 10+ minutes.

### Code Quality and Linting
**ALWAYS run these before committing:**

1. **Check code formatting**:
   ```bash
   uv run ruff format --check --diff src/stubber/
   ```
   - Takes: ~4 seconds. Shows what would be reformatted.

2. **Format code** (if needed):
   ```bash
   uv run ruff format src/stubber/
   ```
   - Takes: ~4-8 seconds. NEVER CANCEL. Set timeout to 2+ minutes.

3. **Check imports**:
   ```bash
   uv run autoflake --check --remove-all-unused-imports --recursive src/stubber/
   ```
   - Takes: ~1-2 seconds. Set timeout to 2+ minutes.

4. **Type checking**:
   ```bash
   uv run pyright --version
   ```
   - Takes: ~1 second. Verify pyright is available for type checking.

### Configuration and Environment
The project uses a configuration system that may have GitHub API dependencies. If you encounter GitHub API rate limiting errors:
- This is NORMAL and expected in CI environments
- The system has fallbacks that allow most functionality to work
- Tests may show warnings about "Could not read micropython versions from git" - this is expected

### Validation Scenarios
**ALWAYS test these scenarios after making changes to core functionality:**

1. **Complete validation workflow**:
   ```bash
   # Test core functionality (3 tests should pass)
   uv run pytest tests/rst/test_constants.py -v
   
   # Test code formatting
   uv run ruff format --check src/stubber/__init__.py
   
   # Test configuration system
   uv run stubber show-config | head -3
   ```
   - Takes: ~4-5 seconds total. All should complete without errors.

2. **Basic stubber functionality**:
   ```bash
   uv run stubber show-config
   uv run stubber --help
   uv run stubber make-variants --help
   ```
   - Should display configuration and help without errors
   - Takes: ~1-2 seconds each

3. **Type checking tools**:
   ```bash
   uv run pyright --version
   uv run mypy --version
   ```
   - Should show version numbers
   - Takes: ~1 second each

4. **Python import test**:
   ```bash
   uv run python -c "import src.stubber; print('Import successful')"
   ```
   - Should print "Import successful"
   - Takes: ~1 second

5. **Workspace creation**:
   ```bash
   mkdir -p test-workspace/all-stubs
   cd test-workspace
   uv run --directory=.. stubber show-config
   ```
   - Test working from different directories
   - Takes: ~2 seconds

## Common Issues and Limitations

### GitHub API Rate Limiting
- **Issue**: Commands may fail with "403: Forbidden" GitHub API errors
- **Solution**: This is normal in CI environments. The system has fallbacks. Most functionality still works.
- **Warning Messages**: You may see "Could not read micropython versions from git" - this is expected
- **DO NOT**: Try to fix API authentication issues unless specifically requested.

### Expected Warning Messages (NORMAL)
These warnings are normal and do not indicate problems:
```
Request GET /repos/micropython/micropython failed with 403: Forbidden
WARNING | Could not read micropython versions from git: Object of type bytes is not JSON serializable  
WARNING | Could not read stable/preview versions from git: Object of type bytes is not JSON serializable
```

### Network Dependencies
- Some commands require internet access to clone repositories or download stubs
- In offline/CI environments, use test data from the `data/` directory
- The `tests/` directory contains comprehensive test data for offline validation

### Build and Runtime Environment
- **uv required**: All commands must be run with the `uv run` prefix
- **Python version**: Requires Python 3.10+ (configured in pyproject.toml)
- **Virtual environment**: uv automatically manages the `.venv` virtual environment
- **Directory context**: Some commands are sensitive to working directory

### Test Failures (Expected)
Some tests may fail due to external dependencies:
- RST/documentation tests may fail if upstream docs change
- GitHub API-dependent tests will fail in rate-limited environments
- 150+ tests should pass; 5-10 failures due to external issues is normal

## Key Projects and Structure

### Source Code Layout
- `src/stubber/`: Main source code
  - `board/`: MicroPython board-specific stub generation scripts
  - `commands/`: CLI command implementations  
  - `rst/`: Documentation-to-stub conversion
  - `utils/`: Utility functions and configuration
  - `publish/`: Publishing and packaging logic

### Test Structure  
- `tests/`: All test files
  - `common/`: Configuration and basic functionality tests
  - `rst/`: Documentation processing tests (150+ tests)
  - `utils/`: Utility function tests
  - `data/`: Test data and fixtures

### Key Files
- `pyproject.toml`: Project metadata, dependencies (PEP 621), and tool settings
- `.github/workflows/pytest.yml`: CI configuration
- `docs/developing.md`: Development documentation
- `readme.md`: Project overview and basic usage

## Timing Expectations and Timeouts

**CRITICAL**: Set appropriate timeouts for all commands:

- **uv sync**: 5+ minutes timeout
- **uv run commands**: 2+ minutes timeout  
- **Test runs**: 5-10+ minutes timeout
- **Ruff formatting**: 2+ minutes timeout
- **Stub generation**: 10+ minutes timeout (if implemented)

**NEVER CANCEL** long-running operations. Build and test processes may legitimately take several minutes.

### Advanced Usage

### Documentation Building
Test documentation system (if modifying docs):
```bash
uv run sphinx-build --version
# Should show sphinx version
```
- For full docs build: `uv run sphinx-build docs/ docs/_build/` 
- Takes: Variable time (5-15 minutes). Set timeout to 20+ minutes. NEVER CANCEL.

### Working from Different Directories
The stubber tool can be run from any directory using uv:
```bash
# From subdirectory:
uv run --directory=.. stubber show-config

# From workspace:
cd my-workspace
uv run --directory=/path/to/micropython-stubber stubber --help
```

### Creating Workspace
```bash
mkdir my-stub-workspace
cd my-stub-workspace
mkdir all-stubs
# Now ready for stub operations
```

### Minification and Variants
```bash
uv run stubber make-variants
```
- Creates minified versions of createstubs.py for MicroPython deployment
- Takes: ~5-30 seconds depending on file sizes. Set timeout to 5+ minutes.

### Development Workflow Best Practices
1. **Always start with**: `uv sync --group dev --group docs --group test`
2. **Before any commit**: Run tests and formatting checks
3. **After changes**: Run validation scenarios
4. **For PRs**: Run full test suite

Remember: **ALWAYS validate commands work before including them in your changes. Test every single command you recommend.**

## Debugging and Troubleshooting

### Debug Test Runs
When debugging test failures:
```bash
# Run with full output and no coverage for debugging
uv run pytest tests/path/to/test.py -v -s --tb=long --no-cov
```

### Check uv Environment
If imports fail:
```bash
# Check the environment / resolve the project
uv sync
uv pip list

# Reinstall if needed
uv sync --group dev --group docs --group test
```

### Verbose Stubber Output  
For debugging stubber commands:
```bash
# Use verbose flags for more information
uv run stubber -V show-config
uv run stubber -VV some-command  # Even more verbose
```

### Configuration Debug
If configuration issues occur:
```bash
# Show current configuration
uv run stubber show-config

# Check project structure
ls -la pyproject.toml src/stubber/
```

## Quick Reference Commands

**Setup**: `uv sync --group dev --group docs --group test` (17s, 5min timeout)  
**Test**: `uv run pytest tests/rst/test_constants.py -v` (1s, 2min timeout)  
**Format**: `uv run ruff format --check src/stubber/` (4s, 2min timeout)  
**Config**: `uv run stubber show-config` (2s, 2min timeout)  
**Help**: `uv run stubber --help` (1s, 2min timeout)  
**Type Check**: `uv run pyright --version` (1s, 2min timeout)