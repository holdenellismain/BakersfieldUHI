# in your terminal run
# py -m pip install rasterio numpy re

import rasterio # for loading in geotiffs
import numpy as np # for raster calcs
import os # for accessing files from your device
import re # regular expressions for matching file name formats
from collections import defaultdict

# Set the path to your folder
folder_path = "C:/Users/fires/Downloads/LANDSAT/"

# Pattern to match the first date in the filename (ex: 20230905)
date_pattern = re.compile(r'_(\d{8})_')

# create a list of all filenames
files_list = []
for filename in os.listdir(folder_path):
    if filename.endswith('.TIF'):
        files_list.append(filename)

# create a nested structure
# format example:
# {"2013" : {
#       "20130907" : ["LT08_...B4.TIF", "LT08_...B5.TIF"]
#   }
# }
dates_dict = defaultdict(lambda: defaultdict(list))
for fname in files_list:
    match = re.search(r'_(\d{8})_', fname)
    if match:
        full_date = match.group(1)
        year = full_date[:4]
        day = full_date
        dates_dict[year][day].append(fname)

for year in dates_dict:
    # Create a folder for all the LST readings for each summer
    yearly_path = f'{folder_path}{year}'
    print(yearly_path)
    os.makedirs(yearly_path)
    
    profile = None
    # raster calculations for LANDSAT 8 (2013-2023)
    if int(year) > 2012:
        for day in dates_dict[year]:
            output_path = f"{yearly_path}/{day}_LST.tif"
            band4_path = next((f for f in dates_dict[year][day] if f.endswith("B4.TIF")), None)
            band5_path = next((f for f in dates_dict[year][day] if f.endswith("B5.TIF")), None)
            band10_path = next((f for f in dates_dict[year][day] if f.endswith("B10.TIF")), None)

            if not all([band4_path, band5_path, band10_path]):
                print(f"Warning: One or more bands missing for date {day}. Skipping...")
                continue  # skip iteration

            # Read rasters for all bands
            with rasterio.open(folder_path + band4_path) as b4, \
                rasterio.open(folder_path + band5_path) as b5, \
                rasterio.open(folder_path + band10_path) as b10:

                # Check they have the same shape and transform
                if (b4.shape != b5.shape or b4.shape != b10.shape or
                    b4.transform != b5.transform or b4.transform != b10.transform):
                    raise ValueError("Input rasters do not match in shape or georeferencing")

                # Read the raster data as arrays
                data4 = b4.read(1, masked=True).astype(np.float32) / 10000 # need to do this to avoid floating point divison errors due to large numbers
                data5 = b5.read(1, masked=True).astype(np.float32) / 10000
                data10 = b10.read(1, masked=True)

                # raster arithmetic
                toa10 = data10 * 0.000342 + 0.1 - 0.29
                bt = 1321.0789 / np.log((774.8853 / toa10)+1) - 273.15 
                ndvi = (data5 - data4) / (data4 + data5)
                property_min = np.min(ndvi)
                property_max = np.max(ndvi)
                pv = np.square((ndvi - property_min) / (property_max + property_min))
                emissivity = 0.004*pv + 0.986
                result = bt / (1+10.895*bt/14380*np.log(emissivity))

                # print warning if average temperature is unrealistic
                avg_temp = np.mean(result)
                if avg_temp > 60 or avg_temp < 10:
                    print(f'Date {day} has an average temperature of {avg_temp}')
                    continue # and don't write

                # set nodata value
                nodata_val = -9999
                result = np.where(
                    (data4 == b4.nodata) | (data5 == b5.nodata) | (data10 == b10.nodata),
                    nodata_val,
                    result
                )

                # Write output raster
                profile = b4.profile
                profile.update(dtype=rasterio.float32, nodata=nodata_val, count=1)

                with rasterio.open(output_path, "w", **profile) as dst:
                    dst.write(result.astype(rasterio.float32), 1)  
    
    # raster calculations for LANDSAT 5 (2003-2012)
    else:
        for day in dates_dict[year]:
            output_path = f"{yearly_path}/{day}_LST.tif"
            band6_path = next((f for f in dates_dict[year][day] if f.endswith("B6.TIF")), None)

            if not band6_path:
                print(f"Missing band 6. Skipping...")
                continue  # skip iteration

            # Read raster
            with rasterio.open(folder_path + band6_path) as b6:

                # convert the raster data to an array
                data6 = b6.read(1, masked=True)

                # raster arithmetic
                radiance =  ((15.303-1.238)/(255-1))*(data6-1)+1.238
                bt = 1260.56/np.log((607.76/radiance)+1)
                result = bt - 273.15

                # print warning if average temperature is unrealistic
                avg_temp = np.mean(result)
                if avg_temp > 60 or avg_temp < 10:
                    print(f'Date {day} has an average temperature of {avg_temp}')
                    continue # and don't write

                # set nodata value
                nodata_val = -9999
                result = np.where(data6 == b6.nodata, nodata_val, result)

                # Write output raster
                profile = b6.profile
                profile.update(dtype=rasterio.float32, nodata=nodata_val, count=1)

                with rasterio.open(output_path, "w", **profile) as dst:
                    dst.write(result.astype(rasterio.float32), 1)

print("Complete")