# 🌈 Spectrometer DAS | 光谱仪数据采集系统

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green?logo=qt&logoColor=white)
![PyQtGraph](https://img.shields.io/badge/Plotting-PyQtGraph-orange?logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
![License](https://img.shields.io/badge/License-MIT-purple)

**一个基于 Python + PyQt6 的高性能光谱数据采集与可视化平台。**

[功能特性](#-核心功能) • [快速开始](#-快速开始) • [硬件接入](#-硬件接入指南) • [开发计划](#-开发计划-to-do)

</div>

---

## 📖 项目简介

**Spectrometer DAS** 专为实验室光学测量环境设计。它提供了一个轻量级但功能强大的上位机界面，能够实现高帧率的光谱波形显示、实时的硬件参数控制以及灵活的数据交互。

当前版本内置 **模拟模式 (Simulation Mode)**，无需连接物理设备即可体验完整的数据流处理与交互逻辑，非常适合作为光谱仪（如 Ocean Optics、Avantes）或自制 STM32 光谱分析设备的上位机框架。

## 📸 界面预览

> *（在此处插入软件运行截图：建议包含“波形显示”、“右键菜单”和“控制面板”三个视角的拼接图）*
> ![Dashboard Demo](screenshots/demo_placeholder.png)

## ✨ 核心功能

| 模块 | 功能描述 |
| :--- | :--- |
| **⚡ 高性能绘图** | 基于 `PyQtGraph` 优化，支持 **>30 FPS** 的实时光谱刷新，毫秒级响应。 |
| **🎛️ 硬件控制** | 支持实时调节 **积分时间 (Integration Time)**，内置物理模型模拟信号随积分时间的线性响应。 |
| **🔍 交互体验** | **自动聚焦**: 采集启动时自动适配视野。<br>**三键操作**: 左键平移、右键缩放、中键框选。<br>**全中文菜单**: 深度汉化右键菜单（坐标轴设置、导出等）。 |
| **🔌 开放架构** | 采用 **HAL (硬件抽象层)** 设计，驱动逻辑与 UI 完全解耦，支持快速移植 STM32/串口设备。 |

## 🚀 快速开始

### 1. 环境准备

确保已安装 Python 3.8+。推荐使用 `conda` 或 `venv` 管理环境。

```bash
git clone [https://github.com/your-username/Spectrometer-GUI.git](https://github.com/your-username/Spectrometer-GUI.git)
cd Spectrometer-GUI
```

### 2. 安装依赖

```bash
# 安装核心依赖
pip install PyQt6 pyqtgraph numpy

# (可选) 如果未来接入串口设备
pip install pyserial
```

### 3. 运行程序

```bash
python main.py
```
*程序启动后将默认进入模拟模式，并在控制台输出模拟的波长范围和强度信息。*

## 📂 项目结构

```text
Spectrometer-GUI/
├── drivers/                 # 核心驱动层
│   ├── __init__.py
│   ├── abstract_driver.py   # 定义硬件接口规范 (Protocol/ABC)
│   └── simulation.py        # 模拟驱动实现 (高斯噪声+动态波峰)
├── ui/                      # 界面逻辑
│   ├── main_window.py       # 主窗口 UI 定义
│   └── plot_widget.py       # 定制化绘图组件
├── utils/
│   └── ui_translation.py    # PyQtGraph 汉化字典
├── main.py                  # 程序入口
├── requirements.txt         # 依赖列表
└── README.md                # 项目文档
```

## 🔌 硬件接入指南

本项目采用面向接口编程的思想。要接入真实的 Ocean Optics 光谱仪或 STM32 自制设备，只需继承基类并重写 `acquire` 方法。

### 步骤示例

1. 在 `drivers/` 目录下新建 `my_device.py`。
2. 实现数据获取逻辑：

```python
import numpy as np
# 引入厂商 SDK，例如: import seabreeze.spectrometers as sb

class RealSpectrometer:
    def __init__(self):
        # 初始化设备连接
        # self.spec = sb.Spectrometer.from_first_available()
        pass

    def acquire_spectrum(self):
        """
        必须返回两个 numpy 数组:
        :return: (wavelengths, intensities)
        """
        # 伪代码：调用硬件 API
        # wv = self.spec.wavelengths()
        # inten = self.spec.intensities()
        
        # 返回真实数据
        return wv, inten
```

3. 在 `main.py` 中替换驱动实例：

```python
# from drivers.simulation import SimulationDriver
from drivers.my_device import RealSpectrometer

# driver = SimulationDriver() 
driver = RealSpectrometer() # 切换为真实硬件
```

## 📝 开发计划 (To-Do)

### Phase 1: 基础建设 (已完成)
- [x] PyQt6 + PyQtGraph 基础框架搭建
- [x] 实时数据流与高帧率刷新
- [x] 积分时间模拟控制
- [x] 右键菜单深度汉化

### Phase 2: 功能完善 (进行中)
- [ ] **数据持久化**: 支持导出 `.csv` / `.txt` / `.json` 格式
- [ ] **寻峰算法**: 自动标记最大波长 (${\lambda}_{max}$) 与半高全宽 (FWHM)
- [ ] **暗背景扣除**: 实现 $I_{real} = I_{raw} - I_{dark}$ 算法

### Phase 3: 硬件生态
- [ ] 接入 Ocean Optics (SeaBreeze 库)
- [ ] 接入 STM32 (基于 PySerial 的 USB-VCP 通信)

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。

---

<div align="center">
  <p>Created with ❤️ by <b>lizibai</b> @ Sichuan University</p>
  <p><i>Measurement & Control Technology and Instruments</i></p>
</div>
