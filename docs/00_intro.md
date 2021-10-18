
# Boost MicroPython productivity in VSCode

The intellisense and code linting that is so prevalent in modern editors, does not work out-of-the-gate for MicroPython projects.
While the language is Python, the modules used are different from CPython , and also different ports have different modules and classes , or the same class with different parameters.

Writing MicroPython code in a modern editor should not need to involve keeping a browser open to check for the exact parameters to read a sensor, light-up a led or send a network request.

Fortunately with some additional configuration and data, it is possible to make the editors understand your flavor of MicroPython. even if you run a on-off custom firmware version.

![demo](img/demo.gif)

In order to achieve this a few things are needed:
1) Stub files for the native / enabled modules in the firmware using PEP 484 Type Hints
2) Specific configuration of the VSCode Python extensions 
3) Specific configuration of Pylint
4) Suppression of warnings that collide with the MicroPython principals or code optimization.

With that in place, VSCode will understand MicroPython for the most part, and help you to write code, and catch more errors before deploying it to your board. 


Note that the above is not limited to VSCode and pylint, but it happens to be the combination that I use. 

A lot of subs have already been generated and are shared on github or other means,  so it is quite likely that you can just grab a copy be be productive in a few minutes.

For now you will need to [configure this by hand](#manual-configuration), or use the [micropy cli` tool](#using-micropy-cli)

1. The sister-repo [**MicroPython-stubs**][stubs-repo] contains [all stubs][all-stubs] I have collected with the help of others, and which can be used directly.
That repo also contains examples configuration files that can be easily adopted to your setup.

2. A second repo [micropy-stubs repo][stubs-repo2] maintained by BradenM,  also contains stubs but in a structure used and distributed by the [micropy-cli](#using-micropy-cli) tool.
you should use micropy-cli to consume stubs in this repo.

The (stretch) goal is to create a VSCode add-in to simplify the configuration, and allow easy switching between different firmwares and versions.

## Licensing 

MicroPython-Stubber is licensed under the MIT license, and all contributions should follow this [LICENSE](LICENSE).

