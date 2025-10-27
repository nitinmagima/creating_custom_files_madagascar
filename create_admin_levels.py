#!/usr/bin/env python3
"""
Create Admin 0 and Admin 1 Shapefiles from Admin 2

This script processes Madagascar administrative boundary data to create
three separate shapefiles for different administrative levels:
- Admin 0: National boundaries (country level)
- Admin 1: Regional boundaries (province/region level)
- Admin 2: District boundaries (district level)

The script dissolves (merges) lower-level boundaries to create higher-level
boundaries, ensuring geometries are properly unified.

Requirements:
    - geopandas
    - zipfile (standard library)
    - tempfile (standard library)
    - pathlib (standard library)

Usage:
    python create_admin_levels.py

Input:
    SHP_ADM2_UPDATE.zip - Original admin 2 shapefile

Output:
    SHP_ADM2_UPDATE.zip - New zip file containing all three admin levels
    (overwrites the original file)
"""

import geopandas as gpd
import zipfile
import tempfile
import os
import shutil
from pathlib import Path

def main():
    """
    Main function to process shapefiles and create admin levels.
    
    Process:
    1. Extract the original admin 2 shapefile from the input zip
    2. Read the shapefile using GeoPandas
    3. Create admin 0 by dissolving all polygons into one national boundary
    4. Create admin 1 by dissolving polygons grouped by region code
    5. Create admin 2 by filtering columns from the original data
    6. Save all three shapefiles with consistent naming
    7. Package everything into a new zip file
    """
    # Input and output paths
    input_zip = "SHP_ADM2_UPDATE.zip"
    output_zip = "SHP_ADM2_UPDATE.zip"
    
    # Create temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        print("Extracting shapefile from zip...")
        # Extract the shapefile from zip
        with zipfile.ZipFile(input_zip, 'r') as zip_ref:
            zip_ref.extractall(temp_path)
        
        # Read the admin 2 shapefile
        shapefile_path = temp_path / "SHP_ADM2_UPDATE" / "mdg_bnd_adm2_dis_pam.shp"
        print(f"Reading shapefile: {shapefile_path}")
        gdf = gpd.read_file(shapefile_path)
        
        print(f"Original shapefile has {len(gdf)} features")
        print(f"Columns: {list(gdf.columns)}")
        
        # Create admin 0 (National) - dissolve by ADM0_PCODE
        # This merges all 120 district polygons into 1 national boundary
        print("\nCreating Admin 0 (National) shapefile...")
        adm0 = gdf.dissolve(by='ADM0_PCODE', aggfunc='first')
        # Reset index to make ADM0_PCODE a column again, then select fields
        adm0 = adm0.reset_index()
        adm0 = adm0[['ADM0_PCODE', 'ADM0_EN', 'geometry']]
        print(f"Admin 0 has {len(adm0)} feature(s)")
        
        # Create admin 1 (Regional) - dissolve by ADM1_PCODE
        # This merges district polygons that share the same region code
        print("\nCreating Admin 1 (Regional) shapefile...")
        adm1 = gdf.dissolve(by='ADM1_PCODE', aggfunc='first')
        # Reset index to make ADM1_PCODE a column again, then select fields
        adm1 = adm1.reset_index()
        adm1 = adm1[['ADM1_PCODE', 'ADM1_EN', 'ADM1_TYPE', 'geometry']]
        print(f"Admin 1 has {len(adm1)} feature(s)")
        
        # Create admin 2 (District) - keep original geometries but filter columns
        # This preserves all 120 district boundaries
        print("\nCreating Admin 2 (District) shapefile...")
        adm2 = gdf[['ADM2_PCODE', 'ADM2_EN', 'ADM2_TYPE', 'geometry']].copy()
        print(f"Admin 2 has {len(adm2)} feature(s)")
        
        # Save shapefiles to temporary directory
        print("\nSaving shapefiles...")
        adm0_path = temp_path / "mdg_adm0.shp"
        adm1_path = temp_path / "mdg_adm1.shp"
        adm2_path = temp_path / "mdg_adm2.shp"
        
        adm0.to_file(adm0_path)
        adm1.to_file(adm1_path)
        adm2.to_file(adm2_path)
        
        print(f"Saved Admin 0: {adm0_path}")
        print(f"Saved Admin 1: {adm1_path}")
        print(f"Saved Admin 2: {adm2_path}")
        
        # Create new zip file with all three shapefiles
        print(f"\nCreating new zip file: {output_zip}")
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            # Add all shapefile components for each admin level
            for admin_level in ['mdg_adm0', 'mdg_adm1', 'mdg_adm2']:
                for ext in ['.shp', '.shx', '.dbf', '.prj', '.cpg', '.sbn', '.sbx', '.shp.xml']:
                    file_path = temp_path / f"{admin_level}{ext}"
                    if file_path.exists():
                        zip_ref.write(file_path, file_path.name)
                        print(f"  Added: {file_path.name}")
        
        print(f"\nSuccessfully created {output_zip} with all three admin levels!")
        print("\nLayer names:")
        print("- Admin 0 (National): mdg_adm0")
        print("- Admin 1 (Regional): mdg_adm1") 
        print("- Admin 2 (District): mdg_adm2")

if __name__ == "__main__":
    main()
