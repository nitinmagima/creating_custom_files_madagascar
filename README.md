# Madagascar Administrative Boundaries - Shapefile Processing

This repository contains tools to process Madagascar administrative boundary data for use in web mapping applications.

## Overview

The original shapefile contains Madagascar's administrative level 2 (district) boundaries. This script processes that data to create three separate shapefiles representing different administrative hierarchies:

- **Admin 0 (National)**: Country-level boundary for Madagascar
- **Admin 1 (Regional)**: Regional/province-level boundaries
- **Admin 2 (District)**: District-level boundaries (original data)

## What the Script Does

### Process Flow

1. **Reads** the original admin 2 shapefile from `SHP_ADM2_UPDATE.zip`
2. **Dissolves** (merges) district polygons to create higher-level boundaries:
   - All 120 districts → 1 national boundary (Admin 0)
   - Districts grouped by region → Multiple regional boundaries (Admin 1)
   - Original districts preserved (Admin 2)
3. **Filters** attributes to keep only relevant fields for each admin level
4. **Saves** all three shapefiles with consistent naming
5. **Packages** everything into a new zip file

### Dissolving Explained

**Dissolving** is a GIS operation that merges adjacent polygons based on a shared attribute. For example:
- To create Admin 1, all districts with `ADM1_PCODE = "MG23"` are merged into one regional polygon
- Shared boundaries between districts disappear, creating a unified regional boundary
- This maintains geographic accuracy while reducing complexity

## Files

### Input
- `SHP_ADM2_UPDATE.zip` - Original shapefile containing 120 district boundaries with the following structure:
  ```
  SHP_ADM2_UPDATE/
    └── mdg_bnd_adm2_dis_pam.* (shapefile components)
  ```

### Output
- `SHP_ADM2_UPDATE.zip` - New zip file (replaces original) containing:
  ```
  mdg_adm0.* (National boundary shapefile)
  mdg_adm1.* (Regional boundaries shapefile)
  mdg_adm2.* (District boundaries shapefile)
  ```

### Script
- `create_admin_levels.py` - Python script that performs the processing

## Data Structure

### Admin 0 (National) - Layer: `mdg_adm0`
- **Features**: 1 (entire country)
- **Fields**:
  - `ADM0_PCODE`: Country P-code (e.g., "MG")
  - `ADM0_EN`: Country name in English (e.g., "Madagascar")
  - `geometry`: Polygon geometry

### Admin 1 (Regional) - Layer: `mdg_adm1`
- **Features**: ~22-23 (regions/provinces)
- **Fields**:
  - `ADM1_PCODE`: Region P-code (e.g., "MG23")
  - `ADM1_EN`: Region name in English (e.g., "Androy")
  - `ADM1_TYPE`: Administrative type (e.g., "Region")
  - `geometry`: Polygon geometry

### Admin 2 (District) - Layer: `mdg_adm2`
- **Features**: 120 (districts)
- **Fields**:
  - `ADM2_PCODE`: District P-code (e.g., "MG2301")
  - `ADM2_EN`: District name in English (e.g., "Ambovombe Androy")
  - `ADM2_TYPE`: Administrative type (e.g., "District")
  - `geometry`: Polygon geometry

## Requirements

### Python Dependencies
```bash
pip install geopandas
```

GeoPandas will automatically install required dependencies:
- pandas
- shapely
- fiona
- pyproj

### System Requirements
- Python 3.7+
- GDAL/OGR (usually installed with GeoPandas)

## Usage

### Running the Script

1. Ensure `SHP_ADM2_UPDATE.zip` is in the same directory as the script
2. Run the script:
   ```bash
   python create_admin_levels.py
   ```
3. The script will:
   - Display progress information
   - Show feature counts for each admin level
   - Create a new `SHP_ADM2_UPDATE.zip` with all three admin levels

