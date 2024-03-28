# Python Scripts for 3D Model Conversion

This repository contains three Python scripts for converting 3D models between different formats and extracting data from them. The scripts are designed to work with OBJ, BVH, and FBX file formats, commonly used in 3D modeling and animation.

## 1. obj2npy.py

### Implementation:

1. **Read OBJ File**: The script opens an OBJ file and reads the vertex (`v`) and face (`f`) data line by line.
2. **Extract Data**: Vertex coordinates and face indices are extracted and stored in separate lists.
3. **Convert to NumPy Arrays**: The lists are converted to NumPy arrays for easier manipulation and storage.
4. **Export Arrays**: The NumPy arrays are saved to disk as `.npy` files, one for vertices and one for faces.
5. **Visualization (Optional)**: The script can also generate a 3D plot of the model using Matplotlib.

### Usage:

To convert an OBJ file to NumPy format and optionally visualize it:

```bash
python obj2npy.py --input_dir <path_to_input_directory> --output_dir <path_to_output_directory>
```

## 2. bvh2npy.py

### Implementation:

1. **Read BVH File**: The script opens a BVH file and parses the hierarchical skeleton data.
2. **Extract Data**: Joint names, parent indices, and offset positions are extracted from the hierarchy.
3. **Convert to NumPy Arrays**: The extracted data is converted to NumPy arrays for easier manipulation and storage.
4. **Export Arrays**: The NumPy arrays are saved to disk as `.npy` files, one for joint offsets, one for links (parent-child relationships), and one for joint names.
5. **Visualization (Optional)**: The script can also generate a 3D plot of the skeleton using Matplotlib.

### Usage:

To convert a BVH file to NumPy format and optionally visualize it:

```bash
python bvh2npy.py --input_dir <path_to_input_directory> --output_dir <path_to_output_directory>
```

## 3. convert.py

### Implementation:

1. **Read FBX File**: The script uses Blender's Python API to import an FBX file into a new Blender scene.
2. **Apply Transformations**: Any necessary transformations are applied to the imported objects.
3. **Export Data**: Depending on the options provided, the script can export the mesh as an OBJ file, the skeleton as a BVH file, and optionally save the original FBX file and the Blender file.
4. **Optional Exports**: The script also provides options to export UVs, normals, and to filter files based on the presence of a skeleton.

### Usage:

To extract data from an FBX file using Blender:

```bash
blender --background --python convert.py -- --dataset_dir <path_to_dataset_directory> --output_dir <path_to_output_directory> [--save-orig] [--save-blend] [--export-skeleton] [--export-mesh] [--export-uv] [--export-normals] [--only-has-skeleton] [--number <number_of_digits>]
```

**Note:** This script requires Blender to be installed and accessible from the command line.