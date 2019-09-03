# Running Dac-Man's Test Suite

Dac-Man's test suite is based on pytest.

To run the tests, clone Dac-Man's source repository and navigate to the `tests` directory:

```sh
git clone https://github.com/dghoshal-lbl/dac-man && cd dac-man/tests
```

Then, install the additional dependencies in Dac-Man's environment:

```sh
pip install pytest pytest-console-scripts
```

Finally, run the tests with `pytest`.
The `--verbose` flag is optional, and gives more information about individual tests being run.

```sh
pytest --verbose
```
