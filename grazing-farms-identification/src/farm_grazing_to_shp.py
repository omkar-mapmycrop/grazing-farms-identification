#!/usr/bin/env python3
import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple
import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape, Polygon, MultiPolygon
from shapely.validation import make_valid
from skimage import measure
def pixel_area_ha(transform):
    resx = abs(transform.a); resy = abs(transform.e)
    return (resx * resy) / 10000.0
def label_components(mask: np.ndarray, connectivity: int = 2) -> np.ndarray:
    labels = measure.label(mask.astype(np.uint8), connectivity=connectivity, background=0)
    return labels
def calc_shape_metrics(geom: Polygon) -> dict:
    area_m2 = geom.area; perim_m = geom.length
    compactness = (4.0 * np.pi * area_m2) / (perim_m ** 2 + 1e-9) if area_m2>0 and perim_m>0 else 0.0
    hull = geom.convex_hull; convexity = (area_m2 / hull.area) if hull.area>0 else 0.0
    mrr = geom.minimum_rotated_rectangle
    from shapely.geometry import Polygon as _Poly
    if isinstance(mrr, _Poly):
        coords = list(mrr.exterior.coords)
        edges = [np.linalg.norm(np.array(coords[i]) - np.array(coords[(i+1)%len(coords)])) for i in range(len(coords)-1)]
        edges = sorted(edges, reverse=True)
        elongation = (edges[0]/edges[1]) if len(edges)>=2 and edges[1]>0 else 1.0
    else:
        elongation = 1.0
    return {"area_ha": area_m2/10000.0, "perimeter_m": perim_m, "compactness": float(compactness),
            "convexity": float(convexity), "elongation": float(elongation)}
def vectorize_labels(labels: np.ndarray, transform, class_value: int = 1):
    out = []; mask = (labels > 0).astype("uint8")
    for geom, val in shapes(mask, mask=None, transform=transform):
        if val == 1: out.append(({"class": class_value}, shape(geom)))
    return out
def simplify_and_smooth(geom: Polygon, tol_m: float) -> Polygon:
    if geom.is_empty: return geom
    g = geom.simplify(tol_m, preserve_topology=True)
    d = max(tol_m, 1.0)
    try: g2 = g.buffer(d).buffer(-d)
    except Exception: g2 = g
    try: g2 = make_valid(g2)
    except Exception: g2 = g2.buffer(0)
    return g2
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raster", required=True)
    ap.add_argument("--out_shp", default="results/grazing_patches.shp")
    ap.add_argument("--out_geojson", default="results/grazing_patches.geojson")
    ap.add_argument("--grazing_value", type=int, default=1)
    ap.add_argument("--min_pixels", type=int, default=100)
    ap.add_argument("--min_ha", type=float, default=2.0)
    ap.add_argument("--max_ha", type=float, default=500.0)
    ap.add_argument("--simplify_tol", type=float, default=10.0)
    args = ap.parse_args()
    with rasterio.open(args.raster) as src:
        arr = src.read(1); transform = src.transform; crs = src.crs
    grazing_mask = (arr == args.grazing_value)
    labels = label_components(grazing_mask, connectivity=2)
    # remove small components by pixel count
    unique, counts = np.unique(labels, return_counts=True)
    keep = set(int(u) for u,c in zip(unique, counts) if (u>0 and c>=args.min_pixels))
    labels_filtered = np.where(np.isin(labels, list(keep)), labels, 0)
    geoms = vectorize_labels(labels_filtered, transform, class_value=args.grazing_value)
    recs, geos = [], []
    from shapely.geometry import MultiPolygon, Polygon
    for attrs, poly in geoms:
        if poly.is_empty: continue
        parts = list(poly.geoms) if isinstance(poly, MultiPolygon) else [poly]
        for p in parts:
            if p.is_empty: continue
            metrics = calc_shape_metrics(p)
            if metrics["area_ha"] < args.min_ha or metrics["area_ha"] > args.max_ha: continue
            p2 = simplify_and_smooth(p, args.simplify_tol)
            metrics2 = calc_shape_metrics(p2)
            recs.append({**attrs, **metrics2}); geos.append(p2)
    if not geos: print("No polygons after filtering; nothing to write."); return
    gdf = gpd.GeoDataFrame(recs, geometry=geos, crs=crs)
    Path(args.out_shp).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_geojson).parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(args.out_shp)
    gdf.to_file(args.out_geojson, driver="GeoJSON")
    print(f"Wrote {len(gdf)} polygons → {args.out_shp} and {args.out_geojson}")
if __name__ == "__main__":
    main()
