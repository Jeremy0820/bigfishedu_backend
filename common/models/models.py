from common.models import db
from datetime import datetime

course_collections = db.Table(
    "course_collections",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True, doc="用户ID"),
    db.Column("course_id", db.Integer, db.ForeignKey("course.id"), primary_key=True, doc="课程ID"),
    db.Column("is_delete", db.Integer, default=0, doc="状态(0:收藏, 1:取消收藏)"),
    db.Column("create_time", db.DateTime, default=datetime.now, doc="创建时间"),
    db.Column("update_time", db.DateTime, default=datetime.now, onupdate=datetime.now, doc='更新时间'),
)

gift_collections = db.Table(
    'gift_collections',
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True, doc="用户ID"),
    db.Column("gift_id", db.Integer, db.ForeignKey("gift.id"), primary_key=True, doc="礼物ID"),
    db.Column("is_delete", db.Integer, default=1, doc="状态(1:收藏, 0:取消收藏)"),
    db.Column("create_time", db.DateTime, default=datetime.now, doc="创建时间"),
    db.Column("update_time", db.DateTime, default=datetime.now, onupdate=datetime.now, doc='更新时间'),
)


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, doc="用户主键ID")
    user_name = db.Column(db.String(64), doc="用户名昵称")
    nick_name = db.Column(db.String(64), doc="用户昵称")
    avatar = db.Column(db.String(255), doc="用户头像")
    session_key = db.Column(db.String(255), doc="session_key")
    openid = db.Column(db.String(64), doc="openid")
    score = db.Column(db.Float, doc="用户积分数")
    coin = db.Column(db.Integer, doc="用户金币数")
    day_coin = db.Column(db.Integer, doc="进入单日金币上线")
    total_coin = db.Column(db.BigInteger, doc="用户累计金币数")
    recommend_code = db.Column(db.String(255), doc="用户推荐唯一码")
    is_recommended = db.Column(db.Integer, doc="是否被推荐, 1:被推荐过, 0:未被推荐过")
    is_vip = db.Column(db.Integer, default=0, doc="0:普通用户; 1:月VIP; 2:季度VIP; 3:年VIP会员; 4:终身会员")

    adress = db.relationship("Adress", backref="user")
    spirit = db.relationship("Spirit", backref="user")
    order = db.relationship("Order", backref="user")
    coursecollections = db.relationship('Course', secondary=course_collections, lazy="subquery",
                                        backref=db.backref('users', lazy=True))
    giftcollections = db.relationship("Gift", secondary=gift_collections, lazy="subquery",
                                      backref=db.backref('users', lazy=True))
    exchange_money_records = db.relationship("ExMoneyRecords", backref="user")


class Course(db.Model):
    __tablename__ = "course"

    id = db.Column(db.Integer, primary_key=True, doc="课程主键ID", autoincrement=True)
    course_title = db.Column(db.String(64), doc="课程标题")
    grade = db.Column(db.String(32), doc="年级")
    uod = db.Column(db.String(32), doc="上下册")
    category = db.Column(db.String(32), doc="分类")
    version = db.Column(db.String(32), doc="教材版本")
    source = db.Column(db.String(255), doc="资源下载地址")
    recommend = db.Column(db.Integer, doc="是否推荐, 1:推荐, 0:不推荐", default=0)
    cover = db.Column(db.String(255), doc="封面图片外链")
    is_banner = db.Column(db.Integer, doc="banner标识: 1是banner图, 0不是banner图")
    banner_pic = db.Column(db.Text, doc="banner图连接")
    status = db.Column(db.Integer, doc="课程状态, 0:下架, 1:上架")

    chapter = db.relationship("Chapter", backref="course")


class Chapter(db.Model):
    __tablename__ = "chapter"

    id = db.Column(db.Integer, primary_key=True, doc="章主键ID", autoincrement=True)
    chapter_title = db.Column(db.String(64), doc="章名称")
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    section = db.relationship("Section", backref="chapter")


class Section(db.Model):
    __tablename__ = "section"

    id = db.Column(db.Integer, primary_key=True, doc="节主键id", autoincrement=True)
    section_title = db.Column(db.String(64), doc="节名称")
    video_url = db.Column(db.String(255), doc="视频教程外链")
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'))


