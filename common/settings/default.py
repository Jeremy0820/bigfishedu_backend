from datetime import datetime, timedelta


class DefaultConfig(object):
    """
    FLASK默认配置
    """
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 追踪数据的修改信号
    SQLALCHEMY_ECHO = False

    # miniProgress Settings
    APP_ID = ''
    APP_SECRET = ''

    # JWT配置
    JWT_SECRET = 'LSJFLSJFLWE23O9UDFNSDFfkdhfkhsd2328423829347kdjhf09d78fv8usdhmzbniW#$%^&FDGHFRGH^%hgsdfksdhw8ry3'
    EXPIRY = datetime.utcnow() + timedelta(days=14)