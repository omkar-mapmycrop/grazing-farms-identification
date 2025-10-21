#!/usr/bin/env python3
import argparse, subprocess, sys
def run(cmd):
    print("\n$ " + " ".join(cmd))
    subprocess.run(cmd, check=True)
def main(cfg):
    run([sys.executable, "-m", "src.dem_slope_reclass", "--config", cfg])
    run([sys.executable, "-m", "src.indices", "--config", cfg])
    run([sys.executable, "-m", "src.resample", "--config", cfg])
    run([sys.executable, "-m", "src.mask_indices", "--config", cfg])
    run([sys.executable, "-m", "src.consensus_mask", "--config", cfg])
    run([sys.executable, "-m", "src.farm_boundary_raster", "--config", cfg])
    run([sys.executable, "-m", "src.apply_farm_on_grazing", "--config", cfg])
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--config", required=True); a=ap.parse_args(); main(a.config)
