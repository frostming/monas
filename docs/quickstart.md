# Quick Start

## Install Monas

**Monas** requires Python >=3.8.

It is recommended to install with `pipx`, if `pipx` haven't been installed yet, refer to the [pipx's docs](https://github.com/pipxproject/pipx)

```bash
pipx install monas
```

Alternatively, install with `pip` to the user site:

```bash
python -m pip install --user monas
```

## Create a monorepo

Monas is integrated with Git. You need to install it if it isn't on your system.

```bash
git init mono-project
cd mono-project
monas init
```

## Add a subpackage

```bash
monas new foo
```

Answer a few questions and the subpackage `foo` will be created under `packages/` directory.

See what packages are added:

```bash
monas list
```

## Install all packages and dependencies

```bash
monas install
```

Monas will create a virtualenv under each subpackage and install all dependencies into it.
The subpackage itself and other subpackages, if required, are installed in **editable mode**.
That is to say, any changes locally will take effect immediately.

## Add dependencies to the subpackages

```bash
monas add click
```

The dependencies will be installed into the `.venv` folder under each subpackage.

## Submit and push

```bash
git add .
git commit -m "initial commit"
git remote add origin <your repo url>
git push -u origin main
```

## Bump version and Publish

```bash
monas bump
monas publish
```

A git tag of the specified version together with a PyPI release will be published.
