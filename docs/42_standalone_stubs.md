# Build Standalone Port Stubs

MicroPython's Unix, Windows, and WebAssembly PyScript ports run without a physical microcontroller. Their firmware stubs are generated from locally built or published interpreters instead of through a serial connection.

This workflow is intended for maintainers of the `micropython-stubs` packages. Run all `just` recipes from the root of the `micropython-stubber` repository.

## Supported Ports

| Port | Interpreter | Stub generation |
| --- | --- | --- |
| Unix | Native `micropython` executable | `sa_ports_stub.py` runs `createstubs.py` directly |
| Windows | Native `micropython.exe` executable | `sa_ports_stub.py` runs `createstubs.py` directly |
| WebAssembly PyScript | `micropython.mjs` and `micropython.wasm` | The browser tool runs `createstubs.py` through PyScript |

Use Linux or WSL to build the interpreters. Generating Windows stubs from WSL also requires Windows executable interoperability.

The examples below use `stable`. You can substitute `preview` or a specific MicroPython version accepted by `sa_ports_build.py`. Use the same version for every build, generation, merge, and package step.

## Unix And Windows

Build and register both native interpreters with `mpflash`:

```bash
just sa_build stable
```

Generate the Unix stubs:

```bash
just sa_stub stable unix
```

Generate the Windows stubs:

```bash
just sa_stub stable windows
```

Each `sa_stub` run performs the complete port workflow:

1. Locate the matching interpreter registered with `mpflash`.
2. Run `createstubs.py` with that interpreter.
3. Write the firmware stubs under `repos/micropython-stubs/stubs/`.
4. Run `stubber merge` for the port and version.
5. Run `stubber build` to create the installable package.

Set `MPFLASH_FIRMWARE` before building and generating stubs if the firmware files must be stored somewhere other than the `mpflash` default. Both commands must resolve the same firmware folder and registration database.

## WebAssembly PyScript

Build the local PyScript interpreter bundle:

```bash
just sa_wasm stable
```

This creates a ZIP in `firmware/` containing `micropython.mjs` and `micropython.wasm`. Stub generation then continues in a Chromium-based browser:

1. Start the ZIP-aware server:

   ```bash
   just wasm_stub
   ```

2. Open the URL printed by the server.
3. Select **Local build**, choose the matching ZIP, and select **Generate stubs**.
4. When prompted for an output directory, select `webassembly-stubber/WASM-TEMP`.
5. Wait for synchronization, then copy the generated directory from `webassembly-stubber/WASM-TEMP/stubs/` to `repos/micropython-stubs/stubs/`.
6. Merge the stubs and build the package:

   ```bash
   just wasm_build stable
   ```

The browser also lists published MicroPython WebAssembly interpreters and PyScript releases. Select one of those instead of **Local build** when a local interpreter build is not required.

For browser behavior, local ZIP requirements, and troubleshooting, see the [WebAssembly Firmware Stub Generator](https://github.com/Josverl/micropython-stubber/tree/main/webassembly-stubber#readme).

## Troubleshooting

- Run the recipes from the repository root; their paths assume the standard workspace layout.
- Ensure `repos/micropython` and `repos/micropython-stubs` exist before starting.
- If `sa_stub` cannot find an interpreter, rebuild the same version and confirm the firmware folder printed by both commands is identical.
- If a Windows executable cannot run from Linux, use WSL with Windows interoperability enabled.
- Use `just wasm_stub` for WebAssembly. A plain HTTP server cannot discover or serve the ZIP bundles.