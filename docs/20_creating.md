# Using MicroPython Stubber 

This section describes how to use micropython-stubber to create and maintain {ref}`stubs <stub-files>` for a MicroPython {ref}`firmware <firmware>` or project.

If you just want to use the stubs, then you can skip this section and instead read the documentation in the sister-repo [micropython-stubs][] section [using-the-stubs][]. 
## Command Reference

| Task | Primary Command | Aliases | Description |
|------|-----------------|---------|-------------|
| Clone repositories | `stubber clone --add-stubs` | - | Clone MicroPython repos locally |
| Switch version | `stubber switch v1.22.2` | - | Switch to specific version/branch/commit |
| Generate doc stubs | `stubber docs-stubs` | `docstubs`, `docs`, `get-docstubs` | Create {ref}`doc stubs <doc-stubs>` from documentation |
| Generate frozen stubs | `stubber frozen-stubs` | - | Create {ref}`frozen stubs <frozen-stubs>` from frozen modules |
| Generate MCU stubs | `stubber mcu-stubs` | `mcu`, `get-mcu-stubs` | Create {ref}`MCU stubs <mcu-stubs>` from connected device |
| Get core stubs | `stubber get-core` | - | Download {ref}`CPython <cpython>` compatibility stubs |
| Build packages | `stubber build` | - | Build stub packages for distribution |
| Publish packages | `stubber publish-stubs` | - | Publish stubs to repository |
| Merge stubs | `stubber merge` | - | Combine different stub types |
| Show configuration | `stubber show-config` | `config` | Display current configuration |
| Create variants | `stubber variants` | `make-variants` | Create minified createstubs variants |

## Quick Start

For official MicroPython releases, follow the standard workflow:

```bash
pip install micropython-stubber
stubber clone --add-stubs
stubber switch stable
# if you have made any updates : 
stubber docs-stubs
stubber frozen-stubs
# connect a mcu via serial 
stubber mcu-stubs
```

The `stubber mcu-stubs` command will create the {ref}`stubs <stub-files>` on the {ref}`MCU <mcu>`, copy them to the pc and {ref}`merge <merge>` them with the other stubs,
and create a type-stub package in the `micropython-stubs/publish` folder.

You can specify the version of the stubs using the `--version` parameter on the various commands, for example `--version=1.22.2` or `--version=latest`.

The name of the folder will be based on the the detected name of the port and the board, including the version, and will be logged as part of the output of the command, as shown below:

```
                                                         Results
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━┓
┃ Result   ┃ Name/Path                                                                                ┃ Version  ┃ Error ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━┩
│ Build OK │ micropython-esp32-esp32_generic_c6-stubs                                                 │ 1.27.0a1 │       │
│          │ repos/micropython-stubs/publish/micropython-v1_27_0_preview-esp32-esp32_generic_c6-stubs │          │       │
└──────────┴──────────────────────────────────────────────────────────────────────────────────────────┴──────────┴───────┘
```

## Custom MicroPython Builds

If you're working with a fork, branch, pull request, or custom build of MicroPython, see the [Custom MicroPython Guide](25_custom_micropython.md) for detailed step-by-step instructions.



