# Testing Dac-Man

## Running the `dacman` command-line tool

To verify that Dac-Man was installed successfully,
activate the Dac-Man environment (by default named `dacman-env`).
Once the environment is active, it's name should be displayed on the shell prompt.

Next, invoke `dacman` on the command line:

```sh
$ conda activate dacman-env
(dacman-env)$ dacman --help
```

If the help message is successfully printed, the installation of Dac-Man was successful.

!!! important
    The Dac-Man environment needs to be activated each time a new shell session is started.

## Running the test suite

Dac-Man's test suite is based on pytest.

To run the tests, clone Dac-Man's source repository and navigate to the `tests` directory:

```sh
git clone https://github.com/deduce-dev/dac-man && cd dac-man/tests
```

Next, if using the Conda environment, install additional dependencies
by updating Dac-Man's environment:

```sh
conda env update --name dacman-env --file ../dependencies/conda/pytest.yml
```

Finally, run the tests with `pytest`.
The `--verbose` flag (optional) gives more information about individual tests being run.

```sh
pytest --verbose
```
