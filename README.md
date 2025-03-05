# 图片标注查看器

一个用于查看和管理图片及其标注文件的Python GUI应用程序。

## 功能特点

- 同时显示原始图片和标注可视化效果
- 支持图片分类移动功能
- 支持保存功能
- 支持操作撤销
- 键盘快捷键支持
- 自动文件重命名和序号管理

## 环境要求

- Python 3.6+
- OpenCV (cv2)
- Pillow
- tkinter (Python标准库)
- numpy

## 安装步骤

1. 克隆或下载此仓库
2. 安装所需依赖:
```bash
pip install opencv-python
pip install Pillow
pip install numpy
```

## 使用说明

1. 运行程序:
```bash
python main.py
```

2. 程序启动后会依次要求选择以下文件夹:
   - 源文件夹(包含原始图片和标注文件)
   - ERROR文件夹
   - INACCURATE文件夹
   - SINGLE_LIGHT文件夹
   - 保存文件夹

3. 界面操作:
   - 左侧显示原始图片
   - 右侧显示标注可视化效果
   - 底部按钮提供各种操作功能

4. 快捷键:
   - `←` : 上一张图片
   - `→` : 下一张图片
   - `A` : 移动到ERROR文件夹
   - `S` : 移动到INACCURATE文件夹
   - `D` : 移动到SINGLE_LIGHT文件夹
   - `F` : 保存图片
   - `Z` : 撤销上一步操作
   - `Q` : 退出程序

## 文件说明

- `main.py`: 主程序文件
- 图片文件支持格式: .png, .jpg, .jpeg, .bmp
- 标注文件格式: .txt (与图片同名)

## 注意事项

1. 确保所有目标文件夹均已存在
2. 标注文件应与图片位于同一文件夹
3. 图片移动时会自动携带对应的标注文件
4. 支持操作撤销，但仅限最近一次操作

## 开发说明

- 使用tkinter构建GUI界面
- 使用OpenCV处理图像
- 使用Pillow进行图像显示
- 支持文件管理和操作历史记录

## 许可证

MIT License
