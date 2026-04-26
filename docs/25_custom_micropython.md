# Generating Stubs for Custom MicroPython Builds

This guide explains how to generate stubs for custom MicroPython builds, including:
- Custom branches or forks
- Pull requests (PRs) 
- Specific commits
- Local modifications

**New in v1.26.0+**: The `stubber clone` and `stubber switch` commands have been enhanced to work with custom repositories and arbitrary git references (branches, commits, tags).

If you just want to contribute stubs for a standard board running an official release, see the [Quick Start](05_quick_start.md) guide instead.

## Prerequisites

Install micropython-stubber and set up a working directory as described in the [Quick Start – Prerequisites and Steps 1–2](05_quick_start.md).

## Enhanced CLI Commands

The following CLI commands have been enhanced to support custom builds:

### `stubber clone` - Enhanced for Custom Repositories

```bash
# Clone your fork of MicroPython (uses default micropython-lib)
stubber clone --mpy-repo https://github.com/YOUR_USERNAME/micropython.git

# Clone both custom MicroPython and custom micropython-lib
stubber clone \
  --mpy-repo https://github.com/YOUR_USERNAME/micropython.git \
  --mpy-lib-repo https://github.com/YOUR_USERNAME/micropython-lib.git \
  --add-stubs

# Clone with just custom micropython-lib (uses default MicroPython)
stubber clone --mpy-lib-repo https://github.com/YOUR_USERNAME/micropython-lib.git
```

### `stubber switch` - Enhanced for Any Git Reference

```bash
# Switch to any branch
stubber switch feature-branch

# Switch to any commit hash
stubber switch abc123def456

# Switch to traditional tags (still works)
stubber switch v1.22.0

# Switch to special versions
stubber switch preview
stubber switch stable
```

## Scenario-Based Workflows

## Scenario 1: Working with a Fork

If you have a fork of MicroPython with custom changes:

### Step 1: Clone Your Custom Repository

You can now use the enhanced `stubber clone` command with custom repositories:

```bash
# Clone your fork directly using the enhanced clone command
stubber clone --mpy-repo https://github.com/YOUR_USERNAME/micropython.git --add-stubs

# Or manually clone if you prefer more control:
mkdir repos
cd repos

# Clone your fork instead of the official repo
git clone https://github.com/YOUR_USERNAME/micropython.git
git clone https://github.com/micropython/micropython-lib.git

# Optional: clone stubs repo for reference
git clone https://github.com/josverl/micropython-stubs.git

cd ..
```

### Step 2: Switch to Your Branch/Commit

The `stubber switch` command now accepts arbitrary branches and commits:

```bash
# Switch to your custom branch
stubber switch your-custom-branch

# Or switch to a specific commit
stubber switch abc123def456

# Or switch to a PR branch (if you fetched it)
stubber switch pr-12345
```

### Step 3: Generate Stubs

Now you can use the stubber commands with your custom setup:

```bash
# Generate documentation stubs from your custom MicroPython
stubber docstubs --version=custom

# Generate frozen module stubs
stubber frozen --version=custom

# If you have a connected board with your custom firmware:
stubber firmware-stubs --version=custom  # alias mcu-stubs still works
```

## Scenario 2: Working with a Pull Request

To generate stubs for a specific Pull Request:

### Step 1: Clone and Checkout PR

```bash
# Create standard workspace
stubber init
cd micropython-stubs/repos/micropython

# Fetch the PR (replace 12345 with PR number)
git fetch origin pull/12345/head:pr-12345

cd ../..

# Now switch to the PR branch using stubber
stubber switch pr-12345
```

### Step 2: Generate Stubs

```bash
stubber docstubs --version=pr-12345
stubber frozen --version=pr-12345
```

## Scenario 3: Working with Local Modifications

If you have local modifications to MicroPython:

### Step 1: Prepare Your Modified Repository

```bash
# Create standard workspace first
stubber init
cd micropython-stubs/repos/micropython

# Apply your modifications
# ... make your changes ...

# Optionally commit your changes
git add .
git commit -m "My custom modifications"
git tag my-custom-build  # Create a tag for reference

cd ../..
```

### Step 2: Switch and Generate Stubs

