# Testing Dac-Man installation

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
