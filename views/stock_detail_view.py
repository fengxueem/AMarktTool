from config import STOCK_INDICATOR_MA, STOCK_INDICATOR_MAGIC_NINE

from customtkinter import CTkFrame, CTkButton
from customtkinter import CTkCheckBox, CTkLabel
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates

class DateFrame(CTkFrame):
    def __init__(self, master, label_text):
        super().__init__(master)

        self.date_label = ctk.CTkLabel(self, text=label_text)
        self.date_label.grid(row = 0,column = 0, sticky="nw")
        self.date_entry = ctk.CTkEntry(self, placeholder_text="YYYY-MM-DD")
        self.date_entry.grid(row = 1,column = 0, sticky="nw")

class StockIndicatorCheckboxFrame(CTkFrame):
    def __init__(self, master, title, values):
        super().__init__(master)
        self.grid_rowconfigure(0, weight=1)
        self.values = values
        self.title = title
        self.checkboxes = []

        self.title = CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(5, 5), sticky="ns")

        for i, value in enumerate(self.values):
            checkbox = CTkCheckBox(self, text=value)
            checkbox.grid(row=0, column=i+1, padx=10, pady=(5, 5))
            self.checkboxes.append(checkbox)
    
    def get_checkbox_by_text(self, text):
        for checkbox in self.checkboxes:
            if checkbox.cget("text") == text:
                return checkbox

class StockInfoFrame(CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # 创建股票代码和名称
        self.stock_code = CTkLabel(self, fg_color="gray30", corner_radius=6, font=ctk.CTkFont(size=20))
        self.stock_code.grid(row = 0, column = 0, padx=10)
        self.stock_name = CTkLabel(self, fg_color="gray30", corner_radius=6, font=ctk.CTkFont(size=20))
        self.stock_name.grid(row = 0, column = 1, padx=10)

class StockDetailView(CTkFrame):    
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        # let child widgets use the whole window space
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(4, weight=1)
        self.grid_rowconfigure(1, weight=1)
        # 创建股票信息控件
        self.stock_info_frame = StockInfoFrame(self)
        self.stock_info_frame.grid(row = 0, column = 0)
        # 创建日期输入控件和刷新按钮
        self.start_date_frame = DateFrame(self, "开始日期:")
        self.start_date_frame.grid(row = 0, column = 1)
        self.end_date_frame = DateFrame(self, "结束日期:")
        self.end_date_frame.grid(row = 0, column = 2)        
        # 创建刷新按钮
        self.refresh_button = CTkButton(self, text="刷新")
        self.refresh_button.grid(row = 0, column = 3)
        # 创建基础股市指标选项框
        self.stock_indicator_frame = StockIndicatorCheckboxFrame(self, "指标", values=[STOCK_INDICATOR_MA, STOCK_INDICATOR_MAGIC_NINE])
        self.stock_indicator_frame.grid(row = 0, column = 4)
        
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
        self.canvas._tkcanvas.grid(row = 1,column = 0, sticky="nsew", columnspan=5)
    
        # 创建注释文本，初始时不可见
        self.annot = self.ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                            bbox=dict(boxstyle=ctk.ROUND, fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)
        
        # 添加水平虚线和垂直虚线
        self.horizontal_line = self.ax.axhline(y=0, color='gray', linestyle='--', linewidth=1, visible=False)
        self.vertical_line = self.ax.axvline(x=0, color='gray', linestyle='--', linewidth=1, visible=False)

        # 添加 MA 线
        self.ma_lines = []
        
        # 添加神奇九转标记
        self.magic_nine_annotations= []