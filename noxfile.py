import os

import nox

os.environ["PDM_IGNORE_SAVED_PYTHON"] = "1"


@nox.session(python=("3.7", "3.8", "3.9", "3.10", "3.11"))
def test(session):
    session.run("pdm", "install", "-dGtest", external=True)
    session.run("pytest", "tests/")


@nox.session(python="3.9")
def docs(session):
    session.install("-r", "docs/requirements.txt")

    # Generate documentation into `build/docs`
    session.run("sphinx-build", "-W", "-b", "html", "docs/", "build/docs")


@nox.session(name="docs-live", python="3.9")
def docs_live(session):
    session.install("-r", "docs/requirements.txt")
    session.install("-e", ".")
    session.install("sphinx-autobuild")

    session.run(
        "sphinx-autobuild",
        "docs/",
        "build/docs",
        # Rebuild all files when rebuilding
        "-a",
        # Trigger rebuilds on code changes (for autodoc)
        "--watch",
        "src/monas",
        # Use a not-common high-numbered port
        "--port",
        "8765",
    )
