import numpy as np
from astropy import units as u
from gammapy.data import EventList
from gammapy.irf import EnergyDependentTablePSF, EnergyDispersion
from gammapy.maps import Map, MapAxis, WcsNDMap, WcsGeom
from gammapy.modeling import Fit, Datasets
from gammapy.modeling.models import (
    LogParabolaSpectralModel,
    SkyDiffuseCube,
    SkyModels,
    BackgroundModel,
    create_fermi_isotropic_diffuse_model,
)
from gammapy.cube import MapDataset, PSFKernel, MapEvaluator
from gammapy.catalog import SourceCatalog4FGL, SourceCatalog3FHL
from pathlib import Path


# ## How to prepare the dataset
# These steps are covered by others tutorials so we are going to go trought without much details.
# To go further see :
# - https://docs.gammapy.org/0.14/notebooks/fermi_lat.html

# ### Create the Fermi-LAT dataset for a 3D analysis
# 
# First we look for our source of interrest in the latest Fermi-LAT general catalog, 4FGL, and get its `SkyModel`. By default the spectrum returned from the catalog is a power-law. For our joint analysis we update the spectral model to a log-parabola, and we freeze the spatial model (source position).

# In[ ]:


FGL4 = SourceCatalog4FGL()
crab = FGL4["Crab Nebula"]  #
crab_mod = crab.sky_model()
crab_mod.name = "Crab Nebula"
crab_pos = crab.position.galactic
# freeze position
crab_mod.spatial_model.parameters.freeze_all()
# change spectrum to LogParabola (default is PowerLaw for the Crab)
crab_mod.spectral_model = LogParabolaSpectralModel(
    amplitude=crab.data["LP_Flux_Density"],
    alpha=crab.data["LP_Index"],
    beta=crab.data["LP_beta"],
    reference=crab.data["Pivot_Energy"],
)
print(crab_mod)


# We use the events associated to 3FHL catalog in order to a produce counts cube. We select a 5-by-4 degree region centered on the Crab in Galactic coordinates, and photon energies between 10 GeV and 2 TeV. 

# In[ ]:


# Counts
events = EventList.read("$GAMMAPY_DATA/fermi_3fhl/fermi_3fhl_events_selected.fits.gz")

e_min, e_max = 0.01, 2.0
El_fermi = np.logspace(np.log10(e_min), np.log10(e_max), 6) * u.TeV
energy_axis = MapAxis.from_edges(El_fermi, name="energy", unit="TeV", interp="log")
counts = Map.create(
    skydir=crab_pos,
    npix=(50, 40),
    proj="CAR",
    coordsys="GAL",
    binsz=0.1,
    axes=[energy_axis],
    dtype=float,
)
counts.fill_by_coord({"skycoord": events.radec, "energy": events.energy})
counts.sum_over_axes().smooth(2).plot(stretch="log", vmax=50, cmap="nipy_spectral")


# 
# Then we prepare the associated exposure, PSF, and energy dispersion. 

# In[ ]:


# Exposure
exposure_hpx = Map.read("$GAMMAPY_DATA/fermi_3fhl/fermi_3fhl_exposure_cube_hpx.fits.gz")
# Unit is not stored in the file, set it manually
exposure_hpx.unit = "cm2 s"

# For exposure, we choose a geometry with node_type='center',
# whereas for counts it was node_type='edge'
axis = MapAxis.from_nodes(
    counts.geom.axes[0].center, name="energy", unit="GeV", interp="log"
)
wcs = counts.geom.wcs
geom = WcsGeom(wcs=wcs, npix=counts.geom.npix, axes=[axis])
coord = counts.geom.get_coord()
data = exposure_hpx.interp_by_coord(coord)
exposure = WcsNDMap(geom, data, unit=exposure_hpx.unit, dtype=float)

# read PSF
psf = EnergyDependentTablePSF.read("$GAMMAPY_DATA/fermi_3fhl/fermi_3fhl_psf_gc.fits.gz")
# Let's compute a PSF kernel matching the pixel size of our map
psf_kernel = PSFKernel.from_table_psf(psf, counts.geom, max_radius="1 deg")

# Energy Dispersion
# For simplicity we assume a diagonal energy dispersion:
e_true = exposure.geom.axes[0].edges
e_reco = counts.geom.axes[0].edges
edisp = EnergyDispersion.from_diagonal_response(e_true=e_true, e_reco=e_reco)


