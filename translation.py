from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenu

# -----------------------------------------------------------------------------
# 汉化字典：包含一级菜单、二级菜单及所有已知选项
# -----------------------------------------------------------------------------
TRANSLATION_DICT = {
    # === Level 1: 主菜单 (ViewBox Menu) ===
    "View All": "查看全部 (View All)",
    "X Axis": "X 轴设置",
    "Y Axis": "Y 轴设置",
    "Mouse Mode": "鼠标模式",
    "Plot Options": "绘图选项",
    "Export...": "导出...",

    # === Level 2: 坐标轴设置 (X/Y Axis) ===
    "Auto Range": "自动量程 (Auto)",
    "Link Axis": "联动其他轴",  # 可能会有下级菜单选择联动哪个窗口
    "Log Scale": "对数坐标 (Log)",
    "Grid": "显示网格",
    "Invert Axis": "反转坐标轴",
    "Show Axis": "显示坐标轴",
    "Lock Aspect Ratio": "锁定纵横比",
    "Auto Range X": "X轴自动量程", # 极少情况出现
    "Auto Range Y": "Y轴自动量程",

    # === Level 2: 鼠标模式 (Mouse Mode) ===
    "3 Button": "三键模式 (推荐)",
    "1 Button": "单键模式 (平板)",

    # === Level 2: 绘图选项 (Plot Options) ===
    "Transforms": "数据变换",
    "Downsample": "降采样 (优化性能)",
    "Average": "平均 (Average)",
    "Mean": "均值 (Mean)",
    "Clip to View": "仅渲染可见区域 (Clip)",
    "Alpha": "透明度 (Alpha)",
    "Points": "显示数据点 (Points)",
    
    # === Level 3: 变换与降采样 (Transforms / Downsample) ===
    "FFT": "快速傅里叶变换 (FFT)",
    "Log X": "对数 X",
    "Log Y": "对数 Y",
    "Derivative": "导数 (Derivative)",
    "Phase": "相位",
    "Magnitude": "幅值",
    "Subsample": "抽样 (最快)",
    "Peak": "峰值保留 (最准)",
    
    # === Export 菜单 (Scene Menu) ===
    "Export": "导出面板",
    "Data": "数据",
    "Image": "图片",
    "SVG": "SVG 矢量图",
    "CSV": "CSV 表格数据",
    "Matplotlib Window": "发送至 Matplotlib",
    "Copy": "复制到剪贴板",
    "Close": "关闭"
}

def _translate_action(action):
    """翻译单个 Action 的文本"""
    text = action.text()
    # 移除可能存在的快捷键标记 '&' (例如 "&Export" -> "Export")
    clean_text = text.replace('&', '')
    
    if clean_text in TRANSLATION_DICT:
        action.setText(TRANSLATION_DICT[clean_text])
    elif text in TRANSLATION_DICT:
        action.setText(TRANSLATION_DICT[text])

def _recursive_translate(obj):
    """
    递归遍历菜单结构
    obj: 可以是 QMenu, QAction 列表, 或 QWidgetAction
    """
    if obj is None:
        return

    # 1. 获取 Action 列表
    actions = []
    if isinstance(obj, list):
        actions = obj
    elif hasattr(obj, 'actions'):
        actions = obj.actions()
    
    # 2. 遍历处理
    for action in actions:
        # --- A. 尝试翻译当前菜单项的名字 ---
        # 这一步解决了 "X Axis", "Plot Options" 自身不变成中文的问题
        _translate_action(action)

        # --- B. 检查是否有子菜单 (Sub Menu) ---
        if action.menu():
            _recursive_translate(action.menu())

def apply_graph_translation(plot_widget):
    """
    [主入口] 调用此函数即可汉化 plot_widget 的右键菜单
    """
    # 1. 获取 PlotItem (核心绘图对象)
    plot_item = plot_widget.getPlotItem()
    
    # 2. 汉化 ViewBox 菜单 (主绘图区的右键)
    if plot_item and hasattr(plot_item, 'vb'):
        # 强制构建菜单 (PyQtGraph 默认是懒加载，不点右键不生成，这里强制生成)
        if plot_item.vb.menu is None:
            plot_item.vb.getMenu(None)
        
        # 执行汉化
        _recursive_translate(plot_item.vb.menu)

    # 3. 汉化 Scene 菜单 (包含 Export 选项)
    scene = plot_widget.scene()
    if hasattr(scene, 'contextMenu'):
        if scene.contextMenu:
            _recursive_translate(scene.contextMenu)