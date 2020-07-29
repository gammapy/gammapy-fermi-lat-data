from astropy import units as u
from gammapy.data import EventList
from gammapy.irf import EnergyDependentTablePSF, EDispKernelMap, PSFMap
from gammapy.maps import Map, MapAxis, WcsGeom
from gammapy.datasets import Datasets, MapDataset
from gammapy.modeling.models import (
    LogParabolaSpectralModel,
    SkyDiffuseCube,
    create_fermi_isotropic_diffuse_model,
    Models,
    BackgroundModel
)
from gammapy.modeling import Fit
from gammapy.catalog import SourceCatalog4FGL, SourceCatalog3FHL
from pathlib import Path
from regions import RectangleSkyRegion


FGL4 = SourceCatalog4FGL()
crab = FGL4["Crab Nebula"]  #
model_crab = crab.sky_model()

crab_pos = crab.position.galactic
# freeze position
model_crab.spatial_model.parameters.freeze_all()
# change spectrum to LogParabola (default is PowerLaw for the Crab)
model_crab.spectral_model = LogParabolaSpectralModel(
    amplitude=crab.data["LP_Flux_Density"],
    alpha=crab.data["LP_Index"],
    beta=crab.data["LP_beta"],
    reference=crab.data["Pivot_Energy"],
)

energy_axis = MapAxis.from_energy_bounds("10 GeV", "2 TeV", nbin=5)

geom = WcsGeom.create(
    skydir=model_crab.position,
    width=(5 * u.deg, 4 * u.deg),
    proj="CAR",
    frame="galactic",
    binsz=0.1,
    axes=[energy_axis],
)

dataset = MapDataset.create(geom, name="Fermi-LAT")

# Counts map
events = EventList.read("$GAMMAPY_DATA/fermi_3fhl/fermi_3fhl_events_selected.fits.gz")
dataset.counts.fill_events(events)

# Exposure
exposure_hpx = Map.read("$GAMMAPY_DATA/fermi_3fhl/fermi_3fhl_exposure_cube_hpx.fits.gz")
exposure_hpx.unit = "cm2 s"

coords = dataset.exposure.geom.get_coord()
value = u.Quantity(exposure_hpx.interp_by_coord(coords), "cm2 s")
dataset.exposure.quantity = value

# read PSF
psf = EnergyDependentTablePSF.read("$GAMMAPY_DATA/fermi_3fhl/fermi_3fhl_psf_gc.fits.gz")
dataset.psf = PSFMap.from_energy_dependent_table_psf(psf)


# define safe mask
width, height = geom.width

margin = 0.2 * u.deg
region = RectangleSkyRegion(
    center=geom.center_skydir,
    width=(width - 2 * margin)[0],
    height=(height - 2 * margin)[0],
)

mask = geom.region_mask([region])
dataset.mask_safe = Map.from_geom(geom, data=mask)


map_iem = Map.read("$FERMI_DIFFUSE_DIR/gll_iem_v06.fits")
map_iem.unit = "cm-2 s-1 MeV-1 sr-1"

map_iem_roi = map_iem.cutout(
    position=geom.center_skydir, width=geom.width
)

filename = "Fermi-LAT-3FHL_iem.fits"
map_iem_roi.write(filename, overwrite=True)

model_iem = SkyDiffuseCube(
    map_iem_roi, name="iem_v06", filename=f"$GAMMAPY_DATA/fermi-3fhl-crab/{filename}"
)

#%% ISO
filename = "$GAMMAPY_DATA/fermi_3fhl/iso_P8R2_SOURCE_V6_v06.txt"
model_iso = create_fermi_isotropic_diffuse_model(
    filename=filename, interp_kwargs={"fill_value": None}
)

dataset.models = Models([model_iem, model_iso])

# TODO: don't use fermi background this way
npred = dataset.npred()
bkg = BackgroundModel(npred, datasets_names=[dataset.name], name="iem_v06")
dataset.models = [model_crab, bkg]


fit = Fit([dataset])
result = fit.run()


Datasets([dataset]).write(
    path=Path("$GAMMAPY_FERMI_LAT_DATA/3FHL/crab/"), prefix="Fermi-LAT-3FHL", overwrite=True,
    write_covariance=False
)