# Given the PSF of Fermi-LAT, sources outside the analysis region can be reconstructed inside. So we have to define a mask that exclude pixels close to our region boundary. The size of this margin is set as the PSF 99% containment radius.

# In[ ]:


# fit mask
psf_r99max = psf.containment_radius(10 * u.GeV, fraction=0.99)
coords = counts.geom.get_coord()
mask = (
    (coords["lon"] >= coords["lon"].min() + psf_r99max)
    & (coords["lon"] <= coords["lon"].max() - psf_r99max)
    & (coords["lat"] >= coords["lat"].min() + psf_r99max)
    & (coords["lat"] <= coords["lat"].max() - psf_r99max)
)
mask_fermi = WcsNDMap(counts.geom, mask)


# We read the interstellar emission model and the isotropic spectrum associated with the 3FHL catalog in order to evaluate their contribution to the total counts. For simplicity we merge these two backgrounds in an unique `BackgroundModel` and we are going to fit only a global normalisation for this background model.

# In[ ]:


#%% IEM
iem_fermi = Map.read("$GAMMAPY_DATA/catalogs/fermi/gll_iem_v06.fits.gz")
# Unit is not stored in the file, set it manually
iem_fermi.unit = "cm-2 s-1 MeV-1 sr-1"

# Interpolate the diffuse emission model onto the counts geometry
# The resolution of `diffuse_galactic_fermi` is low: bin size = 0.5 deg
# We use ``interp=3`` which means cubic spline interpolation
data = iem_fermi.interp_by_coord(
    {"skycoord": coord.skycoord, "energy": coord["energy"]}, interp=3
)
iem_fermi_roi = WcsNDMap(exposure.geom, data, unit=iem_fermi.unit)
model_iem = SkyDiffuseCube(iem_fermi_roi, name="iem_v06")
eval_iem = MapEvaluator(model=model_iem, exposure=exposure, psf=psf_kernel, edisp=edisp)
bkg_iem = eval_iem.compute_npred()

#%% ISO
filename = "$GAMMAPY_DATA/fermi_3fhl/iso_P8R2_SOURCE_V6_v06.txt"
model_iso = create_fermi_isotropic_diffuse_model(
    filename=filename, interp_kwargs={"fill_value": None}
)
eval_iso = MapEvaluator(model=model_iso, exposure=exposure, edisp=edisp)
bkg_iso = eval_iso.compute_npred()

# merge iem and iso  backgrounds for simplicity
background_total = bkg_iso + bkg_iem
background_model = BackgroundModel(background_total)

background_total.sum_over_axes().smooth(2).plot(
    stretch="log", vmax=50, cmap="nipy_spectral"
)


# The sources model is set by looking for the 3FHL catalog sources in our analysis region, exluding our source of interest that we add separetely (as we already defined its model at the begining of the notebook).
# 

# In[ ]:


# Sources model
FHL3 = SourceCatalog3FHL()
in_roi = FHL3.positions.galactic.contained_by(wcs)
FHL3_roi = []
focus = ["3FHL J0534.5+2201"]  # crab is given seprately
for ks in range(len(FHL3.table)):
    if in_roi[ks] == True and FHL3[ks].name not in focus:
        model = FHL3[ks].sky_model()
        model.parameters.freeze_all()  # freeze the other sources
        FHL3_roi.append(model)
model_total = SkyModels([crab_mod] + FHL3_roi)


# All the data and models necessary for the analysis are collected into the dataset object. Then we can run a fit for this dataset and look at the residuals map (in sigma unit).

# In[ ]:


# Dataset
dataset_fermi = MapDataset(
    model=model_total,
    counts=counts,
    exposure=exposure,
    psf=psf_kernel,
    edisp=edisp,
    background_model=background_model,
    mask_fit=mask_fermi,
    name="Fermi-LAT",
)
results = Fit(dataset_fermi).optimize()
print(results)

dataset_fermi.plot_residuals(
    method="diff/sqrt(model)",
    smooth_kernel="gauss",
    smooth_radius=0.1 * u.deg,
    region=None,
    figsize=(12, 4),
    cmap="jet",
    vmin=-3,
    vmax=3,
)


# We can save data and models using the datasets serialization. For now this works only for map datasets.

# In[ ]:


Datasets([dataset_fermi]).to_yaml(
    path=Path("$GAMMAPY_FERMI_LAT_DATA/3FHL/crab/"), prefix="Fermi-LAT-3FHL", overwrite=True
)







