from flask import Flask
from common.models import db
from flask_restful import Api
from edubackend.resources.bpttest import tbp
from edubackend.resources.course_bpt import course_bpt
from edubackend.resources.gift_bpt import gift_bpt
from edubackend.resources.user_profile_bpt import user_profile_bpt


def create_flask_app(config):
    app = Flask(__name__)
    # 加载配置
    app.config.from_object(config)
    # 注册蓝图
    app.register_blueprint(tbp)  # 测试蓝图
    app.register_blueprint(course_bpt)  # 课程蓝图
    app.register_blueprint(gift_bpt)  # 礼品蓝图
    app.register_blueprint(user_profile_bpt)  # 个人中心蓝图
    # db对象绑定app
    db.init_app(app)
    # 创建api对象
    api = Api(app)


    return app