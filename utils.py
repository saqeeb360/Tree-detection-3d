import laspy
import numpy as np
# import matplotlib.pyplot as plt
import cv2
# from tqdm import tqdm
import os
import geopandas as gpd
from shapely.geometry import Point
from pyproj import CRS
import warnings
warnings.filterwarnings("ignore")


ROOT_DIR = os.path.abspath("")
TESTDATA_DIR = os.path.join(ROOT_DIR, "test_data")
RESULT_FOLDER = os.path.join(ROOT_DIR, "test_results")