### Expected Output
```
Extracting shapefile from zip...
Reading shapefile: /tmp/.../mdg_bnd_adm2_dis_pam.shp
Original shapefile has 120 features
Columns: ['ADM0_PCODE', 'ADM0_EN', 'ADM1_PCODE', 'ADM1_EN', 'ADM1_TYPE', ...]

Creating Admin 0 (National) shapefile...
Admin 0 has 1 feature(s)

Creating Admin 1 (Regional) shapefile...
Admin 1 has XX feature(s)

Creating Admin 2 (District) shapefile...
Admin 2 has 120 feature(s)

Saving shapefiles...
Creating new zip file: SHP_ADM2_UPDATE.zip
Successfully created SHP_ADM2_UPDATE.zip with all three admin levels!
```

## Integration with Flask Map Application

### YAML Configuration

The output shapefiles are designed to work with Fiona package in a Flask-based mapping application. Update your YAML configuration as follows:

```yaml
shapes:
    - name: National
      file: madagascar/shapes/2025-10/SHP_ADM2_UPDATE.zip
      layer: mdg_adm0
      key_field: ADM0_PCODE
      label_field: ADM0_EN

    - name: Regional
      file: madagascar/shapes/2025-10/SHP_ADM2_UPDATE.zip
      layer: mdg_adm1
      key_field: ADM1_PCODE
      label_field: ADM1_EN

    - name: District
      file: madagascar/shapes/2025-10/SHP_ADM2_UPDATE.zip
      layer: mdg_adm2
      key_field: ADM2_PCODE
      label_field: ADM2_EN
```

### Reading with Fiona

```python
import fiona

# Read National boundaries
with fiona.open('zip://SHP_ADM2_UPDATE.zip!mdg_adm0.shp') as src:
    for feature in src:
        pcode = feature['properties']['ADM0_PCODE']
        name = feature['properties']['ADM0_EN']
        geometry = feature['geometry']

# Read Regional boundaries
with fiona.open('zip://SHP_ADM2_UPDATE.zip!mdg_adm1.shp') as src:
    for feature in src:
        pcode = feature['properties']['ADM1_PCODE']
        name = feature['properties']['ADM1_EN']
        geometry = feature['geometry']

# Read District boundaries
with fiona.open('zip://SHP_ADM2_UPDATE.zip!mdg_adm2.shp') as src:
    for feature in src:
        pcode = feature['properties']['ADM2_PCODE']
        name = feature['properties']['ADM2_EN']
        geometry = feature['geometry']
```

## Coordinate System

All shapefiles use **WGS 84 / World Mercator (EPSG:3395)**:
- Projected coordinate system in meters
- Suitable for web mapping applications
- Can be reprojected to WGS 84 (EPSG:4326) for Leaflet/web maps if needed

## Data Source

- **Source**: PAM (World Food Programme)
- **Last Updated**: August 20, 2025
- **Original Feature Count**: 120 districts
- **Coverage**: Madagascar administrative boundaries

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'geopandas'**
   - Solution: `pip install geopandas`

2. **GDAL/OGR not found**
   - Solution: Install GDAL before GeoPandas
   - macOS: `brew install gdal`
   - Ubuntu: `sudo apt-get install gdal-bin libgdal-dev`
   - Windows: Use conda: `conda install geopandas`

3. **Memory issues with large shapefiles**
   - The script uses temporary directories to minimize memory usage
   - Dissolving operations may require significant RAM for complex geometries

4. **Zip file already exists**
   - The script overwrites the original `SHP_ADM2_UPDATE.zip`
   - Back up the original file if you want to preserve it

## Notes

- The dissolve operation uses `aggfunc='first'` which takes the first occurrence of attribute values when merging
- Field filtering ensures clean, minimal attribute tables for each admin level
- All shapefile components (.shp, .shx, .dbf, .prj, .cpg) are included in the output
- The script cleans up temporary files automatically

## License

Data provided by PAM (World Food Programme). Please check with the data provider for licensing and usage restrictions.

## Support

For issues or questions about the script, please refer to the code comments in `create_admin_levels.py`.
