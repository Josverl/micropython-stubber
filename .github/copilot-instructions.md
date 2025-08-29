# MicroPython Stubber Development Instructions

**ALWAYS follow these instructions first and fallback to additional search and context gathering only if the information in these instructions is incomplete or found to be in error.**

## Working Effectively
This is a Python project that creates type stubs for MicroPython development in editors like VSCode. The project uses Poetry for dependency management and has both CPython and MicroPython components.

### Bootstrap and Setup
Follow these exact commands in order:

1. **Install Poetry** (if not available):
   ```bash
   pipx install poetry
   ```
   - Takes: ~1-2 minutes. NEVER CANCEL. Set timeout to 5+ minutes.

2. **Install all dependencies**:
   ```bash
   poetry install --with dev --with docs --with test
   ```
   - Takes: ~17 seconds normally, up to 2 minutes on slow connections. NEVER CANCEL. Set timeout to 5+ minutes.

3. **Verify installation**:
   ```bash
   poetry run stubber --help
   ```
   - Takes: ~1 second. Should show the stubber command help.

### Testing
**ALWAYS run tests to validate your changes:**

1. **Run core tests** (fast validation):
   ```bash
   poetry run pytest tests/rst/test_constants.py tests/common/ -v
   ```
   - Takes: ~3-5 seconds. NEVER CANCEL. Set timeout to 2+ minutes.

2. **Run broader test suite**:
   ```bash
   poetry run pytest tests/rst/ tests/utils/ -v --tb=short --maxfail=5
   ```
   - Takes: ~3-4 seconds. NEVER CANCEL. Set timeout to 5+ minutes.
   - Expect: 150+ tests to pass, some may fail due to GitHub API rate limiting (this is normal).

3. **Run full test suite** (when needed):
   ```bash
   poetry run pytest --cov --cov-branch --cov-report=xml
   ```
   - Takes: ~30-60 seconds. NEVER CANCEL. Set timeout to 10+ minutes.

### Code Quality and Linting
**ALWAYS run these before committing:**

1. **Check code formatting**:
   ```bash
   poetry run black --check --diff src/stubber/
   ```
   - Takes: ~4 seconds. Shows what would be reformatted.

2. **Format code** (if needed):
   ```bash
   poetry run black src/stubber/
   ```
   - Takes: ~4-8 seconds. NEVER CANCEL. Set timeout to 2+ minutes.

3. **Check imports**:
   ```bash
   poetry run autoflake --check --remove-all-unused-imports --recursive src/stubber/
   ```
   - Takes: ~1-2 seconds. Set timeout to 2+ minutes.

4. **Type checking**:
   ```bash
   poetry run pyright --version
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
   poetry run pytest tests/rst/test_constants.py -v
   
   # Test code formatting
   poetry run black --check src/stubber/__init__.py
   
   # Test configuration system
   poetry run stubber show-config | head -3
   ```
   - Takes: ~4-5 seconds total. All should complete without errors.

2. **Basic stubber functionality**:
   ```bash
   poetry run stubber show-config
   poetry run stubber --help
   poetry run stubber make-variants --help
   ```
   - Should display configuration and help without errors
   - Takes: ~1-2 seconds each

3. **Type checking tools**:
   ```bash
   poetry run pyright --version
   poetry run mypy --version
   ```
   - Should show version numbers
   - Takes: ~1 second each

4. **Python import test**:
   ```bash
   poetry run python -c "import src.stubber; print('Import successful')"
   ```
   - Should print "Import successful"
   - Takes: ~1 second

5. **Workspace creation**:
   ```bash
   mkdir -p test-workspace/all-stubs
   cd test-workspace
   poetry run --directory=.. stubber show-config
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
- **Poetry required**: All commands must be run with `poetry run` prefix
- **Python version**: Requires Python 3.9+ (configured in pyproject.toml)
- **Virtual environment**: Poetry automatically manages the virtual environment
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
- `pyproject.toml`: Poetry configuration, dependencies, and project settings
- `.github/workflows/pytest.yml`: CI configuration
- `docs/developing.md`: Development documentation
- `readme.md`: Project overview and basic usage

## Timing Expectations and Timeouts

**CRITICAL**: Set appropriate timeouts for all commands:

- **Poetry install**: 5+ minutes timeout
- **Poetry commands**: 2+ minutes timeout  
- **Test runs**: 5-10+ minutes timeout
- **Black formatting**: 2+ minutes timeout
- **Stub generation**: 10+ minutes timeout (if implemented)

**NEVER CANCEL** long-running operations. Build and test processes may legitimately take several minutes.

### Advanced Usage

### Documentation Building
Test documentation system (if modifying docs):
```bash
poetry run sphinx-build --version
# Should show sphinx version
```
- For full docs build: `poetry run sphinx-build docs/ docs/_build/` 
- Takes: Variable time (5-15 minutes). Set timeout to 20+ minutes. NEVER CANCEL.

### Working from Different Directories
The stubber tool can be run from any directory using Poetry:
```bash
# From subdirectory:
poetry run --directory=.. stubber show-config

# From workspace:
cd my-workspace
poetry run --directory=/path/to/micropython-stubber stubber --help
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
poetry run stubber make-variants
```
- Creates minified versions of createstubs.py for MicroPython deployment
- Takes: ~5-30 seconds depending on file sizes. Set timeout to 5+ minutes.

### Development Workflow Best Practices
1. **Always start with**: `poetry install --with dev --with docs --with test`
2. **Before any commit**: Run tests and formatting checks
3. **After changes**: Run validation scenarios
4. **For PRs**: Run full test suite

Remember: **ALWAYS validate commands work before including them in your changes. Test every single command you recommend.**

## Debugging and Troubleshooting

### Debug Test Runs
When debugging test failures:
```bash
# Run with full output and no coverage for debugging
poetry run pytest tests/path/to/test.py -v -s --tb=long --no-cov
```

### Check Poetry Environment
If imports fail:
```bash
# Check Poetry environment status
poetry env info
poetry check

# Reinstall if needed
poetry install --with dev --with docs --with test
```

### Verbose Stubber Output  
For debugging stubber commands:
```bash
# Use verbose flags for more information
poetry run stubber -V show-config
poetry run stubber -VV some-command  # Even more verbose
```

### Configuration Debug
If configuration issues occur:
```bash
# Show current configuration
poetry run stubber show-config

# Check project structure
ls -la pyproject.toml src/stubber/
```

## Quick Reference Commands

**Setup**: `poetry install --with dev --with docs --with test` (17s, 5min timeout)  
**Test**: `poetry run pytest tests/rst/test_constants.py -v` (1s, 2min timeout)  
**Format**: `poetry run black --check src/stubber/` (4s, 2min timeout)  
**Config**: `poetry run stubber show-config` (2s, 2min timeout)  
**Help**: `poetry run stubber --help` (1s, 2min timeout)  
**Type Check**: `poetry run pyright --version` (1s, 2min timeout)