from config import STOCK_DETAIL_FRAME
from models import Model
from views.stock_detail_window import StockDetailWindow

from .__base__ import BaseController

import akshare as ak
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc
import pandas as pd
import numpy as np

class StockDetailController(BaseController):
    def __init__(self, view : StockDetailWindow, model : Model, stock_code : str) -> None:
        self.view = view
        self.model = model
        self.frame = self.view.frames[STOCK_DETAIL_FRAME]
        self.stock_code = stock_code
        # 存放股票历史数据
        self.quotes = []

        # 连接鼠标悬浮事件和滚轮放大事件处理函数
        self.frame.fig.canvas.mpl_connect("motion_notify_event", self.hover)
        self.frame.fig.canvas.mpl_connect('scroll_event', self.zoom)
        # 连接按钮的刷新数据事件
        self.frame.refresh_button.configure(command = self.refresh_data)
        
    # 更新注释文本的内容和位置
    def update_annot(self, ohlc, x, y):
        date = mdates.num2date(ohlc[0]).strftime('%Y-%m-%d')
        text = f"date: {date}\nopen: {ohlc[1]}\nclose: {ohlc[2]}\nhigh: {ohlc[3]}\nlow: {ohlc[4]}"
        self.frame.annot.xy = (x, y)
        self.frame.annot.set_text(text)
        self.frame.annot.get_bbox_patch().set_alpha(0.4)

    # 鼠标悬停事件处理函数
    def hover(self, event):
        vis = self.frame.annot.get_visible()
        if event.inaxes == self.frame.ax:
            for i, bar in enumerate(self.quotes):
                if bar[0] - 0.3 <= event.xdata <= bar[0] + 0.3:
                    self.update_annot(bar, event.xdata, event.ydata)
                    self.frame.annot.set_visible(True)
                    self.frame.fig.canvas.draw_idle()
                    return
        if vis:
            self.frame.annot.set_visible(False)
            self.frame.fig.canvas.draw_idle()

    # 缩放事件处理函数
    def zoom(self, event):
        base_scale = 1.1
        if event.button == 'up' or event.button == 'down':
            if event.key == 'control':  # 检查是否按下 Ctrl 键
                cur_xlim = self.frame.ax.get_xlim()
                cur_ylim = self.frame.ax.get_ylim()
                cur_xrange = (cur_xlim[1] - cur_xlim[0]) * 0.5
                cur_yrange = (cur_ylim[1] - cur_ylim[0]) * 0.5
                xdata = event.xdata
                ydata = event.ydata
                if event.button == 'up':
                    scale_factor = 1 / base_scale
                elif event.button == 'down':
                    scale_factor = base_scale
                else:
                    scale_factor = 1
                self.frame.ax.set_xlim([xdata - cur_xrange * scale_factor,
                            xdata + cur_xrange * scale_factor])
                self.frame.ax.set_ylim([ydata - cur_yrange * scale_factor,
                            ydata + cur_yrange * scale_factor])
                self.frame.fig.canvas.draw_idle()

     # 刷新数据并重新绘制图表的函数
    def refresh_data(self):
        # 获取股票价格开始和结束时间
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        end_date = datetime.now().strftime('%Y%m%d')

        # 使用akshare获取股票数据
        stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=self.stock_code, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")

        # 准备数据格式
        stock_zh_a_hist_df['日期'] = pd.to_datetime(stock_zh_a_hist_df['日期'])
        stock_zh_a_hist_df['日期'] = mdates.date2num(np.array(stock_zh_a_hist_df['日期'].dt.to_pydatetime()))
        quotes = stock_zh_a_hist_df[['日期', '开盘', '最高', '最低', '收盘']].values

        # 清除旧的图表
        self.frame.ax.clear()

        # 绘制新的 K 线图
        candlestick_ohlc(self.frame.ax, quotes, width=0.6, colorup='g', colordown='r', alpha=0.8)
        self.frame.ax.xaxis_date()
        self.frame.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.frame.ax.grid(True)

        # 重绘图表
        self.frame.canvas.draw_idle()