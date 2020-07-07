# Dac-Man: A Framework to Track, Compare and Analyze Large Scientific Data Changes

The **Dac-Man** (**Da**ta **C**hange **Man**agement) framework allows users to
efficiently and effectively identify, track and manage data change and associated provenance in scientific datasets.

## Features

Dac-Man's key features include:

- **HPC support**. Dac-Man provides MPI support for enabling parallel change capture in HPC environments
  allowing users to find changes without necessarily moving the datasets to a common location
- **Extendable**. Users can plug-in their own scripts to calculate changes
- **Support for remote comparison**. Changes in datasets can be identified and compared across systems without moving data to a single location
- **Flexible command-line options**. Dac-Man provides different options to configure change detection
- **Detailed output**. Dac-Man outputs contain details on the different types and amount of change
- **Customizable logging**. Users can customize where and what to log,
  including detailed steps in the change capture process

## Getting Started

Dac-Man is developed using Python 3, and distributed under the "new" or "revised" BSD [license](./license/#license).
To get up and running with Dac-Man, install the tool following the [installation instructions](./install/#installing-dac-man-using-conda),
then use the [Quickstart](./quickstart) to try out features.
