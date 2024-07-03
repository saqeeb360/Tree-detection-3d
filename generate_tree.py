from utils import *

width = 4
delta = 2

print("Getting Files...")

for folder in os.listdir(TESTDATA_DIR):
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

            allBoxes = np.load(os.path.join(folder_path, f'{filename_without_ext}_allBoxes.npy'))
            innerBoxes = np.load(os.path.join(folder_path, f'{filename_without_ext}_innerBoxes.npy'))
            outerBoxes = np.load(os.path.join(folder_path, f'{filename_without_ext}_outerBoxes.npy'))

            t5 = innerBoxes - allBoxes
            t6 = np.where(t5 < -0.1, -120, t5)
            t6 = np.where(t6 > 0.01, 120, t6)
            t6 = t6+120
            t6 = np.where(t6<125, 0, t6)

            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
            res = cv2.morphologyEx(t6,cv2.MORPH_OPEN,kernel)
            res = np.where(res > 100, 240, res)

            maxShape_x, maxShape_y = res.shape
            t1, t2 = np.meshgrid(np.linspace(xmin,xmax, maxShape_x), np.linspace(ymin,ymax, maxShape_y))

            # All presumable tree points
            geometry = []

            res = np.array(res, dtype=np.uint8)
            # _, thresholded = cv2.threshold(res, 100, 255, cv2.THRESH_BINARY)
            _, labels, stats, centroids = cv2.connectedComponentsWithStats(res, connectivity=8)
            cntBoxes = 0
            for label in range(1, len(stats)):
                x, y, width, height, area = stats[label]
                if area > 5 and area < 100:   # Exclude small noise regions
                    # areacheck.append(area)
                    cv2.rectangle(res, (x, y), (x + width, y + height), 200 , 1)
                    cntBoxes += 1
                    shapex = t1[x+round(width/2),y+round(height/2)]
                    shapey = t2[x+round(width/2),y+round(height/2)]
                    geometry.append(Point(shapex, shapey, 270))

            crs = new_las.header.parse_crs()  # Set the correct CRS
            gdf = gpd.GeoDataFrame(geometry=geometry, crs=crs)

            # Define the output shapefile path
            directory = os.path.join(RESULT_FOLDER, folder, filename_without_ext)
            os.makedirs(directory, exist_ok=True)

            output_shapefile = os.path.join(directory, filename_without_ext+".shp")

            # Save the GeoDataFrame to a shapefile
            gdf.to_file(output_shapefile, driver="ESRI Shapefile")

            print(f'Total tree in {filename} is {cntBoxes}')

print("Completed.")