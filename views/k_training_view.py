from config import STOCK_INDICATOR_MA, STOCK_INDICATOR_MAGIC_NINE

from customtkinter import CTkFrame
from customtkinter import CTkLabel
from customtkinter import CTkCheckBox
from customtkinter import CTkButton
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates

class StockIndicatorCheckboxFrame(CTkFrame):
    def __init__(self, master, title, values):
        super().__init__(master)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.title = title
        self.checkboxes = []

        self.title = CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(5, 5), sticky="nsew")

        for i, value in enumerate(self.values):
            checkbox = CTkCheckBox(self, text=value)
            checkbox.grid(row=0, column=i+1, padx=1, pady=(5, 5))
            self.checkboxes.append(checkbox)
    
    def get_checkbox_by_text(self, text):
        for checkbox in self.checkboxes:
            if checkbox.cget("text") == text:
                return checkbox

class TradingFrame(CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        # 买入按钮
        self.buy_button = CTkButton(self, width=100, text="Buy(↑)", fg_color='red', font=ctk.CTkFont(weight='bold', size=14))
        self.buy_button.grid(row=0, column=0, padx=5)
        # 卖出按钮
        self.sell_button = CTkButton(self, width=100, text="Sell(↓)", fg_color='blue', font=ctk.CTkFont(weight='bold', size=14))
        self.sell_button.grid(row=0, column=1, padx=5)
        # 下一日按钮
        self.next_button = CTkButton(self, width=100, text="Next(空格)", font=ctk.CTkFont(weight='bold', size=14))
        self.next_button.grid(row=0, column=2, padx=5)
        # 刷新按钮
        self.refresh_button = CTkButton(self, width=100, text="下一局", font=ctk.CTkFont(weight='bold', size=14))
        self.refresh_button.grid(row=0, column=3, padx=5)

class PocketFrame(CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # 钱包额度
        self.money_left_str = CTkLabel(self, text='0', fg_color="gray30", corner_radius=6, font=ctk.CTkFont(weight='bold', size=14))
        self.money_left_str.grid(row=0, column=0, padx=20)
        self.money_left = CTkLabel(self, text='钱包余额', fg_color="gray30", corner_radius=6)
        self.money_left.grid(row=1, column=0, padx=20)
        # 仓位
        self.position_str = CTkLabel(self, text='0%', fg_color="gray30", corner_radius=6, font=ctk.CTkFont(weight='bold', size=14))
        self.position_str.grid(row=0, column=1, padx=10)
        self.position = CTkLabel(self, text='仓位', fg_color="gray30", corner_radius=6)
        self.position.grid(row=1, column=1, padx=10)
        # 本局收益
        self.total_profit_str = CTkLabel(self, text='0%', fg_color="gray30", corner_radius=6, font=ctk.CTkFont(weight='bold', size=14))
        self.total_profit_str.grid(row=0, column=2, padx=10)
        self.total_profit = CTkLabel(self, text='本局收益', fg_color="gray30", corner_radius=6)
        self.total_profit.grid(row=1, column=2, padx=10)
        # 开仓收益
        self.open_profit_str = CTkLabel(self, text='0%', fg_color="gray30", corner_radius=6, font=ctk.CTkFont(weight='bold', size=14))
        self.open_profit_str.grid(row=0, column=3, padx=10)
        self.open_profit = CTkLabel(self, text='开仓收益', fg_color="gray30", corner_radius=6)
        self.open_profit.grid(row=1, column=3, padx=10)
        # 剩余k线
        self.candle_left_str = CTkLabel(self, text='150', fg_color="gray30", corner_radius=6, font=ctk.CTkFont(weight='bold', size=14))
        self.candle_left_str.grid(row=0, column=4, padx=10)
        self.candle_left = CTkLabel(self, text='剩余k线', fg_color="gray30", corner_radius=6)
        self.candle_left.grid(row=1, column=4, padx=10)

class KTrainingView(CTkFrame):    
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        # let child widgets use the whole window space
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=100)
        # 创建买入卖出按钮
        self.trading_frame = TradingFrame(self)
        self.trading_frame.grid(row=0, column=0)
        # 创建基础股市指标选项框
        self.stock_indicator_frame = StockIndicatorCheckboxFrame(self, "指标", values=[STOCK_INDICATOR_MA, STOCK_INDICATOR_MAGIC_NINE])
        self.stock_indicator_frame.grid(row=0, column=1)
        # 创建利润详情显示框
        self.pocket_frame = PocketFrame(self) 
        self.pocket_frame.grid(row=0, column=2)
        
        # 创建 matplotlib 图表
        self.fig = Figure()
        # 调整绘图的面积，尽可能充满整个窗口
        self.fig.subplots_adjust(left=0.03, right=0.97, bottom=0.05, top=0.99)
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
        
        # 添加鼠标悬浮水平虚线和垂直虚线
        self.mouse_horizontal_line = self.ax.axhline(y=0, color='gray', linestyle='--', linewidth=1, visible=False)
        self.mouse_vertical_line = self.ax.axvline(x=0, color='gray', linestyle='--', linewidth=1, visible=False)
        
        # 添加 MA 线
        self.ma_lines = []
        
        # 添加神奇九转标记
        self.magic_nine_annotations= []
        
        # 添加训练起始虚线
        self.start_training_vertical_line = None

        # 买入标记
        self.buy_annotations=[]

        # 卖出标记
        self.sell_annotations=[]
    