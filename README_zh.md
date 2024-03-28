# 3D 模型转换 Python 脚本

此仓库包含三个 Python 脚本，用于在不同格式之间转换 3D 模型并提取数据。这些脚本设计用于处理常用于 3D 建模和动画的 OBJ、BVH 和 FBX 文件格式。

## 1. obj2npy.py

### 实现步骤：

1. **读取 OBJ 文件**：脚本打开一个 OBJ 文件，并逐行读取顶点（`v`）和面（`f`）数据。
2. **提取数据**：从文件中提取顶点坐标和面索引，并分别存储在列表中。
3. **转换为 NumPy 数组**：将列表转换为 NumPy 数组，以便于操作和存储。
4. **导出数组**：将 NumPy 数组保存到磁盘上的 `.npy` 文件中，一个用于顶点，一个用于面。
5. **可视化（可选）**：脚本还可以使用 Matplotlib 生成模型的 3D 绘图。

### 使用方式：

要将 OBJ 文件转换为 NumPy 格式并可选地进行可视化，请使用以下命令：

```bash
python obj2npy.py --input_dir <输入目录路径> --output_dir <输出目录路径>
```

## 2. bvh2npy.py

### 实现步骤：

1. **读取 BVH 文件**：脚本打开一个 BVH 文件，并解析层次骨架数据。
2. **提取数据**：从层次结构中提取关节名称、父索引和偏移位置。
3. **转换为 NumPy 数组**：将提取的数据转换为 NumPy 数组，以便于操作和存储。
4. **导出数组**：将 NumPy 数组保存到磁盘上的 `.npy` 文件中，分别用于关节偏移、链接（父子关系）和关节名称。
5. **可视化（可选）**：脚本还可以使用 Matplotlib 生成骨架的 3D 绘图。

### 使用方式：

要将 BVH 文件转换为 NumPy 格式并可选地进行可视化，请使用以下命令：

```bash
python bvh2npy.py --input_dir <输入目录路径> --output_dir <输出目录路径>
```

## 3. convert.py

### 实现步骤：

1. **读取 FBX 文件**：脚本使用 Blender 的 Python API 将 FBX 文件导入到一个新的 Blender 场景中。
2. **应用变换**：对导入的对象应用任何必要的变换。
3. **导出数据**：根据提供的选项，脚本可以将网格导出为 OBJ 文件，将骨架导出为 BVH 文件，并可选地保存原始 FBX 文件和 Blender 文件。
4. **可选导出**：脚本还提供了导出 UV、法线以及根据骨架存在与否过滤文件的选项。

### 使用方式：

要使用 Blender 提取 FBX 文件中的数据，请使用以下命令：

```bash
blender --background --python convert.py -- --dataset_dir <数据集目录路径> --output_dir <输出目录路径> [--save-orig] [--save-blend] [--export-skeleton] [--export-mesh] [--export-uv] [--export-normals] [--only-has-skeleton] [--number <数字位数>]
```

**注意：**此脚本需要安装 bpy 并且能够从命令行访问。