# Running Custom Change Analyses

Dac-Man offers several ways for users to customize how change analyses are performed.
An overview of these methods is given below.

## Specifying custom analysis scripts via the command line

As we have seen in the [Quickstart](../../quickstart) section, when comparing the contents of two files,
Dac-Man's default behavior is to automatically select one of the available plug-ins to perform the comparison.

Dac-Man also allows users to use their own change analysis scripts instead of the available plug-ins,
by specifying the path to an executable with the `--script` option when invoking Dac-Man via the command-line interface:

```sh
dacman diff <file1> <file2> --script /path/to/myscript
```

For example, to use the Unix `diff` tool to compare all the modified files in the directories `dir1` and `dir2`,
run the following command:

```sh
dacman diff /path/to/dir1 /path/to/dir2 --datachange --script /usr/bin/diff
```

The `--datachange` option tells to compare the data within the files of the two directories.

!!! example
    An example showing how to use custom scripts for data change analysis can be found [here](../../examples/script).

## Configuring plug-in selection for specific file types

The criteria used by Dac-Man to automatically select the plug-in to use for each file content comparison is based on the file type.
When Dac-Man is run for the first time, a plug-ins configuration file is created in the user's home directory,
under `$HOME/.dacman/config/plugins.yaml`.
Users can edit this file to override the default behavior and customize the selection of a plug-in for comparisons of specific file types.

The entries specified in the `plugins.yaml` file can refer to any of the plug-ins available within the Dac-Man plug-in framework.
All of the included plug-ins will be available once their dependencies (if any) have been installed.
For an overview of the included plug-ins, refer to the corresponding entry under the *Plug-ins* section.
For steps on installing dependencies for the build-in plug-ins, see [here](../../install/dependencies).

## Developing a fully customized change analysis using custom plug-ins and the Dac-Man API

In addition to the included plug-in, users can also create and register their own plug-ins in Dac-Man.
The [Plug-in API](../../reference/plugins-api) section describes the Dac-Man plug-in API
that can be used to create user-defined plug-ins in Dac-Man.

Finally, in addition to using the `dacman` command-line utility,
Dac-Man's Python API allows users to use Dac-Man's functionality within their own change analysis pipelines.
The API also provides the necessary module for users to specify a plug-in in their code.

!!! example
    An example showing how to extend Dac-Man's included plug-ins, and use Dac-Man's API to incorporate them into custom analysis scripts can be found [here](../../examples/csv-simple).
