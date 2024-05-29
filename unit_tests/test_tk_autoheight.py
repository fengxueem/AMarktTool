from tkinter import ttk, Tk, Frame, Canvas, Scrollbar, Label, Entry, Button, StringVar
 
 
def get_size(screen_width, screen_height, frame_width, frame_height, scrollbar_zise=15):
    # canvas_width: 画布宽度, canvas_height: 画布高度
    # scroll_area_width: 滚动区域宽度, scroll_area_height: 滚动区域高度
    if screen_width >= frame_width and screen_height >= frame_height:  # 没有滚动条
        canvas_width = frame_width
        canvas_height = frame_height
        scroll_area_width = frame_width
        scroll_area_height = frame_height
    elif screen_width >= frame_width and screen_height < frame_height:  # 只有垂直滚动条
        canvas_width = frame_width + scrollbar_zise
        canvas_height = screen_height
        scroll_area_width = frame_width + scrollbar_zise  # 增加垂直滚动条占用的高度
        scroll_area_height = frame_height
    elif screen_width < frame_width and screen_height >= frame_height:  # 只有水平滚动条
        canvas_width = screen_width
        canvas_height = frame_height + scrollbar_zise
        scroll_area_width = frame_width
        scroll_area_height = frame_height + scrollbar_zise  # 增加水平滚动条占用的高度
    elif screen_width < frame_width and screen_height < frame_height:  # 同时有水平和垂直滚动条
        canvas_width = screen_width
        canvas_height = screen_height
        scroll_area_width = frame_width + scrollbar_zise  # 增加垂直滚动条占用的高度
        scroll_area_height = frame_height + scrollbar_zise  # 增加水平滚动条占用的高度
    return canvas_width, canvas_height, scroll_area_width, scroll_area_height
 
 
def paint_canvas(root, frame_class, scrollbar_zise=15):
    # 生成画布，把frame绘制到画布上
    canvas = Canvas(root)
    frame = frame_class(canvas)
    root.frame = frame
 
    frame.update()  # 刷新后才能获取到组件加载后的总内容尺寸
    screen_width, screen_height = frame.winfo_screenwidth(), frame.winfo_screenheight()
    # 测试参数：
    # screen_width, screen_height = 1515, 920
    # screen_width, screen_height = 1000, 920
    # screen_width, screen_height = 1515, 600
    # screen_width, screen_height = 1000, 600
    # screen_width, screen_height = 1920, 600
    # screen_width, screen_height = 1000, 1080
 
    frame_width, frame_height = frame.winfo_reqwidth(), frame.winfo_reqheight()
    canvas_width, canvas_height, scroll_area_width, scroll_area_height = get_size(screen_width, screen_height, frame_width, frame_height, scrollbar_zise)
 
    # 垂直滚动条
    if scroll_area_height > canvas_height:
        vbar = Scrollbar(canvas, cursor='hand1', orient='vertical', command=canvas.yview)
        vbar.place(x=canvas_width - scrollbar_zise, width=scrollbar_zise, height=canvas_height)
        canvas.config(yscrollcommand=vbar.set)  # 绑定画布和滚动条的滚动
 
    # 水平滚动条
    if scroll_area_width > canvas_width:
        # 如果有垂直滚动条，水平滚动条宽度要减去垂直滚动条宽度
        hbar_width = canvas_width - (scroll_area_height > canvas_height and scrollbar_zise or 0)
        hbar = Scrollbar(canvas, cursor='hand1', orient='horizontal', command=canvas.xview)
        hbar.place(y=canvas_height - scrollbar_zise, width=hbar_width, height=scrollbar_zise)
        canvas.config(xscrollcommand=hbar.set)  # 绑定画布和滚动条的滚动
 
    # 刷新画布尺寸参数
    canvas.config(width=canvas_width, height=canvas_height, scrollregion=(0, 0, scroll_area_width, scroll_area_height))
 
    # 创建画布可见内容窗口，注意尺寸为frame尺寸的一半
    canvas.create_window((int(frame_width / 2), int(frame_height / 2)), window=frame)
    canvas.grid(row=0, column=0, padx=0, pady=0)
 
    # 返回窗口在屏幕中的位置
    return int((screen_width - canvas_width) / 2), int((screen_height - canvas_height - 100) / 2)
 
 
def paint_root(root, title, frame_class):
    # scrollbar_zise为滚动条的高度或者宽度
    root.title(title)
    root.resizable(False, False)  # 禁用窗口缩放
    root.update_idletasks()
 
    paint_x, paint_y = paint_canvas(root, frame_class)  # 在root上绘制画布
 
    # 调整窗口位置
    root.geometry('+%s+%s' % (paint_x, paint_y))
    root.deiconify()
    root.mainloop()
 
 
