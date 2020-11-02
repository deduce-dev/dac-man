# Troubleshooting

This section contains information about some of the issues that may arise while using Dac-Man.

!!! important
    If your issue is not addressed by this material, we encourage you to let us know, either by opening an issue on Dac-Man's [issue tracker](https://github.com/deduce-dev/dac-man/issues), or by contacting us at dac-man at lbl dot gov.

## `dacman: command not found error when invoking dacman`

Check that Dac-Man's environment is active before running the `dacman` command.

If Dac-Man was e.g. installed in a Conda environment:

```sh
conda activate dacman-env
```

## Plug-ins are not selected when analyzing changes in supported file types

When analyzing changes in files of type e.g. `csv`, the corresponding plug-in (e.g. the CSV plug-in) should be used by default by Dac-Man.

If this is not the case, make sure that all optional dependencies for that plug-in (e.g. for the CSV plug-in, the `pandas` library) are installed, as described [here](../install/dependencies/).

## Errors when installing dependencies for included plug-ins individually in a Conda environment

Try to install dependencies in a single step, as described in [this section](../install/dependencies/#using-conda).

## General errors during Dac-Man execution

If the `dacman` command is available in the current environment,
but the program crashes during execution for unspecified reasons,
it is possible that re-installing Dac-Man from scratch might solve the issues.

First, clean up the current installation by removing the existing Dac-Man environment:

```sh
conda env remove --name dacman-env
```

Then, install Dac-Man from scratch following the [installation steps](../install/).
