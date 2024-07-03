# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /myapp

# Copy the current directory contents into the container at /myapp
# COPY . .
COPY requirements.txt ./
COPY *.py ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create directories for data
RUN mkdir -p /myapp/test_data
RUN mkdir -p /myapp/test_results

# Define the default command to run when starting the container
CMD ["python3", "preprocess.py"]

# docker build -t treedetection3d:1 . 
# docker run -it --rm -v "%cd%/:/myapp/" treedetection3d:1 python3 preprocess.py
# docker run -it --rm -v "%cd%/:/myapp/" treedetection3d:1 python3 generate_tree.py