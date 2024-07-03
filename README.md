# Tree Detection in 3d las files

This code helps to detect position of trees in a las file which has x,y,z coordinates points and its respective RGB value.

#### Step to run this code:
- Add two folders "test_data" and "test_results" in the root folder.
- Inside the "test_data" folder, add subfolders that contain the LAS files.

The folder structure is below:
```bash
tree detection 3d
│
├── test_data
│   ├───extra 1
│   │   └── extra 1.las
│   └───gevra
│       └── gevra.las
├── test_results
│   └── ... (test result files)
├── preprocess.py
├── generate_tree.py
├── utils.py
├── Dockerfile
├── README.md
└── requirements.txt

```
1. Open cmd and use the below commands to create directory, build a image, preprocess, generate_tree.

2. Create 2 folders with the names
"test_data", "test_results". Run the below command and ignore error(folder already exist).
```cmd
mkdir test_data test_results
```

3. Install docker desktop and then run the below command on cmd to build a image.
```cmd
docker build -t treedetection3d:1 .
```

4. Now run the "preprocess.py" and then the "generate_tree.py" to get the tree shapefiles.
```cmd
docker run -it --rm -v "%cd%/:/myapp/" treedetection3d:1 python3 preprocess.py
docker run -it --rm -v "%cd%/:/myapp/" treedetection3d:1 python3 generate_tree.py
```