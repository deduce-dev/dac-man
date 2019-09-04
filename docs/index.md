# Dac-Man: A Framework to Track, Compare and Analyze Large Scientific Data Changes

Scientific datasets are updated frequently due to changes in instrument configuration, software updates, quality assessments or data cleaning algorithms.
However, due to the large size and complex data structures of these datasets,
existing tools either do not scale or are unable to generate meaningful change information.

The **Dac-Man** (**Da**ta **C**hange **Man**agement) framework allows users to
efficiently and effectively identify, track and manage data change and associated provenance in scientific datasets.
There are two main components of Dac-Man:

- Change tracker that keeps track of the changes between different
  versions of a dataset
- Query manager that manages data change related queries

## Features

The key features of Dac-Man include:

- **HPC support**. Dac-Man provides MPI support for enabling parallel change capture in HPC environments
- **Offline comparison**. Datasets can be compared away from the actual location of the data,
  allowing users to find changes without necessarily moving the datasets to a common location
- **Extendable**. Users can plug-in their own scripts to calculate changes
- **Flexible command-line options**. Dac-Man provides different options to configure change detection
- **Detailed output**. Dac-Man outputs contain details on the different types and amount of change
- **Customizable logging**. Users can customize where and what to log,
  including the detailed steps in the change capture process

## Getting Started

Dac-Man is developed using Python 3, and distributed under the "new" or "revised" BSD [license](./license/#license).
For detailed instructions on the installation, refer to the [Installation](./install) section.
To quickly get up-and-running with Dac-Man, head over to the [Quickstart](./quickstart) section.
