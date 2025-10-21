#!/usr/bin/env python3
import argparse, yaml
def main(config_path: str):
    cfg = yaml.safe_load(open(config_path))
    print("Indices step placeholder — plug in your NAIP patch generator here.")
    print("Expected outputs dirs:", cfg["paths"]["indices"])
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()
    main(args.config)
