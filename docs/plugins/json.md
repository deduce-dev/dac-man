# The Dac-Man JSON plug-in

The Dac-Man JSON plug-in allows users to detect, analyze, and display semantic
changes in JSON (JavaScript Object Notation) files.

## Key concepts

The following differences are compared through this plug-in:

- If both keys are present at the same levels in the JSON, values between
   these keys are compared for differences.
- If keys are present/absent in one but not the other, the differences
   are listed.

It is important to note that the computation here only applies to the semantic
side of JSON, and any structural comparison is not accounted for. The ordering
of keys and values in a file are not taken into account by the plug-in. For
example, if both files contain the key `key1`, but have them at different
lines of the file, this plug-in will not treat that as a difference.

## Usage

### Requirements

No additional dependencies.

### Using the JSON Plug-in

As this is an included Dac-Man plug-in, the JSON plug-in will be used by default
when comparing JSON files.

The [`examples/json/`](https://github.com/deduce-dev/dac-man/blob/master/examples/json/) directory of the Dac-Man source code repository contains two example JSON files.
To compare these example files, navigate to the `examples/json/` directory
and run `dacman diff` with the paths to the example files of `a.json` and `b.json`
followed by the `--datachange` option:

```sh
cd examples/json
dacman diff a.json b.json --datachange
```

### Output

The following is the output from the comparison.

```
$ dacman diff a.json b.json --datachange
[INFO] Runtime system = default
[INFO] Starting diff calculation
[INFO] Sequentially comparing dataset pairs.
[INFO] Plugin <class 'dacman.plugins.csv.CSVPlugin'> supports: ['csv']
[INFO] Plugin <class 'dacman.plugins.hdf5.HDF5Plugin'> supports: ['h5']
[INFO] Plugin <class 'dacman.plugins.json.JSONPlugin'> supports: ['json']
[INFO] Plugin <class 'dacman.plugins.default.DefaultPlugin'> supports: ['default']
Data comparator plugin = JSONPlugin
[INFO] Comparing /dac-man/examples/json/a.json and /dac-man/examples/json/b.json using JSONPlugin

Contents in a.json denoted with "+"
Contents in b.json denoted with "-"


-  pets: {
-  }
+  name: John Doe
-  name: Jane Doe
  cars: {
-    car2: {
-      brand: Tesla
-      color: white
-    }
    car1: {
+      brand: Ford
-      brand:
+      color: white
-      color: black
    }
  }
+  age: 30
-  age: 33
[INFO] --- No custom detail level specified, using default detail level.

Level 0 detail:
        a.json has -66.67% less keys than b.json

[INFO] Data comparison complete.
[INFO] Diff completed
```

### Interpreting the comparison output

The first couple of printouts are for informational purposes and the actual
comparison output is printed after the line `[INFO] Comparing ... using JSONPlugin`.

The lines denoted with `+` are the contents present in the file `a.json`,
but not in `b.json`. Likewise, `-` denotes the contents present in `b.json` that are
different from that in `a.json`

At the end of the output, the reader will note the following message:
`[INFO] --- No custom detail level specified, using default detail level.`
It is possible to have the plug-in output the differences in more detail.
The default output level used here is level 0. The section titled
"Extending included plug-ins" will cover aspects of how to have the plug-in
output in more detail.
