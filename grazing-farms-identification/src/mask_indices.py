#!/usr/bin/env python3
import argparse, yaml, numpy as np, rasterio
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
def classify_file(file_path: Path, out_dir: Path, thr_min: float, thr_max: float):
    out_path = out_dir / f"{file_path.stem}_active_new.tif"
    if out_path.exists(): return ("skipped", file_path.name)
    with rasterio.open(file_path) as src:
        img = src.read(1).astype("float32")
        if src.nodata is not None: img[img == src.nodata] = np.nan
        valid = ~np.isnan(img); mask = np.zeros_like(img, dtype="uint8")
        mask[valid] = 2; mask[(img >= thr_min) & (img <= thr_max) & valid] = 1
        meta = src.meta.copy(); meta.update(dtype="uint8", count=1, compress="lzw", nodata=0)
        with rasterio.open(out_path, "w", **meta) as dst: dst.write(mask, 1)
    return ("ok", file_path.name)
def main(config_path: str):
    cfg = yaml.safe_load(open(config_path))
    ndvi_dir = Path(cfg["paths"]["indices"]["ndvi_dir"])
    savi_dir = Path(cfg["paths"]["indices"]["savi_dir"])
    out_ndvi = Path(cfg["paths"]["indices"]["ndvi_active_dir"]); out_ndvi.mkdir(parents=True, exist_ok=True)
    out_savi = Path(cfg["paths"]["indices"]["savi_active_dir"]); out_savi.mkdir(parents=True, exist_ok=True)
    t_ndvi = cfg["thresholds"]["ndvi"]; t_savi = cfg["thresholds"]["savi"]
    for idx_name, in_dir, out_dir, thr in [("NDVI", ndvi_dir, out_ndvi, t_ndvi), ("SAVI", savi_dir, out_savi, t_savi)]:
        files = sorted(in_dir.glob("*.tif")); 
        if not files: print(f"No {idx_name} files in {in_dir}"); continue
        with ProcessPoolExecutor() as exe:
            futs = [exe.submit(classify_file, f, out_dir, thr["min"], thr["max"]) for f in files]
            for _ in tqdm(as_completed(futs), total=len(futs), desc=f"{idx_name} classify"): pass
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--config", required=True); a=ap.parse_args(); main(a.config)
