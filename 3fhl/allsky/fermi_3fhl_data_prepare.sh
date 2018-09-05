# This is as script to prepare Fermi 3FHL all sky data

# Basic analysis Parameters
EMIN=10000
EMAX=2000000
ZMAX=105
EVENT_CLASS=128
EVENT_TYPE=3
IRF=P8R2_SOURCE_V6 # Corresponding to event type 128
EBINALG=LOG
NEBINS=17

# Time cuts taken from 3FHL paper
TMIN=239557417.
TMAX=460250000.

# Raw data files
EVENTS_LIST=$FERMI_FT1_FILE # Fermi FT1 file environment variable
SPACECRAFT=$FERMI_FT2_FILE # Fermi FT2 file environment variable

# Data files
EVENTS=fermi_3fhl_events.fits
EVENTS_SELECTED=fermi_3fhl_events_selected.fits
LIVETIME=fermi_3fhl_livetime.fits
EXPOSURE=fermi_3fhl_exposure_cube_hpx.fits
COUNTS=fermi_3fhl_counts_cube_hpx.fits
PSF=fermi_3fhl_psf_gc.fits

## Merge weekly photon files and apply energy cut
#gtselect infile=$EVENTS_LIST outfile=$EVENTS_SELECTED ra=0 dec=0 rad=180 \
#         tmin=$TMIN tmax=$TMAX emin=$EMIN emax=$EMAX zmax=$ZMAX \
#         evclass=$EVENT_CLASS evtype=$EVENT_TYPE

## Update GTI list
#gtmktime scfile=$SPACECRAFT filter="(DATA_QUAL>0)&&(LAT_CONFIG==1)" \
#         roicut=no evfile=$EVENTS_SELECTED outfile=$EVENTS

# Compute livetime cube
# gtltcube zmax=$ZMAX evfile=$EVENTS scfile=$SPACECRAFT \
#          outfile=$LIVETIME dcostheta=0.025 binsz=1

# Counts cube
gtbin evfile=$EVENTS outfile=$COUNTS algorithm=HEALPIX SCFILE=$SPACECRAFT \
      coordsys=CEL hpx_ordering_scheme=RING hpx_order=6 hpx_ebin=true ebinalg=LOG \
      emin=$EMIN emax=$EMAX enumbins=$NEBINS

# Compute exposure cube
gtexpcube2 infile=$LIVETIME outfile=$EXPOSURE irf=$IRF cmap=$COUNTS \
        ebinalg=$EBINALG emin=$EMIN emax=$EMAX enumbins=$NEBINS bincalc=EDGE

# Compute psf cube
# gtpsf expcube=$LIVETIME outfile=$PSF irfs=$IRF ra=266.42 dec=-29.01 \
# emin=$EMIN emax=$EMAX nenergies=$NEBINS thetamax=10 ntheta=300

# Zip files
# gzip $EVENTS_SELECTED_GTI
# gzip $COUNTS
# gzip $EXPOSURE
# gzip $LIVETIME
# gzip $PSF

