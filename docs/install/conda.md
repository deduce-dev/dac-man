# Installing Dac-Man using Conda

The recommended way to install and run Dac-Man is through a Conda environment.
This will allow you to install Dac-Man inside an independent Python installation,
avoiding problems such as lack of administrator rights, old Python version, conflicting packages, etc.

## Installing the `conda` package manager

The `conda` package manager is used to create and manage Conda environments.

`conda` is available for all major operating systems (GNU/Linux, macOS, Windows).
Refer to the [Conda install guide](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)
for detailed information on how to install `conda` for your system.

## Installing Dac-Man in a new Conda environment

After installing `conda`, clone the Dac-Man source code repository using Git
and navigate to the root of the repository:

```sh
git clone https://github.com/dghoshal-lbl/dac-man && cd dac-man
```

Then, run this command to automatically create a Conda environment and install Dac-Man at the same time:

```sh
conda env create --file environment.yml && conda activate dacman-env
```

!!! tip
    This will install only the dependencies needed for Dac-Man's core functionality. [These additional instructions](../../install/dependencies) describe how to install dependencies for all of Dac-Man's built-in plug-ins in a single step.

## Testing the installation

After the installation is complete, verify that the environment is active:

```sh
# the shell prompt should contain the name of the environment
(dacman-env)$ which python
# this should return a Python executable under a Conda subdirectory,
# e.g. "/opt/conda/envs/dacman-env/bin/python"
```

!!! note
    The Conda environment where Dac-Man is installed needs to be activated (`conda activate dacman-env`) whenever a new shell session is started.

Finally, verify that the `dacman` command-line tool is working properly:

```sh
(dacman-env)$ dacman --help
```

Now that `dacman` is operational, head over to the [next section](../../use/desktop) for instructions and examples on how to use Dac-Man.

---

## Installing Dac-Man in an existing environment

Instead of creating a Conda environment for Dac-Man from scratch, it's possible to install Dac-Man in an existing environment.

From the root of Dac-Man's repository, after activating the environment,
install Dac-Man using Pip:

```sh
pip install .
```

## Installing Dac-Man on NERSC

At NERSC, `conda` is already installed, but needs to be loaded with the `module` command, e.g.:

```sh
module load python/3.7-anaconda-2019.07
```

Once the module is loaded, the `conda` command will be available to the shell.
From there, follow the same steps as described [above](#installing-dac-man-in-a-new-conda-environment).

For more information, refer to the [NERSC documentation](https://docs.nersc.gov/programming/high-level-environments/python/#conda-environments).
