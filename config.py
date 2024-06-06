# ==== Application Configs ====
# Application Title
APP_NAME="AMarktTool"

# Application Width
APP_WIDTH=1000

# Application Minimal Width
APP_MIN_WIDTH=600

# Application Height
APP_HEIGHT=750

# Application Minimal Height
APP_MIN_HEIGHT=700

# Frames
MAGIC_NINE_FRAME='magic_nine'
K_TRAINING_FRAME='k_training'
WELCOME_FRAME='welcome'

# Windows
STOCK_DETAIL_WINDOW='stock_detail'

# Models
STOCK_DETAIL_MODEL='stock_detail'

# ==== Controller Configs ====
STOCK_DETAIL_CONTROLLER=STOCK_DETAIL_WINDOW
EVENT_OPEN_STOCK_DETAIL='OPEN_STOCK_DETAIL_WINDOWS'
EVENT_HIDE_STOCK_DETAIL='HIDE_STOCK_DETAIL_WINDOWS'

# ==== Menu Configs ====
MAGIC_NINE_BTN='神奇九转'
MAGIC_NINE_BTN_DISABLED='神奇九转加载中...'
K_TRAINING_BTN='K线训练'

# ==== Welcome Page Configs ====
WELCOME_MSG='欢迎使用 AMarktTool :)\n'

# ==== Magic Nine Page Configs ====
TABLE_WIDTH_INDEX=20 
TABLE_WIDTH_STOCK_CODE=180
TABLE_WIDTH_STOCK_NAME=250
TABLE_WIDTH_SIGNAL_DATE=250

TABLE_INDEX='#'
TABLE_STOCK_CODE='代码'
TABLE_STOCK_NAME='名称'
TABLE_SIGNAL_DATE='信号日期'

AK_DATE_FORMAT="%Y%m%d"
AK_DATAFRAME_DATE='日期'
AK_DATAFRAME_CLOSING_PRICE='收盘'

# ==== Stock Detail Window Configs ====
# Window Width and Height
STOCK_DETAIL_WINDOW_WIDTH=1500
STOCK_DETAIL_WINDOW_HEIGHT=800

# Frames
STOCK_DETAIL_FRAME='stock_detail'

# MA color map
MA_COLOR_MAP = {
    'MA5': 'black',
    'MA10': 'orange',
    'MA20': 'pink',
}

# stock indicator's nicknames
STOCK_INDICATOR_MA='MA'
STOCK_INDICATOR_MAGIC_NINE='M9'

# ==== K Training Configs ====
# default values when training starts
K_TRAINING_DEFAULT_KANDLE_LEFT=150
K_TRAINING_DEFAULT_MONEY_LEFT=10000

# stock data structure
STOCK_DATA_CODE='代码'
STOCK_DATA_NAME='名称'
STOCK_DATA_LISTING_DATE='上市日期'

# moving average lines
K_TRAINING_MA_LINE_5='MA5'
K_TRAINING_MA_LINE_10='MA10'
K_TRAINING_MA_LINE_20='MA20'

# ==== akshare API Configs ====
AK_API_SH_STOCK_NAME='证券简称'
AK_API_SZ_STOCK_NAME='A股简称'
AK_API_STUPID_ST='ST'
AK_API_HIST_DF_DATE='日期'
AK_API_HIST_DF_OPEN='开盘'
AK_API_HIST_DF_CLOSE='收盘'
AK_API_HIST_DF_HIGH='最高'
AK_API_HIST_DF_LOW='最低'
AK_API_STOCK_DF_NAME='名称'
