# Installing additional dependencies

Dac-Man has a modular structure, and by default will only install packages that are necessary to its core functionality.

It's possible to install additional dependencies by updating Dac-Man's Conda environment
using environment files in the `environment` directory of the source code repository.

## Installing dependencies for all built-in plug-ins

To update Dac-Man's environment to enable all built-in plug-ins,
from the root of the local copy of the Dac-Man source code repository,
run:

```sh
conda env update --name dacman-env --file environment/builtin-plugins.yml
```
