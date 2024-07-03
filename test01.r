require(lidR) # Most of the LiDAR processing
require(rlas) # Necessary for writelax
require(rgdal) # Writing to shp or raster
require(tictoc) # for timing
require(sp) # A few spatial operations
require(concaveman) # For concave hulls
require(raster)

# Input and output paths
files <- list.files(path="/Users/saqeeb/Desktop/IITK/Courses/My Thesis/Kota/Results Final/P3-2c/", pattern="*.las", full.names=TRUE, recursive=FALSE)
outws <- "/Users/saqeeb/Desktop/IITK/Courses/My Thesis/Kota/Results Final/P3-2c/rCode"

lasfilternoise <- function(las, sensitivity){
  # Create a function to filter noise from point cloud
  # https://cran.r-project.org/web/packages/lidR/vignettes/lidR-catalog-apply-examples.html
  p95 <- grid_metrics(las, ~quantile(Z, probs = 0.95), 10)
  las <- merge_spatial(las, p95, "p95")
  las <- filter_poi(las, Z < p95*sensitivity)
  las$p95 <- NULL
  return(las)
}

normalize <- function(las_denoised, f){
  # Normalize data 
  las_dtm <- readLAS(f)
  dtm <- rasterize_terrain(las_dtm, algorithm = knnidw(k = 8, p = 2))
  las_normalized <- normalize_height(las_denoised, dtm)
  return(las_normalized)
}

chm <- function(las_normalized){
  # Generate a normalized canopy height model ~198 seconds
  # https://github.com/Jean-Romain/lidR/wiki/Segment-individual-trees-and-compute-metrics
  algo <- pitfree(c(0,2,5,10,15), c(3,1.5), subcircle = 0.2)
  chm  <- grid_canopy(las_normalized, 0.5, algo)
  
  # Smooth the CHM with double pass median filter
  ker <- matrix(1,3,3)
  chm_s <- focal(chm, w = ker, fun = median)
  return(chm_s)
}

treeseg <- function(canopy_height_model, las_normalized){
  # tree segmentation
  algo <- watershed(canopy_height_model, th = 4)
  las_watershed  <- segment_trees(las_normalized, algo)
  
  # remove points that are not assigned to a tree
  trees <- filter_poi(las_watershed, !is.na(treeID))
  return(trees)
}

tree_hull_polys <- function(las_trees){
  # Generate polygon tree canopies
  hulls  <- delineate_crowns(las_trees, type = "concave", concavity = 2, func = .stdmetrics)
  #hulls_sub <- subset(hulls, area <1200 & area > 3) # Not needed with new pitfree algorithm in CHM
  return(hulls)
}

counter <- 1

for (f in files) {
  tic(paste(basename(f), "processed"))
  # Read in las file and write index file
  print(paste("Reading ", basename(f), " | ", counter, " of ", length(files)))
  las <- readLAS(f, filter="-keep_class 0 2 6") # read las and keep class 2 (bare earth) and 5 (trees) classes
  #las <- filter_poi(las, G < 35000)
  writelax(f) # Create a spatial index file (.lax) to speed up processing
  
  print("Filtering noise...")
  las_denoised <- lasfilternoise(las, sensitivity = 1.2)
  print("Normalizing...")
  las_normalized <- normalize(las_denoised, f)
  print("Generating CHM...")
  canopy_height_model <- chm(las_normalized)
  print("Tree Segmentation...")
  las_trees <- treeseg(canopy_height_model, las_normalized)
  print("Generating Tree hulls...")
  final_tree_hulls <- tree_hull_polys(las_trees)
  print("Writing to shp...")
  # Write to shapefile
  writeOGR(obj = final_tree_hulls, dsn = outws, layer = paste(tools::file_path_sans_ext(basename(f)), "-r",sep=""), driver = "ESRI Shapefile")
  toc()
  counter <- counter + 1
  rm(las, las_denoised, las_normalized, canopy_height_model, las_trees, final_tree_hulls) # Remove all of the stored objects prior to the next iteration (Comment out if you want to inspect the output)
  print("On to the next las...")
}

print("Processing complete.")

# writeRaster(canopy_height_model,"/Users/saqeeb/Downloads/My Thesis/Kota/R analysis/chm_SJER.tiff",format = "GTiff",overwrite = TRUE)



                          