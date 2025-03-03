# Data_Cleansed

## 简介
这是一个基于 Python 和 Tkinter 的图片标注查看工具，支持浏览图片及其标注信息，并提供以下功能：
1. **图片导航**：支持上一张/下一张切换。
2. **标注可视化**：在图片上绘制标注框和类别 ID。
3. **文件管理**：将图片移动到指定的目标文件夹（如 `ERROR`、`INACCURATE`、`SINGLE_LIGHT`）。
4. **撤销功能**：支持撤销最近一次移动操作。
5. **文件夹选择**：通过图形界面选择源文件夹和目标文件夹路径。

---

## 功能列表
- **加载图片**：从指定的源文件夹加载图片及其标注文件（`.txt` 格式）。
- **标注显示**：在标注图中绘制四边形框、中心点以及类别 ID。
- **图片管理**：
  - 将图片移动到不同的目标文件夹（`ERROR`、`INACCURATE`、`SINGLE_LIGHT`）。
  - 自动按序号重命名移动后的图片和标注文件。
- **撤销操作**：恢复最近一次移动操作，将文件移回原位置。
- **快捷键支持**：
  - `←`：上一张。
  - `→`：下一张。
  - `D`：保留当前图片。
  - `E`：移动到 `ERROR` 文件夹。
  - `I`：移动到 `INACCURATE` 文件夹。
  - `S`：移动到 `SINGLE_LIGHT` 文件夹。
  - `Z`：撤销最近一次操作。
  - `Q`：退出程序。


---

## 环境部署

### 1. 安装 Python
确保你的系统已安装 Python 3.6 或更高版本。可以通过以下命令检查：
```bash
python --version
```
如果未安装，请根据操作系统选择合适的安装方式：
- **Windows**：从 [Python 官方网站](https://www.python.org/downloads/) 下载并安装。
- **macOS**：使用 Homebrew 安装：
  ```bash
  brew install python
  ```
- **Linux**：使用包管理器安装（例如 Ubuntu）：
  ```bash
  sudo apt update
  sudo apt install python3 python3-pip
  ```

### 2. 安装依赖库
本项目依赖以下 Python 库：
- `opencv-python-headless`：用于图片处理和标注绘制。
- `Pillow`：用于图像显示。
- `numpy`：用于数值计算。
- `tkinter`：用于图形界面（通常随 Python 自带，但某些系统可能需要额外安装）。

运行以下命令安装这些依赖库：
```bash
pip install opencv-python-headless pillow numpy
```

#### 特别说明：
- **OpenCV**：
  - 如果你需要 GUI 功能（如摄像头捕获），可以安装完整版的 OpenCV：
    ```bash
    pip install opencv-python
    ```
  - 如果你只需要处理图片而不需要 GUI 功能，推荐使用轻量版（`opencv-python-headless`）。
- **Tkinter**：
  - 在大多数 Linux 发行版中，Tkinter 可能需要单独安装。例如，在 Ubuntu 上运行：
    ```bash
    sudo apt install python3-tk
    ```
  - Windows 和 macOS 通常默认包含 Tkinter。

### 3. 检查依赖是否安装成功
安装完成后，可以通过以下命令验证依赖库是否正确安装：
```bash
python -c "import cv2; import PIL; import numpy; import tkinter"
```
如果没有报错，则说明依赖库安装成功。

---

### 4. 准备数据
- **源文件夹**：包含图片文件（如 `.jpg`、`.png`）及其对应的标注文件（`.txt`）。
  - 标注文件格式示例：
    ```
    class_id x1 y1 x2 y2 x3 y3 x4 y4
    ```
    - `class_id`：目标类别 ID。
    - `x1, y1, ..., x4, y4`：归一化的坐标值（范围为 `[0, 1]`），表示标注框的四个顶点。

- **目标文件夹**：用于存放分类后的图片和标注文件。

---

### 5. 其他依赖（可选）
如果你在 Windows 上运行程序，可能需要安装以下组件以支持 OpenCV 的正常运行：
- **Microsoft Visual C++ Redistributable**：
  - 下载地址：[Microsoft Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)
  - 安装后重启计算机。

---

## 运行方式

### 1. 启动程序
运行以下命令启动程序：
```bash
python annotation_viewer.py
```

### 2. 文件夹选择
- 程序启动后会弹出多个文件夹选择对话框：
  - **源文件夹**：存放原始图片和标注文件的文件夹。
  - **目标文件夹**：
    - `ERROR`：存放错误标注的图片。
    - `INACCURATE`：存放标注不准确的图片。
    - `SINGLE_LIGHT`：存放单灯标注的图片。

### 3. 使用界面
- 主界面分为两部分：
  - 左侧显示原图。
  - 右侧显示标注图（包括标注框、中心点和类别 ID）。
- 使用按钮或快捷键进行操作：
  - 浏览图片、移动图片、撤销操作等。

---

## 示例目录结构
假设你的数据目录结构如下：
```
/home/hero/Datasets_of_Car/
├── TOTAL/
│   ├── image1.jpg
│   ├── image1.txt
│   ├── image2.jpg
│   ├── image2.txt
│   └── ...
├── ERROR/
├── INACCURATE/
└── SINGLE_LIGHT/
```

- **源文件夹**：`/home/hero/Datasets_of_Car/TOTAL`
- **目标文件夹**：
  - `ERROR`：`/home/hero/Datasets_of_Car/ERROR`
  - `INACCURATE`：`/home/hero/Datasets_of_Car/INACCURATE`
  - `SINGLE_LIGHT`：`/home/hero/Datasets_of_Car/SINGLE_LIGHT`

---

## 注意事项
1. **标注文件格式**：
   - 确保标注文件的格式正确（每行一个目标，格式为 `class_id x1 y1 x2 y2 x3 y3 x4 y4`）。
   - 坐标值应为归一化值（范围为 `[0, 1]`）。

2. **文件覆盖问题**：
   - 如果目标文件夹中已有同名文件，程序会自动递增编号以避免覆盖。

3. **性能优化**：
   - 如果图片数量较多，建议定期清理源文件夹中的已处理文件，以提高加载速度。

---

## 常见问题

### Q1: 程序无法启动或报错
- 检查是否安装了所有依赖项（`opencv-python-headless`、`pillow`、`numpy`）。
- 确保 Python 版本符合要求（3.6 或更高版本）。

### Q2: 标注未正确显示
- 检查标注文件的格式是否正确。
- 确保标注文件的坐标值为归一化值（范围为 `[0, 1]`）。

### Q3: 文件夹选择对话框未弹出
- 确保运行环境支持图形界面（如 Windows、macOS 或带有桌面环境的 Linux）。

---

## 贡献与反馈
如果你在使用过程中遇到问题或有改进建议，欢迎提交 Issue 或 Pull Request。我们非常乐意接受你的贡献！

---

## 许可证
本项目采用 MIT 许可证。