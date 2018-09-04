"""This script computes an allsky background correction map based
on the parameters fiven in the 3FHL catalog.
"""
import numpy as np
import healpy as hp

from astropy.coordinates import Angle, SkyCoord
from astropy.modeling.models import Disk2D

from gammapy.catalog import SourceCatalog3FHL

# Healpix parameters
NSIDE = 32
NPIX = hp.nside2npix(NSIDE)
NEST = False
SMOOTH = True

# setup data an coordinates
data = np.zeros(NPIX)
norm = np.zeros(NPIX)
ipix = np.arange(NPIX)

# convert coordinates
theta, phi = hp.pix2ang(NSIDE, ipix, nest=NEST)
lon, lat = Angle(phi, unit='rad'), Angle(np.pi / 2 - theta, unit='rad')
positions = SkyCoord(lon, lat, frame='galactic')

fermi_3fhl = SourceCatalog3FHL()

for roi in fermi_3fhl.rois:
    glon = Angle(roi['GLON'], unit='deg')
    glat = Angle(roi['GLAT'], unit='deg')
    center = SkyCoord(glon, glat, frame='galactic')

    separation = positions.separation(center)
    mask = separation.deg < roi['RADIUS']

    data[mask] += roi['PARNAM2'] * roi['PARNAM1']
    norm[mask] += 1.

# renormalize data and set to nan to mean
data /= norm
data[~np.isfinite(data)] = np.nanmean(data)

if SMOOTH:
  data = hp.smoothing(map_in=data, sigma= Angle('5deg').rad)

hp.write_map('background_norm_hpx.fits', m=data, nest=NEST, coord='G')
