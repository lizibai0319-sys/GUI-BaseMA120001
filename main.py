import sys
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QGroupBox, 
                             QDoubleSpinBox, QFrame, QCheckBox, QFormLayout)
from PyQt6.QtCore import QTimer, pyqtSlot, Qt
from translation import apply_graph_translation

# -----------------------------------------------------------------------------
# 1. 数据接口层 (Data Interface)
# -----------------------------------------------------------------------------
class SpectrometerDriver:
    def __init__(self):
        self.connected = False
        self.pixels = 2048
        # 模拟波长范围 350-1000nm
        self.wavelengths = np.linspace(350, 1000, self.pixels)
        self.integration_time = 10.0 

    def connect_device(self):
        self.connected = True
        return True

    def disconnect_device(self):
        self.connected = False

    def set_integration_time(self, ms):
        self.integration_time = ms

    def acquire_spectrum(self):
        if not self.connected:
            return None, None
        
        # --- 模拟数据 ---
        gain = self.integration_time / 10.0
        noise = np.random.normal(0, 2.0 * np.sqrt(gain), self.pixels)
        
        # 模拟主峰位置 (随机抖动一点点，模拟不稳定)
        center = 600 + np.random.uniform(-0.5, 0.5)
        sigma = 8
        peak_height = 100 * gain
        peak = peak_height * np.exp(-0.5 * ((self.wavelengths - center) / sigma) ** 2)
        
        # 模拟次峰
        peak2 = (40 * gain) * np.exp(-0.5 * ((self.wavelengths - 850) / 20) ** 2)
        
        intensities = peak + peak2 + noise + 10 
        
        return self.wavelengths, intensities

