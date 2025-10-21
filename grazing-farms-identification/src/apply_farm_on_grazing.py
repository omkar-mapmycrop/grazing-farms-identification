#!/usr/bin/env python3
import argparse, yaml, rasterio, numpy as np, shutil
from pathlib import Path
from rasterio.windows import Window
from rasterio.merge import merge
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
PATCH_SIZE = 4096
MAX_THREADS = 32
def windows(h, w):
    for r in range(0, h, PATCH_SIZE):
        for c in range(0, w, PATCH_SIZE):
            yield Window(c, r, min(PATCH_SIZE, w-c), min(PATCH_SIZE, h-r))
def process(win, profile, grazing_path: Path, farm_mask: Path, tmp_dir: Path, enforce_val: int):
    with rasterio.open(grazing_path) as g, rasterio.open(farm_mask) as f:
        a = g.read(1, window=win)
        b = f.read(1, window=win)
    a[b == 2] = enforce_val
    outf = tmp_dir / f"patch_{int(win.col_off)}_{int(win.row_off)}.tif"
    pf = profile.copy()
    pf.update(height=win.height, width=win.width, transform=rasterio.windows.transform(win, profile["transform"]),
              compress="lzw", tiled=True, blockxsize=256, blockysize=256)
    with rasterio.open(outf, "w", **pf) as dst: dst.write(a, 1)
    return outf
def main(config_path: str):
    cfg = yaml.safe_load(open(config_path))
    grazing = Path(cfg["paths"]["mosaics"]["grazing_mosaic"])
    farm_mask = Path(cfg["paths"]["farms"]["farm_mask"])
    out_path  = Path(cfg["paths"]["mosaics"]["grazing_with_farms"])
    enforce_val = int(cfg["consensus"]["enforce_farm_as_class"])
    tmp_dir = out_path.parent / "_tmp_patches"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    with rasterio.open(grazing) as g:
        profile = g.profile; h, w = g.height, g.width
    wins = list(windows(h, w))
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as exe:
        futs = [exe.submit(process, win, profile, grazing, farm_mask, tmp_dir, enforce_val) for win in wins]
        for _ in tqdm(as_completed(futs), total=len(futs), desc="Apply farm mask"): pass
    srcs = [rasterio.open(p) for p in sorted(tmp_dir.glob("*.tif"))]
    mosaic, transform = merge(srcs, method="first")
    for s in srcs: s.close()
    profile.update(height=mosaic.shape[1], width=mosaic.shape[2], transform=transform, compress="lzw", tiled=True)
    with rasterio.open(out_path, "w", **profile) as dst: dst.write(mosaic[0], 1)
    shutil.rmtree(tmp_dir, ignore_errors=True)
    print(f"Final raster saved → {out_path}")
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--config", required=True); a=ap.parse_args(); main(a.config)
