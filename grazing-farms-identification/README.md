# Grazing Farms Identification

An independent, production-grade pipeline to generate **Grazing / Non‑Grazing** maps using NAIP imagery, DEM slope, CDL crop type, and farm boundaries.

## 🧭 End-to-end flow

1. **Fetch data from S3 → local** (optional): `src/s3_fetch.py`
2. **DEM → Slope → Reclassification**: `src/dem_slope_reclass.py`
3. **Resample CDL & Slope** to the NDVI grid: `src/resample.py`
4. **Compute NAIP indices** (NDVI, SAVI, EVI, optional GLCM): `src/indices.py`
5. **Reclassify indices** into Grazing (1) / Non‑Grazing (2): `src/mask_indices.py`
6. **Consensus mask** across NDVI+SAVI+CDL+Slope: `src/consensus_mask.py`
7. **Farm boundary → raster mask** aligned to grid: `src/farm_boundary_raster.py`
8. **AOI-specific farm mask (optional)**: `src/farm_aoi_mask.py`
9. **Apply farm mask onto grazing mosaic**: `src/apply_farm_on_grazing.py`
10. **One-shot runner**: `src/pipeline.py`

## 🗂️ Repo layout

```
grazing-farms-identification/
├─ config/
│  └─ config.yaml
├─ src/
│  ├─ s3_fetch.py
│  ├─ indices.py
│  ├─ dem_slope_reclass.py
│  ├─ resample.py
│  ├─ mask_indices.py
│  ├─ consensus_mask.py
│  ├─ farm_boundary_raster.py
│  ├─ farm_aoi_mask.py
│  ├─ apply_farm_on_grazing.py
│  └─ farm_grazing_to_shp.py
├─ docs/
│  ├─ flowchart.md
│  └─ QA_checklist.md
├─ .github/workflows/python-ci.yml
├─ configs/sample-config.yaml
├─ scripts/run_pipeline.sh
├─ data/.gitkeep
├─ results/.gitkeep
├─ .env.example
├─ .gitignore
├─ LICENSE
├─ requirements.txt
├─ pyproject.toml
├─ Makefile
└─ README.md
```

## 🚀 Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m src.pipeline --config config/config.yaml
```

## Phase 4: Boundary Creation & Delineation (Steps 15–18)
- **Step 15**: remove noise (<100 px), keep 2–500 ha, compute shape metrics
- **Step 16**: connected components → patches (IDs + area)
- **Step 17**: vectorize to polygons (class label retained), export SHP/GeoJSON
- **Step 18**: simplify (10 m), smooth, ensure valid geometry

### CLI
```bash
python -m src.farm_grazing_to_shp   --raster /path/to/mosaic_final_grazing_farmupdated_new.tif   --out_shp results/grazing_patches.shp   --out_geojson results/grazing_patches.geojson   --grazing_value 1   --min_pixels 100   --min_ha 2 --max_ha 500   --simplify_tol 10
```