class TableFrame(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
 
        incr_button = Button(self, text='增加表格', command=self.incr_table)
        incr_button.grid(row=0, column=1, pady=10)
 
        decr_button = Button(self, text='缩减表格', command=self.decr_table)
        decr_button.grid(row=0, column=3, pady=10)
 
        self.table = ttk.Treeview(self, height=45, show='headings')  # 显示45行
        self.table['columns'] = tuple(['□'] + [str(i + 1) for i in range(15)])
        for column in self.table['columns']:
            self.table.column(column, width=100)
            self.table.heading(column, text=column)
        self.table.heading('□', command=self.select_all)  # 表头选框绑定事件
        self.table.column('□', width=20)  # 调整列宽
 
        # 控制隐藏列
        displaycolumns = []
        for col in self.table['columns']:
            if col != '隐藏列名':
                displaycolumns.append(col)
        self.table['displaycolumns'] = displaycolumns
 
        self.table.bind('<Double-1>', self.double_select_one)  # 绑定双击行选中事件
        self.table.bind('<ButtonRelease-1>', self.select_one)  # 绑定单击选框选中事件
        self.refresh_table_data()
 
        self.table.grid(row=1, column=0, columnspan=5, padx=0, pady=0)
 
        # 为表格增加滚动条
        vbar = Scrollbar(self, cursor='hand1', orient='vertical', command=self.table.yview)
        self.table.configure(yscrollcommand=vbar.set)
        vbar.grid(row=1, column=5, padx=0, pady=0, sticky='NS')
 
    def get_table_data(self):  # 获取表格数据，自定义表格内容时修改这个方法
        table_data = []
        for index, data in enumerate([list(range(15))] * table_root.rows):
            table_data.append(['□'] + ['%s:%s' % (index + 1, i + 1) for i in data])
        return table_data
 
    def refresh_table_data(self):  # 刷新表格数据
        self.table.heading('□', text='□')
        self.table.all_selected = False
        self.table.selected_values = {}
        for row in self.table.get_children():
            self.table.delete(row)
        for table_data in self.get_table_data():
            self.table.insert('', 'end', values=table_data)
 
    def incr_table(self):  # 表格增加一行
        table_root.rows += 1
        self.refresh_table_data()
 
    def decr_table(self):  # 表格减少一行
        table_root.rows -= 1
        self.refresh_table_data()
 
    def double_select_one(self, event):  # 双击行
        selection_row = self.table.identify('row', event.x, event.y)
        selection_column = self.table.identify('column', event.x, event.y)
        if not selection_row or not selection_column:  # 排除点击表头的情况
            return
        values = self.table.item(selection_row, 'values')
        value = values[0] == '□' and '☑' or '□'
        self.table.set(selection_row, column='#1', value=value)
        if value == '□':
            self.table.selected_values.pop(selection_row, None)
        else:
            self.table.selected_values.update({selection_row: values})
 
    def select_one(self, event):  # 单击选框
        selection_column = self.table.identify('column', event.x, event.y)
        if selection_column == '#1':  # 点击的是第一列的选框
            self.double_select_one(event)
 
    def select_all(self):  # 单击全选
        value = self.table.all_selected and '□' or '☑'
        self.table.heading('□', text=value)
        self.table.selected_values = {}
        for row in self.table.get_children():
            self.table.set(row, column='#1', value=value)
            if value == '☑':
                self.table.selected_values.update({row: self.table.item(row, 'values')})
        self.table.all_selected = not self.table.all_selected
 
 
class MainFrame(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
 
        self.rows_text = Label(self, width=8, text='行数：')
        self.rows_text.grid(row=0, column=0, padx=0, pady=10)
        self.rows_str = StringVar()
        self.rows = Entry(self, width=10, textvariable=self.rows_str)
        self.rows_str.set('100')
        self.rows.grid(row=0, column=1, padx=0, pady=10)
 
        refresh_button = Button(self, text='显示表格', command=self.refresh_table)
        refresh_button.grid(row=0, column=2, padx=4, pady=10)
 
    def refresh_table(self):
        global table_root
        if table_root is None or not table_root.children:  # 如果首次打开窗口或窗口被关闭
            table_root = Tk()
            table_root.rows = int(self.rows.get() or 100)  # 输入的行数
            paint_root(table_root, '表格界面', TableFrame)
        else:
            table_root.rows = int(self.rows.get() or 100)  # 输入的行数
            table_root.frame.refresh_table_data()
 
            # 窗口升起
            table_root.lift()
            table_root.focus_force()
 
if __name__ == '__main__':
    main_root, table_root = Tk(), None
    paint_root(main_root, '主界面', MainFrame)