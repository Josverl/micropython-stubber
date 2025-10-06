To create stubs for a locally built MicroPython WebAssembly version you can either: 
- place the `micropython.mjs`  and `micropython.wasm` files in the `build-pyscript` folder 
- update the `interpreter` line in the `createstubs-req.toml` file to point to the micropython.mjs file  inthat folder.

- or host your custom build folder, e.g.:
  ```bash
  python -m http.server -d ./my-custom-build-folder --bind
    ```
- and point to that folder in the `createstubs-req.toml` file, e.g.:
  ```toml
  interpreter = "./my-custom-build-folder/micropython.mjs"
  ```