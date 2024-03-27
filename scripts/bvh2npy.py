import re
import os
import sys
import argparse
import numpy as np
import tqdm
from matplotlib import pyplot as plt

class BVHData:
    def __init__(self, file_path):
        # load in the static and motion data from indicated bvh file
        self.file_path = file_path
        self.load(file_path)

    def load(self, filename):
        f = open(filename, "r")

        i = 0
        active = -1
        end_site = False

        names = []
        offsets = np.array([]).reshape((0, 3))
        parents = np.array([], dtype=int)

        for line in f:
            if "HIERARCHY" in line or "MOTION" in line:
                continue

            rmatch = re.match(r"ROOT (\w+:?\w+)", line)
            if rmatch:
                names.append(rmatch.group(1))
                offsets = np.append(offsets, np.array([[0, 0, 0]]), axis=0)
                parents = np.append(parents, active)
                active = len(parents) - 1
                continue

            if "{" in line or "}" in line:
                if "}" in line and end_site:
                    end_site = False
                elif "}" in line:
                    active = parents[active]
                continue

            offmatch = re.match(r"\s*OFFSET\s+([\-\d\.e]+)\s+([\-\d\.e]+)\s+([\-\d\.e]+)", line)
            if offmatch:
                if not end_site:
                    offsets[active] = np.array([list(map(float, offmatch.groups()))])
                continue

            jmatch = re.match(r"\s*JOINT\s+(\w+:?\w+)", line)
            if jmatch:
                names.append(jmatch.group(1))
                offsets = np.append(offsets, np.array([[0, 0, 0]]), axis=0)
                parents = np.append(parents, active)
                active = len(parents) - 1
                continue

            if "End Site" in line:
                end_site = True
                continue

        f.close()

        # delete ":" from joint name
        names = [name[name.find(':') + 1 :] if ':' in name else name for name in names]

        # joint information
        self.joint_names = names
        self.joint_parents = parents
        self.joint_offsets = offsets

    def compute_global_positions(self):
        global_positions = np.zeros_like(self.joint_offsets)
        for i, offset in enumerate(self.joint_offsets):
            if self.joint_parents[i] == -1:
                global_positions[i] = offset
            else:
                parent_global_position = global_positions[self.joint_parents[i]]
                global_positions[i] = offset + parent_global_position
        return global_positions

    def export(self, path):
        global_positions = self.compute_global_positions()

        # Export joint information
        np.save(f"{path}_skel.npy", global_positions)

        # Generate and export link information
        links = np.array([[parent, child] for child, parent in enumerate(self.joint_parents) if parent != -1])
        np.save(f"{path}_link.npy", links)

        # Export joint names
        np.save(f"{path}_names.npy", self.joint_names, allow_pickle=True)

        print(f"Exported to {path}_skel.npy, {path}_link.npy, {path}_names.npy")
        print(f"Exported skel shape: {global_positions.shape}")
        print(f"Exported link shape: {links.shape}")
        print(f"Exported names shape: {len(self.joint_names)}")

    @staticmethod
    def show(directory):
        # Find the numpy files in the directory
        files = os.listdir(directory)
        # Only support one file
        # Check the number of _skel.npy files
        skel_files = [f for f in files if f.endswith("_skel.npy")]
        if len(skel_files) != 1:
            print(f"Expected 1 _skel.npy file, found {len(skel_files)}")
            return
        # Check the number of _link.npy files
        link_files = [f for f in files if f.endswith("_link.npy")]
        if len(link_files) != 1:
            print(f"Expected 1 _link.npy file, found {len(link_files)}")
            return
        # Check the number of _names.npy files
        names_files = [f for f in files if f.endswith("_names.npy")]
        if len(names_files) != 1:
            print(f"Expected 1 _names.npy file, found {len(names_files)}")
            return
        
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
        if skel_file and link_file and names_file:
            global_positions = np.load(skel_file)
            links = np.load(link_file)
            joint_names = np.load(names_file, allow_pickle=True)

            # Plotting
            fig = plt.figure(figsize=(8, 8))
            ax = fig.add_subplot(111, projection='3d')

            # Plot joints
            ax.scatter(global_positions[:, 0], global_positions[:, 1], global_positions[:, 2], marker='o', c='r', label='Joints')

            # Plot links
            for link in links:
                start_pos, end_pos = global_positions[link[0]], global_positions[link[1]]
                ax.plot([start_pos[0], end_pos[0]], [start_pos[1], end_pos[1]], [start_pos[2], end_pos[2]], 'black')

            # Annotate joint names
            for i, name in enumerate(joint_names):
                ax.text(global_positions[i, 0], global_positions[i, 1], global_positions[i, 2], name)

            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')

            plt.legend()
            plt.show()
        else:
            print("Required numpy files not found in the directory.")

def process_bvh_files(input_dir, output_dir):
    bvh_files = [f for f in os.listdir(input_dir) if f.endswith('.bvh')]
    for bvh_file in tqdm.tqdm(bvh_files, desc="Processing BVH files"):
        file_path = os.path.join(input_dir, bvh_file)
        bvh_data = BVHData(file_path)
        output_subdir = os.path.join(output_dir, os.path.splitext(bvh_file)[0])
        os.makedirs(output_subdir, exist_ok=True)
        bvh_data.export(os.path.join(output_subdir, os.path.splitext(bvh_file)[0]))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process multiple BVH files and export to numpy format.')
    parser.add_argument('input_dir', type=str, help='Input directory containing BVH files.')
    parser.add_argument('output_dir', type=str, help='Output directory for numpy files.')
    args = parser.parse_args()
    
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir, exist_ok=True)

    process_bvh_files(args.input_dir, args.output_dir)
