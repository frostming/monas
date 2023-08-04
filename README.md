# Monas

<!--index start-->

[![Tests](https://github.com/frostming/monas/workflows/Tests/badge.svg)](https://github.com/frostming/monas/actions?query=workflow%3Aci)
[![pypi version](https://img.shields.io/pypi/v/monas.svg)](https://pypi.org/project/monas/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)

Python monorepo made easy.

🚧 **[WIP]** This project still in a rapid development and the behaviors may change. 🚧

➡️ [Example Repository](https://github.com/frostming/monas-example-repo)

## About this project

**Monas** is a tool to manage multiple Python projects in a single repository, or the so called ["Monorepo"](https://en.wikipedia.org/wiki/Monorepo).
It is mainly inspired by [Lerna](https://lerna.js.org/). In a monorepo, some dependencies are shared across packages while others are different. When you change the code of one of these shared dependencies, you may want to run the test suite across all dependant packages. Monas makes the workflow easier.

<!--index end-->

## Installation

**Monas** requires Python >=3.8.

It is recommended to install with `pipx`, if `pipx` haven't been installed yet, refer to the [pipx's docs](https://github.com/pipxproject/pipx)

```bash
pipx install monas
```

Alternatively, install with `pip` to the user site:

```bash
python -m pip install --user monas
```

## To-do

- [x] Documentation
- [x] Tests
- [x] `setup.cfg` support
- [ ] (Possible) Poetry backend support
- [ ] `src` package layout

## License

MIT.
