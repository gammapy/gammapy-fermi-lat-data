import logging
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.table import Table
from astropy.io import fits
from gammapy.maps import Map
from gammapy.spectrum.models import PowerLaw
from gammapy.irf import EnergyDependentTablePSF
from gammapy.cube import PSFKernel
from gammapy.data import EventList


log = logging.getLogger(__name__)


def make_gll_cutout():
    filename = '$FERMI_DIFFUSE_DIR/gll_iem_v06.fits'

    log.info('Reading {}'.format(filename))
    diffuse_allsky = Map.read(filename)

    position = SkyCoord(0, 0, frame='galactic', unit='deg')
    diffuse_gc = diffuse_allsky.cutout(position=position, width=(25, 15))

    filename = 'gll_iem_v06_gc.fits.gz'
    log.info('Writing {}'.format(filename))
    diffuse_gc.write(filename, conv='fgst-template', overwrite=True)


def make_images():
    counts_cube = Map.read("fermi-3fhl-gc-counts-cube.fits.gz")
    counts = counts_cube.sum_over_axes()
    counts.write("fermi-3fhl-gc-counts.fits.gz", overwrite=True)

    background_cube = Map.read("fermi-3fhl-gc-background-cube.fits.gz")
    background = background_cube.sum_over_axes()
    background.write("fermi-3fhl-gc-background.fits.gz", overwrite=True)

    exposure_cube = Map.read("fermi-3fhl-gc-exposure-cube.fits.gz")

    # define a weighting spectrum
    spectrum = PowerLaw(index=2)

    # compute and normalize the weigths
    energy_axis = exposure_cube.geom.get_axis_by_name("energy")
    weights = spectrum(energy_axis.center * u.MeV)
    weights /= weights.sum()

    # compute weighted exposure map
    exposure_cube.data *= weights[:, np.newaxis, np.newaxis].value
    exposure = exposure_cube.sum_over_axes()
    exposure.write("fermi-3fhl-gc-exposure.fits.gz", overwrite=True)

    # load psf
    table_psf = EnergyDependentTablePSF.read("fermi-3fhl-gc-psf-cube.fits.gz")

    # compute mean PSF in given energy band
    table_psf_mean = table_psf.table_psf_in_energy_band([10, 500] * u.GeV, spectrum=spectrum)

    # compute PSF kernel
    kernel = PSFKernel.from_table_psf(table_psf=table_psf_mean, geom=exposure.geom, max_radius=0.5 * u.deg)
    kernel.write("fermi-3fhl-gc-psf.fits.gz", overwrite=True)


def make_events():
    counts = Map.read("fermi-3fhl-gc-counts.fits.gz")
    events = EventList.read("../allsky/fermi_3fhl_events_selected.fits.gz")
    selection = counts.geom.contains(events.radec)
    table = events.table[selection]

    table_gti = Table.read("../allsky/fermi_3fhl_events_selected.fits.gz", hdu="GTI")

    hdu_list = fits.HDUList()
    hdu_list.append(fits.BinTableHDU(table))
    hdu_list.append(fits.BinTableHDU(table_gti))
    hdu_list.writeto("fermi-3fhl-gc-events.fits.gz", overwrite=True)


if __name__ == "__main__":
    make_gll_cutout()
    # make_images()
    # make_events()
