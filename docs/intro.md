
# Boost MicroPython Productivity in VS Code

The {ref}`IntelliSense <intellisense>` and code linting that is so prevalent in modern editors, does not work out-of-the-gate for MicroPython projects.
While the language is Python, the modules used are different from {ref}`CPython <cpython>`, and also different {ref}`ports <port>` have different modules and classes, or the same class with different parameters.

Writing MicroPython code in a modern editor should not need to involve keeping a browser open to check for the exact parameters to read a sensor, light-up a LED or send a network request.

Fortunately with some additional configuration and data, it is possible to make the editors understand your flavor of MicroPython, even if you run a one-off custom firmware version.

![demo](img/demo.gif)

In order to achieve this a few things are needed:
1) {ref}`Stub files <stub-files>` for the native / enabled modules in the {ref}`firmware <firmware>` using PEP 484 {ref}`Type Hints <type-hints>`
2) Specific configuration of the VS Code Python extensions 
3) Specific configuration of {ref}`Pylint <pylint>`
4) Suppression of warnings that collide with the MicroPython principles or code optimization.

With that in place, VS Code will understand MicroPython for the most part, and help you to write code, and catch more errors before deploying it to your board. 


Note that the above is not limited to VS Code and pylint, but it happens to be the combination that I use.

A lot of stubs have already been generated and are shared on GitHub or other means, so it is quite likely that you can just grab a copy to be productive in a few minutes.For now you will need to configure this by hand, or use the `micropy cli` tool

1. The sister-repo [**MicroPython-stubs**][stubs-repo] contains [all stubs][all-stubs] I have collected with the help of others, and which can be used directly.
That repo also contains examples configuration files that can be easily adopted to your setup.

2. A second repo [micropy-stubs repo][stubs-repo2] maintained by BradenM, also contains stubs but in a structure used and distributed by the micropy-cli tool.
You should use micropy-cli to consume stubs in this repo.

The (stretch) goal is to create a VS Code add-in to simplify the configuration, and allow easy switching between different firmwares and versions.

## Licensing 

MicroPython-Stubber is licensed under the MIT license, and all contributions should follow this [LICENSE](https://github.com/Josverl/micropython-stubber/blob/main/LICENSE).

