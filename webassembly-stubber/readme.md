# WebAssembly Firmware Type Stubs Generator

This folder contains an HTML page that can be used to create initial firmware type stubs for **WebAssembly** and **PyScript** environments.

## Contents

- **`createstubs-pyscript-hosted.html`** - Interactive HTML page that runs MicroPython's createstubs in the browser
- **`mount_createstubs.py`** - Python script that handles the stub generation process
- **`createstubs-req.toml`** - Configuration file for PyScript requirements
- **`stubs/`** - Output directory where generated stubs are saved

## Usage

1. **Start the local server** (required for proper file access):
   ```bash
   python -m http.server -d ./webassembly-stubber --bind 127.0.0.1
   ```
2. Open `http://127.0.0.1:8000/createstubs-pyscript-hosted.html` in a web browser
3. The page will automatically run the stub generation process using PyScript
4. When prompted, select a local folder where the stubs should be saved
5. The generated firmware stubs will be saved to a `stubs` subfolder in your selected location

## Finding Available MicroPython Versions

To find available MicroPython WebAssembly versions, use the included query script:

```bash
python query_jsdelivr_versions.py
```

This will display all published versions of `@micropython/micropython-webassembly-pyscript` from jsDelivr CDN. You can then update the `createstubs-req.toml` file to use a specific version by modifying the `interpreter` line:

```toml
# Use latest version
interpreter = "https://cdn.jsdelivr.net/npm/@micropython/micropython-webassembly-pyscript@latest/micropython.mjs"

# Use specific stable version
interpreter = "https://cdn.jsdelivr.net/npm/@micropython/micropython-webassembly-pyscript@1.26.0/micropython.mjs"

# Use preview version
interpreter = "https://cdn.jsdelivr.net/npm/@micropython/micropython-webassembly-pyscript@1.27.0-preview-282/micropython.mjs"
```

## Features

- **Browser-based**: No local MicroPython installation required
- **Multiple versions**: Supports different MicroPython versions (v1.24.1, v1.25.0, v1.26-preview)
- **Automatic sync**: Generated stubs are synchronized to your local filesystem
- **Interactive**: Uses PyScript's persistent filesystem for easy file management

## Notes

- Generated stubs are compatible with IDEs and type checkers
- Select an empty or dedicated folder for output to avoid sync performance issues
- The selected folder path is saved in browser cookies for convenience
- **Troubleshooting**: If the page becomes unresponsive, or you want to select a different folder; clear your browser cookies for the http://127.0.0.1:8000/ site.

- Part of the [micropython-stubber](https://github.com/josverl/micropython-stubber) project
