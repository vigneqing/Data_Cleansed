import os
import shutil
import cv2
import tkinter as tk
from tkinter import ttk, messagebox, font
from PIL import Image, ImageTk
import numpy as np

class AnnotationViewer:
    def __init__(self, root, image_folder, dest_folders):
        self.root = root
        self.image_folder = image_folder
        self.dest_folders = dest_folders  # 三个目标文件夹：错误、不准确、单灯条
        self.image_files = self.get_image_files()
        self.current_index = 0
        
        # 确保目标文件夹存在
        for folder in self.dest_folders.values():
            os.makedirs(folder, exist_ok=True)
        
        self.setup_ui()
        self.load_image()

    def get_image_files(self):
        """获取并持续更新图片文件列表"""
        return sorted([
            f for f in os.listdir(self.image_folder) 
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))
        ])

    def setup_ui(self):
        """创建界面布局"""
        self.root.title("图片标注工具")
        
        # 设置字体
        custom_font = font.Font(family="Arial", size=18, weight="normal")
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 图片显示区域
        img_frame = ttk.Frame(main_frame)
        img_frame.pack(fill=tk.BOTH, expand=True)
        
        # 原图显示
        self.orig_canvas = tk.Canvas(img_frame, width=800, height=700)
        self.orig_canvas.pack(side=tk.LEFT, padx=10, pady=10)
        
        # 标注图显示
        self.annot_canvas = tk.Canvas(img_frame, width=800, height=700)
        self.annot_canvas.pack(side=tk.LEFT, padx=10, pady=10)
        
        # 控制面板
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 导航按钮
        nav_frame = ttk.Frame(control_frame)
        nav_frame.pack(side=tk.LEFT, padx=10)
        ttk.Button(nav_frame, text="←", command=self.prev_image, style="TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="→", command=self.next_image, style="TButton").pack(side=tk.LEFT, padx=2)
        
        # 功能按钮
        func_frame = ttk.Frame(control_frame)
        func_frame.pack(side=tk.LEFT, padx=10)
        ttk.Button(func_frame, text="ERROR(A)", command=lambda: self.move_image("error"), style="TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(func_frame, text="INACCURATE (S)", command=lambda: self.move_image("inaccurate"), style="TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(func_frame, text="SINGLE (D)", command=lambda: self.move_image("single_light"), style="TButton").pack(side=tk.LEFT, padx=5)
        
        # 退出按钮
        ttk.Button(control_frame, text="退出 (Q)", command=self.root.quit, style="TButton").pack(side=tk.RIGHT, padx=10)
        
        # 绑定键盘事件
        self.root.bind("<Key>", self.handle_keypress)
        self.root.bind("<Left>", lambda e: self.prev_image())
        self.root.bind("<Right>", lambda e: self.next_image())

        # 设置按钮字体
        style = ttk.Style()
        style.configure("TButton", font=custom_font)

    def handle_keypress(self, event):
        """处理键盘事件"""
        key = event.char.lower()
        if key == 'a':
            self.move_image("error")
        elif key == 's':
            self.move_image("inaccurate")
        elif key == 'd':
            self.move_image("single_light")
        elif key == 'q':
            self.root.quit()

    def navigate_image(self, step):
        """通用导航方法"""
        self.current_index = (self.current_index + step) % len(self.image_files)
        self.load_image()

    def prev_image(self):
        """查看上一张"""
        self.navigate_image(-1)

    def next_image(self):
        """查看下一张"""
        self.navigate_image(1)

    def load_image(self):
        """加载当前图片和标注"""
        if not self.image_files:
            messagebox.showinfo("提示", "没有找到任何图片文件")
            self.root.quit()
            return
            
        self.current_index = max(0, min(self.current_index, len(self.image_files)-1))
        self.current_file = self.image_files[self.current_index]
        image_path = os.path.join(self.image_folder, self.current_file)
        
        if not os.path.exists(image_path):
            messagebox.showwarning("文件丢失", f"找不到文件: {self.current_file}")
            self.image_files = self.get_image_files()
            self.load_image()
            return

        # 加载原图
        self.orig_image = cv2.imread(image_path)
        if self.orig_image is None:
            messagebox.showwarning("文件损坏", f"无法读取图片: {self.current_file}")
            self.image_files = self.get_image_files()
            self.load_image()
            return
        self.orig_image = cv2.cvtColor(self.orig_image, cv2.COLOR_BGR2RGB)
        
        # 加载标注
        label_path = os.path.splitext(image_path)[0] + ".txt"
        self.annotations = []
        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                self.annotations = f.readlines()
        
        # 生成标注图
        self.annot_image = self.draw_annotations(self.orig_image.copy())
        self.show_images()

    def draw_annotations(self, img):
        """绘制标注到图片上"""
        for line in self.annotations:
            parts = line.strip().split()
            class_id = parts[0]
            coords = [float(x) for x in parts[1:]]
            points = [(int(coords[i] * img.shape[1]), int(coords[i+1] * img.shape[0]))
                    for i in range(0, len(coords), 2)]
            # 绘制四边形
            if len(points) >= 4:
                pts = np.array(points[:4], np.int32).reshape((-1, 1, 2))
                cv2.polylines(img, [pts], isClosed=True, color=(0, 255, 0), thickness=1)  # 将线条粗细改为1
                # 在四边形上方标注类别ID
                x_min = min(p[0] for p in points[:4])
                y_min = min(p[1] for p in points[:4])
                cv2.putText(img, class_id, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            # 绘制中心点
            for point in points:
                cv2.circle(img, point, 2, (255, 0, 0), -1)  # 将点的大小改为2
        return img

    def show_images(self):
        """在Canvas上显示图片"""
        # 调整图片大小
        orig_img = self.resize_image(self.orig_image, 800, 700)
        annot_img = self.resize_image(self.annot_image, 800, 700)
        
        # 更新原图显示
        self.orig_photo = ImageTk.PhotoImage(image=Image.fromarray(orig_img))
        self.orig_canvas.create_image(0, 0, anchor=tk.NW, image=self.orig_photo)
        self.orig_canvas.config(scrollregion=self.orig_canvas.bbox(tk.ALL))
        
        # 更新标注图显示
        self.annot_photo = ImageTk.PhotoImage(image=Image.fromarray(annot_img))
        self.annot_canvas.create_image(0, 0, anchor=tk.NW, image=self.annot_photo)
        self.annot_canvas.config(scrollregion=self.annot_canvas.bbox(tk.ALL))
        
        # 更新窗口标题
        self.root.title(f"图片标注工具 - {self.current_file} ({self.current_index+1}/{len(self.image_files)})")

    def resize_image(self, img, max_width, max_height):
        """调整图片大小保持比例"""
        h, w = img.shape[:2]
        ratio = min(max_width/w, max_height/h)
        new_size = (int(w*ratio), int(h*ratio))
        return cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)

    def move_image(self, category):
        """移动图片到指定类别目录"""
        dest_folder = self.dest_folders[category]
        
        # 获取目标目录中已有的最大序号
        existing_files = [f for f in os.listdir(dest_folder) if f.startswith("image_")]
        if existing_files:
            max_index = max(int(f.split("_")[1].split(".")[0]) for f in existing_files)
        else:
            max_index = 0
        
        # 生成新的文件名（序号递增）
        new_index = max_index + 1
        new_name = f"image_{new_index}"
        
        # 获取文件扩展名
        base_name, ext = os.path.splitext(self.current_file)
        
        # 检查目标目录中是否已经存在同名文件
        while os.path.exists(os.path.join(dest_folder, f"{new_name}{ext}")):
            new_index += 1
            new_name = f"image_{new_index}"
        
        # 移动并重命名图片文件
        src_img = os.path.join(self.image_folder, self.current_file)
        dst_img = os.path.join(dest_folder, f"{new_name}{ext}")
        shutil.move(src_img, dst_img)
        
        # 移动并重命名标注文件
        src_txt = os.path.join(self.image_folder, base_name + ".txt")
        if os.path.exists(src_txt):
            dst_txt = os.path.join(dest_folder, f"{new_name}.txt")
            shutil.move(src_txt, dst_txt)
        
        # 更新文件列表并加载下一张图片
        self.image_files = self.get_image_files()
        self.load_image()

if __name__ == "__main__":
    root = tk.Tk()
    
    # 用户提供的四个路径：源文件夹和三个目标文件夹
    #下面的路径都要改成自己的
    image_folder = "/home/hero/Datasets_of_Car/TOTAL/xj_hero"
    dest_folders = {
        "error": "/home/hero/Datasets_of_Car/ERROR",
        "inaccurate": "/home/hero/Datasets_of_Car/inaccurate",
        "single_light": "/home/hero/Datasets_of_Car/HALF"
    }
    
    viewer = AnnotationViewer(root, image_folder, dest_folders)
    root.mainloop()
