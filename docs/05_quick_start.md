(quick-start)=
# Quick Start

This page walks you through generating a complete set of MicroPython stubs for a specific board in about 10 minutes.
No prior knowledge of the project internals is needed.

## What are stubs, and why do I need them?

{ref}`Stub files <stub-files>` teach your editor (VS Code, PyCharm, …) about the MicroPython modules that are available on your board.
Without them, the editor has no way to offer code-completion or type-checking for `machine`, `network`, `uos`, and every other MicroPython-specific module.

Three complementary stub types are combined to give the best coverage:

| Stub type | Source | Command |
|-----------|--------|---------|
| {ref}`Doc stubs <doc-stubs>` | MicroPython documentation | `stubber docstubs` |
| {ref}`Frozen stubs <frozen-stubs>` | Modules frozen into firmware source | `stubber frozen` |
| {ref}`Firmware stubs <mcu-stubs>` | Connected board (optional) | `stubber firmware-stubs` |

## Prerequisites

* Python 3.9 or newer installed on your PC.
* Git installed (needed to clone the MicroPython source tree).
* A working directory — for example `~/my-stubs`.

## Step 1 – Install micropython-stubber

```bash
pip install micropython-stubber
```

Verify the installation:

```bash
stubber --help
```

## Step 2 – Create a working directory

```bash
mkdir ~/my-stubs
cd ~/my-stubs
```

All subsequent commands should be run from inside this directory.

## Step 3 – Clone the required repositories

This downloads the MicroPython source tree and the stub storage repository:

```bash
stubber clone --add-stubs
```

The command creates a `repos/` subdirectory containing:

```
repos/
├── micropython/        ← MicroPython source (for doc & frozen stubs)
├── micropython-lib/    ← MicroPython library source
└── micropython-stubs/  ← Where generated stubs are stored
```

## Step 4 – Select the firmware version

Switch to the latest stable release:

```bash
stubber switch stable
```

You can also pin to a specific version, for example `stubber switch v1.22.2`, or use `preview` for the latest nightly build.

## Step 5 – Generate doc stubs

Doc stubs are generated from the MicroPython documentation.
They contain full parameter names and descriptions:

```bash
stubber docstubs --enrich
```

## Step 6 – Generate frozen stubs

Frozen stubs cover the Python modules that are compiled directly into the firmware:

```bash
stubber frozen --version stable --enrich
```

## Step 7 (optional) – Generate firmware stubs from a connected device

If you have a board connected to your PC you can generate stubs directly from it.
This captures any board-specific modules that are not documented elsewhere:

```bash
stubber firmware-stubs
```

## Step 8 – Merge and build the stub package

Combine all stub types for your target port and board into a single package:

```bash
# Replace esp32 / ESP32_GENERIC with your own port and board
stubber merge --port esp32 --board ESP32_GENERIC --version stable
stubber build --port esp32 --board ESP32_GENERIC --version stable
```

The resulting stub package is placed under `repos/micropython-stubs/publish/`.

## Full workflow at a glance

```bash
pip install micropython-stubber
mkdir ~/my-stubs && cd ~/my-stubs

stubber clone --add-stubs
stubber switch stable
stubber docstubs --enrich
stubber frozen --version stable --enrich
stubber merge --port esp32 --board ESP32_GENERIC --version stable
stubber build --port esp32 --board ESP32_GENERIC --version stable

# Optional: capture stubs from a connected device
# stubber firmware-stubs
```

## Next steps

* **Use the stubs in your editor** – see the [MicroPython-stubs][stubs-repo] repository for ready-to-use packages and editor configuration examples.
* **Generate stubs for a custom or forked firmware** – see [Generating Stubs for Custom MicroPython Builds](25_custom_micropython.md).
* **Understand what each stub type contains** – see [Approach to collecting stub information](10_approach.md).
* **Full command reference** – see [Using MicroPython Stubber](20_creating.md).

[stubs-repo]: https://github.com/Josverl/micropython-stubs
