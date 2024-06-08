from config import K_TRAINING_FRAME
from config import MA_COLOR_MAP, STOCK_INDICATOR_MA, STOCK_INDICATOR_MAGIC_NINE
from models import Model
from views import View

from .__base__ import BaseController

import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc

class KTrainingController(BaseController):
    def __init__(self, view : View, model : Model) -> None:
        self.view = view
        self.model = model
        self.frame = self.view.frames[K_TRAINING_FRAME]
        # 关闭刷新按钮
        self.frame.trading_frame.refresh_button.configure(state='disabled')
        # 连接鼠标悬浮事件处理函数
        self.frame.canvas.mpl_connect("motion_notify_event", self.hover)
        self.frame.canvas.mpl_connect('scroll_event', self.zoom_and_pan)
        # 连接checkbox的指标绘制事件
        self.frame.stock_indicator_frame.get_checkbox_by_text(text=STOCK_INDICATOR_MA).configure(command = self.refresh_ma)
        self.frame.stock_indicator_frame.get_checkbox_by_text(text=STOCK_INDICATOR_MAGIC_NINE).configure(command = self.refresh_m9)
        # 连接控制按钮对应的函数并设置键盘快捷方式
        self.frame.trading_frame.buy_button.configure(command = self.buy)
        self.frame.trading_frame.sell_button.configure(command = self.sell)
        self.frame.trading_frame.next_button.configure(command = self.next_day)
        self.frame.trading_frame.refresh_button.configure(command = self.start_a_new_play)
        # 买入：上键
        # 卖出：下键
        # 下一日：空格键
        view.bind("<Up>", lambda event: self.buy())
        view.bind("<Down>", lambda event: self.sell())
        view.bind("<space>", lambda event: self.next_day())
        # 窗口开启后默认绘制一次
        self.refresh_figure()
        self.update_pocket_frame()

    # 更新注释文本的内容和位置
    def update_annot(self, ohlc, x, y):
        text = f"open: {ohlc[1]}\nclose: {ohlc[2]}\nhigh: {ohlc[3]}\nlow: {ohlc[4]}"
        self.frame.annot.xy = (x, y)
        self.frame.annot.set_text(text)
        self.frame.annot.get_bbox_patch().set_alpha(0.4)

    # 鼠标悬停事件处理函数
    def hover(self, event):
        is_annot_vis = self.frame.annot.get_visible()
        is_lines_vis = self.frame.mouse_horizontal_line.get_visible()
        if event.inaxes == self.frame.ax:
            for _, bar in enumerate(self.model.k_training_model.quotes):
                if bar[0] - 0.3 <= event.xdata <= bar[0] + 0.3:
                    # 绘制注释
                    self.update_annot(bar, bar[0], bar[4])
                    self.frame.annot.set_visible(True)
                    # 绘制虚线
                    self.frame.mouse_horizontal_line.set_ydata([event.ydata, event.ydata])  # 注意这里将 ydata 包装成列表
                    self.frame.mouse_vertical_line.set_xdata([bar[0], bar[0]])  # 注意这里将 xdata 包装成列表
                    self.frame.mouse_horizontal_line.set_visible(True)
                    self.frame.mouse_vertical_line.set_visible(True)
                    self.frame.fig.canvas.draw_idle()
                    return
        # 鼠标不在 K 线图内时隐藏注释
        if is_annot_vis:
            self.frame.annot.set_visible(False)
            self.frame.fig.canvas.draw_idle()
        # 鼠标不在 K 线图内时隐藏虚线
        if is_lines_vis:
            self.frame.mouse_horizontal_line.set_visible(False)
            self.frame.mouse_vertical_line.set_visible(False)
            self.frame.fig.canvas.draw_idle()

    # 刷新数据并重新绘制图表的函数
    def refresh_figure(self):
        # 清除旧的图表
        self.frame.ax.clear()

        # 绘制新的 K 线图
        candlestick_ohlc(self.frame.ax, self.model.k_training_model.quotes, width=0.6, colorup='r', colordown='g', alpha=0.8)
        self.frame.ax.xaxis_date()
        self.frame.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.frame.ax.grid(True)
        # 这是训练开始时的x轴范围
        new_xlim = [mdates.date2num(self.model.k_training_model.start_date), self.model.k_training_model.start_training_date_in_float]
        self.frame.ax.set_xlim(new_xlim)
        # 隐藏刻度标签
        # self.frame.ax.set_xticklabels([])

        # 重绘图表
        self.frame.canvas.draw_idle()
        # 为新图表添加注释文本
        self.frame.annot = self.frame.ax.annotate("", xy=(0,0), xytext=(10,20), textcoords="offset points",
                            bbox=dict(boxstyle='round', fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        self.frame.annot.set_visible(False)
        # 为新图表添加注释虚线
        self.frame.mouse_horizontal_line = self.frame.ax.axhline(y=self.model.k_training_model.quotes[0][1], color='gray', linestyle='--', linewidth=1, visible=False)
        self.frame.mouse_vertical_line = self.frame.ax.axvline(x=self.model.k_training_model.quotes[0][0], color='gray', linestyle='--', linewidth=1, visible=False)
        # 重新绘制平均线
        self.frame.ma_lines.clear()
        self.refresh_ma()
        # 重新绘制神奇九转标记
        self.frame.magic_nine_annotations.clear()
        self.refresh_m9()
        # 重新绘制训练起始虚线
        self.frame.start_training_vertical_line = self.frame.ax.axvline(x=self.model.k_training_model.start_training_date_in_float, color='red', linestyle='--', linewidth=2)
        # 重新绘制买入、卖出标记
        self.frame.buy_annotations.clear()
        self.frame.sell_annotations.clear()
        # 重新绘制开仓成本线
        self.frame.open_cost_price_line = self.frame.ax.axhline(y=self.model.k_training_model.quotes[0][1], color='orange', linestyle='--', linewidth=2, visible=False)
   
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
        self.frame.canvas.draw_idle()
    
    # 训练进入下一个交易日
    def next_day(self):
        self.model.k_training_model.go_to_next_day()
        # 更新图表x轴范围
        cur_xlim = self.frame.ax.get_xlim()
        new_xlim = [cur_xlim[0], self.model.k_training_model.current_training_date_in_float]
        self.frame.ax.set_xlim(new_xlim)
        # 根据新的x轴范围计算y轴的最大最小值
        low_min, high_max = self.model.k_training_model.find_price_range(new_xlim[0], new_xlim[1])
        self.frame.ax.set_ylim([low_min, high_max])
        # 更新新一天的交易信息
        self.update_pocket_frame()
        # 重绘图表
        self.frame.canvas.draw_idle()
        if self.model.k_training_model.is_end():
            self.settle_this_play()
            
    def settle_this_play(self):
        res = self.model.k_training_model.settel()
        if res:
            # 卖出成功
            # 绘制卖出记号
            (last_sell_record_date, last_sell_record_price) = self.model.k_training_model.get_sell_records()[-1]
            this_sell_annot = self.frame.ax.annotate("", xy=(last_sell_record_date, last_sell_record_price), xytext=(-2,20), textcoords="offset points",
                                    bbox=dict(boxstyle='round', fc="b"),
                                    arrowprops=dict(arrowstyle="->")
                                )
            this_sell_annot.set_text('S')
            this_sell_annot.get_bbox_patch().set_alpha(0.4)
            this_sell_annot.set_visible(True)
            self.frame.sell_annotations.append(this_sell_annot)
            # 隐藏成本线
            self.frame.open_cost_price_line.set_visible(False)
        # 更改控制按钮
        self.frame.trading_frame.next_button.configure(state='disabled')
        self.frame.trading_frame.buy_button.configure(state='disabled')
        self.frame.trading_frame.sell_button.configure(state='disabled')
        self.frame.trading_frame.refresh_button.configure(state='normal')
        # 更新新一天的交易信息
        self.update_pocket_frame()
        # 重绘图表
        self.frame.canvas.draw_idle()
        
    def update_pocket_frame(self):
        self.frame.pocket_frame.money_left_str.configure(text=self.model.k_training_model.get_money_left_str())
        self.frame.pocket_frame.position_str.configure(text=self.model.k_training_model.get_position_str())
        self.frame.pocket_frame.total_profit_str.configure(text=self.model.k_training_model.get_total_profit_str())
        self.frame.pocket_frame.open_profit_str.configure(text=self.model.k_training_model.get_open_profit_str())
        self.frame.pocket_frame.candle_left_str.configure(text=self.model.k_training_model.get_kandle_left_str())

    def buy(self):
        res = self.model.k_training_model.buy(1.0)
        if res:
            # 买入成功
            # 绘制买入记号
            (last_buy_record_date, last_buy_record_price) = self.model.k_training_model.get_buy_records()[-1]
            this_buy_annot = self.frame.ax.annotate("", xy=(last_buy_record_date, last_buy_record_price), xytext=(-2,20), textcoords="offset points",
                                    bbox=dict(boxstyle='round', fc="r"),
                                    arrowprops=dict(arrowstyle="->")
                                )
            this_buy_annot.set_text('B')
            this_buy_annot.get_bbox_patch().set_alpha(0.4)
            this_buy_annot.set_visible(True)
            self.frame.buy_annotations.append(this_buy_annot)
            # 绘制成本线
            open_cost_price = self.model.k_training_model.get_cost_price()
            self.frame.open_cost_price_line.set_ydata([open_cost_price, open_cost_price])
            self.frame.open_cost_price_line.set_visible(True)
        else:
            # 买入失败
            return
        self.next_day()
        
    def sell(self):
        res = self.model.k_training_model.sell(1.0)
        if res:
            # 卖出成功
            # 绘制卖出记号
            (last_sell_record_date, last_sell_record_price) = self.model.k_training_model.get_sell_records()[-1]
            this_sell_annot = self.frame.ax.annotate("", xy=(last_sell_record_date, last_sell_record_price), xytext=(-2,20), textcoords="offset points",
                                    bbox=dict(boxstyle='round', fc="b"),
                                    arrowprops=dict(arrowstyle="->")
                                )
            this_sell_annot.set_text('S')
            this_sell_annot.get_bbox_patch().set_alpha(0.4)
            this_sell_annot.set_visible(True)
            self.frame.sell_annotations.append(this_sell_annot)
            # 绘制成本线
            open_cost_price = self.model.k_training_model.get_cost_price()
            if open_cost_price is not None:
                self.frame.open_cost_price_line.set_ydata([open_cost_price, open_cost_price])
            else:
                # 若全部卖出，则隐藏成本线
                self.frame.open_cost_price_line.set_visible(False)
        else:
            # 卖出失败
            return
        self.next_day()
    
    def start_a_new_play(self):
        self.model.k_training_model.restart()
        self.refresh_figure()
        self.update_pocket_frame()
        # 更改控制按钮
        self.frame.trading_frame.next_button.configure(state='normal')
        self.frame.trading_frame.buy_button.configure(state='normal')
        self.frame.trading_frame.sell_button.configure(state='normal')
        self.frame.trading_frame.refresh_button.configure(state='disabled')
    
    # 缩放与平移事件处理函数
    def zoom_and_pan(self, event):
        base_scale = 1.03
        start_date_in_float_num = mdates.date2num(self.model.k_training_model.start_date)
        current_training_date_in_float_num = self.model.k_training_model.current_training_date_in_float
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
                new_low = max(xdata - step, start_date_in_float_num)
                new_high = min(xdata + step, current_training_date_in_float_num)
                # 如果缩放到达边界，即某一侧到极限不能再放大或缩小，则另一侧需要弥补放大或缩小的损失。
                if new_low == start_date_in_float_num:
                    if event.button == 'up':
                        new_high = cur_xlim[1] - step
                    elif event.button == 'down':
                        new_high = cur_xlim[1] + step
                    # 同样确保其不超过 quotes 范围
                    new_high = min(new_high, current_training_date_in_float_num)
                if new_high == current_training_date_in_float_num:
                    if event.button == 'up':
                        new_low = cur_xlim[0] + step
                    elif event.button == 'down':
                        new_low = cur_xlim[0] - step
                    # 同样确保其不超过 quotes 范围
                    new_low = max(new_low, start_date_in_float_num)
                # 这是新的x轴范围
                new_xlim = [new_low, new_high]
                self.frame.ax.set_xlim(new_xlim)

                # 根据新的x轴范围计算y轴的最大最小值
                low_min, high_max = self.model.k_training_model.find_price_range(new_xlim[0], new_xlim[1])
                self.frame.ax.set_ylim([low_min, high_max])
            else: 
                # 平移操作
                cur_xlim = self.frame.ax.get_xlim()
                # 平移到达左右两边后不能继续平移
                if event.button == 'up' and cur_xlim[1] == current_training_date_in_float_num:
                    return
                if event.button == 'down' and cur_xlim[0] == start_date_in_float_num:
                    return
                cur_xrange = max(1.0, (cur_xlim[1] - cur_xlim[0]) * 0.02)
                # 计算移动步长
                if event.button == 'up':
                    scale_factor = base_scale
                elif event.button == 'down':
                    scale_factor = -base_scale
                step = cur_xrange * scale_factor
                # 保证平移后不超过股价日期的上下界限
                new_low = max(cur_xlim[0] + step, start_date_in_float_num)
                new_high = min(cur_xlim[1] + step, current_training_date_in_float_num)
                # 这是新的x轴范围
                new_xlim = [new_low, new_high]
                self.frame.ax.set_xlim(new_xlim)

                # 根据新的x轴范围计算y轴的最大最小值
                low_min, high_max = self.model.k_training_model.find_price_range(new_xlim[0], new_xlim[1])
                self.frame.ax.set_ylim([low_min, high_max])
                
            self.frame.canvas.draw_idle()