class Gift(db.Model):
    __tablename__ = "gift"

    id = db.Column(db.Integer, primary_key=True, doc="礼物主键id", autoincrement=True)
    banner = db.Column(db.Text, doc="banner图片连接集合")
    gift_title = db.Column(db.String(255), doc="礼物标题")
    price = db.Column(db.Float, doc="礼物价格")
    status = db.Column(db.Integer, doc="礼物状态, 0:无货, 1:正常, -1:下架")
    notice = db.Column(db.String(255), doc="提示信息")
    pics = db.Column(db.Text, doc="详情图片")
    link = db.Column(db.Text, doc="pdd链接")

    order = db.relationship("Order", backref="gift")


class Spirit(db.Model):
    __tablename__ = "spirit"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, doc="愿望清单主键ID")
    content = db.Column(db.Text, doc="愿望描述")
    qq = db.Column(db.String(32), doc="qq号码")
    wechat = db.Column(db.String(32), doc="微信号")
    tel_num = db.Column(db.String(32), doc="电话号")
    date = db.Column(db.DATE, default=datetime.date, doc="生成日期")
    status = db.Column(db.Integer, doc="愿望状态, 0:等待处理, 1:已实现 2.驳回", default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class Faq(db.Model):
    __tablename__ = "faq"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, doc="常见问题主键ID")
    title = db.Column(db.String(255), doc="问题标题")
    ans = db.Column(db.String(255), doc="问题答案")
    video_url = db.Column(db.String(255), doc="解答视频外链")


class Adress(db.Model):
    __tablename__ = "adress"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, doc="收货地址主键ID")
    provinces = db.Column(db.String(64), doc="省份")
    city = db.Column(db.String(64), doc="城市")
    area = db.Column(db.String(64), doc="区域")
    address_detail = db.Column(db.String(255), doc="详细地址")
    is_default = db.Column(db.Integer, doc="是否为默认地址, 1:是, 0:否")
    real_name = db.Column(db.String(32), doc="真实姓名")
    tel_phone = db.Column(db.String(32), doc="电话号码")
    status = db.Column(db.Integer, default=1, doc="地址状态,-1:已删除, 1:正常")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class Order(db.Model):
    __tablename__ = "order"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, doc="礼品兑换订单主键ID")
    order_number = db.Column(db.String(255), doc="订单编号")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), doc="关联用户ID")
    gift_id = db.Column(db.Integer, db.ForeignKey("gift.id"), doc="关联礼品ID")
    logistics_number = db.Column(db.String(255), doc="物流编号")
    logistics_info = db.Column(db.Text, doc="物流信息")
    status = db.Column(db.Integer, default=0, doc="订单状态(-1:关闭, 0:处理中, 1:已发货, 2.收货完成)")
    create_time = db.Column(db.DateTime, default=datetime.now, doc="订单创建时间")
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, doc="更新时间")


class InviteReward(db.Model):
    __tablename__ = "invite_reward"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, doc="好友邀请记录主键ID")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), doc="邀请人ID")
    invited_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), doc="被邀请人id")
    reward = db.Column(db.Integer, doc="奖励金币数")
    msg = db.Column(db.String(255), doc="系统信息")
    create_time = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.Integer, doc="邀请状态, (1:成功, 0:失败, 2:重复)")


class ExMoneyRecords(db.Model):
    __tablename__ = "ex_money_records"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, doc="积分提现记录主键ID")
    exchange_number = db.Column(db.String(255), doc="兑换编号")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    exchage_coin = db.Column(db.Integer, doc="兑换金币数")
    exchange_money = db.Column(db.Integer, doc="兑换现金数")
    status = db.Column(db.Integer, doc="记录状态(-1:驳回, 0:处理中, 1:兑换完成)")
    create_time = db.Column(db.DateTime, default=datetime.now, doc="记录创建时间")
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, doc="更新时间")


class Notice(db.Model):
    __tablename__ = "notice"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, doc="通知消息主键ID")
    type = db.Column(db.Integer, doc="通知类型(0:首页, 1:gift页面, 2:个人中心)")
    msg = db.Column(db.String(255), doc="消息体")
    status = db.Column(db.Integer, doc="状态(0:禁用, 2:正常)")
