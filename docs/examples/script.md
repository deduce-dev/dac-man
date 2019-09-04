# Using custom scripts for change analysis

This section shows how arbitrary scripts for change analysis
can be integrated within Dac-Man,
by going through a simple example use case and the few steps needed,
using both Python and a shell (Bash) to develop the script.

## Requirements

By indicating an executable file to the `--script` flag of `dacman diff`,
users can use an arbitrary script (e.g. `my_change_analysis`) to perform the change analysis,
overriding Dac-Man's default behavior.

The only requirements for the script are
that it is executable,
and that it accepts exactly two arguments when invoked via the command line,
corresponding to the pair of files being compared.

To make a script executable, the exact procedure depends on the operating system (OS).
For most UNIX-based OSes, including macOS and GNU/Linux,
the executable permissions need to be set (`chmod +x my_change_analysis`),
and the first line of the file should indicate how the file should be run
via the so-called "shebang" (`#!`) notation, e.g. `#!/bin/bash` for a Bash script.

The requirement on the command-line arguments means that the script should support
being invoked e.g. `my_change_analysis file_A file_B`,
where `file_A` and `file_B` are two strings representing the paths to the files being examined for changes.

## Example: detecting changes in counts of a pattern in text files

For this example, we consider the case where we want to detect changes
in how many times a certain pattern *P* is found in each source file.

This change analysis consists of:

- For each source file, count how many times *P* appears in the file's content
- Calculate the difference between the two values
- Display the results

### Using Python

A complete example implementing this change analysis using Python is available at [`examples/scripts/diff_pattern_count.py`](https://github.com/dghoshal-lbl/dac-man/blob/master/examples/scripts/diff_pattern_count.py).

The content of the script can be modified as needed,
for example to change the value of the pattern being searched (`"e"`, in this particular example).

After saving the script as `diff_pattern_count.py`,
we make the script executable by adding the `#!/usr/bin/env python3` line at the top of the file,
and adding the correct permissions with `chmod +x diff_pattern_count.py`.

The script can then be set when running `dacman diff` by indicating its path via the `--script` flag.
For example, if the script was saved e.g. in the `/home/user` directory,
and the data is the example data in the `examples/simple` directory of Dac-Man source code repository:

```sh
dacman diff v0 v1 --datachange --script /home/user/diff_pattern_count.py
```

### Using Bash

Even though Dac-Man itself is written in Python,
custom change analysis scripts can be developed using any language.

An example implementing the same change analysis written in Bash and using the `grep`, `wc` and `bc` UNIX programs is available at [`examples/scripts/diff_pattern_count.sh`](https://github.com/dghoshal-lbl/dac-man/blob/master/examples/scripts/diff_pattern_count.sh).

Once the appropriate "shebang" is set (`#!/bin/bash`), the same steps as the Python script apply:

```sh
dacman diff v0 v1 --datachange --script /home/user/diff_pattern_count.sh
```
