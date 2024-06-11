from config import STOCK_DETAIL_FRAME
from config import MA_COLOR_MAP, STOCK_INDICATOR_MA, STOCK_INDICATOR_MAGIC_NINE
from models.stock_detail_model import StockDetailModel
from views.stock_detail_window import StockDetailWindow

from .__base__ import BaseController

from datetime import datetime, timedelta
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc

class StockDetailController(BaseController):
    def __init__(self, view : StockDetailWindow, model : StockDetailModel) -> None:
        self.view = view
        self.model = model
        self.frame = self.view.frames[STOCK_DETAIL_FRAME]
        # 存放股票历史数据
        # '日期', '开盘', '最高', '最低', '收盘'
        self.quotes = []
        # 修改股票名称和股票代码
        self.frame.stock_info_frame.stock_code.configure(text=self.model.get_stock_code())
        self.frame.stock_info_frame.stock_name.configure(text=self.model.get_stock_name())
        # 连接鼠标悬浮事件和滚轮放大事件处理函数
        self.frame.canvas.mpl_connect("motion_notify_event", self.hover)
        self.frame.canvas.mpl_connect('scroll_event', self.zoom_and_pan)
        # 连接按钮的刷新数据事件
        self.frame.refresh_button.configure(command = self.refresh_data)
        # 链接checkbox的指标绘制事件
        self.frame.stock_indicator_frame.get_checkbox_by_text(text=STOCK_INDICATOR_MA).configure(command = self.refresh_ma)
        self.frame.stock_indicator_frame.get_checkbox_by_text(text=STOCK_INDICATOR_MAGIC_NINE).configure(command = self.refresh_m9)
        # 窗口开启后默认绘制一次
        self.refresh_data()
        
    # 更新注释文本的内容和位置
    def update_annot(self, ohlc, x, y):
        date = mdates.num2date(ohlc[0]).strftime('%Y-%m-%d')
        text = f"{date}\nopen: {ohlc[1]}\nclose: {ohlc[2]}\nhigh: {ohlc[3]}\nlow: {ohlc[4]}"
        self.frame.annot.xy = (x, y)
        self.frame.annot.set_text(text)
        self.frame.annot.get_bbox_patch().set_alpha(0.4)

    # 鼠标悬停事件处理函数
    def hover(self, event):
        is_annot_vis = self.frame.annot.get_visible()
        is_lines_vis = self.frame.horizontal_line.get_visible()
        if event.inaxes == self.frame.ax:
            for _, bar in enumerate(self.quotes):
                if bar[0] - 0.3 <= event.xdata <= bar[0] + 0.3:
                    # 绘制注释
                    self.update_annot(bar, bar[0], bar[4])
                    self.frame.annot.set_visible(True)
                    # 绘制虚线
                    self.frame.horizontal_line.set_ydata([event.ydata, event.ydata])  # 注意这里将 ydata 包装成列表
                    self.frame.vertical_line.set_xdata([bar[0], bar[0]])  # 注意这里将 xdata 包装成列表
                    self.frame.horizontal_line.set_visible(True)
                    self.frame.vertical_line.set_visible(True)
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

    # 缩放与平移事件处理函数
    def zoom_and_pan(self, event):
        base_scale = 1.03
        if event.button == 'up' or event.button == 'down':
            if event.key == 'control':
                # 按下 Ctrl 键则代表放大或缩小
                cur_xlim = self.frame.ax.get_xlim()
                cur_xrange = max(1.0, cur_xlim[1] - cur_xlim[0])
                xdata = event.xdata
                if event.button == 'up':
                    scale_factor = 1 / base_scale
                elif event.button == 'down':
                    scale_factor = base_scale
                # 计算移动步长
                step = cur_xrange * scale_factor / 2
                # 保证移动后不超过股价日期的上下界限
                new_low = max(xdata - step, self.model.quotes[0][0])
                new_high = min(xdata + step, self.model.quotes[-1][0])
                # 如果缩放到达边界，即某一侧到极限不能再放大或缩小，则另一侧需要弥补放大或缩小的损失。
                if new_low == self.model.quotes[0][0]:
                    if event.button == 'up':
                        new_high = cur_xlim[1] - step
                    elif event.button == 'down':
                        new_high = cur_xlim[1] + step
                    # 同样确保其不超过 quotes 范围
                    new_high = min(new_high, self.model.quotes[-1][0])
                if new_high == self.model.quotes[-1][0]:
                    if event.button == 'up':
                        new_low = cur_xlim[0] + step
                    elif event.button == 'down':
                        new_low = cur_xlim[0] - step
                    # 同样确保其不超过 quotes 范围
                    new_low = max(new_low, self.model.quotes[0][0])
                # 这是新的x轴范围
                new_xlim = [new_low, new_high]
                self.frame.ax.set_xlim(new_xlim)

                # 根据新的x轴范围计算y轴的最大最小值
                low_min, high_max = self.model.find_price_range(new_xlim[0], new_xlim[1])
                self.frame.ax.set_ylim([low_min, high_max])
            else: 
                # 平移操作
                cur_xlim = self.frame.ax.get_xlim()
                # 平移到达左右两边后不能继续平移
                if event.button == 'up' and cur_xlim[1] == self.model.quotes[-1][0]:
                    return
                if event.button == 'down' and cur_xlim[0] == self.model.quotes[0][0]:
                    return
                cur_xrange = max(1.0, (cur_xlim[1] - cur_xlim[0]) * 0.02)
                # 计算移动步长
                if event.button == 'up':
                    scale_factor = base_scale
                elif event.button == 'down':
                    scale_factor = -base_scale
                step = cur_xrange * scale_factor
                # 保证平移后不超过股价日期的上下界限
                new_low = max(cur_xlim[0] + step, self.model.quotes[0][0])
                new_high = min(cur_xlim[1] + step, self.model.quotes[-1][0])
                # 这是新的x轴范围
                new_xlim = [new_low, new_high]
                self.frame.ax.set_xlim(new_xlim)

                # 根据新的x轴范围计算y轴的最大最小值
                low_min, high_max = self.model.find_price_range(new_xlim[0], new_xlim[1])
                self.frame.ax.set_ylim([low_min, high_max])
                
            self.frame.canvas.draw_idle()

     # 刷新数据并重新绘制图表的函数
    def refresh_data(self):
        # 获取股票价格开始和结束时间
        start_date = self.frame.start_date_frame.date_entry.get()
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y%m%d')

        end_date = self.frame.end_date_frame.date_entry.get()
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y%m%d')
        self.quotes = self.model.get_stock_quotes(start_date, end_date)

        # 清除旧的图表
        self.frame.ax.clear()

        # 绘制新的 K 线图
        candlestick_ohlc(self.frame.ax, self.quotes, width=0.6, colorup='r', colordown='g', alpha=0.8)
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
        self.frame.horizontal_line = self.frame.ax.axhline(y=self.quotes[0][1], color='gray', linestyle='--', linewidth=1, visible=False)
        self.frame.vertical_line = self.frame.ax.axvline(x=self.quotes[0][0], color='gray', linestyle='--', linewidth=1, visible=False)
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
                ma_lines = self.model.get_MAs()
                if ma_lines is None:
                    return
                for key, value in ma_lines.items():
                    self.frame.ma_lines.append(self.frame.ax.plot(self.quotes[:, 0], value, label=key, color=MA_COLOR_MAP[key])[0])
            else:  # 如果 MA 线已经绘制，则显示它们
                for ma_line in self.frame.ma_lines:
                    ma_line.set_visible(True)
            self.frame.ax.legend()
        else:
            # 如果 MA 线已经绘制，则隐藏它们
            for ma_line in self.frame.ma_lines:
                ma_line.set_visible(False)
                # 隐藏图例
                self.frame.ax.legend().set_visible(False)
        self.frame.canvas.draw_idle()

    # 神奇九转的绘制函数
    # 根据 checkbox 的状态绘制或隐藏
    def refresh_m9(self):
        if self.frame.stock_indicator_frame.get_checkbox_by_text(text=STOCK_INDICATOR_MAGIC_NINE).get():
            # 如果 M9 还未绘制，则绘制它们
            if len(self.frame.magic_nine_annotations) == 0:
                m9_annots = self.model.get_M9s()
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
            else:  # 如果 M9 已经绘制，则显示它们
                for m9_annot in self.frame.magic_nine_annotations:
                    m9_annot.set_visible(True)
        else:
            # 如果 M9 已经绘制，则隐藏它们
            for m9_annot in self.frame.magic_nine_annotations:
                m9_annot.set_visible(False)
        self.frame.canvas.draw_idle()