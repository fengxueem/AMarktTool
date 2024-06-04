from customtkinter import CTkFrame, CTkButton
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

class DateFrame(CTkFrame):
    def __init__(self, master, label_text):
        super().__init__(master)

        self.date_label = ctk.CTkLabel(self, text=label_text)
        self.date_label.grid(row = 0,column = 0, sticky="nw")
        self.date_entry = ctk.CTkEntry(self, placeholder_text="YYYY-MM-DD")
        self.date_entry.grid(row = 1,column = 0, sticky="nw")

class StockDetailView(CTkFrame):    
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        # let child widgets use the whole window space
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(1, weight=1)
        # 创建日期输入控件和刷新按钮
        self.start_date_frame = DateFrame(self, "开始日期:")
        self.start_date_frame.grid(row = 0, column = 0)
        self.end_date_frame = DateFrame(self, "结束日期:")
        self.end_date_frame.grid(row = 0, column = 1)        
        # 创建刷新按钮
        self.refresh_button = CTkButton(self, text="刷新")
        self.refresh_button.grid(row = 0, column = 2)
        
        # 创建 matplotlib 图表
        self.fig = Figure()
        # 调整绘图的面积，尽可能充满整个窗口
        self.fig.subplots_adjust(left=0.025, right=0.975, bottom=0.03, top=0.99)
        self.ax = self.fig.add_subplot(111)
        self.ax.xaxis_date()
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.ax.grid(True)
        
        # 将图表嵌入到 customtkinter 窗口中
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)        
        self.canvas._tkcanvas.grid(row = 1,column = 0, sticky="nsew", columnspan=3)
    
        # 创建注释文本，初始时不可见
        self.annot = self.ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                            bbox=dict(boxstyle=ctk.ROUND, fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)
        
        # 添加水平虚线和垂直虚线
        self.horizontal_line = self.ax.axhline(y=0, color='gray', linestyle='--', linewidth=1, visible=False)
        self.vertical_line = self.ax.axvline(x=0, color='gray', linestyle='--', linewidth=1, visible=False)
