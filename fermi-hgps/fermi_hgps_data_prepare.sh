# This is as script to prepare Fermi all sky data

# Basic analysis Parameters
EMIN=10000
EMAX=3000000
ZMAX=90
EVENT_CLASS=128
EVENT_TYPE=3
TMIN=239557417
TMAX=498694560
IRF=P8R2_SOURCE_V6 # Corresponding to event type 128
NEBINS=17

# WCS specification for the HGPS region for exposure cube
NXPIX=1504
NYPIX=80
BINSZ=0.125
XREF=341
YREF=0
PROJ=CAR
COORDSYS=GAL

# Raw data files
EVENTS_LIST=$FERMI_FT1_FILE # Fermi FT1 file environment variable
SPACECRAFT=$FERMI_FT2_FILE # Fermi FT2 file environment variable

# Data files
EVENTS=fermi_10_3000_GeV_events.fits
EVENTS_SELECTED=fermi_10_3000_GeV_events_selected.fits
EXPOSURE=fermi_10_3000_GeV_exposure_cube.fits
LIVETIME=fermi_10_3000_GeV_livetime_cube.fits
COUNTS=fermi_10_3000_GeV_counts_cube.fits
PSF=fermi_10_3000_GeV_psf_gc.fits

# # Merge weekly photon files and apply energy cut
# gtselect infile=$EVENTS_LIST outfile=$EVENTS_SELECTED ra=0 dec=0 rad=180 \
#          tmin=$TMIN tmax=$TMAX emin=$EMIN emax=$EMAX zmax=$ZMAX \
#          evclass=$EVENT_CLASS evtype=$EVENT_TYPE

# # Update GTI list
# gtmktime scfile=$SPACECRAFT filter="(DATA_QUAL>0)&&(LAT_CONFIG==1)" \
#          roicut=no evfile=$EVENTS_SELECTED outfile=$EVENTS

# Compute livetime cube
#gtltcube zmax=$ZMAX evfile=$EVENTS_SELECTED_GTI scfile=$SPACECRAFT
#         outfile=$LIVETIME dcostheta=0.025 binsz=1

# # Counts cube
# gtbin evfile=$EVENTS outfile=$COUNTS algorithm=HEALPIX SCFILE=$SPACECRAFT \
#       coordsys=GAL hpx_ordering_scheme=RING hpx_order=5 hpx_ebin=true ebinalg=LOG \
#       emin=$EMIN emax=$EMAX enumbins=$NEBINS
# gzip $COUNTS

# Compute exposure cube
gtexpcube2 infile=$LIVETIME cmap=none outfile=$EXPOSURE irfs=$IRF evtype=$EVENT_TYPE \
           nxpix=$NXPIX nypix=$NYPIX binsz=$BINSZ xref=$XREF yref=$YREF axisrot=0 proj=$PROJ \
           coordsys=$COORDSYS emin=$EMIN emax=$EMAX enumbins=$NEBINS

# Compute PSF
gtpsf expcube=$LIVETIME outfile=$PSF irfs=$IRF \
      ra=266.42 dec=-29.01 emin=$EMIN emax=$EMAX \
      nenergies=$NEBINS thetamax=10 ntheta=300
