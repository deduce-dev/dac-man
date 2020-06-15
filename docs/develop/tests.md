# Running Dac-Man's Test Suite

Dac-Man's test suite is based on pytest.

To run the tests, clone Dac-Man's source repository and navigate to the `tests` directory:

```sh
git clone https://github.com/dghoshal-lbl/dac-man && cd dac-man/tests
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
