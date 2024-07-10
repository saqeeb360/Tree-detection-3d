require(lidR) # Most of the LiDAR processing
require(rlas) # Necessary for writelax
require(rgdal) # Writing to shp or raster
require(tictoc) # for timing
require(sp) # A few spatial operations
require(concaveman) # For concave hulls
require(raster)

# Base directory containing subdirectories with LAS files
base_dir <- "./test_data"
outws <- "./test_results"

# List all subdirectories
subdirs <- list.dirs(base_dir, full.names = TRUE, recursive = TRUE)

# Function to process LAS files
process_las_files <- function(files, outws) {
  lasfilternoise <- function(las, sensitivity){
    p95 <- grid_metrics(las, ~quantile(Z, probs = 0.95), 10)
    las <- merge_spatial(las, p95, "p95")
    las <- filter_poi(las, Z < p95 * sensitivity)
    las$p95 <- NULL
    return(las)
  }

  normalize <- function(las_denoised, f){
    las_dtm <- readLAS(f)
    dtm <- rasterize_terrain(las_dtm, algorithm = knnidw(k = 8, p = 2))
    las_normalized <- normalize_height(las_denoised, dtm)
    return(las_normalized)
  }

  chm <- function(las_normalized){
    algo <- pitfree(c(0,2,5,10,15), c(3,1.5), subcircle = 0.2)
    chm <- grid_canopy(las_normalized, 0.5, algo)
    ker <- matrix(1, 3, 3)
    chm_s <- focal(chm, w = ker, fun = median)
    return(chm_s)
  }

  treeseg <- function(canopy_height_model, las_normalized){
    algo <- watershed(canopy_height_model, th = 4)
    las_watershed <- segment_trees(las_normalized, algo)
    trees <- filter_poi(las_watershed, !is.na(treeID))
    return(trees)
  }

  tree_hull_polys <- function(las_trees){
    hulls <- delineate_crowns(las_trees, type = "concave", concavity = 2, func = .stdmetrics)
    return(hulls)
  }

  counter <- 1
  for (f in files) {
    tic(paste(basename(f), "processed"))
    print(paste("Reading", basename(f), "|", counter, "of", length(files)))
    las <- readLAS(f, filter = "-keep_class 0 2 6")
    writelax(f)
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
    writeOGR(obj = final_tree_hulls, dsn = outws, layer = paste(tools::file_path_sans_ext(basename(f)), "-r", sep = ""), driver = "ESRI Shapefile")
    toc()
    counter <- counter + 1
    rm(las, las_denoised, las_normalized, canopy_height_model, las_trees, final_tree_hulls)
    print("On to the next las...")
  }

  print("Processing complete.")
}

# Process LAS files in each subdirectory
for (subdir in subdirs) {
  files <- list.files(path = subdir, pattern = "\\.las$", full.names = TRUE, recursive = FALSE)
  if (length(files) > 0) {
    print(paste("Processing files in directory:", subdir))
    process_las_files(files, outws)
  }
}
