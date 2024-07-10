from utils import *

width = 4
delta = 2

print("Getting Files...")
subdirs = os.listdir(TESTDATA_DIR)
# subdirs = ['121_pcl']

for folder in subdirs:
    try:
        folder_path = os.path.join(TESTDATA_DIR, folder)
        if not os.path.isdir(folder_path):
            print(f"Skipping {folder_path} as it is not a directory.")
            continue
        folder_dir = os.listdir(folder_path)
        for filename in folder_dir:
            if filename.endswith(".las"):
                try:
                    print(f'\nWorking on {filename}')
                    file_path = os.path.join(folder_path, filename)
                    # print(file_path)
                    filename_without_ext, _ = os.path.splitext(filename)

                    new_las = laspy.read(file_path)
                    xmax, xmin = np.max(new_las.x), np.min(new_las.x)
                    ymax, ymin = np.max(new_las.y), np.min(new_las.y)

                    # Check if the .npy files already exist
                    temp_dir = os.path.join(folder_path, 'temp')
                    allBoxes_path = os.path.join(temp_dir, f'{filename_without_ext}_allBoxes.npy')
                    innerBoxes_path = os.path.join(temp_dir, f'{filename_without_ext}_innerBoxes.npy')
                    outerBoxes_path = os.path.join(temp_dir, f'{filename_without_ext}_outerBoxes.npy')

                    if not (os.path.exists(allBoxes_path) and os.path.exists(innerBoxes_path) and os.path.exists(outerBoxes_path)):
                        print(f"Skipping {filename} as the required .npy files are missing.")
                        continue

                    # Define the output shapefile path
                    directory = os.path.join(RESULT_FOLDER, folder, filename_without_ext, "py_results")
                    os.makedirs(directory, exist_ok=True)

                    output_shapefile = os.path.join(directory, f"{filename_without_ext}_py_output.shp")

                    # Check if the output shapefile already exists
                    if os.path.exists(output_shapefile):
                        print(f"Skipping {filename} as the output shapefile already exists.")
                        continue

                    allBoxes = np.load(allBoxes_path)
                    innerBoxes = np.load(innerBoxes_path)
                    outerBoxes = np.load(outerBoxes_path)

                    t5 = innerBoxes - allBoxes
                    t6 = np.where(t5 < -0.1, -120, t5)
                    t6 = np.where(t6 > 0.01, 120, t6)
                    t6 = t6 + 120
                    t6 = np.where(t6 < 125, 0, t6)

                    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
                    res = cv2.morphologyEx(t6, cv2.MORPH_OPEN, kernel)
                    res = np.where(res > 100, 240, res)

                    maxShape_x, maxShape_y = res.shape
                    t1, t2 = np.meshgrid(np.linspace(xmin, xmax, maxShape_x), np.linspace(ymin, ymax, maxShape_y))

                    # All presumable tree points
                    geometry = []

                    res = np.array(res, dtype=np.uint8)
                    _, labels, stats, centroids = cv2.connectedComponentsWithStats(res, connectivity=8)
                    cntBoxes = 0
                    for label in range(1, len(stats)):
                        x, y, width, height, area = stats[label]
                        if area > 5 and area < 100:  # Exclude small noise regions
                            cv2.rectangle(res, (x, y), (x + width, y + height), 200, 1)
                            cntBoxes += 1
                            shapex = t1[x + round(width / 2), y + round(height / 2)]
                            shapey = t2[x + round(width / 2), y + round(height / 2)]
                            geometry.append(Point(shapex, shapey, 270))

                    crs = new_las.header.parse_crs()  # Set the correct CRS
                    gdf = gpd.GeoDataFrame(geometry=geometry, crs=crs)

                    # Save the GeoDataFrame to a shapefile
                    gdf.to_file(output_shapefile, driver="ESRI Shapefile")

                    print(f'Total trees in {filename} is {cntBoxes}')

                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
                    continue
    except Exception as e:
        print(f"Error processing folder {folder}: {e}")

print("\nCompleted tree generation.")