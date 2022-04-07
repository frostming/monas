# Integration

**Monas** does not manage dependencies or environments itself, but it should work with most tools of Python packaging.

## PEP 517 support

Since subpackages are installed in **editable mode**, Monas supports all build backends that support editable installation.
The list includes:

1. [setuptools](https://setuptools.pypa.io/)
2. [pdm](https://pdm.fming.dev/)
3. [flit](https://flit.pypa.io/)
4. [hatch](https://ofek.dev/hatch/latest/)

Moreover, the above backends now all support [PEP 621]/[PEP 631] metadata, so Monas will initialize the project
metadata with PEP 621 format stored in `pyproject.toml`. At present, Monas does not work with package
managers that do not support PEP 621.

[pep 621]: https://www.python.org/dev/peps/pep-0621/
[pep 631]: https://www.python.org/dev/peps/pep-0631/

## Installer

Monas uses `virtualenv` and `pip` to install dependencies by creating a `.venv` folder under each subpackage.
Fortunately, the above selected package managers can detect virtualenv automatically and you can start your work from it.

```{note} Monas works the same in arbitrary sub directories in the project.

```

```{admonition} No lock files will be created
:class: note

Monas, however, does not create any lock files. This is to ensure the installation is fast and correct. That is to say,
Monas doesn't talk with any package managers other than `pip`.

Thanks to the standardization of PEP 621 and PEP 631, Monas is able to add new dependency lines into the
`pyproject.toml` file in a uniform way. You can anyway use your favorite package managers from the subpackage directory
and create lock files if necessary.
```
