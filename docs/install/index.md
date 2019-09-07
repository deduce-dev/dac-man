# Installing Dac-Man

Dac-Man is distributed as a Python package, and is compatible with modern Python installation tools and methods.

The installation method described [here](./#installing-dac-man-using-conda) is suitable for most use cases.
Choose this if you're unsure, or don't have particular reasons for choosing a different method.

Refer to the rest of this guide for other available methods.

## Requirements

Dac-Man is written in Python 3, and is compatible with version 3.6 or greater.

It is known to work with the following operating systems:

- GNU/Linux
- macOS
- Unix-like OSs

## Installing Dac-Man using Conda

The recommended way to install and run Dac-Man is through a Conda environment.
This will allow you to install Dac-Man inside an independent Python installation,
avoiding problems such as lack of administrator rights, old Python version, conflicting packages, etc.

### Installing the `conda` package manager

The `conda` package manager is used to create and manage Conda environments.

`conda` is available for all major operating systems (GNU/Linux, macOS, Windows).
Refer to the [Conda install guide](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)
for detailed information on how to install `conda` for your system.

### Installing Dac-Man in a new Conda environment

After installing `conda`, clone the Dac-Man source code repository using Git:

```sh
git clone https://github.com/dghoshal-lbl/dac-man
```

Then, navigate to the root of the cloned repository
and run this command to automatically create a Conda environment
and install Dac-Man, together with its core dependencies, at the same time:

```sh
cd dac-man
conda env create --file ./environment.yml
```

!!! tip
    This will install only the dependencies needed for Dac-Man's core functionality. [These additional instructions](../../install/dependencies) describe how to install dependencies for all of Dac-Man's built-in plug-ins in a single step.

## Installing Dac-Man in an existing environment

Instead of creating a Conda environment for Dac-Man from scratch, it's possible to install Dac-Man in an existing environment.

### Installing in an existing Python virtual environment (virtualenv)

These steps illustrate how to install Dac-Man in an existing Python virtual environment (virtualenv) named e.g. `my-existing-venv`.

First, activate the virtualenv:

```sh
source /path/to/my-existing-env/bin/activate
```

Then, from the root of Dac-Man's repository,
run the following command to install Dac-Man as well as its core dependencies.

```sh
pip install .
```

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
    Also in this case, only Dac-man's core dependencies will be installed after these steps. Instructions on how to install dependencies for enabling Dac-Man's built-in plug-ins can be found on [this page](../../install/dependencies), depending on whether Pip ([here](../../install/dependencies/#using-pip)) or Conda ([here](../../install/dependencies/#using-conda)) was used to install Dac-Man.


## Installing Dac-Man in Binder

Thanks to [Binder](https://mybinder.readthedocs.io), it's possible to install Dac-Man in a temporary cloud environment,
without having to install it locally.

Clicking on this button will create a Dac-Man environment on Binder and open a web terminal: [![badge](https://img.shields.io/badge/launch-binder-579ACA.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFkAAABZCAMAAABi1XidAAAB8lBMVEX///9XmsrmZYH1olJXmsr1olJXmsrmZYH1olJXmsr1olJXmsrmZYH1olL1olJXmsr1olJXmsrmZYH1olL1olJXmsrmZYH1olJXmsr1olL1olJXmsrmZYH1olL1olJXmsrmZYH1olL1olL0nFf1olJXmsrmZYH1olJXmsq8dZb1olJXmsrmZYH1olJXmspXmspXmsr1olL1olJXmsrmZYH1olJXmsr1olL1olJXmsrmZYH1olL1olLeaIVXmsrmZYH1olL1olL1olJXmsrmZYH1olLna31Xmsr1olJXmsr1olJXmsrmZYH1olLqoVr1olJXmsr1olJXmsrmZYH1olL1olKkfaPobXvviGabgadXmsqThKuofKHmZ4Dobnr1olJXmsr1olJXmspXmsr1olJXmsrfZ4TuhWn1olL1olJXmsqBi7X1olJXmspZmslbmMhbmsdemsVfl8ZgmsNim8Jpk8F0m7R4m7F5nLB6jbh7jbiDirOEibOGnKaMhq+PnaCVg6qWg6qegKaff6WhnpKofKGtnomxeZy3noG6dZi+n3vCcpPDcpPGn3bLb4/Mb47UbIrVa4rYoGjdaIbeaIXhoWHmZYHobXvpcHjqdHXreHLroVrsfG/uhGnuh2bwj2Hxk17yl1vzmljzm1j0nlX1olL3AJXWAAAAbXRSTlMAEBAQHx8gICAuLjAwMDw9PUBAQEpQUFBXV1hgYGBkcHBwcXl8gICAgoiIkJCQlJicnJ2goKCmqK+wsLC4usDAwMjP0NDQ1NbW3Nzg4ODi5+3v8PDw8/T09PX29vb39/f5+fr7+/z8/Pz9/v7+zczCxgAABC5JREFUeAHN1ul3k0UUBvCb1CTVpmpaitAGSLSpSuKCLWpbTKNJFGlcSMAFF63iUmRccNG6gLbuxkXU66JAUef/9LSpmXnyLr3T5AO/rzl5zj137p136BISy44fKJXuGN/d19PUfYeO67Znqtf2KH33Id1psXoFdW30sPZ1sMvs2D060AHqws4FHeJojLZqnw53cmfvg+XR8mC0OEjuxrXEkX5ydeVJLVIlV0e10PXk5k7dYeHu7Cj1j+49uKg7uLU61tGLw1lq27ugQYlclHC4bgv7VQ+TAyj5Zc/UjsPvs1sd5cWryWObtvWT2EPa4rtnWW3JkpjggEpbOsPr7F7EyNewtpBIslA7p43HCsnwooXTEc3UmPmCNn5lrqTJxy6nRmcavGZVt/3Da2pD5NHvsOHJCrdc1G2r3DITpU7yic7w/7Rxnjc0kt5GC4djiv2Sz3Fb2iEZg41/ddsFDoyuYrIkmFehz0HR2thPgQqMyQYb2OtB0WxsZ3BeG3+wpRb1vzl2UYBog8FfGhttFKjtAclnZYrRo9ryG9uG/FZQU4AEg8ZE9LjGMzTmqKXPLnlWVnIlQQTvxJf8ip7VgjZjyVPrjw1te5otM7RmP7xm+sK2Gv9I8Gi++BRbEkR9EBw8zRUcKxwp73xkaLiqQb+kGduJTNHG72zcW9LoJgqQxpP3/Tj//c3yB0tqzaml05/+orHLksVO+95kX7/7qgJvnjlrfr2Ggsyx0eoy9uPzN5SPd86aXggOsEKW2Prz7du3VID3/tzs/sSRs2w7ovVHKtjrX2pd7ZMlTxAYfBAL9jiDwfLkq55Tm7ifhMlTGPyCAs7RFRhn47JnlcB9RM5T97ASuZXIcVNuUDIndpDbdsfrqsOppeXl5Y+XVKdjFCTh+zGaVuj0d9zy05PPK3QzBamxdwtTCrzyg/2Rvf2EstUjordGwa/kx9mSJLr8mLLtCW8HHGJc2R5hS219IiF6PnTusOqcMl57gm0Z8kanKMAQg0qSyuZfn7zItsbGyO9QlnxY0eCuD1XL2ys/MsrQhltE7Ug0uFOzufJFE2PxBo/YAx8XPPdDwWN0MrDRYIZF0mSMKCNHgaIVFoBbNoLJ7tEQDKxGF0kcLQimojCZopv0OkNOyWCCg9XMVAi7ARJzQdM2QUh0gmBozjc3Skg6dSBRqDGYSUOu66Zg+I2fNZs/M3/f/Grl/XnyF1Gw3VKCez0PN5IUfFLqvgUN4C0qNqYs5YhPL+aVZYDE4IpUk57oSFnJm4FyCqqOE0jhY2SMyLFoo56zyo6becOS5UVDdj7Vih0zp+tcMhwRpBeLyqtIjlJKAIZSbI8SGSF3k0pA3mR5tHuwPFoa7N7reoq2bqCsAk1HqCu5uvI1n6JuRXI+S1Mco54YmYTwcn6Aeic+kssXi8XpXC4V3t7/ADuTNKaQJdScAAAAAElFTkSuQmCC)](https://mybinder.org/v2/gh/dghoshal-lbl/dac-man/master?urlpath=/terminals/1)

!!! note
    It might take a few minutes for Binder to setup the environment.

!!! warning
    After a period of inactivity, Binder environment (along with all data that was added by users during the session) are automatically and irreversibly deactivated and destroyed .

### Binder Limitations

Although a valuable tool for distributing test environments, Binder's mode of operation might make it unsuitable for certain workflows and/or datasets.
Make sure to read the [documentation](https://mybinder.readthedocs.io/en/latest/) carefully, in particular the [usage guidelines](https://mybinder.readthedocs.io/en/latest/user-guidelines.html) and the [user privacy policy](https://mybinder.readthedocs.io/en/latest/faq.html#how-does-mybinder-org-ensure-user-privacy).

Outside of a quick evaluation, the recommended way of using Dac-Man is to install it in the users' computing environment, and run it on a [personal computer](../use/desktop) or on an [HPC cluster](../use/hpc).
