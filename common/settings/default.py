from datetime import datetime, timedelta


class DefaultConfig(object):
    """
    FLASK默认配置
    """
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:0820^ABcd@124.221.232.186:3306/bigfish_edu'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 追踪数据的修改信号
    SQLALCHEMY_ECHO = False

    # miniProgress Settings
    APP_ID = 'wxbb6d7c5f0f46a40b'
    APP_SECRET = 'd58b82b21eb58cf31f4d587e56790a0e'

    # JWT配置
    JWT_SECRET = 'LSJFLSJFLWE23O9UDFNSDFfkdhfkhsd2328423829347kdjhf09d78fv8usdhmzbniW#$%^&FDGHFRGH^%hgsdfksdhw8ry3'
    EXPIRY = datetime.utcnow() + timedelta(days=14)