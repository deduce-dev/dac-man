# Installing Dac-Man from source

!!! tip
    Dac-Man's modular architecture and versatile [plug-in framework](../../use/plugins) should cover most use cases that require custom extensions to Dac-Man core functionality.

To install Dac-Man from source, create and/or activate the desired environment as described [here](../conda).

Then, clone the repository using Git and enter the local `dac-man` directory:

```sh
git clone https://github.com/dghoshal-lbl/dac-man && cd dac-man
```

Dac-Man can then be installed using Pip:

```sh
pip install .
```

!!! tip
    The `-e/--editable` flag can be passed to `pip install` to install Dac-Man in [editable mode](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs), so that modifications made to the code in the source directory will be immediately available to the environment without having to re-install Dac-Man after every update.
