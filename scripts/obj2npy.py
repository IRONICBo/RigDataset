import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import os
import tqdm
import argparse

class OBJData:
    def __init__(self, file_path):
        self.file_path = file_path
        self.vertices = np.array([])
        self.faces = np.array([])
        self.vertices, self.faces = self.load_obj(file_path)

    def load_obj(self, filename):
        vertices = []
        faces = []

        with open(filename, 'r') as file:
            for line in file:
                if line.startswith('v '):
                    vertices.append(list(map(float, line.strip().split()[1:4])))
                elif line.startswith('f '):
                    face = [int(i.split('/')[0]) - 1 for i in line.strip().split()[1:]]
                    faces.append(face)

        return np.array(vertices), np.array(faces)

    @staticmethod
    def show(directory):
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

            # Plotting
            fig = plt.figure(figsize=(12, 12))
            ax = fig.add_subplot(111, projection='3d')

            ax.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2], marker='o', c='b', s=0.05, label='Vertices')

            for face in faces:
                face_vertices = vertices[face]
                face_vertices = np.append(face_vertices, [face_vertices[0]], axis=0)
                ax.plot(face_vertices[:, 0], face_vertices[:, 1], face_vertices[:, 2], color='r', linewidth=0.01, label='Faces')

            max_range = np.array([vertices[:, 0].max() - vertices[:, 0].min(), vertices[:, 1].max() - vertices[:, 1].min(), vertices[:, 2].max() - vertices[:, 2].min()]).max() / 2.0
            mid_x = (vertices[:, 0].max() + vertices[:, 0].min()) * 0.5
            mid_y = (vertices[:, 1].max() + vertices[:, 1].min()) * 0.5
            mid_z = (vertices[:, 2].max() + vertices[:, 2].min()) * 0.5

            ax.set_xlim(mid_x - max_range, mid_x + max_range)
            ax.set_ylim(mid_y - max_range, mid_y + max_range)
            ax.set_zlim(mid_z - max_range, mid_z + max_range)

            ax.view_init(elev=100., azim=-90)
            plt.show()
        else:
            print("Required numpy files not found in the directory.")

    def export(self, path):
        np.save(f"{path}_vertices.npy", self.vertices)
        np.save(f"{path}_faces.npy", self.faces)

        print(f"Exported to {path}_vertices.npy and {path}_faces.npy")
        print(f"Exported vertices shape: {self.vertices.shape}")
        print(f"Exported faces shape: {self.faces.shape}")

    def load_from(self, directory):
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
            self.vertices = np.load(vertices_file)
            self.faces = np.load(faces_file)
        else:
            raise FileNotFoundError("Required numpy files not found in the directory.")

    def export_to_obj(self, output_path):
        with open(output_path, 'w') as f:
            f.write("# Exported OBJ file\n")
            for vertex in self.vertices:
                f.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")
            for face in self.faces:
                f.write("f " + " ".join([str(v + 1) for v in face]) + "\n")

def process_obj_files(input_dir, output_dir):
    obj_files = [f for f in os.listdir(input_dir) if f.endswith('.obj')]
    for obj_file in tqdm.tqdm(obj_files, desc="Processing OBJ files"):
        file_path = os.path.join(input_dir, obj_file)
        obj_data = OBJData(file_path)
        output_subdir = os.path.join(output_dir, os.path.splitext(obj_file)[0])
        os.makedirs(output_subdir, exist_ok=True)
        obj_data.export(os.path.join(output_subdir, os.path.splitext(obj_file)[0]))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process multiple OBJ files and export to numpy format.')
    parser.add_argument('input_dir', type=str, help='Input directory containing OBJ files.')
    parser.add_argument('output_dir', type=str, help='Output directory for numpy files.')
    args = parser.parse_args()
    
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir, exist_ok=True)

    process_obj_files(args.input_dir, args.output_dir)

# Example usage:
# obj_data = OBJData('./path/to/your.obj')
# obj_data.show()

# Example usage
# obj_data = OBJData()
# obj_data.load_from("path")
# obj_data.export_to_obj("output.obj")