
import os
import shutil
import cv2
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import numpy as np


class AnnotationViewer:
    def __init__(self, root, image_folder, dest_folders, save_folder):
        self.root = root
        self.image_folder = image_folder
        self.dest_folders = dest_folders 
        self.save_folder = save_folder  # 新增保存文件夹
        self.image_files = self.get_image_files()
        self.current_index = 0
        self.history = []  # 用于存储操作历史记录

        # 确保目标文件夹存在
        for folder in self.dest_folders.values():
            os.makedirs(folder, exist_ok=True)
        os.makedirs(self.save_folder, exist_ok=True)  # 确保保存文件夹存在

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
        self.root.title("图片标注查看器")

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 图片显示区域
        img_frame = ttk.Frame(main_frame)
        img_frame.pack(fill=tk.BOTH, expand=True)

        # 原图显示
        self.orig_canvas = tk.Canvas(img_frame, width=600, height=500)
        self.orig_canvas.pack(side=tk.LEFT, padx=10, pady=10)

        # 标注图显示
        self.annot_canvas = tk.Canvas(img_frame, width=600, height=500)
        self.annot_canvas.pack(side=tk.LEFT, padx=10, pady=10)

        # 控制面板
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        # 导航按钮
        nav_frame = ttk.Frame(control_frame)
        nav_frame.pack(side=tk.LEFT, padx=10)
        ttk.Button(nav_frame, text="上一张 (←)", command=self.prev_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="下一张 (→)", command=self.next_image).pack(side=tk.LEFT, padx=2)

        # 功能按钮
        func_frame = ttk.Frame(control_frame)
        func_frame.pack(side=tk.LEFT, padx=10)
        ttk.Button(func_frame, text="移动到 ERROR (A)", command=lambda: self.move_image("error")).pack(side=tk.LEFT, padx=2)
        ttk.Button(func_frame, text="移动到 INACCURATE (S)", command=lambda: self.move_image("inaccurate")).pack(side=tk.LEFT, padx=2)
        ttk.Button(func_frame, text="移动到 SINGLE_LIGHT (D)", command=lambda: self.move_image("single_light")).pack(side=tk.LEFT, padx=2)
        ttk.Button(func_frame, text="保存 (F)", command=self.save_image).pack(side=tk.LEFT, padx=2)  # 保留保存按钮
        ttk.Button(func_frame, text="撤销 (Z)", command=self.undo).pack(side=tk.LEFT, padx=2)  # 新增撤销按钮

        # 退出按钮
        ttk.Button(control_frame, text="退出 (Q)", command=self.root.quit).pack(side=tk.RIGHT, padx=10)

        # 绑定键盘事件
        self.root.bind("<Key>", self.handle_keypress)
        self.root.bind("<Left>", lambda e: self.prev_image())
        self.root.bind("<Right>", lambda e: self.next_image())
        self.root.bind("z", lambda e: self.undo())  # 绑定撤销快捷键 Z
        self.root.bind("f", lambda e: self.save_image())  # 绑定保存快捷键 F

    def handle_keypress(self, event):
        """处理键盘事件"""
        key = event.char.lower()
        if key == 'a':  # 快捷键 A 对应 ERROR 文件夹
            self.move_image("error")
        elif key == 's':  # 快捷键 S 对应 INACCURATE 文件夹
            self.move_image("inaccurate")
        elif key == 'd':  # 快捷键 D 对应 SINGLE_LIGHT 文件夹
            self.move_image("single_light")
        elif key == 'f':  # 快捷键 F 对应保存
            self.save_image()
        elif key == 'q':
            self.root.quit()
        elif key == 'z':  # 快捷键 Z 对应撤销
            self.undo()

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

        self.current_index = max(0, min(self.current_index, len(self.image_files) - 1))
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
            points = [(int(coords[i] * img.shape[1]), int(coords[i + 1] * img.shape[0]))for i in range(0, len(coords), 2)]
            # 绘制四边形
            if len(points) >= 4:
                pts = np.array(points[:4], np.int32).reshape((-1, 1, 2))
                cv2.polylines(img, [pts], isClosed=True, color=(0, 255, 0), thickness=1)
            # 绘制中心点
            for point in points:
                cv2.circle(img, point, 2, (255, 0, 0), -1)
            # 绘制类别 ID 文本
            if points:
                text_position = points[0]
                cv2.putText(
                    img,
                    f"ID: {class_id}",
                    (text_position[0] + 5, text_position[1] + 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA
                )
        return img

    def show_images(self):
        """在 Canvas 上显示图片"""
        orig_img = self.resize_image(self.orig_image, 600, 500)
        annot_img = self.resize_image(self.annot_image, 600, 500)

        self.orig_photo = ImageTk.PhotoImage(image=Image.fromarray(orig_img))
        self.orig_canvas.create_image(0, 0, anchor=tk.NW, image=self.orig_photo)
        self.orig_canvas.config(scrollregion=self.orig_canvas.bbox(tk.ALL))

        self.annot_photo = ImageTk.PhotoImage(image=Image.fromarray(annot_img))
        self.annot_canvas.create_image(0, 0, anchor=tk.NW, image=self.annot_photo)
        self.annot_canvas.config(scrollregion=self.annot_canvas.bbox(tk.ALL))

        self.root.title(f"图片标注查看器 - {self.current_file} ({self.current_index + 1}/{len(self.image_files)})")

    def resize_image(self, img, max_width, max_height):
        """调整图片大小保持比例"""
        h, w = img.shape[:2]
        ratio = min(max_width / w, max_height / h)
        new_size = (int(w * ratio), int(h * ratio))
        return cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)

    def move_image(self, dest_key):
        """移动图片到指定的目标文件夹"""
        dest_folder = self.dest_folders.get(dest_key)
        if not dest_folder:
            messagebox.showwarning("错误", f"无效的目标文件夹: {dest_key}")
            return

        # 获取目标目录中已有的最大序号
        existing_files = [f for f in os.listdir(dest_folder) if f.startswith("image_")]
        max_index = max([int(f.split("_")[1].split(".")[0]) for f in existing_files], default=0)

        # 生成新的文件名（序号递增）
        new_index = max_index + 1
        new_name = f"image_{new_index}"
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
        dst_txt = None
        if os.path.exists(src_txt):
            dst_txt = os.path.join(dest_folder, f"{new_name}.txt")
            shutil.move(src_txt, dst_txt)

        # 记录操作历史
        self.history.append({
            "action": "move",
            "src_img": src_img,
            "dst_img": dst_img,
            "src_txt": src_txt,
            "dst_txt": dst_txt
        })

        # 更新文件列表并加载下一张图片
        self.image_files = self.get_image_files()
        self.load_image()

    def save_image(self):
        """保存当前图片和标注到保存文件夹"""
        if not self.save_folder:
            messagebox.showwarning("错误", "未指定保存文件夹")
            return

        # 获取目标目录中已有的最大序号
        existing_files = [f for f in os.listdir(self.save_folder) if f.startswith("image_")]
        max_index = max([int(f.split("_")[1].split(".")[0]) for f in existing_files], default=0)

        # 生成新的文件名（序号递增）
        new_index = max_index + 1
        new_name = f"image_{new_index}"
        base_name, ext = os.path.splitext(self.current_file)

        # 检查目标目录中是否已经存在同名文件
        while os.path.exists(os.path.join(self.save_folder, f"{new_name}{ext}")):
            new_index += 1
            new_name = f"image_{new_index}"

        # 移动并重命名图片文件
        src_img = os.path.join(self.image_folder, self.current_file)
        dst_img = os.path.join(self.save_folder, f"{new_name}{ext}")
        shutil.move(src_img, dst_img)

        # 移动并重命名标注文件
        src_txt = os.path.join(self.image_folder, base_name + ".txt")
        dst_txt = None
        if os.path.exists(src_txt):
            dst_txt = os.path.join(self.save_folder, f"{new_name}.txt")
            shutil.move(src_txt, dst_txt)

        # 记录操作历史
        self.history.append({
            "action": "save",
            "src_img": src_img,
            "dst_img": dst_img,
            "src_txt": src_txt,
            "dst_txt": dst_txt
        })

        # 更新文件列表并加载下一张图片
        self.image_files = self.get_image_files()
        self.load_image()
            
    def undo(self):
        """撤销上一次操作"""
        if not self.history:
            messagebox.showinfo("提示", "没有可以撤销的操作")
            return

        # 取出最近的一次操作记录
        last_action = self.history.pop()

        try:
            if last_action["action"] == "move":
                # 恢复图片文件
                shutil.move(last_action["dst_img"], last_action["src_img"])

                # 恢复标注文件（如果存在）
                if last_action["dst_txt"] and os.path.exists(last_action["dst_txt"]):
                    shutil.move(last_action["dst_txt"], last_action["src_txt"])

            elif last_action["action"] == "save":
                # 创建文件的副本，然后删除原文件
                if os.path.exists(last_action["dst_img"]):
                    shutil.copy2(last_action["dst_img"], last_action["src_img"])
                    os.remove(last_action["dst_img"])

                # 对标注文件执行相同操作
                if last_action["dst_txt"] and os.path.exists(last_action["dst_txt"]):
                    shutil.copy2(last_action["dst_txt"], last_action["src_txt"])
                    os.remove(last_action["dst_txt"])

            # 更新文件列表并重新加载当前图片
            self.image_files = self.get_image_files()
            self.load_image()

        except Exception as e:
            messagebox.showerror("错误", f"撤销操作失败: {str(e)}")
            # 发生错误时，从历史记录中移除失败的操作
            self.history = self.history[:-1] if self.history else []


def select_folder(title):
    """弹出文件夹选择对话框"""
    folder = filedialog.askdirectory(title=title)
    if not folder:
        raise ValueError("未选择文件夹，请重新运行程序并选择文件夹")
    return folder


if __name__ == "__main__":
    root = tk.Tk()

    # 用户通过窗口选择文件夹路径
    image_folder = select_folder("请选择源文件夹")
    dest_folders = {
        "error": select_folder("请选择 ERROR 文件夹"),
        "inaccurate": select_folder("请选择 INACCURATE 文件夹"),
        "single_light": select_folder("请选择 SINGLE_LIGHT 文件夹")
    }
    save_folder = select_folder("请选择保存文件夹")  # 新增保存文件夹选择

    viewer = AnnotationViewer(root, image_folder, dest_folders, save_folder)
    root.mainloop()

