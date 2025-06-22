# BakersfieldUHI

## Goals

In this group project from my GEOG 176C class, we studied the Bakersfield Urban Heat Island (UHI). More specificially, we wanted to study how its magnitude changed over time and what types of development caused it.

## Skills / Tools Used

- ArcGIS Model Builder
- Python
- Linear Regression

## Steps
### Data Collection / Processing
1. Download [NLCD](https://earthexplorer.usgs.gov/), [monthly air temperature](https://prism.oregonstate.edu/recent/), [urban boundaries](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html), [DEM](https://geodat-kernco.opendata.arcgis.com/datasets/efdd30f982bc40b2a398d559dfee44fc) and [LANDSAT images](https://earthexplorer.usgs.gov/)
2. Define rural boundary for 2010 and 2020 census using a 15km buffer (recommendation of Wang et. al.) and excluding areas over 305m in elevation.
3. Average June, July, August, and September monthly air temperatures to get a single temperature raster for each year using ArcGIS.
4. Estimate land surface temperature following the procedure of Avdan and Jovanovska (2016) using [remote.py](remote.py) and then average these images in ArcGIS.

The model for averaging the rasters is shown below
![averagingmodel](https://github.com/user-attachments/assets/f709bd4d-caa7-4cd7-ac62-c6c9270c4e25)

### Measuring Change

The average temperature for each year within the rural area was subtracted for the average tempeature within the urban area, for both air and land measurments.

### Measuring Cause

OLS regression was implemented for with air temperature and land surface temperature as the response variable using this model:

![regressionmodel](https://github.com/user-attachments/assets/2370087c-f54e-4f9e-943c-5dcb3e6f01c3)

A few notes:
- The land cover raster was resampled using majority resampling to match the grid of the air temperature
- Sample points for the regression were taken using a 50x50 grid within the study area for LST and a 14x16 grid for air temperature
- Land cover types were dummy encoded with the natural grassland as the reference class.

## Results

![magnitude](https://github.com/user-attachments/assets/128fb135-5bec-40e7-a3c4-4a04d7d35409)

There seems to be no trend in the annual change in the magnitude of the heat island.

![LST](https://github.com/user-attachments/assets/c1c41db4-63ae-445d-ae09-5d2e1d2c69f6)
![regressiontable](https://github.com/user-attachments/assets/1dee43bb-9390-419f-b6ba-b67d574cdcfa)

Suprisingly, the natural grassland was hotter than the urban area and agricultural land was far cooler due to irrigation. This is likely due to the effects of irrigated surfaces in the city such as lawns and golf courses offsetting the effect of paved surfaces.

Full results and discussion can be found in our [poster](ResearchPoster.pdf)

## Sources
- Avdan, U., Jovanovska, G., & Tian, G. (2016). Algorithm for Automated Mapping of Land Surface Temperature Using LANDSAT 8 Satellite Data. Journal of Sensors, 2016(2016), 1–8. https://doi.org/10.1155/2016/1480307
- PRISM Group, Oregon State University, https://prism.oregonstate.edu, data created 4 Feb 2014, accessed 25 April  2025.
- Ratcliffe, M. (2022, December 21). Redefining urban areas following the 2020 census. Census.gov.https://www.census.gov/newsroom/blogs/random-samplings/2022/12/redefining-urban-areas-following-2020-census.html
- U.S. Geological Survey, 2025, EarthExplorer, accessed 18 April  2025 at URL https://earthexplorer.usgs.gov/
- Wang, Z., Fan, C., Zhao, Q., & Myint, S. W. (2020). “A Geographically Weighted Regression Approach to Understanding Urbanization Impacts on Urban Warming and Cooling: A Case Study of Las Vegas.” Remote Sensing, 12(2), 222. https://doi.org/10.3390/rs12020222
