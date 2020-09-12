# The Dac-Man plug-in framework

## What is a Dac-Man plug-in?

A Dac-Man plug-in is a component of the Dac-Man framework used to analyze changes between two files, typically specific to a particular file format.

When Dac-Man detects that two versions of the same file are not identical,
it selects the appropriate plug-in based on the filetype,
and performs the final part of the change analysis by running the change analysis implemented in the plug-in's `compare()` method,
passing the paths of the two files as arguments.

In terms of the concrete implementation, a Dac-Man plug-in is a subclass of the `Comparator` base class.
The [Plug-in API](../../reference/plugins-api) page of this document's reference section contains the description of the `Comparator` base class and its methods.

## Included plug-ins

A standard Dac-Man installation already includes several plug-ins in the `dacman/plugins` subdirectory of Dac-Man's repository.
These *included plug-ins* support various file formats commonly used for scientific data.

The included plug-ins are described on individual pages in this section,
accessible via the navigation menu on the left.
The documentation for each plug-in follows this general structure:

- **Key concepts**: a conceptual description of the data model, assumptions, and terminology on which the plug-in's functionality is based
- **Usage**: steps needed to enable and run the plug-in, and pointers to example files to test its functionality
- **API** Reference for high-level functionality and configuration options that can be used to quickly adapt an included plug-in to perform a more specific change analysis for files of the supported type

## Plug-in dependencies

A plug-in's functionality might depend on extra packages on top of Dac-Man's own dependencies.
If so, these additional dependencies must be installed before the plug-in can be used.
This also applies to some of the included plug-ins, such as the HDF5, CSV, and Excel plug-ins.
For instructions on how to install dependencies for the included plug-ins,
refer to the [Installing plug-in dependencies](../../install/dependencies) section.
For instructions specific to a single plug-in,
refer to the *Requirements* section on the plug-in's documentation page.

## User-defined plug-ins

In addition to the included plug-ins, users can also create and use their own plug-ins in Dac-Man.
Generally speaking, user-defined plug-ins are used to adapt or extend Dac-Man's change analysis functionality to a particular data format.

The [Plug-in API](../../reference/plugins-api) section describes the Dac-Man plug-in API
that can be used to create user-defined plug-ins in Dac-Man.

We can distinguish two main strategies to create user-defined plug-ins:

- **Extending an included plug-in**: a new plug-in is created by subclassing one of the included plug-ins.
  This can be used when analyzing changes in datasets where files are in one of the supported formats, and have some kind of shared schema or internal structure that can be leveraged to make the change analysis more specific
- **Creating a plug-in from scratch**: a new plug-in is created by subclassing the `Comparator` base class directly. This can be used to enable change analyses between datasets where files are in a format other than those supported by the included plug-ins, including custom file formats

Examples covering both of these strategies are available in the *Extending an included plug-in* and *Creating a plug-in from scratch* sections.
The examples include a step-by-step walkthrough of the plug-in's creation,
as well as pointers to the complete example scripts and datasets.