# -----------------------------------------------------------------------------
# 2. GUI 展示层 (Visual Layer)
# -----------------------------------------------------------------------------
class SpectrumWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.driver = SpectrometerDriver()
        
        self.timer = QTimer()
        self.timer.setInterval(50) 
        self.timer.timeout.connect(self.update_plot)

        # 标志位：用于判断是否是点击开始后的第一帧
        self.first_frame_flag = False

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("光谱仪数据采集系统 v3.0 - 自动聚焦版")
        self.resize(1100, 700)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. 侧边栏
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)

        # 2. 绘图区
        self.plot_area = self.create_plot_area()
        main_layout.addWidget(self.plot_area)

    def create_sidebar(self):
        sidebar_frame = QFrame()
        sidebar_frame.setFixedWidth(280)
        sidebar_frame.setStyleSheet("QFrame { background-color: #f0f0f0; border-right: 1px solid #d0d0d0; }")
        
        layout = QVBoxLayout(sidebar_frame)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(15)

        # 标题
        layout.addWidget(QLabel("<b>控制面板</b>"))

        # -- 连接 --
        conn_group = QGroupBox("1. 连接")
        conn_layout = QVBoxLayout()
        self.lbl_status = QLabel("● 未连接")
        self.lbl_status.setStyleSheet("color: red")
        self.btn_connect = QPushButton("连接设备")
        self.btn_connect.clicked.connect(self.toggle_connection)
        conn_layout.addWidget(self.lbl_status)
        conn_layout.addWidget(self.btn_connect)
        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)

        # -- 参数 --
        param_group = QGroupBox("2. 参数")
        param_layout = QFormLayout()
        self.spin_integration = QDoubleSpinBox()
        self.spin_integration.setRange(1.0, 5000.0)
        self.spin_integration.setValue(10.0)
        self.spin_integration.setSuffix(" ms")
        self.spin_integration.valueChanged.connect(lambda v: self.driver.set_integration_time(v))
        param_layout.addRow("积分时间:", self.spin_integration)
        param_group.setLayout(param_layout)
        layout.addWidget(param_group)

        # -- 视图控制 (新增功能) --
        view_group = QGroupBox("3. 视图控制")
        view_layout = QVBoxLayout()
        
        # 自动 Y 轴复选框
        self.chk_auto_y = QCheckBox("自动缩放 Y 轴 (Auto-Y)")
        self.chk_auto_y.setToolTip("勾选后，Y轴范围会随波峰高度自动变化")
        self.chk_auto_y.setChecked(False) 
        self.chk_auto_y.stateChanged.connect(self.toggle_auto_y)
        
        # 手动寻找峰值按钮
        self.btn_find_peak = QPushButton("🔍 寻找峰值 (Focus)")
        self.btn_find_peak.clicked.connect(self.focus_on_peak)

        view_layout.addWidget(self.chk_auto_y)
        view_layout.addWidget(self.btn_find_peak)
        view_group.setLayout(view_layout)
        layout.addWidget(view_group)

        # -- 采集 --
        acq_group = QGroupBox("4. 采集")
        acq_layout = QVBoxLayout()
        self.btn_start = QPushButton("开始采集")
        self.btn_start.setMinimumHeight(50)
        self.btn_start.setEnabled(False)
        self.btn_start.clicked.connect(self.toggle_acquisition)
        acq_layout.addWidget(self.btn_start)
        acq_group.setLayout(acq_layout)
        layout.addWidget(acq_group)

        layout.addStretch()
        return sidebar_frame

    def create_plot_area(self):
        self.plot_widget = pg.PlotWidget(title="光谱数据")
        self.plot_widget.setLabel('left', '强度', units='Counts')
        self.plot_widget.setLabel('bottom', '波长', units='nm')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setBackground('k')

        # 汉化
        apply_graph_translation(self.plot_widget)
        #lucky number:4562284593
        # 初始视图范围 (随便设一个，反正一开始没数据)
        self.plot_widget.setXRange(300, 1100)
        self.plot_widget.setYRange(0, 100)

        self.curve = self.plot_widget.plot(pen=pg.mkPen('#00FFFF', width=2))
        return self.plot_widget

    # --- 核心逻辑 ---

    def toggle_connection(self):
        if not self.driver.connected:
            if self.driver.connect_device():
                self.btn_connect.setText("断开设备")
                self.lbl_status.setText("● 已连接")
                self.lbl_status.setStyleSheet("color: #00FF00")
                self.btn_start.setEnabled(True)
        else:
            self.stop_acquisition()
            self.driver.disconnect_device()
            self.btn_connect.setText("连接设备")
            self.lbl_status.setText("● 未连接")
            self.lbl_status.setStyleSheet("color: red")
            self.btn_start.setEnabled(False)

    def toggle_acquisition(self):
        if self.timer.isActive():
            self.stop_acquisition()
        else:
            self.start_acquisition()

    def start_acquisition(self):
        self.timer.start()
        self.btn_start.setText("停止采集")
        self.btn_start.setStyleSheet("background-color: #ffcccc; color: red; font-weight: bold;")
        
        # 核心逻辑：设置标志位，告诉程序“下一帧数据是第一帧，需要自动跳转”
        self.first_frame_flag = True 

    def stop_acquisition(self):
        self.timer.stop()
        self.btn_start.setText("开始采集")
        self.btn_start.setStyleSheet("")

    def toggle_auto_y(self, state):
        """切换是否持续自动调整 Y 轴"""
        if state == 2: # Checked
            self.plot_widget.enableAutoRange(axis='y')
        else:
            self.plot_widget.disableAutoRange(axis='y')

    def focus_on_peak(self):
        """手动点击：将视图聚焦到当前的波形上"""
        self.plot_widget.autoRange() # PyQtGraph 的 autoRange 会自动计算当前数据的边界

    @pyqtSlot()
    def update_plot(self):
        wavelengths, intensities = self.driver.acquire_spectrum()
        if wavelengths is not None:
            self.curve.setData(wavelengths, intensities)
            
            # --- 自动跳转逻辑 ---
            if self.first_frame_flag:
                # 这是一个“一次性”动作：仅在点击开始后的第一帧执行
                self.plot_widget.autoRange() # 自动缩放 X 和 Y 以适应数据
                self.first_frame_flag = False # 重置标志位，后续允许用户自由缩放
            
            # 如果用户勾选了 "自动缩放 Y"，我们需要持续保持 Y 轴适应
            if self.chk_auto_y.isChecked():
                # 注意：我们通常不自动缩放 X 轴，因为用户通常希望 X 轴固定显示全谱
                self.plot_widget.enableAutoRange(axis='y')
            else:
                # 如果没有勾选，且不是第一帧，PyQtGraph 默认会保持用户上次的缩放状态
                pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    if hasattr(sys, 'set_app_id'):
         import ctypes
         try: ctypes.windll.shcore.SetProcessDpiAwareness(1)
         except: pass
    window = SpectrumWindow()
    window.show()
    sys.exit(app.exec())