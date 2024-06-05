from config import K_TRAINING_FRAME
from config import MA_COLOR_MAP, STOCK_INDICATOR_MA, STOCK_INDICATOR_MAGIC_NINE
from models import Model
from views import View

from .__base__ import BaseController

from datetime import datetime, timedelta
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc

class KTrainingController(BaseController):
    def __init__(self, view : View, model : Model) -> None:
        self.view = view
        self.model = model
        self.frame = self.view.frames[K_TRAINING_FRAME]
        # 连接鼠标悬浮事件处理函数
        self.frame.canvas.mpl_connect("motion_notify_event", self.hover)
        # 链接checkbox的指标绘制事件
        self.frame.stock_indicator_frame.get_checkbox_by_text(text=STOCK_INDICATOR_MA).configure(command = self.refresh_ma)
        self.frame.stock_indicator_frame.get_checkbox_by_text(text=STOCK_INDICATOR_MAGIC_NINE).configure(command = self.refresh_m9)
        # 窗口开启后默认绘制一次
        self.refresh_data()
        
    # 更新注释文本的内容和位置
    def update_annot(self, ohlc, x, y):
        date = mdates.num2date(ohlc[0]).strftime('%Y-%m-%d')
        text = f"date: {date}\nopen: {ohlc[1]}\nclose: {ohlc[2]}\nhigh: {ohlc[3]}\nlow: {ohlc[4]}"
        self.frame.annot.xy = (x, y)
        self.frame.annot.set_text(text)
        self.frame.annot.get_bbox_patch().set_alpha(0.4)

    # 鼠标悬停事件处理函数
    def hover(self, event):
        is_annot_vis = self.frame.annot.get_visible()
        is_lines_vis = self.frame.horizontal_line.get_visible()
        if event.inaxes == self.frame.ax:
            # 绘制虚线
            self.frame.horizontal_line.set_ydata([event.ydata, event.ydata])  # 注意这里将 ydata 包装成列表
            self.frame.vertical_line.set_xdata([event.xdata, event.xdata])  # 注意这里将 xdata 包装成列表
            self.frame.horizontal_line.set_visible(True)
            self.frame.vertical_line.set_visible(True)
            self.frame.fig.canvas.draw_idle()
            # 绘制注释
            for _, bar in enumerate(self.model.k_training_model.quotes):
                if bar[0] - 0.3 <= event.xdata <= bar[0] + 0.3:
                    self.update_annot(bar, event.xdata, event.ydata)
                    self.frame.annot.set_visible(True)
                    self.frame.fig.canvas.draw_idle()
                    return
        # 鼠标不在 K 线图内时隐藏注释
        if is_annot_vis:
            self.frame.annot.set_visible(False)
            self.frame.fig.canvas.draw_idle()
        # 鼠标不在 K 线图内时隐藏虚线
        if is_lines_vis:
            self.frame.horizontal_line.set_visible(False)
            self.frame.vertical_line.set_visible(False)
            self.frame.fig.canvas.draw_idle()

    # 刷新数据并重新绘制图表的函数
    def refresh_data(self):
        # 清除旧的图表
        self.frame.ax.clear()

        # 绘制新的 K 线图
        candlestick_ohlc(self.frame.ax, self.model.k_training_model.quotes, width=0.6, colorup='r', colordown='g', alpha=0.8)
        self.frame.ax.xaxis_date()
        self.frame.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.frame.ax.grid(True)

        # 重绘图表
        self.frame.canvas.draw_idle()
        # 为新图表添加注释文本
        self.frame.annot = self.frame.ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                            bbox=dict(boxstyle='round', fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        self.frame.annot.set_visible(False)
        # 为新图表添加注释虚线
        self.frame.horizontal_line = self.frame.ax.axhline(y=self.model.k_training_model.quotes[0][1], color='gray', linestyle='--', linewidth=1, visible=False)
        self.frame.vertical_line = self.frame.ax.axvline(x=self.model.k_training_model.quotes[0][0], color='gray', linestyle='--', linewidth=1, visible=False)
        # 重新绘制平均线
        self.frame.ma_lines.clear()
        self.refresh_ma()
        # 重新绘制神奇九转标记
        self.frame.magic_nine_annotations.clear()
        self.refresh_m9()
        
    # 移动平均线的绘制函数
    # 根据 checkbox 的状态绘制或隐藏
    def refresh_ma(self):
        if self.frame.stock_indicator_frame.get_checkbox_by_text(text=STOCK_INDICATOR_MA).get():
            # 如果 MA 线还未绘制，则绘制它们
            if len(self.frame.ma_lines) == 0:
                ma_lines = self.model.k_training_model.get_MAs()
                if ma_lines is None:
                    return
                for key, value in ma_lines.items():
                    self.frame.ma_lines.append(self.frame.ax.plot(self.model.k_training_model.quotes[:, 0], value, label=key, color=MA_COLOR_MAP[key])[0])
            else:  # 如果 MA 线已经绘制，则显示它们
                for ma_line in self.frame.ma_lines:
                    ma_line.set_visible(True)
        else:
            # 如果 MA 线已经绘制，则隐藏它们
            for ma_line in self.frame.ma_lines:
                ma_line.set_visible(False)
        self.frame.ax.legend()
        self.frame.canvas.draw_idle()

    # 神奇九转的绘制函数
    # 根据 checkbox 的状态绘制或隐藏
    def refresh_m9(self):
        if self.frame.stock_indicator_frame.get_checkbox_by_text(text=STOCK_INDICATOR_MAGIC_NINE).get():
            # 如果 MA 线还未绘制，则绘制它们
            if len(self.frame.magic_nine_annotations) == 0:
                m9_annots = self.model.k_training_model.get_M9s()
                if m9_annots is None:
                    return
                for (x, y) in m9_annots:
                    this_annot = self.frame.ax.annotate("", xy=(x, y), xytext=(-2,20), textcoords="offset points",
                                    bbox=dict(boxstyle='round', fc="r"),
                                    arrowprops=dict(arrowstyle="->")
                                )
                    this_annot.set_text('9')
                    this_annot.get_bbox_patch().set_alpha(0.4)
                    self.frame.magic_nine_annotations.append(this_annot)
            else:  # 如果 MA 线已经绘制，则显示它们
                for m9_annot in self.frame.magic_nine_annotations:
                    m9_annot.set_visible(True)
        else:
            # 如果 MA 线已经绘制，则隐藏它们
            for m9_annot in self.frame.magic_nine_annotations:
                m9_annot.set_visible(False)
        self.frame.ax.legend()
        self.frame.canvas.draw_idle()