from gammapy.maps import Map
from astropy.coordinates import SkyCoord
import logging

log = logging.getLogger(__name__)

filename = '$FERMI_DIFFUSE_DIR/gll_iem_v06.fits'

log.info('Reading {}'.format(filename))
diffuse_allsky = Map.read(filename)

position = SkyCoord(0, 0, frame='galactic', unit='deg')
diffuse_gc = diffuse_allsky.cutout(position=position, width=(15, 8))

filename = 'gll_iem_v06_gc.fits.gz'
log.info('Writing {}'.format(filename))
diffuse_gc.write(filename, conv='fgst-template', overwrite=True)
