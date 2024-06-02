from customtkinter import CTkFrame, CTkButton
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

class StockDetailView(CTkFrame):    
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        
        # 创建刷新按钮
        self.refresh_button = CTkButton(self, text="刷新")
        self.refresh_button.pack(pady=20)
        
        # 创建 matplotlib 图表
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.xaxis_date()
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.ax.grid(True)
        # 创建注释文本，初始时不可见
        self.annot = self.ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                            bbox=dict(boxstyle=ctk.ROUND, fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)
        
        # 将图表嵌入到 customtkinter 窗口中
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=ctk.BOTH, expand=True)
        
        # 添加 matplotlib 导航工具栏
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(fill=ctk.BOTH, expand=True)

        # # 开启交互模式
        plt.ion()
        
        
    