#!/usr/bin/env python3
import argparse, yaml, rasterio, numpy as np
from pathlib import Path
from rasterio.windows import from_bounds
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
def process_patch(ndvi_path, savi_dir, cdl_path, slope_path, out_dir):
    ndvi_name = ndvi_path.name
    savi_path = savi_dir / ndvi_name
    out_path = out_dir / ndvi_path.with_suffix("").name.replace("_active_new","") + "_mask.tif"
    if not savi_path.exists(): return f"missing SAVI for {ndvi_name}"
    if out_path.exists(): return None
    with rasterio.open(ndvi_path) as ndvi, rasterio.open(savi_path) as savi,          rasterio.open(cdl_path) as cdl, rasterio.open(slope_path) as slope:
        ndvi_b = ndvi.bounds
        cdl_w = from_bounds(*ndvi_b, transform=cdl.transform)
        slp_w = from_bounds(*ndvi_b, transform=slope.transform)
        a = ndvi.read(1); b = savi.read(1)
        c = cdl.read(1, window=cdl_w, out_shape=a.shape, resampling=rasterio.enums.Resampling.nearest)
        d = slope.read(1, window=slp_w, out_shape=a.shape, resampling=rasterio.enums.Resampling.nearest)
        final = np.where((a==1)&(b==1)&(c==1)&(d==1), 1, 2).astype("uint8")
        prof = ndvi.profile; prof.update(dtype="uint8", count=1, compress="LZW", tiled=True)
        with rasterio.open(out_path, "w", **prof) as dst: dst.write(final, 1)
    return ndvi_name
def main(config_path: str):
    cfg = yaml.safe_load(open(config_path))
    ndvi_dir = Path(cfg["paths"]["indices"]["ndvi_active_dir"])
    savi_dir = Path(cfg["paths"]["indices"]["savi_active_dir"])
    out_dir = Path(cfg["paths"]["indices"]["final_mask_dir"]); out_dir.mkdir(exist_ok=True, parents=True)
    cdl = Path(cfg["paths"]["cdl"]["cdl_resampled"])
    slope = Path(str(cfg["paths"]["dem"]["slope_reclass"]).replace(".tif","_resampled.tif"))
    files = sorted(ndvi_dir.glob("*.tif"))
    if not files: raise SystemExit("No NDVI active files — run mask_indices first.")
    with ThreadPoolExecutor(max_workers=32) as exe:
        futs = [exe.submit(process_patch, f, Path(savi_dir), Path(cdl), Path(slope), out_dir) for f in files]
        for _ in tqdm(as_completed(futs), total=len(futs), desc="Consensus"): pass
    print(f"Consensus masks → {out_dir}")
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--config", required=True); a=ap.parse_args(); main(a.config)
