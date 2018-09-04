# This is as script to prepare Fermi 3FHL gc all sky data

# Basic analysis Parameters
EMIN=10000
EMAX=30000
ZMAX=105
EVENT_CLASS=128
EVENT_TYPE=3
IRF=P8R2_SOURCE_V6 # Corresponding to event type 128
EBINALG=LOG
NEBINS=1

# Time cuts taken from 3FHL paper
TMIN=239557417.
TMAX=460250000.

# Raw data files
EVENTS_LIST=$FERMI_FT1_FILE # Fermi FT1 file environment variable
SPACECRAFT=$FERMI_FT2_FILE # Fermi FT2 file environment variable

# Data files
EVENTS=../allsky/fermi_3fhl_events.fits
LIVETIME=../allsky/fermi_3fhl_livetime.fits
EVENTS_SELECTED=fermi-3fhl-gc-events-selected.fits
EXPOSURE=fermi-3fhl-gc-exposure.fits
COUNTS=fermi-3fhl-gc-counts.fits
PSF=fermi-3fhl-psf-gc.fits
BACKGROUND=fermi-3fhl-gc-background-npred.fits
MODEL=background-model.xml

# # Counts cube
# gtbin evfile=$EVENTS outfile=$COUNTS algorithm=CCUBE SCFILE=$SPACECRAFT \
#       coordsys=GAL binsz=0.05 nxpix=200 nypix=100 xref=0 yref=0 proj=CAR ebinalg=LOG \
#       emin=$EMIN emax=$EMAX enumbins=$NEBINS axisrot=0

# Compute exposure cube
gtexpcube2 infile=$LIVETIME outfile=$EXPOSURE irf=$IRF coordsys=GAL binsz=0.05 \
      nxpix=200 nypix=100 xref=0 yref=0 proj=CAR ebinalg=$EBINALG cmap=none \
      emin=$EMIN emax=$EMAX enumbins=$NEBINS axisrot=0 bincalc=EDGE

# # Compute psf cube
# gtpsf expcube=$LIVETIME outfile=$PSF irfs=$IRF ra=266.42 dec=-29.01 \
# emin=$EMIN emax=$EMAX nenergies=$NEBINS thetamax=10 ntheta=300

# gtmodel srcmaps=$COUNTS bexpmap=$EXPOSURE expcube=$LIVETIME srcmdl=$MODEL \
#        irfs=$IRF outfile=$BACKGROUND evtype=$EVENT_TYPE outtype=ccube

