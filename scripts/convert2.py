"""Extract rig dataset
"""
import os
import sys
import shutil
import argparse
import bpy
import tqdm


argparser = argparse.ArgumentParser(description="Extract rig dataset")
argparser.add_argument("dataset_dir", type=str)
argparser.add_argument("output_dir", type=str)
argparser.add_argument("--save-orig", action="store_true",
                       help="Save original file")
argparser.add_argument("--save-blend", action="store_true",
                       help="Save blend file")
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
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=os.path.join(dataset_dir, relpath))
    # Apply all transformations
    # bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    # # Clear parent and keep transformation
    # bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    # # Apply all transformations to zero out to current scene level
    # bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    base_path, ext = os.path.splitext(relpath)
    os.makedirs(os.path.dirname(os.path.join(
        output_dir, base_path)), exist_ok=True)

    target_base_path = base_path
    if opts.number > 0:
        # generate basename with <number> digits, padding with zeros
        target_base_path = f"{index:d}"
        target_base_path = target_base_path.zfill(opts.number)

    if opts.save_orig:
        original_path = os.path.join(
            output_dir, target_base_path+"_orig" + ext)
        shutil.copyfile(os.path.join(dataset_dir, relpath), original_path)
        print(f"Copied: {original_path}")

    if opts.save_blend:
        blend_path = os.path.join(output_dir, target_base_path + ".blend")
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        print(f"Saved: {blend_path}")

    obj_path = os.path.join(output_dir, target_base_path + ".obj")
    bvh_path = os.path.join(output_dir, target_base_path + ".bvh")
    os.makedirs(os.path.dirname(obj_path), exist_ok=True)

    # Check if the file has a skeleton
    has_skeleton = False
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            has_skeleton = True
            break

    if opts.only_has_skeleton and not has_skeleton:
        print(f"Skipping: {relpath}, no skeleton found")
        return False

    bpy.ops.object.select_all(action='DESELECT')
    if opts.export_mesh:
        bpy.ops.wm.obj_export(filepath=obj_path, export_materials=False,
                              export_normals=opts.export_normals, export_uv=opts.export_uv,
                              export_triangulated_mesh=True, apply_modifiers=False)
        print(f"Exported: {obj_path}")

    if opts.export_skeleton:
        for obj in bpy.context.scene.objects:
            if obj.type == 'ARMATURE':
                bpy.ops.object.select_all(action='DESELECT')
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