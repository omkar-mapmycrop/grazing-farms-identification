# Grazing Land Detection Pipeline

Multi-source geospatial analysis pipeline for identifying grazing lands using NAIP imagery, vegetation indices, terrain data, and land cover classification.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Rasterio](https://img.shields.io/badge/Rasterio-1.3+-green.svg)](https://rasterio.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


## Overview

This project identifies and delineates grazing lands through multi-criteria analysis using:

**Data**: NAIP imagery-derived vegetation indices (NDVI, SAVI), USDA Cropland Data Layer (CDL), DEM-derived slope, and farm boundary vectors

**Approach**: Consensus-based classification combining vegetation thresholds, land cover filtering, terrain analysis, and farm boundary enforcement

**Output**: Binary grazing/non-grazing raster masks and vectorized grazing patch polygons with geometric attributes

## 📊 Executive Summary

### Mission

Identify and map grazing lands at scale by integrating multi-source geospatial data—NAIP-derived vegetation indices, cropland data layers, terrain analysis, and farm boundaries—to support agricultural monitoring, land use planning, and environmental assessment. Outputs enable stakeholders to quantify grazing extent, patch characteristics, and spatial distribution patterns for statewide analytics.

### Technical Approach

**Input Data:**
- **NAIP Imagery**: 4-band aerial imagery (RGB + NIR) for vegetation index computation
- **Vegetation Indices**: NDVI and SAVI tiles computed from NAIP patches
- **Cropland Data Layer (CDL)**: USDA land cover classification (resampled to match NAIP resolution)
- **DEM Products**: Slope in degrees, reclassified to gentle/steep categories
- **Farm Boundaries**: Vector polygons of known farm parcels (shapefile/GeoJSON)
- **Area of Interest (AOI)**: Study area boundary polygon

**Processing Pipeline:**
1. **DEM Slope Reclassification**: Classify slope into gentle (≤ threshold) vs steep terrain
2. **Indices Computation**: Generate NDVI and SAVI from NAIP patches (placeholder step)
3. **Resampling**: Align CDL and slope rasters to NAIP grid resolution and extent
4. **Threshold Masking**: Binary classification of NDVI and SAVI based on vegetation thresholds
5. **Consensus Mask**: Combine NDVI, SAVI, CDL, and slope masks—grazing identified where all conditions met
6. **Farm Boundary Integration**: Rasterize farm polygons and enforce farm pixels as a specific class
7. **Farm-on-Grazing Application**: Apply farm mask to grazing mosaic, replacing farm areas with designated value

**Output Artifacts:**
- Slope reclassification raster (gentle/steep)
- Active vegetation masks (NDVI and SAVI)
- Consensus grazing masks (per patch)
- Farm boundary raster
- Final grazing mosaic with farms enforced
- Vectorized grazing patches with shape metrics (area, perimeter, compactness, convexity, elongation)

### Performance Metrics 

| Metric | Description | Purpose |
|--------|-------------|---------|
| **Processing Speed** | ~500 patches/min (32 threads) | Parallel throughput for large-scale processing |
| **Patch Coverage** | 4096×4096 pixel tiles | Optimal balance of memory and I/O efficiency |
| **Slope Threshold** | Default ≤15° (configurable) | Distinguishes gentle grazing terrain from steep slopes |
| **NDVI Range** | 0.3 - 0.7 (configurable) | Active vegetation suitable for grazing |
| **SAVI Range** | 0.2 - 0.6 (configurable) | Soil-adjusted vegetation for sparse cover |
| **Min Patch Size** | 2 hectares (configurable) | Filters noise and small artifacts |
| **Max Patch Size** | 500 hectares (configurable) | Upper bound for single contiguous grazing parcels |

**Consensus Logic:**
- Grazing = 1 if ALL conditions true: NDVI_active AND SAVI_active AND CDL_active AND Slope_gentle
- Non-grazing = 2 otherwise
- Farm areas override with enforced class value (from config)

**Shape Metrics (Vectorization):**
- **Area (ha)**: Patch area in hectares
- **Perimeter (m)**: Boundary length in meters
- **Compactness**: (4π × Area) / Perimeter² (1.0 = perfect circle)
- **Convexity**: Area / ConvexHullArea (1.0 = fully convex)
- **Elongation**: LongAxis / ShortAxis of minimum rotated rectangle

### Release Quality Gates

| Category | Metric | Target | Purpose |
|----------|--------|--------|---------|
| **Data Quality** | Valid TIFF reading | ≥99.5% | Clean raster I/O pipeline |
| | CDL/Slope alignment | Perfect overlap | Spatial registration accuracy |
| **Processing** | Patch completion rate | 100% | No dropped tiles in mosaic |
| | Memory usage | ≤16GB/thread | Scalable to large AOIs |
| **Output Quality** | Farm mask coverage | ≥95% of farm polygons | Accurate boundary rasterization |
| | Grazing patch count | Match ground truth ±10% | Validation against reference data |
| **Vectorization** | Polygon validity | 100% | No self-intersections or topology errors |
| | Shape metric completeness | 100% | All attributes computed |
| **Performance** | Processing time | ≤2 hrs for 10K km² | Efficient large-area workflows |
| | Mosaic edge alignment | Perfect seamless merge | No artifacts at tile boundaries |

## Project Structure

```
grazing-detection/
├── configs/
│   └── pipeline_config.yaml       # Main pipeline configuration
├── data/
│   ├── aoi/
│   │   └── study_area.shp         # Area of interest boundary
│   ├── farms/
│   │   ├── farm_boundaries.shp    # Farm parcel polygons
│   │   ├── farm_clipped.shp       # Farms clipped to AOI
│   │   └── farm_mask.tif          # Rasterized farm boundaries
│   ├── dem/
│   │   ├── slope_deg.tif          # Slope in degrees
│   │   ├── slope_reclass.tif      # Reclassified slope (1=gentle, 2=steep)
│   │   └── slope_reclass_resampled.tif
│   ├── cdl/
│   │   ├── cdl_raw.tif            # Raw USDA CDL
│   │   └── cdl_resampled.tif      # Resampled to NAIP grid
│   ├── indices/
│   │   ├── ndvi/                  # Raw NDVI patches
│   │   ├── savi/                  # Raw SAVI patches
│   │   ├── ndvi_active/           # Thresholded NDVI masks
│   │   ├── savi_active/           # Thresholded SAVI masks
│   │   └── final_masks/           # Consensus grazing masks
│   └── mosaics/
│       ├── grazing_mosaic.tif     # Combined grazing mask
│       └── grazing_with_farms.tif # Final output with farms
├── src/
│   ├── dem_slope_reclass.py       # Reclassify slope by threshold
│   ├── indices.py                 # Placeholder for NDVI/SAVI computation
│   ├── resample.py                # Align CDL and slope to NAIP grid
│   ├── mask_indices.py            # Threshold NDVI/SAVI by vegetation range
│   ├── consensus_mask.py          # Multi-criteria consensus classification
│   ├── farm_boundary_raster.py    # Rasterize farm polygons
│   ├── farm_aoi_mask.py           # Create AOI-farm composite mask
│   ├── apply_farm_on_grazing.py   # Enforce farm class on grazing mosaic
│   ├── farm_grazing_to_shp.py     # Vectorize grazing patches with metrics
│   ├── pipeline.py                # Orchestrate full pipeline
│   └── s3_fetch.py                # Download data from S3 (optional)
├── results/
│   ├── grazing_patches.shp        # Vectorized grazing polygons
│   └── grazing_patches.geojson    # GeoJSON format output
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd grazing-detection
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Core dependencies:
- `rasterio>=1.3.0` - Geospatial raster I/O
- `geopandas>=0.14.0` - Vector data handling
- `numpy>=1.24.0` - Numerical operations
- `scipy` - Scientific computing
- `scikit-image>=0.21.0` - Image processing (connected components)
- `shapely>=2.0.0` - Geometric operations
- `pyyaml>=6.0` - Configuration file parsing
- `tqdm` - Progress bars
- `boto3` - AWS S3 access (optional)

### 4. Configure AWS credentials for S3 access

```bash
aws configure
# Enter your AWS Access Key ID, Secret Key, and region
```

### 5. Verify installation

```bash
python -c "import rasterio; print(f'Rasterio: {rasterio.__version__}')"
python -c "import geopandas as gpd; print(f'GeoPandas: {gpd.__version__}')"
python -c "import skimage; print(f'scikit-image: {skimage.__version__}')"
```

## Usage

### Configuration

Edit `configs/pipeline_config.yaml` to set paths and thresholds:

```yaml
paths:
  root: "data"
  aoi: "data/aoi/study_area.shp"
  
  dem:
    slope_deg: "data/dem/slope_deg.tif"
    slope_reclass: "data/dem/slope_reclass.tif"
  
  cdl:
    cdl_src: "data/cdl/cdl_raw.tif"
    cdl_resampled: "data/cdl/cdl_resampled.tif"
  
  indices:
    ndvi_dir: "data/indices/ndvi"
    savi_dir: "data/indices/savi"
    ndvi_active_dir: "data/indices/ndvi_active"
    savi_active_dir: "data/indices/savi_active"
    final_mask_dir: "data/indices/final_masks"
  
  farms:
    farm_shp: "data/farms/farm_boundaries.shp"
    farm_clipped: "data/farms/farm_clipped.shp"
    farm_mask: "data/farms/farm_mask.tif"
  
  mosaics:
    grazing_mosaic: "data/mosaics/grazing_mosaic.tif"
    grazing_with_farms: "data/mosaics/grazing_with_farms.tif"

thresholds:
  slope_reclass:
    gentle_max_deg: 15.0             # Max slope for gentle terrain
  
  ndvi:
    min: 0.3                         # Min NDVI for active vegetation
    max: 0.7                         # Max NDVI for active vegetation
  
  savi:
    min: 0.2                         # Min SAVI for active vegetation
    max: 0.6                         # Max SAVI for active vegetation

consensus:
  enforce_farm_as_class: 3           # Class value for farm pixels in final mosaic
```

### Data Preparation

Your data should be organized with:

1. **NAIP Imagery**: 4-band TIFF files (RGB + NIR) for computing vegetation indices
   - Organize in regular grid tiles for efficient processing
   - Recommended: 5000×5000 pixel tiles with overlap

2. **DEM Products**: Slope raster in degrees
   - Source: USGS 3DEP, SRTM, or state LiDAR
   - Units: degrees (0-90)

3. **CDL Raster**: USDA Cropland Data Layer
   - Download from: https://nassgeodata.gmu.edu/CropScape/
   - Select year matching NAIP acquisition
   - Ensure coverage matches AOI

4. **Farm Boundaries**: Vector polygons (shapefile or GeoJSON)
   - Attributes: farm_id, owner, type (optional)
   - Coordinate system: must match or be reprojectable to NAIP CRS

5. **AOI Boundary**: Study area polygon
   - Single or multi-polygon feature
   - Used to clip all datasets to common extent

### Running the Pipeline

#### Full Pipeline

Run all steps sequentially:

```bash
python src/pipeline.py --config configs/pipeline_config.yaml
```

**Pipeline Stages:**
1. Reclassify slope → gentle/steep
2. Compute NDVI/SAVI (placeholder—integrate your indices generator)
3. Resample CDL and slope to NAIP grid
4. Threshold NDVI and SAVI → active vegetation masks
5. Generate consensus masks → combine all criteria
6. Rasterize farm boundaries
7. Apply farm mask → final grazing map with farms enforced

#### Individual Steps

Run specific processing steps:

**1. Reclassify Slope**
```bash
python src/dem_slope_reclass.py --config configs/pipeline_config.yaml
```
- Input: `slope_deg.tif` (continuous slope in degrees)
- Output: `slope_reclass.tif` (1=gentle, 2=steep)
- Threshold: Set `thresholds.slope_reclass.gentle_max_deg` in config

**2. Compute Vegetation Indices**
```bash
python src/indices.py --config configs/pipeline_config.yaml
```
- **Note**: This is a placeholder script
- Integrate your NAIP patch processor to compute NDVI and SAVI
- Expected outputs: 
  - `data/indices/ndvi/*.tif` (one per NAIP tile)
  - `data/indices/savi/*.tif` (one per NAIP tile)

**3. Resample Ancillary Data**
```bash
python src/resample.py --config configs/pipeline_config.yaml
```
- Aligns CDL and slope rasters to NAIP grid
- Uses first NDVI patch as reference for resolution/extent
- Method: Nearest neighbor resampling (preserves categorical values)

**4. Threshold Vegetation Indices**
```bash
python src/mask_indices.py --config configs/pipeline_config.yaml
```
- Classifies each pixel: 1=active vegetation, 2=inactive
- Processes NDVI and SAVI independently in parallel
- Thresholds: Set `thresholds.ndvi` and `thresholds.savi` in config

**5. Generate Consensus Masks**
```bash
python src/consensus_mask.py --config configs/pipeline_config.yaml
```
- Combines: NDVI_active AND SAVI_active AND CDL_active AND Slope_gentle
- Output: 1=grazing, 2=non-grazing
- One mask per NAIP tile

**6. Rasterize Farm Boundaries**
```bash
python src/farm_boundary_raster.py --config configs/pipeline_config.yaml
```
- Converts farm polygons to raster
- Value: 2 for farm pixels, 0 elsewhere
- Uses `all_touched=True` for complete coverage

**7. Apply Farm Mask to Grazing**
```bash
python src/apply_farm_on_grazing.py --config configs/pipeline_config.yaml
```
- Replaces farm pixels in grazing mosaic with `enforce_farm_as_class` value
- Processes in 4096×4096 patches with 32 threads
- Merges patches into seamless mosaic

**8. Vectorize Grazing Patches**
```bash
python src/farm_grazing_to_shp.py \
    --raster data/mosaics/grazing_with_farms.tif \
    --out_shp results/grazing_patches.shp \
    --out_geojson results/grazing_patches.geojson \
    --grazing_value 1 \
    --min_pixels 100 \
    --min_ha 2.0 \
    --max_ha 500.0 \
    --simplify_tol 10.0
```

**Key Arguments:**

| Argument | Default | Description |
|----------|---------|-------------|
| `--raster` | (required) | Path to grazing raster (1=grazing, 2=non-grazing) |
| `--out_shp` | `results/grazing_patches.shp` | Output shapefile path |
| `--out_geojson` | `results/grazing_patches.geojson` | Output GeoJSON path |
| `--grazing_value` | `1` | Pixel value representing grazing class |
| `--min_pixels` | `100` | Minimum patch size in pixels |
| `--min_ha` | `2.0` | Minimum patch area in hectares |
| `--max_ha` | `500.0` | Maximum patch area in hectares |
| `--simplify_tol` | `10.0` | Simplification tolerance in meters |

**Vectorization Process:**
1. **Connected Components**: Label contiguous grazing pixels (8-connectivity)
2. **Size Filtering**: Remove patches < `min_pixels` or outside `min_ha`-`max_ha` range
3. **Vectorization**: Convert raster labels to polygons
4. **Simplification**: Douglas-Peucker simplification with tolerance
5. **Smoothing**: Buffer-unbuffer operation for rounded edges
6. **Metrics Computation**: Calculate shape attributes for each polygon

**Output Attributes:**
- `class`: Class value (typically 1 for grazing)
- `area_ha`: Patch area in hectares
- `perimeter_m`: Boundary length in meters
- `compactness`: Shape regularity (0-1, 1=circle)
- `convexity`: Ratio to convex hull (0-1, 1=convex)
- `elongation`: Length/width ratio from MRR

### Fetch Data from S3

Data is stored in S3:

```bash
export S3_INPUT_BUCKET="my-naip-bucket"
export S3_INPUT_PREFIX="state/county/naip_2020/"
export LOCAL_DATA_ROOT="data/indices/ndvi"

python src/s3_fetch.py
```

**Environment Variables:**
- `S3_INPUT_BUCKET`: S3 bucket name
- `S3_INPUT_PREFIX`: Object key prefix
- `LOCAL_DATA_ROOT`: Local download directory

### Processing Large Areas

For statewide or multi-county processing:

**1. Tile-Based Processing**
- Process in county or USGS quad tiles
- Run pipeline independently per tile
- Mosaic final outputs using GDAL

**2. Memory Management**
- Increase `PATCH_SIZE` in `apply_farm_on_grazing.py` (default: 4096)
- Reduce `MAX_THREADS` if encountering memory issues
- Use windowed reading for very large rasters

**3. Parallel Execution**
```bash
# Process multiple counties in parallel using GNU parallel
parallel -j 4 python src/pipeline.py --config configs/{}.yaml ::: county1 county2 county3 county4
```

**4. Mosaic Outputs**
```bash
# Merge county-level grazing mosaics
gdal_merge.py -o statewide_grazing.tif -co COMPRESS=LZW -co TILED=YES \
    county1/grazing_with_farms.tif \
    county2/grazing_with_farms.tif \
    county3/grazing_with_farms.tif
```

## Configuration Details

### Threshold Selection

**Slope Threshold (`gentle_max_deg`):**
- **15°**: Standard for agricultural terrain
- **20°**: Accommodates hilly pastures
- **10°**: Strict flat terrain (crop-dominated regions)
- Basis: USDA NRCS slope classification

**NDVI Thresholds:**
- **Min (0.3)**: Separates sparse vegetation from bare soil
- **Max (0.7)**: Excludes dense forest/crops
- Typical grazing NDVI: 0.35-0.65
- Adjust for regional climate/vegetation type

**SAVI Thresholds:**
- **Min (0.2)**: Accounts for soil background in sparse cover
- **Max (0.6)**: Lower than NDVI due to soil adjustment
- Use SAVI in arid/semi-arid regions or early-season imagery

### Consensus Logic

Pixel classified as **grazing** if ALL conditions true:
```
NDVI_active = 1  AND
SAVI_active = 1  AND
CDL_active = 1   AND
Slope_gentle = 1
```

**CDL Active Class** (typical):
- Pasture/Hay: 176
- Grassland/Pasture: 181
- Other Hay/Non Alfalfa: 37
- Configure based on CDL legend for your region

### Farm Boundary Handling

**Three-Class System:**
- `0`: Background/no data
- `1`: Grazing (non-farm)
- `2` or `3`: Farm areas (configurable)

**Farm Enforcement:**
- Farm pixels override grazing classification
- Prevents misclassification of intensive agriculture as grazing
- Set `consensus.enforce_farm_as_class` to desired farm value

### Vectorization Parameters

**Connected Components:**
- `connectivity=2` (8-neighborhood): More permissive, connects diagonal pixels
- `connectivity=1` (4-neighborhood): Stricter, only orthogonal connections

**Size Filtering:**
- `min_pixels`: Removes salt-and-pepper noise
- `min_ha`: Ecological minimum mapping unit (MMU)
- `max_ha`: Separates grazing from large crop fields

**Simplification:**
- `simplify_tol=10.0m`: Balances geometry detail vs file size
- Increase for coarser outlines, decrease for fine detail
- Smoothing improves visual appearance but changes boundaries slightly

## Troubleshooting

### Rasterio/GDAL Errors

**"Cannot open dataset":**
```bash
# Verify file exists and is valid
gdalinfo /path/to/raster.tif

# Check CRS and bounds
rio info /path/to/raster.tif

# Test opening in Python
python -c "import rasterio; rasterio.open('/path/to/raster.tif')"
```

**Coordinate system mismatches:**
```bash
# Reproject to common CRS (e.g., UTM)
gdalwarp -t_srs EPSG:32610 input.tif output.tif

# Or use rasterio warp in Python (see resample.py)
```

### Memory Issues

**Out of Memory (OOM) during processing:**
```python
# Reduce PATCH_SIZE in apply_farm_on_grazing.py
PATCH_SIZE = 2048  # Instead of 4096

# Reduce MAX_THREADS
MAX_THREADS = 16  # Instead of 32

# Process subset area first
python src/consensus_mask.py --config configs/subset_config.yaml
```

### Vectorization Issues

**No polygons output:**
```bash
# Check raster has grazing pixels
rio hist --bins 10 data/mosaics/grazing_with_farms.tif

# Verify grazing value is correct
gdalinfo -stats data/mosaics/grazing_with_farms.tif

# Relax filtering thresholds
python src/farm_grazing_to_shp.py --min_ha 0.5 --min_pixels 50
```

**Self-intersecting polygons:**
- Caused by complex boundaries
- Increase `simplify_tol` parameter
- Script auto-applies `make_valid()` but may still occur

**Excessive polygon count:**
- Reduce noise with larger `min_pixels`
- Increase `min_ha` to merge small patches
- Check for data artifacts (edge effects, compression issues)

## Performance Optimization

### Multi-Threading

**Optimal Thread Count:**
```python
import multiprocessing as mp
optimal_threads = mp.cpu_count() - 2  # Leave headroom for system
```

**Per-Script Threading:**
- `mask_indices.py`: Uses `ProcessPoolExecutor` (CPU-bound)
- `consensus_mask.py`: Uses `ThreadPoolExecutor` (I/O-bound)
- `apply_farm_on_grazing.py`: Uses `ThreadPoolExecutor` with `MAX_THREADS=32`

### I/O Optimization

**Compression Settings:**
```python
profile.update(
    compress="lzw",      # Good compression, fast
    tiled=True,          # Enable tiled access
    blockxsize=512,      # Optimize for random access
    blockysize=512
)
```

**Alternative Compression:**
- `compress="deflate"`: Better compression, slower
- `compress="zstd"`: Best compression (GDAL 3.4+)
- `compress="none"`: Fastest I/O, large files

### Disk Space Management

**Intermediate File Cleanup:**
```bash
# Remove active masks after consensus
rm -rf data/indices/ndvi_active data/indices/savi_active

# Remove resampled ancillary after final mosaic
rm data/cdl/cdl_resampled.tif data/dem/slope_reclass_resampled.tif

# Remove patch directory after mosaic merge
rm -rf data/mosaics/_tmp_patches
```

### Troubleshooting Checklist

- [ ] All input files exist and are readable (`gdalinfo`)
- [ ] CRS matches across all datasets (`rio info --crs`)
- [ ] NDVI/SAVI tiles cover AOI extent
- [ ] Config paths are absolute or relative to script location
- [ ] Sufficient disk space for intermediate files
- [ ] Python dependencies installed (`pip list`)
- [ ] GDAL version ≥3.0 (`gdalinfo --version`)

---

## Acknowledgments

- **USDA NAIP Program**: High-resolution aerial imagery
- **Segmentation Models PyTorch**: Pre-built architectures
- **AWS SageMaker**: Scalable training/inference infrastructure
- **FDA Center for Food Safety**: Use case guidance

---

## 📧 Contact

**Map My Crop Team**  
📧 Email: info@mapmycrop.com  
🌐 Website: [mapmycrop.com](https://mapmycrop.com)

---
