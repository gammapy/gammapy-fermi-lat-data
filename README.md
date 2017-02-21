# Fermi-LAT datasets

This repository contains pre-computed Fermi-LAT datasets, that can be used for
analysis with [gammapy](http://docs.gammapy.org/en/latest/). Currently the
following datasets are included:

| Name  |  Energy Min.  | Energy Max. | Region  |  IRFs  | Exposure  | Zenith Cut |
|-------|---------------|-------------|---------|--------|-----------|------------|
| 2FHL  |    50 GeV     |    2 TeV    | all-sky | Pass 8 | 80 months |   105 deg  |
| 3FHL  |    10 GeV     |    2 TeV    | all-sky | Pass 8 | 84 months |   105 deg  |

A more detailed description and listing of analysis parameters can be found
in the corresponding sub-folders for the [2FHL](2fhl/README.md) and [3FHL](3fhl/README.md)
datset.

## Get the data
To get the data just clone this repository to your local machine using `git`:

```bash
git clone https://github.com/gammapy/gammapy-fermi-lat-data
```
Now define the environment variable `GAMMAPY_FERMI_LAT_DATA` to point to the path
where the repository is located on your machine:

```bash
export GAMMAPY_FERMI_LAT_DATA=path/to/gammapy-fermi-lat-data
```

In addition you have to download the latest galactic diffuse model directly by
clicking [here](https://fermi.gsfc.nasa.gov/ssc/data/analysis/software/aux/gll_iem_v06.fits)
or using the command line:

```bash
wget https://fermi.gsfc.nasa.gov/ssc/data/analysis/software/aux/gll_iem_v06.fits path/to/fermi/diffuse/dir
```

**Note:** if you have an installation of the Fermi science tools, you already have
the galactic diffuse model. It is contained in the sub folder
`path/to/fermi/science/tools/refdata/fermi/galdiffuse/gll_iem_v06.fits`

Define the environment variable `FERMI_DIFFUSE_DIR` to point to the directory
where the `gll_iem_v06.fits` file is contained:

```bash
export FERMI_DIFFUSE_DIR=path/to/fermi/diffuse/dir
```

## Work with the data
Once you've copied the data and defined the environment variables to point to the
corresponding directories, the data is ready to be used. Please check the examples
provided in the docstring  of the [FermiLATDataset](http://docs.gammapy.org/en/latest/api/gammapy.datasets.FermiLATDataset.html#gammapy.datasets.FermiLATDataset)
class from Gammapy or check out the tutorial [Fermi-LAT data with Gammapy](https://github.com/gammapy/gammapy-extra/blob/master/notebooks/data_fermi_lat.ipynb).

## Data preparation for contributors
Every dataset includes a data preparation bash script, which runs the [Fermi-LAT
science tools](https://fermi.gsfc.nasa.gov/ssc/data/analysis/) to compute
events, exposure, livetime and psf for given set of analysis parameters. Running
the scripts to prepare the datasets in this repositiory requires the Fermi-LAT
science tools to be installed. In addition the following environment variables have
to be set:

    * `FERMI_FT1_FILE`: Path to the event files list.
    * `FERMI_FT2_FILE`: Path to the merged spacecraft file.

Normal users don't have to run the script but can just start their analyses from
the datasets provided in this repository.