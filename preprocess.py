from utils import *

print("Starting tree count...")

width = 4
delta = 2
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
                print(f'Working on {filename}')
                file_path = os.path.join(folder_path, filename)
                try:
                    if not os.path.isfile(file_path):
                        print(f"File {file_path} does not exist.")
                        continue

                    filename_without_ext, _ = os.path.splitext(filename)
                    temp_folder_path = os.path.join(folder_path, 'temp')
                    os.makedirs(temp_folder_path, exist_ok=True)
                    
                    allBoxes_path = os.path.join(temp_folder_path, f'{filename_without_ext}_allBoxes.npy')
                    innerBoxes_path = os.path.join(temp_folder_path, f'{filename_without_ext}_innerBoxes.npy')
                    outerBoxes_path = os.path.join(temp_folder_path, f'{filename_without_ext}_outerBoxes.npy')

                    if os.path.exists(allBoxes_path) and os.path.exists(innerBoxes_path) and os.path.exists(outerBoxes_path):
                        print(f"Skipping {filename} as the output files already exist.")
                        continue

                    new_las = laspy.read(file_path)
                    xmax, xmin = np.max(new_las.x), np.min(new_las.x)
                    ymax, ymin = np.max(new_las.y), np.min(new_las.y)

                    x_range = int((xmax - xmin) // delta)
                    y_range = int((ymax - ymin) // delta)
                    innerBoxes = np.ones((x_range, y_range)) * -11
                    outerBoxes = np.ones((x_range, y_range)) * -10
                    allBoxes = np.ones((x_range, y_range)) * -10

                    for j in range(0, y_range):
                        y_start = ymin + j * delta
                        y_end = y_start + width
                        las_slice_y = new_las[new_las.y >= y_start]
                        las_slice_y = las_slice_y[las_slice_y.y <= y_end]
                        if las_slice_y.x.shape[0] > 0:
                            for i in range(0, x_range):
                                x_start = xmin + i * delta
                                x_end = x_start + width
                                las_slice_x = las_slice_y[las_slice_y.x >= x_start]
                                las_slice_x = las_slice_x[las_slice_x.x <= x_end]
                                points_x = las_slice_x.x.shape[0]
                                if points_x > 0:
                                    box_mean = np.mean(las_slice_x.z)
                                    allBoxes[i][j] = box_mean

                                    # inner box
                                    innerX_start = x_start + width / 4
                                    innerX_end = x_end - width / 4
                                    innerY_start = y_start + width / 4
                                    innerY_end = y_end - width / 4

                                    las_inner = las_slice_x[las_slice_x.x >= innerX_start]
                                    las_inner = las_inner[las_inner.x <= innerX_end]
                                    las_inner = las_inner[las_inner.y >= innerY_start]
                                    las_inner = las_inner[las_inner.y <= innerY_end]
                                    points_inner = las_inner.x.shape[0]
                                    if points_inner > 0:
                                        innerBoxmean = np.mean(las_inner.z)
                                        innerBoxes[i][j] = innerBoxmean
                                        outerBoxmean = ((box_mean * points_x) - (innerBoxmean * points_inner)) / (points_x - points_inner)
                                        outerBoxes[i][j] = outerBoxmean
                        print(f"Patch {j} of {y_range} completed in {filename}")

                    print("Saving the variables...")
                    np.save(allBoxes_path, allBoxes)
                    np.save(innerBoxes_path, innerBoxes)
                    np.save(outerBoxes_path, outerBoxes)

                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
    except Exception as e:
        print(f"Error processing folder {folder}: {e}")

print("Completed preprocess.")
