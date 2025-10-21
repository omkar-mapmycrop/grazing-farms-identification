#!/usr/bin/env python3
import argparse, yaml, rasterio, numpy as np, geopandas as gpd
from rasterio.features import geometry_mask
from rasterio import mask as rio_mask
from pathlib import Path
def main(config_path: str):
    cfg = yaml.safe_load(open(config_path))
    aoi_path  = Path(cfg["paths"]["aoi"])
    farm_path = Path(cfg["paths"]["farms"]["farm_shp"])
    ref_path  = Path(str(cfg["paths"]["dem"]["slope_reclass"]).replace(".tif","_resampled.tif"))
    out_path  = Path(cfg["paths"]["root"]) / "farm_aoi_mask.tif"
    with rasterio.open(ref_path) as ref:
        crs = ref.crs; profile = ref.profile
    aoi = gpd.read_file(aoi_path).to_crs(crs)
    farm = gpd.read_file(farm_path).to_crs(crs)
    farm = gpd.overlay(farm, aoi, how="intersection")
    with rasterio.open(ref_path) as ref:
        out_im, out_tr = rio_mask.mask(ref, aoi.geometry, crop=True)
        out_shape = out_im.shape[1:]
    aoi_mask  = geometry_mask(aoi.geometry,  transform=out_tr, invert=True, out_shape=out_shape)
    farm_mask = geometry_mask(farm.geometry, transform=out_tr, invert=True, out_shape=out_shape)
    import numpy as np
    mask = np.zeros(out_shape, dtype="uint8")
    mask[aoi_mask]  = 2
    mask[farm_mask] = 1
    mask[~aoi_mask] = 0
    profile.update(height=out_shape[0], width=out_shape[1], transform=out_tr, count=1, dtype="uint8", compress="lzw", nodata=0)
    with rasterio.open(out_path, "w", **profile) as dst: dst.write(mask, 1)
    print(f"AOI farm mask saved → {out_path}")
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--config", required=True); a=ap.parse_args(); main(a.config)
