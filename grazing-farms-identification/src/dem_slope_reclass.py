#!/usr/bin/env python3
import argparse, yaml, rasterio, numpy as np
from pathlib import Path
def main(config_path: str):
    cfg = yaml.safe_load(open(config_path))
    slope_deg = Path(cfg["paths"]["dem"]["slope_deg"])
    slope_re = Path(cfg["paths"]["dem"]["slope_reclass"])
    gentle_max = float(cfg["thresholds"]["slope_reclass"]["gentle_max_deg"])
    if not slope_deg.exists():
        raise SystemExit(f"Provide slope degrees raster at {slope_deg}")
    with rasterio.open(slope_deg) as src:
        arr = src.read(1).astype("float32"); prof = src.profile
    reclass = np.zeros_like(arr, dtype="uint8")
    reclass[(arr >= 0) & (arr <= gentle_max)] = 1
    reclass[arr > gentle_max] = 2
    prof.update(count=1, dtype="uint8", compress="lzw", nodata=0, tiled=True, blockxsize=512, blockysize=512)
    slope_re.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(slope_re, "w", **prof) as dst: dst.write(reclass, 1)
    print(f"Wrote slope reclass → {slope_re}")
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--config", required=True); a=ap.parse_args(); main(a.config)
