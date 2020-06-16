# Contribute to Dac-Man's Documentation

## Requirements

Dac-Man's HTML documentation is built from the contents of the `docs` directory
using the MkDocs documentation generator with the mkdocs-material theme.

Run the following steps to set up a dedicated Conda environment with all dependencies needed to build the documentation.

From the root directory of the Dac-Man source code repository,
create the Conda environment:

```sh
conda env create --file dependencies/conda/docs.yml
```

Then, activate the environment:

```sh
conda activate dacman-docs
```

## Previewing changes locally

From the root directory of the Dac-Man source code repository
(i.e. where the `mkdocs.yml` file is located),
run `mkdocs serve` to start a local web server that will auto-reload
every time a change is made to one of the files in the `docs` directory.

Refer to the built-in help (`mkdocs serve --help`) for additional information
about available options.

## Building the complete HTML documentation

Running the `mkdocs build` command will create the complete HTML documentation
(by default in the `site` subdirectory),
as a standalone (static) website,
ready to be deployed to any webserver using e.g. (S)FTP or rsync
without requiring any additional dependency.
