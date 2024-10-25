
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import os
import urllib3
import pandas as pd
import webbrowser
from PIL import Image, ImageTk  # 使用Pillow加载和调整图片尺寸

root = tk.Tk()

# 忽略 SSL 证书警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 获取资源文件路径
def resource_path(relative_path):
    """ Get the resource file path after packaging """
    try:
        base_path = sys._MEIPASS  # PyInstaller temporary path
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 定义下载功能
def download_files(user_id, secret_key, url_file, save_directory, progress_bar, total_links):
    try:
        with open(url_file, 'r', encoding='utf-8') as file:
            links = [line.strip() for line in file.readlines()]

        downloaded = 0
        titles = []

        for index, url in enumerate(links, start=1):
            params = {
                'userId': user_id,
                'secretKey': secret_key,
                'url': url
            }

            response = requests.post('https://h.aaaapp.cn/single_post', json=params, verify=False)
            data = response.json()

            if data["succ"] and "medias" in data["data"]:
                medias = data["data"]["medias"]
                title = data["data"].get("text", f"无标题_{index}")
                
                for media_index, media in enumerate(medias, start=1):
                    media_type = media.get("media_type")
                    resource_url = media.get("resource_url")
                    
                    # 文件命名：1-1, 1-2, 2-1, 3 等
                    if len(medias) > 1:
                        file_name = f"{index}-{media_index}.mp4" if media_type == "video" else f"{index}-{media_index}.jpg"
                    else:
                        file_name = f"{index}.mp4" if media_type == "video" else f"{index}.jpg"

                    download_path = os.path.join(save_directory, file_name)
                    download_file(resource_url, download_path)
                    downloaded += 1

                    # 记录标题、链接、文件名到 Excel 数据
                    titles.append({"链接": url, "标题": title, "文件名": file_name})

            # 更新进度条
            progress_bar['value'] = ((index / total_links) * 100)
            root.update_idletasks()

        # 保存标题到Excel文件
        excel_path = os.path.join(save_directory, "titles.xlsx")
        df = pd.DataFrame(titles)
        df.to_excel(excel_path, index=False)

        messagebox.showinfo("下载完成", f"下载完成！总共下载了 {downloaded} 个文件。标题已导出到 {excel_path}")

    except Exception as e:
        messagebox.showerror("错误", f"下载时发生错误：{str(e)}")

# 文件下载功能
def download_file(url, file_path):
    response = requests.get(url, stream=True)
    with open(file_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)

# 打开网页
def open_web():
    webbrowser.open("https://hhm123.com/")

# 创建 GUI
def create_gui():
    # 创建根窗口
    root.title("哼哼猫123大批量下载器")
    root.geometry("600x800")

    # 加载Logo图片并调整尺寸
    logo_image_path = resource_path('logo123.png')
    try:
        logo_img = Image.open(logo_image_path)
        logo_img = logo_img.resize((logo_img.width // 10, logo_img.height // 10), Image.Resampling.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_img)
        tk.Label(root, image=logo_photo).pack(pady=10)
    except FileNotFoundError:
        messagebox.showerror("错误", "找不到 logo123.png 图片文件")

    # 添加标题
    tk.Label(root, text="哼哼猫123批量下载器", font=("Arial", 20)).pack(pady=10)

    # 超链接
    link = tk.Label(root, text="链接：https://hhm123.com/", fg="blue", cursor="hand2", font=("Arial", 12))
    link.pack()
    link.bind("<Button-1>", lambda e: open_web())

    # 创建输入框
    tk.Label(root, text="接口用户ID(userId):").pack(pady=5)
    user_id_entry = tk.Entry(root)
    user_id_entry.pack(pady=5, fill=tk.X, padx=20)

    tk.Label(root, text="接口秘钥(secretKey):").pack(pady=5)
    secret_key_entry = tk.Entry(root)
    secret_key_entry.pack(pady=5, fill=tk.X, padx=20)

    # 选择URL文件
    tk.Label(root, text="选择URL文件:").pack(pady=5)
    url_file_entry = tk.Entry(root)
    url_file_entry.pack(pady=5, fill=tk.X, padx=20)
    tk.Button(root, text="浏览", command=lambda: select_file(url_file_entry)).pack(pady=5)

    # 选择保存目录
    tk.Label(root, text="选择保存文件夹:").pack(pady=5)
    save_dir_entry = tk.Entry(root)
    save_dir_entry.pack(pady=5, fill=tk.X, padx=20)
    tk.Button(root, text="浏览", command=lambda: select_directory(save_dir_entry)).pack(pady=5)

    # 进度条
    tk.Label(root, text="下载进度:").pack(pady=5)
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
    progress_bar.pack(pady=5)

    # 下载按钮
    tk.Button(root, text="开始下载", command=lambda: start_download(
        user_id_entry.get(), secret_key_entry.get(), url_file_entry.get(), 
        save_dir_entry.get(), progress_bar), bg="green", fg="white").pack(pady=20)

    root.mainloop()

# 文件选择功能
def select_file(entry):
    file_path = filedialog.askopenfilename(title="选择URL文件", filetypes=[("Text Files", "*.txt")])
    entry.delete(0, tk.END)
    entry.insert(0, file_path)

# 目录选择功能
def select_directory(entry):
    folder_path = filedialog.askdirectory(title="选择保存文件夹")
    entry.delete(0, tk.END)
    entry.insert(0, folder_path)

# 开始下载功能
def start_download(user_id, secret_key, url_file, save_directory, progress_bar):
    if not user_id or not secret_key or not url_file or not save_directory:
        messagebox.showwarning("警告", "请填写所有字段并选择文件和保存目录。")
    else:
        with open(url_file, 'r', encoding='utf-8') as file:
            total_links = len(file.readlines())  # 计算总任务数
        progress_bar['value'] = 0  # 重置进度条
        download_files(user_id, secret_key, url_file, save_directory, progress_bar, total_links)

if __name__ == "__main__":
    create_gui()

