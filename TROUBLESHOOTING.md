# 常见问题排查指南 (Troubleshooting)

## 代码编辑器显示 "Import Error" 但项目能正常运行

### 问题现象
在 VS Code 中打开 Python 文件时，`import django` 或其他第三方库下方出现波浪线报错，同时提示 `Import "django" could not be resolved`，但在终端使用 `python manage.py runserver` 可以正常启动项目。

### 原因分析
这是因为 VS Code 的 **Python 解释器 (Interpreter)** 没有正确指向项目中的虚拟环境 (`venv`)。编辑器使用了系统默认的 Python (可能未安装相关依赖)，而终端使用的是已激活的虚拟环境。

### 解决方法

1.  **打开命令面板**
    在 VS Code 中按下快捷键 `Ctrl + Shift + P` (Mac 用户按 `Cmd + Shift + P`)。

2.  **搜索并选择解释器**
    输入 `Python: Select Interpreter` 并点击该选项。

3.  **选择编译器 (Interpreter)**
    在弹出的列表中，尝试选择 **路径中包含 `Anaconda`** 的选项（例如 `D:\app\Anaconda\python.exe`）。
    *   **原因**: 您的终端虽然显示 `(venv)`，但实际上使用的是 Anaconda 的环境（其中安装了 Django）。VS Code 需要选择这个实际在工作的环境，原来的 `venv` 可能是空的或未正确配置。

4.  **重启 VS Code (可选)**
    选择后，VS Code底部的状态栏应显示正在加载环境。如果报错仍未消失，尝试重启 VS Code 或按下 `Ctrl + Shift + P` 输入 `Developer: Reload Window`。

---

## 运行 runserver 报错 "ModuleNotFoundError"

### 原因
缺少项目运行所需的依赖包。

### 解决方法
请确保您已激活虚拟环境并安装了 `requirements.txt` 中的依赖。

```bash
# 1. 激活虚拟环境 (Windows)
./venv/Scripts/activate

# 2. 安装/更新依赖
pip install -r requirements.txt
pip install django-bootstrap-v5  # 如果该包未自动安装
```
