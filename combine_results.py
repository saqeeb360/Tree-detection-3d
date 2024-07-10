from utils import *

# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
# pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', None)

print("Starting to combine results...")
subdirs = os.listdir(RESULT_FOLDER)
# subdirs = ['121_pcl']
print(subdirs)

for folder in subdirs:
    try:
        print("\nProcessing folder:", folder)
        folder_path = os.path.join(RESULT_FOLDER, folder)
        if not os.path.isdir(folder_path):
            print(f"Skipping {folder} as it is not a folder.")
            continue
        subfolder = os.listdir(folder_path)
        if len(subfolder) == 0:
            print(f"Skipping {folder} as it is empty.")

        for eachsubfolder in subfolder:
            try:
                eachsubfolderPath = os.path.join(folder_path, eachsubfolder)
                print("Processing subfolder:", eachsubfolderPath)
                
                # Combine results
                py_shapefilePath = os.path.join(eachsubfolderPath, "py_results", f"{eachsubfolder}_py_output.shp")
                r_shapefilePath = os.path.join(eachsubfolderPath, "r_results", f"{eachsubfolder}_r_output.shp")

                if not (os.path.exists(py_shapefilePath) and os.path.exists(r_shapefilePath)):
                    print(f"Skipping {eachsubfolderPath} as required shapefiles are missing.")
                    continue

                point_shapefile = gpd.read_file(py_shapefilePath)
                polygon_shapefile = gpd.read_file(r_shapefilePath)

                combined_shapefile = polygon_shapefile.sjoin(point_shapefile, how="inner", predicate='contains')
                combined_shapefile = combined_shapefile[~combined_shapefile.index.duplicated(keep='first')]
                combined_shapefile = combined_shapefile.drop(['index_right', 'FID'], axis=1)
                combined_shapefile = combined_shapefile.reset_index(drop=True)

                point_crs = point_shapefile.crs
                polygon_crs = polygon_shapefile.crs

                if point_crs is not None:
                    crs = point_crs
                else:
                    crs = None

                gdf = gpd.GeoDataFrame(geometry=combined_shapefile['geometry'], crs=crs)

                # Define the output shapefile path
                outputFolder = os.path.join(eachsubfolderPath, "combined_results")
                os.makedirs(outputFolder, exist_ok=True)
                output_shapefile = os.path.join(outputFolder, f"{eachsubfolder}_final_output.shp")

                # Save the GeoDataFrame to a shapefile
                gdf.to_file(output_shapefile, driver="ESRI Shapefile")

            except Exception as e:
                print(f"Error processing subfolder {eachsubfolder}: {e}")
                continue
    except Exception as e:
        print(f"Error processing folder {folder}: {e}")
        continue

print("Completed...")