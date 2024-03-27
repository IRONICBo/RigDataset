"""Extract rig dataset
"""
import os
import sys
import argparse
import bpy
import tqdm


argparser = argparse.ArgumentParser(description="Extract rig dataset")
argparser.add_argument("dataset_dir", type=str)
argparser.add_argument("output_dir", type=str)
argparser.add_argument("--export-skeleton", type=bool, default=True,
                       help="Export skeleton")
argparser.add_argument("--export-mesh", type=bool, default=True,
                       help="Export mesh")
argparser.add_argument("--export-uv", type=bool, default=False,
                       help="Export UV")
argparser.add_argument("--export-normals", type=bool, default=False,
                       help="Export normals")
argparser.add_argument("--only-has-skeleton", action="store_true",
                       help="Only export files that have skeleton")
argparser.add_argument("--number", type=int, default=0,
                       help="Name files with numbers, 0 for original names")


def process(index: int, dataset_dir: str, output_dir: str, relpath: str, opts: argparse.Namespace) -> bool:
    """Process a single file

    opts:
        dataset_dir (str): dataset directory
        output_dir (str): output directory
        relpath (str): relative path to the file
    """
    print(f"Processing: {relpath}")
    bpy.ops.object.select_all(action='SELECT')

    # Delete all transformations
    # bpy.ops.object.mode_set(mode='OBJECT')
    # for obj in bpy.context.selected_objects:
    #     obj.location = (0, 0, 0)
    #     obj.rotation_euler = (0, 0, 0)
    #     obj.scale = (1, 1, 1)
    #     bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
    
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=os.path.join(dataset_dir, relpath))
    # Apply all transformations
    # bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    # Clear parent and keep transformation
    # bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    # Apply all transformations to zero out to current scene level
    # bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    base_path = os.path.splitext(relpath)[0]
    target_base_path = base_path
    if opts.number > 0:
        # generate basename with <number> digits, padding with zeros
        target_base_path = f"{index:d}"
        target_base_path = target_base_path.zfill(opts.number)

    obj_path = os.path.join(output_dir, target_base_path + ".obj")
    fbx_path = os.path.join(output_dir, target_base_path + ".fbx")
    bvh_path = os.path.join(output_dir, target_base_path + ".bvh")
    os.makedirs(os.path.dirname(obj_path), exist_ok=True)
    os.makedirs(os.path.dirname(fbx_path), exist_ok=True)

    # export fbx
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=False)

    # Check if the file has a skeleton
    has_skeleton = False
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            has_skeleton = True
            break

    if opts.only_has_skeleton and not has_skeleton:
        print(f"Skipping: {relpath}, no skeleton found")
        return False

    bpy.ops.object.select_all(action='SELECT')
    # for obj in bpy.context.selected_objects:
    #     center = obj.location + obj.matrix_world @ obj.data.center
    #     bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
    #     obj.location = (0, 0, 0)
    if opts.export_mesh:
        bpy.ops.wm.obj_export(filepath=obj_path, export_materials=False,
                              export_normals=opts.export_normals, export_uv=opts.export_uv,
                              export_triangulated_mesh=True, apply_modifiers=False)
        # bpy.ops.export_scene.obj(filepath=obj_path, use_selection=True, use_mesh_modifiers=False)
        print(f"Exported: {obj_path}")

    if opts.export_skeleton:
        for obj in bpy.context.scene.objects:
            if obj.type == 'ARMATURE':
                bpy.ops.object.select_all(action='SELECT')
                # for obj in bpy.context.selected_objects:
                #     center = obj.location + obj.matrix_world @ obj.data.center
                #     bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
                #     obj.location = (0, 0, 0)
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.export_anim.bvh(
                    filepath=bvh_path, frame_start=1, frame_end=1, global_scale=0.01, rotate_mode='XYZ')
                print(f"Exported: {bvh_path}")
                break

    return True


def extract(dataset_dir: str, output_dir: str, opts: argparse.Namespace):
    """Extract dataset

    Args:
        dataset_dir (str): dataset directory
        output_dir (str): output directory
    """

    allfiles = []
    for root, _dirs, files in os.walk(dataset_dir):
        for file in files:
            path = os.path.join(root, file)
            relpath = os.path.relpath(path, dataset_dir)
            if relpath.endswith(".fbx"):
                allfiles.append(relpath)

    tqdm.tqdm.write(f"Extracting {len(allfiles)} files")
    exported = 0
    for relpath in tqdm.tqdm(allfiles):
        if process(exported, dataset_dir, output_dir, relpath, opts):
            exported += 1

    tqdm.tqdm.write("Done")
    tqdm.tqdm.write(f"Exported {exported} files")


if __name__ == '__main__':
    args = argparser.parse_args()

    data_dir = sys.argv[1]
    out_dir = sys.argv[2]

    if not os.path.isdir(data_dir):
        print(f"Dataset directory not found: {data_dir}")
        sys.exit(1)

    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    extract(data_dir, out_dir, args)
