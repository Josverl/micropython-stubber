# Boost MicroPython productivity in VSCode
 
  [![pypi version](https://badgen.net/pypi/v/micropython-stubber)](https://pypi.org/project/micropython-stubber/)
  [![python versions](https://badgen.net/pypi/python/micropython-stubber)](https://badgen.net/pypi/python/micropython-stubber)
  [![Documentation Status](https://readthedocs.org/projects/micropython-stubber/badge/?version=latest)](https://micropython-stubber.readthedocs.io/en/latest/?badge=latest "Document build status badge")
  [![Star on GitHub](https://img.shields.io/github/stars/josverl/micropython-stubber.svg?style=social)](https://github.com/josverl/micropython-stubber/stargazers)
  [![All Contributors](https://img.shields.io/badge/all_contributors-19-green.svg?style=flat-square)](#Contributions)
  <!-- break -->
  [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Josverl/micropython-stubber.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Josverl/micropython-stubber/context:python)
  [![pytest tests/common](https://github.com/Josverl/micropython-stubber/actions/workflows/pytest.yml/badge.svg)](https://github.com/Josverl/micropython-stubber/actions/workflows/pytest.yml)
  [![codecov](https://codecov.io/gh/Josverl/micropython-stubber/branch/main/graph/badge.svg?token=WJFGMKBHOV)](https://codecov.io/gh/Josverl/micropython-stubber)
  [![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black "Black badge")
  <!-- break -->
  [![Open in VSCode](https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=Open%20in%20Visual%20Studio%20Code&labelColor=2c2c32&color=007acc&logoColor=007acc
)](https://open.vscode.dev/josverl/micropython-stubber)
  
The intellisense and code linting that is so prevalent in modern editors, does not work out-of-the-gate for MicroPython projects.
While the language is Python, the modules used are different from CPython , and also different ports have different modules and classes , or the same class with different parameters.

Writing MicroPython code in a modern editor should not need to involve keeping a browser open to check for the exact parameters to read a sensor, light-up a led or send a network request.

Fortunately with some additional configuration and data, it is possible to make the editors understand your flavor of MicroPython, wether you use one of the pre-compiled firmwares, but also if you run a one-off custom firmware version.


![demo][]]

In order to achieve this a few things are needed:
1) Stub files for the native / enabled modules in the firmware using PEP 484 Type Hints
2) Specific configuration of the VSCode Python extensions 
3) Specific configuration of Pylint [ Optional ]
4) Suppression of warnings that collide with the MicroPython principals or code optimization.

Please review the documentation on [https://micropython-stubber.readthedocs.io]  

With that in place, VSCode will understand MicroPython for the most part, and help you to write code, and catch more errors before deploying it to your board. 

Note that the above is not limited to VSCode and pylint, but it happens to be the combination that I use. 

A lot of subs have already been generated and are shared on github or other means,  so it is quite likely that you can just grab a copy be be productive in a few minutes.

For now you will need to [configure this by hand](#manual-configuration), or use the [micropy cli` tool](#using-micropy-cli)

1. The sister-repo [**MicroPython-stubs**][stubs-repo] contains [all stubs][all-stubs] I have collected with the help of others, and which can be used directly.
That repo also contains examples configuration files that can be easily adopted to your setup.

2. A second repo [micropy-stubs repo][stubs-repo2] maintained by BradenM, also contains stubs, but in a structure only used and distributed by the [micropy-cli](#using-micropy-cli) tool.
You should use micropy-cli to consume stubs from that repo.

The (stretch) goal is to create a VSCode add-in to simplify the configuration, and allow easy switching between different firmwares and versions.


## Install and basic usage

``` sh
pip install micropython-stubber

# go to your working folder 
cd my_stub_folder
mkdir all-stubs

# clone the micropython repo's and switch to a specific version 
stubber clone
stubber switch --version v1.18

# get the document stubs for the current version ( v1.18 )
stubber get-docstubs

# get the frozen stubs for the current version ( v1.18 )
stubber get-frozen

# get the core CPython compatibility stubs from PyPi 
stubber get-core

# Update the fallback stubs
stubber update-fallback

#
ls all-stubs
dir all-stubs
```


## Developing & testing 

This is described in more detail in the [developing](docs/developing.md) and [testing](docs/testing.md)  documents in the docs folder.

## Branch Main
The name of the default branch has been changed to `main`.
If you have cloned this repo before you main need to adjust the local repro to be aware of this, or create a fresh clone.

To update run the below command:  
``` bash
git branch -m master main                    
git fetch origin
git branch -u origin/main main                      
git remote set-head origin -a
```

for more info see [**Renaming a branch**](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-branches-in-your-repository/renaming-a-branch#updating-a-local-clone-after-a-branch-name-changes)

## Licensing 

MicroPython-Stubber is licensed under the MIT license, and all contributions should follow this [LICENSE](LICENSE).


# Contributions
<!-- spell-checker: disable -->

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://github.com/Josverl"><img src="https://avatars2.githubusercontent.com/u/981654?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Jos Verlinde</b></sub></a><br /><a href="https://github.com/Josverl/micropython-stubber/commits?author=josverl" title="Code">💻</a> <a href="#research-josverl" title="Research">🔬</a> <a href="#ideas-josverl" title="Ideas, Planning, & Feedback">🤔</a> <a href="#content-josverl" title="Content">🖋</a> <a href="#stubs-josverl" title="MicroPython stubs">📚</a> <a href="#test-josverl" title="Test">✔</a></td>
    <td align="center"><a href="https://thonny.org/"><img src="https://avatars1.githubusercontent.com/u/46202078?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Thonny, Python IDE for beginners</b></sub></a><br /><a href="#ideas-thonny" title="Ideas, Planning, & Feedback">🤔</a> <a href="#research-thonny" title="Research">🔬</a></td>
    <td align="center"><a href="https://micropython.org/"><img src="https://avatars1.githubusercontent.com/u/6298560?v=4?s=100" width="100px;" alt=""/><br /><sub><b>MicroPython</b></sub></a><br /><a href="#data-micropython" title="Data">🔣</a> <a href="#stubs-micropython" title="MicroPython stubs">📚</a></td>
    <td align="center"><a href="https://github.com/loboris"><img src="https://avatars3.githubusercontent.com/u/6280349?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Boris Lovosevic</b></sub></a><br /><a href="#data-loboris" title="Data">🔣</a> <a href="#stubs-loboris" title="MicroPython stubs">📚</a></td>
    <td align="center"><a href="https://github.com/pfalcon"><img src="https://avatars3.githubusercontent.com/u/500451?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Paul Sokolovsky</b></sub></a><br /><a href="#data-pfalcon" title="Data">🔣</a> <a href="#stubs-pfalcon" title="MicroPython stubs">📚</a></td>
    <td align="center"><a href="https://github.com/pycopy"><img src="https://avatars0.githubusercontent.com/u/67273174?v=4?s=100" width="100px;" alt=""/><br /><sub><b>pycopy</b></sub></a><br /><a href="#data-pycopy" title="Data">🔣</a> <a href="#stubs-pycopy" title="MicroPython stubs">📚</a></td>
    <td align="center"><a href="https://github.com/pycom"><img src="https://avatars2.githubusercontent.com/u/16415153?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Pycom</b></sub></a><br /><a href="#infra-pycom" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/BradenM"><img src="https://avatars1.githubusercontent.com/u/5913808?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Braden Mars</b></sub></a><br /><a href="https://github.com/Josverl/micropython-stubber/issues?q=author%3ABradenM" title="Bug reports">🐛</a> <a href="https://github.com/Josverl/micropython-stubber/commits?author=BradenM" title="Code">💻</a> <a href="#stubs-BradenM" title="MicroPython stubs">📚</a> <a href="#platform-BradenM" title="Packaging/porting to new platform">📦</a></td>
    <td align="center"><a href="https://binary.com.au/"><img src="https://avatars2.githubusercontent.com/u/175909?v=4?s=100" width="100px;" alt=""/><br /><sub><b>James Manners</b></sub></a><br /><a href="https://github.com/Josverl/micropython-stubber/commits?author=jmannau" title="Code">💻</a> <a href="https://github.com/Josverl/micropython-stubber/issues?q=author%3Ajmannau" title="Bug reports">🐛</a></td>
    <td align="center"><a href="http://patrickwalters.us/"><img src="https://avatars0.githubusercontent.com/u/4002194?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Patrick</b></sub></a><br /><a href="https://github.com/Josverl/micropython-stubber/issues?q=author%3Aaskpatrickw" title="Bug reports">🐛</a> <a href="https://github.com/Josverl/micropython-stubber/commits?author=askpatrickw" title="Code">💻</a> <a href="#stubs-askpatrickw" title="MicroPython stubs">📚</a></td>
    <td align="center"><a href="https://opencollective.com/pythonseverywhere"><img src="https://avatars3.githubusercontent.com/u/16009100?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Paul m. p. P.</b></sub></a><br /><a href="#ideas-pmp-p" title="Ideas, Planning, & Feedback">🤔</a> <a href="#research-pmp-p" title="Research">🔬</a></td>
    <td align="center"><a href="https://github.com/edreamleo"><img src="https://avatars0.githubusercontent.com/u/592928?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Edward K. Ream</b></sub></a><br /><a href="#plugin-edreamleo" title="Plugin/utility libraries">🔌</a></td>
    <td align="center"><a href="https://github.com/dastultz"><img src="https://avatars3.githubusercontent.com/u/4334042?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Daryl Stultz</b></sub></a><br /><a href="#stubs-dastultz" title="MicroPython stubs">📚</a></td>
    <td align="center"><a href="https://github.com/cabletie"><img src="https://avatars1.githubusercontent.com/u/2356734?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Keeping things together</b></sub></a><br /><a href="https://github.com/Josverl/micropython-stubber/issues?q=author%3Acabletie" title="Bug reports">🐛</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/vbolshakov"><img src="https://avatars2.githubusercontent.com/u/2453324?v=4?s=100" width="100px;" alt=""/><br /><sub><b>vbolshakov</b></sub></a><br /><a href="https://github.com/Josverl/micropython-stubber/issues?q=author%3Avbolshakov" title="Bug reports">🐛</a> <a href="#stubs-vbolshakov" title="MicroPython stubs">📚</a></td>
    <td align="center"><a href="https://lemariva.com/"><img src="https://avatars2.githubusercontent.com/u/15173329?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Mauro Riva</b></sub></a><br /><a href="#blog-lemariva" title="Blogposts">📝</a> <a href="https://github.com/Josverl/micropython-stubber/issues?q=author%3Alemariva" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://github.com/MathijsNL"><img src="https://avatars0.githubusercontent.com/u/1612886?v=4?s=100" width="100px;" alt=""/><br /><sub><b>MathijsNL</b></sub></a><br /><a href="https://github.com/Josverl/micropython-stubber/issues?q=author%3AMathijsNL" title="Bug reports">🐛</a></td>
    <td align="center"><a href="http://comingsoon.tm/"><img src="https://avatars0.githubusercontent.com/u/13251689?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Callum Jacob Hays</b></sub></a><br /><a href="https://github.com/Josverl/micropython-stubber/issues?q=author%3ACallumJHays" title="Bug reports">🐛</a> <a href="#test-CallumJHays" title="Test">✔</a></td>
    <td align="center"><a href="https://github.com/v923z"><img src="https://avatars0.githubusercontent.com/u/1310472?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Zoltán Vörös</b></sub></a><br /><a href="#data-v923z" title="Data">🔣</a></td>
    <td align="center"><a href="https://github.com/vincent-l-j"><img src="https://avatars.githubusercontent.com/u/20021376?v=4?s=100" width="100px;" alt=""/><br /><sub><b>vincent-l-j</b></sub></a><br /><a href="https://github.com/Josverl/micropython-stubber/commits?author=vincent-l-j" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/yegorLitvinov"><img src="https://avatars.githubusercontent.com/u/20367310?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Egor Litvinov</b></sub></a><br /><a href="https://github.com/Josverl/micropython-stubber/issues?q=author%3AyegorLitvinov" title="Bug reports">🐛</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

----------------------------

--------------------------------



[stubs-repo]:   https://github.com/Josverl/micropython-stubs
[stubs-repo2]:  https://github.com/BradenM/micropy-stubs
[micropython-stubber]: https://github.com/Josverl/micropython-stubber
[micropython-stubs]: https://github.com/Josverl/micropython-stubs#micropython-stubs
[micropy-cli]: https://github.com/BradenM/micropy-cli
[using-the-stubs]: https://github.com/Josverl/micropython-stubs#using-the-stubs
[demo]:         https://github.com/Josverl/micropython-stubber/blob/main/docs/img/demo.gif?raw=true	"demo of writing code using the stubs"
[stub processing order]: https://github.com/Josverl/micropython-stubber/blob/main/docs/img/stuborder_pylance.png?raw=true	"recommended stub processing order"
[naming-convention]: #naming-convention-and-stub-folder-structure
[all-stubs]: https://github.com/Josverl/micropython-stubs/blob/main/firmwares.md
[micropython]: https://github.com/micropython/micropython
[micropython-lib]:  https://github.com/micropython/micropython-lib
[pycopy]: https://github.com/pfalcon/pycopy
[pycopy-lib]: https://github.com/pfalcon/pycopy-lib

