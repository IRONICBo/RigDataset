import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def show(global_positions, links=None, joint_names=None, faces=None):
    # Plotting
    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(111, projection='3d')

    # Plot joints or vertices
    ax.scatter(global_positions[:, 0], global_positions[:, 1], global_positions[:, 2], marker='o', c='b', s=0.05, label='Vertices' if faces is not None else 'Joints')

    # Plot links
    if links is not None:
        for link in links:
            start_pos, end_pos = global_positions[link[0]], global_positions[link[1]]
            ax.plot([start_pos[0], end_pos[0]], [start_pos[1], end_pos[1]], [start_pos[2], end_pos[2]], 'black')

    # Annotate joint names
    if joint_names is not None:
        for i, name in enumerate(joint_names):
            ax.text(global_positions[i, 0], global_positions[i, 1], global_positions[i, 2], name)

    # Plot faces
    if faces is not None:
        for face in faces:
            face_vertices = global_positions[face]
            face_vertices = np.append(face_vertices, [face_vertices[0]], axis=0)
            ax.plot(face_vertices[:, 0], face_vertices[:, 1], face_vertices[:, 2], color='r', linewidth=0.01, label='Faces')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.legend()
    plt.show()

def show_mesh_dir(directory):
    # Find the numpy files in the directory
    files = os.listdir(directory)
    vertices_file = None
    faces_file = None
    for file in files:
        if file.endswith("_vertices.npy"):
            vertices_file = os.path.join(directory, file)
        elif file.endswith("_faces.npy"):
            faces_file = os.path.join(directory, file)

    # Load data from numpy files
    if vertices_file and faces_file:
        vertices = np.load(vertices_file)
        faces = np.load(faces_file)

        # Use the show function from utils.py
        show(vertices, faces=faces)
    else:
        print("Required numpy files not found in the directory.")

def show_skel_dir(directory):
    # Find the numpy files in the directory
    files = os.listdir(directory)
    skel_file = None
    link_file = None
    names_file = None
    for file in files:
        if file.endswith("_skel.npy"):
            skel_file = os.path.join(directory, file)
        elif file.endswith("_link.npy"):
            link_file = os.path.join(directory, file)
        elif file.endswith("_names.npy"):
            names_file = os.path.join(directory, file)

    # Load data from numpy files
    if skel_file:
        global_positions = np.load(skel_file)
        links = np.load(link_file) if link_file else None
        joint_names = np.load(names_file, allow_pickle=True) if names_file else None

        # Use the show function from utils.py
        show(global_positions, links, joint_names)
    else:
        print("Required _skel.npy file not found in the directory.")
        
