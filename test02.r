require(lidR) # Most of the LiDAR processing
require(rlas) # Necessary for writelax
require(rgdal) # Writing to shp or raster
require(tictoc) # for timing
require(sp) # A few spatial operations
require(concaveman) # For concave hulls
require(raster)

# Check versions
packageVersion("lidR")
packageVersion("rlas")
packageVersion("rgdal")
packageVersion("tictoc")
packageVersion("sp")
packageVersion("concaveman")
packageVersion("raster")