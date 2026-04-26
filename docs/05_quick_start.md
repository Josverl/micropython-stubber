(quick-start)=
# Quick Start – Contributing stubs for a new board

This guide walks you through generating and contributing a complete set of MicroPython stubs for a new port or board to the [micropython-stubs][stubs-repo] project.
No prior knowledge of the project internals is needed.

## What are stubs, and why do I need them?

{ref}`Stub files <stub-files>` teach your editor (VS Code, PyCharm, …) about the MicroPython modules that are available on your board.
Without them, the editor has no way to offer code-completion or type-checking for `machine`, `network`, `uos`, and every other MicroPython-specific module.

Three complementary stub types are combined to give the best coverage:

| Stub type | Source | Command |
|-----------|--------|---------|
| {ref}`Firmware stubs <mcu-stubs>` | Connected board | `stubber firmware-stubs` |
| {ref}`Doc stubs <doc-stubs>` | MicroPython documentation | `stubber docstubs` |
| {ref}`Frozen stubs <frozen-stubs>` | Modules frozen into firmware source | `stubber frozen` |

## Prerequisites

* Python 3.9 or newer installed on your PC.
* Git installed (needed to clone the MicroPython source tree).
* A MicroPython board connected to your PC, flashed with a recent **stable** or **preview** release.
* A working directory — for example `~/my-stubs`.

```{note}
**Platform support:** `stubber` has been tested on both Windows and Unix (Linux / macOS).
Running `stubber` inside **WSL2** is also supported, but can occasionally encounter errors caused by extra timing delays that occur after a device resets — if you see connection timeouts, try running from a native Windows terminal instead.
```

## Step 1 – Install micropython-stubber

```bash
uv tool install micropython-stubber
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

All subsequent commands should be run from inside this directory unless noted otherwise.

## Step 3 – Initialize the workspace

Use one command to:

* clone `micropython-stubs` into `./micropython-stubs`
* clone `micropython` + `micropython-lib` into `./micropython-stubs/repos`
* switch those repos to the latest stable MicroPython version

```bash
stubber init
```

At the end, `stubber init` prints a `cd` command with the full path. Run it before continuing:

```bash
cd ~/my-stubs/micropython-stubs
```

After initialization, your workspace looks like this:

```
~/my-stubs/
└── micropython-stubs/
	├── repos/
	│   ├── micropython/      ← MicroPython source (for doc & frozen stubs)
	│   └── micropython-lib/  ← MicroPython library source
	└── publish/              ← Built stub packages
```

## Step 4 (optional) – Generate doc stubs

Doc stubs are generated from the MicroPython documentation and contain full parameter names and descriptions.
Skip this step if you only need firmware stubs for a new board — the cloned repo already contains up-to-date doc stubs.

```bash
stubber docstubs --enrich
```

## Step 5 (optional) – Generate frozen stubs

Frozen stubs cover Python modules compiled directly into the firmware.
Skip this step if the board's frozen modules are already covered in the cloned repo.

```bash
stubber frozen --version stable --enrich
```

```{note}
Generating frozen stubs requires checking out the MicroPython source tree and can take **10–20 minutes** depending on your internet connection and machine speed.
```

## Step 6 – Generate firmware stubs from a connected device

Connect your board (flashed with a stable or preview MicroPython release) and run:

```bash
stubber firmware-stubs
```

This captures the board-specific modules that may not be documented or frozen elsewhere.
The port, board name, and version are detected automatically and used to name the output folder.

## Step 7 – Merge and build the stub package
The `stubber firmware-stubs` command already runs the below steps,
but in some cases you may want to re-run them after making manual edits 
to the generated stubs, or after regenerating doc/frozen stubs in steps 5 and 6.

Combine all stub types for your board into a single distributable package.
Replace `esp32` / `ESP32_GENERIC` with the values reported by the previous step:

```bash
stubber merge --port esp32 --board ESP32_GENERIC --version stable
stubber build --port esp32 --board ESP32_GENERIC --version stable
```

The resulting stub package is placed under `publish/`.

## Step 8 – Verify the stubs locally

Before opening a pull request, install the built stub package locally to confirm it works in your editor.
Replace the folder name below with the actual name produced by `stubber build`:

```bash
# From inside ~/my-stubs/micropython-stubs
pip install ./publish/micropython-v1_27_0-esp32-esp32_generic_c3-stubs/ --target ../typings
```

The `typings` folder is the conventional location for MicroPython stubs in VS Code projects.
Point your editor's Python extension at this folder to get code-completion and type-checking for your board.

## Step 9 – Contribute your stubs

Open a pull request against [micropython-stubs][stubs-repo] so the new board stubs become available to everyone:

```bash
git checkout -b add-stubs-esp32-esp32_generic-stable
git add .
git commit -m "Add stubs for esp32 ESP32_GENERIC stable"
git push origin add-stubs-esp32-esp32_generic-stable
```

Then open a pull request on GitHub at <https://github.com/Josverl/micropython-stubs/compare>.

## Full workflow at a glance

```bash
pip install micropython-stubber
mkdir ~/my-stubs && cd ~/my-stubs

stubber init
cd ~/my-stubs/micropython-stubs

# Optional: regenerate doc and frozen stubs (takes 10-20 min)
# stubber docstubs --enrich
# stubber frozen --version stable --enrich

# Required: board must be connected with stable/preview firmware
stubber firmware-stubs

stubber merge --port esp32 --board ESP32_GENERIC --version stable
stubber build --port esp32 --board ESP32_GENERIC --version stable

# Verify locally before submitting a PR
pip install ./publish/micropython-v1_27_0-esp32-esp32_generic_c3-stubs/ --target ../typings

# Contribute: open a PR to micropython-stubs
git checkout -b add-stubs-esp32-esp32_generic-stable
git add . && git commit -m "Add stubs for esp32 ESP32_GENERIC stable"
git push origin add-stubs-esp32-esp32_generic-stable
```

## Next steps

* **Use the stubs in your editor** – see the [MicroPython-stubs][stubs-repo] repository for ready-to-use packages and editor configuration examples.
* **Generate stubs for a custom or forked firmware** – see [Generating Stubs for Custom MicroPython Builds](25_custom_micropython.md).
* **Understand what each stub type contains** – see [Approach to collecting stub information](10_approach.md).
* **Full command reference** – see [Using MicroPython Stubber](20_creating.md).

[stubs-repo]: https://github.com/Josverl/micropython-stubs
