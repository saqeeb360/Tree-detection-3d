from utils import *

print("Starting tree count...")

width = 4
delta = 2
# list_of_all_folder = os.listdir(TESTDATA_DIR)
list_of_all_folder = ['P3-1']


for folder in list_of_all_folder:
    folder_path = os.path.join(TESTDATA_DIR, folder)
    folder_dir = os.listdir(folder_path)
    for filename in folder_dir:
        if filename.endswith(".las"):
            print(f'Working on {filename}')
            file_path = os.path.join(folder_path,filename)
            print(file_path)
            filename_without_ext, _ = os.path.splitext(filename)
            
            new_las=laspy.read(file_path)
            xmax, xmin = np.max(new_las.x) , np.min(new_las.x)
            ymax, ymin = np.max(new_las.y) , np.min(new_las.y)

            x_range = int((xmax-xmin)//delta)
            y_range = int((ymax-ymin)//delta)
            innerBoxes = np.ones((x_range, y_range))*-11
            outerBoxes = np.ones((x_range, y_range))*-10
            allBoxes = np.ones((x_range, y_range))*-10

            for j in range(0,y_range):
                y_start = ymin + j*delta
                y_end = y_start + width
                las_slice_y = new_las[new_las.y >= y_start]
                las_slice_y = las_slice_y[las_slice_y.y <= y_end]
                if las_slice_y.x.shape[0] > 0:
                    for i in range(0,x_range):
                        x_start = xmin + i*delta
                        # print(i,j, x_start)
                        x_end = x_start + width
                        las_slice_x = las_slice_y[las_slice_y.x >= x_start]
                        las_slice_x = las_slice_x[las_slice_x.x <= x_end]
                        points_x = las_slice_x.x.shape[0]
                        if points_x > 0:
                            # print(i,j,np.mean(las_slice_x.z)) # print mean for all boxes
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
                                innerBoxmean =  np.mean(las_inner.z)
                                innerBoxes[i][j] = innerBoxmean
                                outerBoxmean = ((box_mean*points_x) - (innerBoxmean*points_inner))/(points_x-points_inner)
                                outerBoxes[i][j] = outerBoxmean
                print(f"Patch {j} of {y_range} completed in {filename}")
                
            
            # directory = os.path.join(TESTDATA_DIR, folder, filename_without_ext)
            # os.makedirs(directory, exist_ok=True)
            
            print("Saving the variables...")
            np.save(os.path.join(folder_path, f'{filename_without_ext}_allBoxes.npy'), allBoxes)
            np.save(os.path.join(folder_path, f'{filename_without_ext}_innerBoxes.npy'), innerBoxes)
            np.save(os.path.join(folder_path, f'{filename_without_ext}_outerBoxes.npy'), outerBoxes)

print("Completed preprocess.")
