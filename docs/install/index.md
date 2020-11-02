# Installing Dac-Man

Dac-Man is distributed as a Python package compatible with common installation tools and methods.

## Requirements

Dac-Man is written in Python 3, and is compatible with version 3.6 or greater.

It is known to work with the following operating systems:

- GNU/Linux
- macOS
- Unix-like OSs

## Installing Dac-Man using Conda

The recommended way to install and run Dac-Man is through a Conda environment.

### Installing the `conda` package manager

The `conda` package manager is used to create and manage Conda environments.

`conda` is available for all major operating systems (GNU/Linux, macOS, Windows).
Refer to the [Conda install guide](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)
for detailed information on how to install `conda` for your system.

### Installing Dac-Man in a new Conda environment

After installing `conda`, clone the Dac-Man source code repository using Git:

```sh
git clone https://github.com/deduce-dev/dac-man
```

Then, navigate to the root of the cloned repository
and run this command to automatically create a Conda environment
and install Dac-Man, together with its core dependencies, at the same time:

```sh
cd dac-man
conda env create --file ./environment.yml
```

!!! important
    This will install only the dependencies needed for Dac-Man's core functionality. Additional dependencies are needed for Dac-Man's plug-in framework, as described later [here](./dependencies/).

!!! note
    By default, the name of the Conda environment is set in `environment.yml` as `dacman-env`. If for any reason a different name for the environment is needed, modify the value for `name` in `environment.yml`, and then adapt the steps described throughout this documentation specifying the new name to the `--name` option of `conda` commands.

### Installing in an existing Conda environment

If using an existing Conda environment, these steps help illustrate how to install Dac-Man.

Assuming our existing environment has the name `my-conda-env`, we navigate
to the root of Dac-Man's repository, then run the following command to install
Dac-Man as well as its core dependencies:

```sh
conda env update --name my-conda-env --file ./environment.yml
```

---

!!! tip
    In this case, only Dac-man's core dependencies will be installed after these steps. Instructions on how to install dependencies for enabling Dac-Man's included plug-ins can be found on [this page](./dependencies), depending on whether Pip ([here](./dependencies/#using-pip)) or Conda ([here](./dependencies/#using-conda)) was used to install Dac-Man.

## Installing Dac-Man in a new Python virtual environment using Pip

Alternatively, we can use Pip to install Dac-man in a virtual environment (virtualenv).

### Installing Dac-Man in a new virtual environment

Using the built-in `venv` Python module, start by setting up a virtual environment with Python 3.6 or later installed.
In this example, our virtual environment is named "dacman-env".
Next, activate the environment.
At this point, your prompt should indicate that you are in the activated environment (note
the activated environment indicated by `(dacman-env)`),
and check the Python version installed, using the command `python --version`

```sh
$ python3 -m venv dacman-env
$ activate dacman-env
$ (dacman-env) python --version
Python 3.7.7
```

Next, clone the Dac-Man source code repository using Git:

```sh
git clone https://github.com/deduce-dev/dac-man
```

Then, navigate to the root of the cloned repository
and run this command to install the core dependencies:

```sh
cd dac-man
pip install .
```

## Installing Dac-Man in an existing environment

Instead of creating an environment for Dac-Man from scratch,
it is possible to install Dac-Man in an existing environment.

### Installing in an existing Conda environment

These steps illustrate how to install Dac-Man in an existing Conda environment
named e.g. `my-conda-env`.

From the root of Dac-Man's repository,
run the following command to install Dac-Man as well as its core dependencies:

```sh
conda env update --name my-conda-env --file ./environment.yml
```

---

!!! tip
    Also in this case, only Dac-man's core dependencies will be installed after these steps. Instructions on how to install dependencies for enabling Dac-Man's included plug-ins can be found on [this page](./dependencies), depending on whether Pip ([here](./dependencies/#using-pip)) or Conda ([here](./dependencies/#using-conda)) was used to install Dac-Man.

### Installing in an existing Python virtual environment (virtualenv)

The steps to install in an existing environment are similar to the instructions
described in [*Installing Dac-Man in a new virtual environment*](#installing-dac-man-in-a-new-virtual-environment).

## Updating Dac-Man

To update Dac-Man from an existing version,
follow the steps described in [*Installing Dac-Man in an existing environment*](../#installing-dac-man-in-an-existing-environment).
These steps will upgrade the Dac-Man package itself, as well as its dependencies,
in the environment where Dac-Man was installed.

!!! tip
    If issues appear after updating, consider installing Dac-Man in a fresh environment instead.
    For more information about addressing common issues, refer to the [*Troubleshooting*](../../troubleshooting/) section.
