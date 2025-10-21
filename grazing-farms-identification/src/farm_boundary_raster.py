#!/usr/bin/env python3
import argparse, yaml, rasterio, geopandas as gpd
from rasterio import features
from pathlib import Path
def main(config_path: str):
    cfg = yaml.safe_load(open(config_path))
    farm_path = Path(cfg["paths"]["farms"]["farm_clipped"])
    ref_path  = Path(str(cfg["paths"]["dem"]["slope_reclass"]).replace(".tif","_resampled.tif"))
    out_path  = Path(cfg["paths"]["farms"]["farm_mask"])
    with rasterio.open(ref_path) as ref:
        prof = ref.profile; shape = ref.shape; transform = ref.transform; crs = ref.crs
    farm = gpd.read_file(farm_path)
    if farm.crs != crs: farm = farm.to_crs(crs)
    mask = features.rasterize(((geom, 2) for geom in farm.geometry if not geom.is_empty),
                              out_shape=shape, transform=transform, fill=0, all_touched=True, dtype="uint8")
    prof.update(count=1, dtype="uint8", compress="lzw", nodata=0, tiled=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(out_path, "w", **prof) as dst: dst.write(mask, 1)
    print(f"Farm raster saved → {out_path}")
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--config", required=True); a=ap.parse_args(); main(a.config)
