# dacman-csv

A plug-in for Dac-man to compute, analyze and visualize differences (_diffs_) between CSV files.

## Installation

1. Clone the Dac-man repository and enter the plugin root directory under `/plugins/csv`

    ```sh
    git clone https://github.com/dghoshal-lbl/dac-man && cd dac-man/plugins/csv
    ```

1. Install the dacman-csv plugin.

    The recommended method is to use Conda to manage virtual environments and install dependencies.

    Run the following command.
    After the installation is finished, follow the instructions to activate the environment.

    ```sh
    conda env create -f environment.yml
    ```

1. Verify that the installation was successful by invoking the `dacman-csv` CLI utility:

    ```sh
    dacman-csv
    ```

1. To test the functionality with some sample data, run with the following options:

    ```sh
    TEST_DIR="data/test2"; dacman-csv --config "$TEST_DIR"/config.py "$TEST_DIR"/v1.csv "$TEST_DIR"/v2.csv
    ```

    ```

## Running the tests

After ensuring that the Conda environment is activated, from the plugin base directory, run:

```sh
pip install .[tests]
```

The test suite can then be run with:

```sh
pytest tests
```