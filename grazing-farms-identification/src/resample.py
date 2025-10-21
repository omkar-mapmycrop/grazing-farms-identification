#!/usr/bin/env python3
import argparse, yaml, rasterio, glob, os
from rasterio.warp import calculate_default_transform, reproject, Resampling
def resample_to(ref_path, src_path, dst_path):
    with rasterio.open(ref_path) as ref, rasterio.open(src_path) as src:
        transform, width, height = calculate_default_transform(
            src.crs, ref.crs, src.width, src.height, *src.bounds, resolution=ref.res
        )
        kwargs = src.meta.copy()
        kwargs.update({"crs": ref.crs, "transform": transform, "width": width, "height": height,
                       "compress": "LZW", "BIGTIFF": "YES", "tiled": True, "blockxsize": 512, "blockysize": 512})
        with rasterio.open(dst_path, "w", **kwargs) as dst:
            for i in range(1, src.count+1):
                reproject(source=rasterio.band(src, i), destination=rasterio.band(dst, i),
                          src_transform=src.transform, src_crs=src.crs,
                          dst_transform=transform, dst_crs=ref.crs,
                          resampling=Resampling.nearest if src.count==1 else Resampling.bilinear, num_threads=4)
    print("Resampled →", dst_path)
def main(config_path: str):
    cfg = yaml.safe_load(open(config_path))
    ndvi_dir = cfg["paths"]["indices"]["ndvi_dir"]
    ndvi_patches = sorted(glob.glob(os.path.join(ndvi_dir, "*.tif")))
    if not ndvi_patches: raise SystemExit("No NDVI patches found — compute indices first.")
    ref = ndvi_patches[0]
    cdl_src = cfg["paths"]["cdl"]["cdl_src"]; cdl_out = cfg["paths"]["cdl"]["cdl_resampled"]
    slope_re = cfg["paths"]["dem"]["slope_reclass"]; slope_out = slope_re.replace(".tif", "_resampled.tif")
    resample_to(ref, cdl_src, cdl_out); resample_to(ref, slope_re, slope_out)
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--config", required=True); a=ap.parse_args(); main(a.config)
