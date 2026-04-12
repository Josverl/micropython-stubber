# Bulk Stubber

The bulk stubber command runs firmware stub generation on one or more connected boards and then completes the full pipeline:

1. Generate stubs on-device.
2. Copy raw stubs into the local stubs repo.
3. Merge firmware stubs with docstubs.
4. Build publishable stub packages.

Use this command:

```bash
stubber firmware-stubs
```

Supported aliases are:

- `stubber firmware`
- `stubber mcu-stubs`
- `stubber get-mcu-stubs`
- `stubber mcu`

## Command Options

```bash
stubber firmware-stubs [OPTIONS]
```

### Core options

- `--variant [Full|Mem|DB]` (default: `DB`)
	- Selects which on-device script to import:
	- `DB` -> `import createstubs_db`
	- `Mem` -> `import createstubs_mem`
	- `Full` -> `import createstubs`

- `--format, -f [py|mpy]` (default: `mpy`)
	- Controls which package manifest is installed via `mip`:
	- `mpy` -> `pkg_mpy.json`
	- `py` -> `pkg_full.json`

### Device selection

- `--serial, --serial-port, -s SERIALPORT` (repeatable, default: `*`)
	- Include only matching serial ports/globs.

- `--ignore, -i SERIALPORT` (repeatable)
	- Ignore matching serial ports/globs.
	- Defaults from the `MPFLASH_IGNORE` environment variable.

- `--bluetooth / --no-bluetooth` (default: `--no-bluetooth`)
	- Include Bluetooth devices in scanning.

### Stub generation behavior

- `--exclude, -e MODULE` (repeatable)
	- Module names to skip during on-board stub generation.
	- The list is uploaded to the board as `modulelist_exclude.txt`.

- `--mount-vfs / --no-mount-vfs` (default: `--mount-vfs`)
	- Controls whether `mpremote mount` is used during generation.
	- Use `--no-mount-vfs` to force on-device flash generation and copy `:stubs` back afterward.

- `--debug / --no-debug` (default: `--no-debug`)
	- Enables more verbose logging.

## What The Command Actually Does

For each selected board, the current implementation performs this flow:

1. Ensures required sister repos exist (`CONFIG.repos`).
2. Discovers boards using `mpflash` and filters out boards marked with `micropython-stubber.ignore = true` in board metadata.
3. Prepares `lib` on-device and appends it to `sys.path` (required for `mpremote mip`).
4. Installs the selected `createstubs` package manifest on-device.
5. Writes `lib/boardname.py` with `BOARD_ID` when available.
6. Optionally uploads `modulelist_exclude.txt`.
7. Runs the selected `createstubs` variant, with retries for robustness.
8. Determines the generated stub folder from `INFO  : Path: ...` output.
9. Loads `modules.json` and validates output quality (requires at least 10 generated `*.p*` files).
10. Runs post-processing (`stubgen` when needed, formatting, autoflake).
11. Copies raw stubs into `CONFIG.stub_path`.
12. Merges docstubs and builds publication packages.
13. Prints summary tables for raw/merged paths and publication results.

## VFS Mounting Behavior

The command normally mounts a host temp folder for speed (`mpremote mount`).
You can override this with `--no-mount-vfs` for any board.

For low-memory ESP8266 boards, the implementation still automatically switches to local flash mode even if `--mount-vfs` is set:

- no VFS mount
- generate stubs on board flash
- copy `:stubs` back to host afterward

## Error Handling and Retries

- `createstubs` execution is retried up to 10 times with 15-second waits.
- Boards are reset before each run.
- Timeout is board-aware:
	- ESP8266: 90 seconds
	- others (including Raspberry Pi Pico / RP2040): 6 minutes
- If one board fails, processing continues with the next board.

## Typical Usage

```bash
# Stub all connected serial boards
stubber firmware-stubs

# Example: Raspberry Pi Pico connected on COM6
stubber firmware-stubs --serial COM6

# Example: Raspberry Pi Pico with module excludes
stubber firmware-stubs --serial COM6 -e _onewire -e webrepl_setup

# Example: Raspberry Pi Pico without mounted VFS
stubber firmware-stubs --serial COM6 --no-mount-vfs

# Exclude problematic modules
stubber firmware-stubs -e _onewire -e webrepl_setup

# Use source scripts instead of mpy
stubber firmware-stubs --format py

# Include Bluetooth scanning
stubber firmware-stubs --bluetooth
```

## Notes

- Success requires more than just generating raw stubs; the command returns success only when publication packages are built.
- If no compatible boards are found, the command exits with an error.
