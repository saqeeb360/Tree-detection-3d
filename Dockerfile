FROM rocker/geospatial:4.1.3

# Install BiocManager
RUN R -e "install.packages('BiocManager')"

# Install EBImage
RUN R -e "BiocManager::install('EBImage')"

# Set the working directory
WORKDIR /myapp

COPY requirements.txt ./
COPY *.py ./
COPY *.R ./

RUN apt-get update && apt-get install -y \
python3 \
python3-pip

RUN pip install --no-cache-dir -r requirements.txt

# Create directories for data
RUN mkdir -p /myapp/test_data
RUN mkdir -p /myapp/test_results

# Run the post-processing script
CMD ["python3", "postprocess.py"]

# docker build -t treedetection3d:1 .
# docker run -it --rm -v "%cd%/:/myapp/" treedetection3d:1 python3 preprocess.py
# docker run -it --rm -v "%cd%/:/myapp/" treedetection3d:1 python3 generate_tree.py
# docker run -it --rm -v "%cd%/:/myapp/" treedetection3d:1 Rscript watershed.R
# docker run -it --rm -v "%cd%/:/myapp/" treedetection3d:1 python3 combine_results.py