```bash
# Switch to your custom tag/commit
stubber switch my-custom-build

# Or if you want to use the current working directory state
stubber docstubs --version=my-custom-build
stubber frozen --version=my-custom-build
```

## Scenario 4: Complete Workflow for Custom Firmware

This is a complete example for generating stubs for a custom RPi Pico W build.

### Step 1: Setup Custom Repository

```bash
mkdir rpi-pico-w-custom
cd rpi-pico-w-custom

# Clone your fork using the enhanced clone command
stubber clone --mpy-repo https://github.com/YOUR_USERNAME/micropython.git --add-stubs

# Switch to your custom branch
stubber switch your-pico-w-branch
```

### Step 2: Build Your Custom Firmware (Optional)

If you need to build the firmware:

```bash
cd repos/micropython

# Install build dependencies (varies by platform)
# For Pico W:
cd ports/rp2
make submodules
make BOARD=RPI_PICO_W

# Your custom firmware is now in build-RPI_PICO_W/firmware.uf2
cd ../../..
```

### Step 3: Generate and publish stubs

Flash your custom firmware to the device and then follow [Quick Start steps 7–9](05_quick_start.md#step-7-generate-firmware-stubs-from-a-connected-device) (firmware stubs, merge, build, and PR), passing `--version=custom-pico-w` to each command:

```bash
stubber firmware-stubs --version=custom-pico-w
stubber merge --version=custom-pico-w --port=rp2 --board=RPI_PICO_W
stubber build --version=custom-pico-w --port=rp2 --board=RPI_PICO_W
```

## Working Without Version Tags

If you prefer to work with the current checkout without specifying versions:

```bash
# This uses whatever is currently checked out
stubber docstubs
stubber frozen
stubber firmware-stubs
```

The stubs will be generated with `latest` as the version identifier.

## Tips and Best Practices

### 1. Naming Your Custom Versions

Use meaningful version names that help you identify your build:
- `--version=my-feature-v1.22.0`
- `--version=pr-12345-dma-support`
- `--version=custom-pico-w-2024-01`

### 2. Directory Structure

Keep your custom builds organized:
```
my-project/
├── repos/
│   ├── micropython/          # Your custom MicroPython
│   ├── micropython-lib/      # Compatible micropython-lib
│   └── micropython-stubs/    # Reference stubs (optional)
├── stubs/                    # Generated stubs
└── firmware/                 # Your built firmware files
```

### 3. Reproducible Builds

Document your exact setup:
```bash
# Save commit hashes for reproducibility
cd repos/micropython
echo "MicroPython: $(git rev-parse HEAD)" > ../build-info.txt
cd ../micropython-lib  
echo "MicroPython-lib: $(git rev-parse HEAD)" >> ../build-info.txt
```

### 4. Version Compatibility

When working with older commits:
- Use compatible micropython-lib versions
- Some features may not be available in older versions
- Check the micropython-stubber compatibility

## Troubleshooting

### Missing Repositories Error

If you get an error about missing repositories:
```
Repo micropython not found, run 'stubber init' (or use 'stubber clone' for custom repo setup) to clone the repos.
```

Make sure your directory structure is correct:
```bash
# Check that repos exist
ls repos/micropython/.git
ls repos/micropython-lib/.git
```

### Version Not Found

If stubber can't find your version, make sure you're using consistent naming:
```bash
# Check what git thinks the current version is
cd repos/micropython
git describe --tags --always
```

### Build Failures

If stub generation fails:
1. Check that your MicroPython modification didn't break documentation parsing
2. Verify all required files are present in your custom build
3. Check the logs for specific error messages

## Getting Help

If you encounter issues:
1. Check the main [micropython-stubber documentation](https://micropython-stubber.readthedocs.io/)
2. Review the [issue tracker](https://github.com/Josverl/micropython-stubber/issues)
3. Provide details about your custom setup when asking for help

## See Also

- [Creating Stubs](20_creating.md) - General stub creation workflow
- [Firmware Stubs](40_firmware_stubs.md) - Device-generated stubs
- [Frozen Stubs](50_frozen_stubs.md) - Frozen module stubs
- [Repository Structure](60_repos.md) - Understanding the repository layout