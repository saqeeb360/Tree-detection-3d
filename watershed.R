options(warn = -1)

suppressPackageStartupMessages({
  require(lidR) # Most of the LiDAR processing
  require(rlas) # Necessary for writelax
  require(rgdal) # Writing to shp or raster
  # require(tictoc) # for timing
  require(sp) # A few spatial operations
  # require(concaveman) # For concave hulls
  require(raster)
  # require(EBImage)
})

base_dir <- "./test_data"
out_base_dir <- "./test_results"

# List all subdirectories
subdirs <- list.dirs(base_dir, full.names = TRUE, recursive = TRUE)
subdirs <- subdirs[subdirs != base_dir]
# subdirs <- c("./test_data/121_pcl")

print(subdirs)

lasfilternoise <- function(las, sensitivity){
  tryCatch({
    p95 <- grid_metrics(las, ~quantile(Z, probs = 0.95), 10)
    las <- merge_spatial(las, p95, "p95")
    las <- filter_poi(las, Z < p95*sensitivity)
    las$p95 <- NULL
    return(las)
  }, error = function(e) {
    print(paste("Error in lasfilternoise:", e))
    return(NULL)
  })
}

normalize <- function(las_denoised, f){
  tryCatch({
    las_dtm <- readLAS(f)
    dtm <- rasterize_terrain(las_dtm, algorithm = knnidw(k = 8, p = 2))
    las_normalized <- normalize_height(las_denoised, dtm)
    return(las_normalized)
  }, error = function(e) {
    print(paste("Error in normalize:", e))
    return(NULL)
  })
}

chm <- function(las_normalized){
  tryCatch({
    algo <- pitfree(c(0,2,5,10,15), c(3,1.5), subcircle = 0.2)
    chm  <- grid_canopy(las_normalized, 0.5, algo)
    
    # Smooth the CHM with double pass median filter
    ker <- matrix(1,3,3)
    chm_s <- focal(chm, w = ker, fun = median)
    return(chm_s)
  }, error = function(e) {
    print(paste("Error in chm:", e))
    return(NULL)
  })
}

treeseg <- function(canopy_height_model, las_normalized){
  tryCatch({
    algo <- watershed(canopy_height_model, th_tree = 4)
    las_watershed  <- segment_trees(las_normalized, algo)
    
    # remove points that are not assigned to a tree
    trees <- filter_poi(las_watershed, !is.na(treeID))
    return(trees)
  }, error = function(e) {
    print(paste("Error in treeseg:", e))
    return(NULL)
  })
}

tree_hull_polys <- function(las_trees){
  tryCatch({
    hulls  <- delineate_crowns(las_trees, type = "concave", concavity = 2, func = .stdmetrics)
    return(hulls)
  }, error = function(e) {
    print(paste("Error in tree_hull_polys:", e))
    return(NULL)
  })
}

process_las_files <- function(files, out_dir) {
  counter <- 1
  for (f in files) {
    tryCatch({
      subdir_name <- tools::file_path_sans_ext(basename(f))
      out_subdir <- file.path(out_dir, subdir_name, "r_results")
      shp_name <- paste0(subdir_name, "_r_output.shp")
      output_shp_path <- file.path(out_subdir, shp_name)
      
      if (file.exists(output_shp_path)) {
        print(paste("Shapefile already exists, skipping:", output_shp_path))
        next
      }
      
      print(paste("Reading ", basename(f), " | ", counter, " of ", length(files)))
      las <- readLAS(f, filter="-keep_class 0 2 6") # read las and keep class 2 (bare earth) and 5 (trees) classes
      writelax(f) # Create a spatial index file (.lax) to speed up processing
      
      print("Filtering noise...")
      las_denoised <- lasfilternoise(las, sensitivity = 1.2)
      if (is.null(las_denoised)) next

      print("Normalizing...")
      las_normalized <- normalize(las_denoised, f)
      if (is.null(las_normalized)) next

      print("Generating CHM...")
      canopy_height_model <- chm(las_normalized)
      if (is.null(canopy_height_model)) next

      print("Tree Segmentation...")
      las_trees <- treeseg(canopy_height_model, las_normalized)
      if (is.null(las_trees)) next

      print("Generating Tree hulls...")
      final_tree_hulls <- tree_hull_polys(las_trees)
      if (is.null(final_tree_hulls)) next

      if (!file.exists(out_subdir)) {
        dir.create(out_subdir, recursive = TRUE)
      }
      
      print("Writing to shp...")
      writeOGR(obj = final_tree_hulls, dsn = out_subdir, layer = tools::file_path_sans_ext(shp_name), driver = "ESRI Shapefile")
      counter <- counter + 1
      rm(las, las_denoised, las_normalized, canopy_height_model, las_trees, final_tree_hulls) # Remove all of the stored objects prior to the next iteration
      print("On to the next las...")
    }, error = function(e) {
      print(paste("Error processing file", f, ":", e))
      next
    })
  }
}

for (subdir in subdirs) {
  tryCatch({
    relative_subdir <- sub(paste0("^", base_dir, "/?"), "", subdir)
    out_subdir <- file.path(out_base_dir, relative_subdir)
    dir.create(out_subdir, recursive = TRUE, showWarnings = FALSE)
    files <- list.files(path = subdir, pattern = "\\.las$", full.names = TRUE, recursive = FALSE)
    if (length(files) > 0) {
      print(paste("Processing files in directory:", subdir))
      process_las_files(files, out_subdir)
    }
  }, error = function(e) {
    print(paste("Error processing subdir", subdir, ":", e))
    next
  })
}


print("Processing complete.")