# WebAssembly Firmware Stub Generator

The browser tool runs `createstubs.py` against a MicroPython WebAssembly interpreter and synchronizes the generated firmware stubs to a local directory.

## Generate Stubs

Run all recipes from the repository root.

1. Start the ZIP-aware server:

   ```bash
   just wasm_stub
   ```

   This creates `webassembly-stubber/WASM-TEMP` and prints the page URL. Keep the server running and open that URL in a Chromium-based browser.

2. Select one interpreter source on the page:

   - **MicroPython version** loads a published `@micropython/micropython-webassembly-pyscript` package.
   - **PyScript release** uses the MicroPython interpreter bundled with that PyScript release.
   - **Local build** loads a ZIP from the repository's `firmware/` directory.

3. Select **Generate stubs**. When the browser requests a directory, select the empty `webassembly-stubber/WASM-TEMP` directory created in step 1.

4. Wait for the terminal output to report that `/stubs` was synchronized. The generated files are now under `webassembly-stubber/WASM-TEMP/stubs/`.

5. Copy the generated firmware stub directory into `repos/micropython-stubs/stubs/`, review it, and build the package for the matching MicroPython version:

   ```bash
   just wasm_build <version>
   ```

   `wasm_build` runs `stubber merge` and `stubber build`; it does not copy the generated files.

## Versions And Local Builds

The page retrieves published MicroPython and PyScript versions automatically and lists them in the corresponding selectors. No separate version query is needed.

To build stable or preview WebAssembly firmware locally, run:

```bash
just sa_wasm stable
just sa_wasm preview
```

For a manually supplied build, create a ZIP containing `micropython.mjs` and `micropython.wasm` at its root, then place it in `firmware/`. Restart `just wasm_stub` if the server is already running; the ZIP filename appears under **Local build**.

## Troubleshooting

- Use `just wasm_stub`, not `python -m http.server`; local ZIP discovery requires `serve.py`.
- Select an empty, dedicated output directory. Synchronizing a directory containing many files can be very slow.
- The browser stores the selected directory handle. Use **Reset output folder** on the page to choose another directory. Close other tabs using the tool if the reset is blocked.
- If port 8000 is already in use, stop the existing server before running `just wasm_stub`.

## Files

- `createstubs-pyscript-hosted.html`: browser interface and PyScript configuration
- `mount_createstubs.py`: mounts the output directory, runs the stubber, and synchronizes `/stubs`
- `serve.py`: local server and ZIP-backed WebAssembly endpoints
- `tests/`: Playwright regression tests
