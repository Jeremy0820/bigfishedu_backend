import uuid
from datetime import datetime
from uuid import uuid1
from flask_restful import Resource
from flask_restful import reqparse
from flask import current_app
from sqlalchemy import and_
import requests
from common.models.models import User, Faq, Spirit, Adress, Notice, ExMoneyRecords, Gift, Order, InviteReward
from common.utils.user_auth import generate_jwt, verify_jwt
from common.models import db


class Login(Resource):
    """
    登录接口
    """

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("nickName", location="json")
        self.parser.add_argument("avatarUrl", location="json")
        self.parser.add_argument("loginCode", location="json")

    def post(self):
        # 获取前端数据
        args = self.parser.parse_args()
        nick_name = args.get("nickName")
        avatar_url = args.get("avatarUrl")
        login_code = args.get("loginCode")

        # 获取openid
        appid = current_app.config.get("APP_ID")
        secret = current_app.config.get("APP_SECRET")
        url = f"https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={login_code}&grant_type=authorization_code"
        res = requests.get(url).json()
        session_key = res["session_key"]
        openid = res["openid"]
        # 判断用户是否为新用户
        user = User.query.filter_by(openid=openid)

        if user.first():
            # 用户存在, 生成生成token直接返回
            token = generate_jwt({"user_id": user.first().id, "openid": openid})
            is_recommended = user.first().is_recommended
            print("-" * 10, token)
            user.update({"nick_name": nick_name, "avatar": avatar_url, "session_key": session_key})
            db.session.commit()
            open_id = user.first().openid
        else:
            # 用户不存在, 落库, 生成token返回
            recommend_code = str(uuid1())
            new_user = User(nick_name=nick_name, avatar=avatar_url, session_key=session_key, openid=openid,
                            recommend_code=recommend_code)
            db.session.add(new_user)
            db.session.flush()
            user_id = new_user.id
            db.session.commit()
            token = generate_jwt({"user_id": user_id, "openid": openid})
            open_id = new_user.openid
            is_recommended = new_user.is_recommended
        return {
            "msg": "ok",
            "code": 200,
            "data": {
                "token": token,
                "openid": open_id,
                "isRecommended": is_recommended
            }
        }


class CoinAndScore(Resource):
    """
    获取个人金币与积分信息
    """

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("token", location="headers")

    def get(self):
        args = self.parser.parse_args()
        token = args.get("token")
        payload = verify_jwt(token)
        if not payload:
            return {'msg': "未登录, 请先登录!", "code": 201}
        user_id = payload["user_id"]
        user = User.query.filter_by(id=user_id).first()
        return {
            "msg": "ok",
            "code": 200,
            "data": {
                "coin": user.coin,
                "score": user.score
            }
        }


class FaqView(Resource):
    """
    常见问题接口
    """

    def get(self):
        faqs = Faq.query.all()
        data = [{"title": faq.title, "answer": faq.ans, "video": faq.video_url} for faq in faqs]
        return {
            "msg": "ok",
            "code": 200,
            "data": data
        }


class MoneyHelpView(Resource):
    """
    打赏程序接口
    """

    def get(self):
        return {
            "msg": "ok",
            "code": 200,
            "data": {
                "msg": "为什么会有打赏功能?本小程序为给同学们提供优质的教学资源,减少资源搜集的时间的个性化定制课堂. 小程序的运行和维护以及内部资源, 鼓励大家学习的小礼品和红包都是程序员小哥哥自掏腰包的.为了减小程序员小哥哥的经济压力, 希望您能够在享受优质教学资源的同时, 如果经济条件允许的情况下, 赞助小哥哥一杯暖心的咖啡.",
                "tip": "点击下方的收款码, 保存与手机上, 使用微信或支付宝扫码即可赞助(量力而行哦)",
                "wechatCode": "http://r8pyi761n.hn-bkt.clouddn.com/wxcode.png",
                "mayiCode": "http://r8pyi761n.hn-bkt.clouddn.com/zfbcode.png"
            }
        }


class BusinessData(Resource):
    """
    商务合作接口
    """

    def get(self):
        return {
            "msg": "ok",
            "code": 200,
            "data": {
                "msg1": "如果您想和我进行上午合作, 请发送邮件至yujeremy0820@gmail.com 收到邮件会第一时间回复! 如与工作日未回复,请耐心等候!",
                "msg2": "",
                "msg3": ""
            }
        }


class MyData(Resource):
    """
    个人资料接口
    """

    def get(self):
        return {
            "msg": "ok",
            "code": 200,
            "data": {
                "avatar": "http://r8pyi761n.hn-bkt.clouddn.com/WechatIMG117.jpeg",
                "desc": "我来自于内蒙古偏远的山区, 在贫穷的家庭艰难的完成了学业. 大学就读与哈尔滨, 现于北京的一家互联网公司工作. 开发该小程序起因于亲戚家的孩子在学习的过程中找不到学习资源, 经常在b站上搜索资源, 而资源的完整性并不好,缺少章节和课件. 故开发该小程序给各位同学提供优质的教学资源, 也希望同学们能够合理的利用平台. 每个读书人都有着为曾经养育过自己的家乡和亲人,教育过自己的老师,帮助过自己的同学做些事情!",
                "word": "相信美好的事情即将发生!"
            }
        }


class SpiritView(Resource):
    """
    许愿接口
    """

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("content", location="json")
        self.parser.add_argument("qq", location="json")
        self.parser.add_argument("wechat", location="json")
        self.parser.add_argument("tel", location="json")
        self.parser.add_argument("token", location="headers")

    def post(self):
        args = self.parser.parse_args()
        token = args.get("token")
        if not token:
            return {
                "msg": "fail",
                "code": 200,
                "data": "愿望发送失败, 请加程序员小哥哥微信联系"
            }
        print("spirit获取的token: ", token)
        payload = verify_jwt(token)
        user_id = payload["user_id"]
        content = args.get("content")
        qq = args.get("qq")
        wechat = args.get("wechat")
        tel = args.get("tel")
        print(content, qq, wechat, tel)
        spirit = Spirit(content=content, qq=qq, wechat=wechat, tel_num=tel, date=datetime.now(), status=0,
                        user_id=user_id)
        db.session.add(spirit)
        db.session.commit()
        return {
            "msg": "ok",
            "code": 200,
            "data": "我已收到您的愿望, 请耐心等待程序员小哥哥进行处理并与您联系哦!"
        }


class AddressView(Resource):
    """
    收货地址接口: 增加, 删除, 查询接口
    """

    def __init__(self):
        self.parser = reqparse.RequestParser()

    def verify_login(self):
        self.parser.add_argument("token", location="headers")
        args = self.parser.parse_args()
        token = args.get("token")
        # token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NDkyNTQ0NTEsInVzZXJfaWQiOjEsIm9wZW5pZCI6Im9wUG9vd0ZYMnVsTkl1ZDdxbnVCT1RIRV83QlUifQ.UINfl6w8Um9v9C8PV6DkUyl0o4KAEezQSsoJtlDRbZ8"
        if not token:
            return False, {
                "msg": "请先登录!",
                "code": 201,
                "data": []
            }
        try:
            payload = verify_jwt(token)
        except Exception as e:
            return False, {
                "msg": "登录过期,请重新登录",
                "code": 201,
                "data": []
            }
        if not payload:
            return False, {
                "msg": "登录过期,请重新登录",
                "code": 201,
                "data": []
            }
        return True, payload

    def get(self):
        flag, res_login = self.verify_login()
        if not flag:
            return res_login
        payload = res_login
        user_id = payload["user_id"]
        addresses = Adress.query.filter(and_(Adress.status == 1, Adress.user_id == user_id)).all()
        addressList = [
            {
                "id": address.id,
                "provinces": address.provinces,
                "city": address.city,
                "area": address.area,
                "address_detail": address.address_detail,
                "real_name": address.real_name,
                "tel_phone": address.tel_phone
            } for address in addresses
        ]

        # 地址数据排序
        def sort_func(item):
            return -int(item['id'])

        addressList = sorted(addressList, key=sort_func)
        return_data = {
            "msg": "ok",
            "code": 200,
            "data": addressList
        }
        return return_data

    def post(self):
        flag, res_login = self.verify_login()
        self.parser.add_argument("provinces", location="json")
        self.parser.add_argument("city", location="json")
        self.parser.add_argument("area", location="json")
        self.parser.add_argument("address_detail", location="json")
        self.parser.add_argument("real_name", location="json")
        self.parser.add_argument("tel_phone", location="json")
        if not flag:
            return res_login
        payload = res_login
        user_id = payload["user_id"]

        args = self.parser.parse_args()
        addresses = Adress.query.filter_by(status=1, user_id=user_id).all()
        if len(addresses) <= 3:
            provinces = args.get("provinces")
            city = args.get("city")
            address_detail = args.get("address_detail")
            area = args.get("area")
            real_name = args.get("real_name")
            tel_phone = args.get("tel_phone")
            if all([provinces, city, real_name, tel_phone, address_detail]):
                address = Adress(provinces=provinces, city=city, area=area, address_detail=address_detail,
                                 real_name=real_name, tel_phone=tel_phone, user_id=user_id, status=1)
                db.session.add(address)
                db.session.commit()
                return {
                    "msg": "添加地址成功",
                    "code": 200,
                    "data": []
                }
            else:
                return {
                    "msg": "地址信息不全",
                    "code": 201,
                    "data": []
                }
        else:
            return {
                "msg": "收货地址过多",
                "code": 205,
                "data": []
            }

    def delete(self):
        flag, res_login = self.verify_login()
        if not flag:
            return res_login
        payload = res_login
        user_id = payload["user_id"]
        self.parser.add_argument("address_id", location="args")
        args = self.parser.parse_args()
        address_id = args.get("address_id")
        address = Adress.query.filter_by(id=address_id, user_id=user_id).first()
        address.status = -1
        db.session.commit()
        return {
            "msg": "删除成功!",
            "code": 200,
            "data": []
        }


class NoticeView(Resource):
    """
    通知接口: 首页, 礼品页, 个人中心页
    """

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("type", location="args")

    def get(self):
        args = self.parser.parse_args()
        type = args.get("type")
        if type:
            notice = Notice.query.filter_by(type=type, status=1).first()
            if notice:
                return {
                    "msg": "ok",
                    "code": 200,
                    "data": {"notice": notice.msg}
                }
            else:
                return {
                    "msg": "request notice fail",
                    "code": 201,
                    "data": {}
                }
        else:
            return {
                "msg": "request notice fail",
                "code": 201,
                "data": {}
            }


class CoinExchangeRule(Resource):
    """
    金币兑换规则接口
    """

    def get(self):
        return {
            "msg": "ok",
            "code": 200,
            "data": [
                "金币兑换规则为: 100金币兑换1积分",
                "金币与积分的兑换比并不是一成不变的",
                "兑换比会根据礼品的时长价格升降做动态调整"
            ]
        }


class CoinExchangeTip(Resource):
    """
    金币兑换积分小贴士接口
    """

    def get(self):
        return {
            "msg": "ok",
            "code": 200,
            "data": [
                "点击广告可以获得更多金币",
                "邀请好友, 好友和你都有机会获得大额金币"
            ]
        }


class CoinToScore(Resource):
    """
    金币兑换积分接口
    """

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("token", location="headers")

    def get(self):
        args = self.parser.parse_args()
        token = args.get("token")
        if not token:
            return {
                "msg": "请先登录!",
                "code": 201,
                "data": []
            }
        try:
            payload = verify_jwt(token)
        except:
            return {
                "msg": "请重新登录!",
                "code": 201,
                "data": []
            }
        user_id = None
        if payload:
            user_id = payload["user_id"]
        else:
            return {
                "msg": "请登录!",
                "code": 201,
                "data": []
            }
        if user_id:
            user = User.query.filter_by(id=user_id).first()
            coin_num = user.coin
            score_num = user.score
            if coin_num < 100:
                return {
                    "msg": "金币不足",
                    "code": 202,
                    "data": []
                }
            reset_coin_num = coin_num % 100
            new_score_num = (coin_num - reset_coin_num) / 100 + score_num

            user.coin = reset_coin_num
            user.score = new_score_num
            db.session.add(user)
            db.session.commit()
            return {
                "msg": "兑换成功!",
                "code": 200,
                "data": {
                    "coin": reset_coin_num,
                    "score": new_score_num
                }
            }


class GiftCollections(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("token", location="headers")

    def get(self):
        args = self.parser.parse_args()
        token = args.get("token")
        print(token)
        if not token:
            return {
                "msg": "请先登录!",
                "code": 201,
                "data": []
            }
        try:
            payload = verify_jwt(token)
        except:
            return {
                "msg": "请重新登录!",
                "code": 201,
                "data": []
            }
        user_id = None
        if payload:
            user_id = payload["user_id"]
        else:
            return {
                "msg": "请登录!",
                "code": 201,
                "data": []
            }
        if user_id:
            user = User.query.filter_by(id=user_id).first()
            gift_collections_lst = user.giftcollections
            return_data = [
                {"id": gift.id, "title": gift.gift_title, "price": gift.price, "cover": gift.banner.split(",")[0]} for
                gift in gift_collections_lst]
            print(return_data)
            return {
                "msg": "ok",
                "code": 200,
                "data": return_data
            }


class InviteCode(Resource):
    """
    好友邀请码接口: 获取当前用户的邀请码
    """

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("token", location="headers")

    def get(self):
        args = self.parser.parse_args()
        token = args.get("token")
        if not token:
            return {
                "msg": "请先登录!",
                "code": 201,
                "data": []
            }
        try:
            payload = verify_jwt(token)
        except:
            return {
                "msg": "请重新登录!",
                "code": 201,
                "data": []
            }
        user_id = None
        if payload:
            user_id = payload["user_id"]
        else:
            return {
                "msg": "请登录!",
                "code": 201,
                "data": []
            }
        if user_id:
            user = User.query.filter_by(id=user_id).first()
            code = user.openid
            return {
                "msg": "ok",
                "code": 200,
                "data": {
                    "code": code
                }
            }


class InviteFriendSure(Resource):
    """
    好友邀请确认接口
    """

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("token", location="headers")
        self.parser.add_argument("code", location="json")

    def post(self):
        args = self.parser.parse_args()
        token = args.get("token")
        code = args.get("code")
        if not token:
            return {
                "msg": "请先登录!",
                "code": 201,
                "data": []
            }
        try:
            payload = verify_jwt(token)
        except:
            return {
                "msg": "请重新登录!",
                "code": 201,
                "data": []
            }
        user_id = None
        if payload:
            user_id = payload["user_id"]
        else:
            return {
                "msg": "请登录!",
                "code": 201,
                "data": []
            }

        if user_id and code:
            invited_user = User.query.filter_by(id=user_id).first()
            if invited_user.openid == code:
                return {
                    "msg": "自己不能邀请自己",
                    "code": 200,
                    "data": []
                }
            print("flagflag:", invited_user.is_recommended)
            if not invited_user.is_recommended:
                invite_user = User.query.filter_by(openid=code).first()
                if not invite_user:
                    return {
                        "msg": "邀请码错误",
                        "code": 202,
                        "data": []
                    }
                invited_user.coin = invited_user.coin + 2000
                invited_user.is_recommended = 1
                invite_user.coin = invite_user.coin + 2000
                db.session.add(invite_user)
                db.session.add(invited_user)
                db.session.commit()
                # 生成邀请记录
                invite_reward = InviteReward(user_id=user_id, invited_user_id=invited_user.id, reward=2000)
                db.session.add(invite_reward)
                db.session.commit()
                return {
                    "msg": "ok",
                    "code": 200,
                    "data": []
                }
            elif invited_user.is_recommended == 1:
                return {
                    "msg": "用户已被邀请过!",
                    "code": 202,
                    "data": []
                }

        return {
            "msg": "邀请确认失败!",
            "code": 202,
            "data": []
        }


class InviteTip(Resource):
    """
    好友邀请小贴士接口
    """

    def get(self):
        return {
            "msg": "ok",
            "code": 200,
            "data": [
                "好友邀请, 双方都会获得大量金币哦",
                "邀请你的好友加入, 经复制你的专属邀请码, 发送给好友",
                "好友成功登录小程序后, 填写你的邀请码, 并点击下方的确定邀请, 即可完成"
            ]
        }


class ScoreToMoneyTip(Resource):
    """
    积分提现小贴士接口
    """

    def get(self):
        return {
            "msg": "ok",
            "code": 200,
            "data": [
                "积分兑换小贴士1",
                "积分兑换小贴士2",
                "积分兑换小贴士3",
                "积分兑换小贴士4",
            ]
        }


class ScoreExchangeMoney(Resource):
    """
    积分提现接口
    """

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("token", location="headers")
        self.parser.add_argument("limit", location="args")

    def get(self):
        args = self.parser.parse_args()
        token = args.get("token")
        print("积分提现接口:", token)
        if not token:
            return {
                "msg": "请先登录!",
                "code": 201,
                "data": []
            }
        try:
            payload = verify_jwt(token)
        except:
            return {
                "msg": "请重新登录!",
                "code": 201,
                "data": []
            }
        user_id = None
        if payload:
            user_id = payload["user_id"]
        else:
            return {
                "msg": "请登录!",
                "code": 201,
                "data": []
            }
        if not user_id:
            return {
                "msg": "请登录!",
                "code": 201,
                "data": []
            }
        limit = args.get("limit")
        try:
            limit = int(limit)
        except:
            return {
                "msg": "兑换金额错误!",
                "code": 202,
                "data": []
            }
        user = User.query.filter_by(id=user_id).first()
        score = user.score
        money_num = score / 100.0
        if money_num < limit:
            return {
                "msg": "积分不足!",
                "code": 203,
                "data": []
            }
        # 扣减积分
        user.score = user.score - limit * 100
        db.session.add(user)
        db.session.commit()

        # 生成提现记录
        exchange_number = str(uuid.uuid1())
        exchange_money_record = ExMoneyRecords(exchange_number=exchange_number, user_id=user_id, exchange_money=limit,
                                               status=0)
        db.session.add(exchange_money_record)
        db.session.commit()

        # 查询该用户所有未处理提现记录
        records = user.exchange_money_records
        euids = [{"exchangeUid": record.exchange_number} for record in records]
        return {
            "msg": "ok",
            "code": 200,
            "data": []
        }


class ScoreExchangeMoneyRecords(Resource):
    """
    积分提现记录接口
    """

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("token", location="headers")

    def get(self):
        args = self.parser.parse_args()
        token = args.get("token")
        if not token:
            return {
                "msg": "请先登录!",
                "code": 201,
                "data": []
            }
        try:
            payload = verify_jwt(token)
        except:
            return {
                "msg": "请重新登录!",
                "code": 201,
                "data": []
            }
        user_id = None
        if payload:
            user_id = payload["user_id"]
        else:
            return {
                "msg": "请登录!",
                "code": 201,
                "data": []
            }
        if not user_id:
            return {
                "msg": "请登录!",
                "code": 201,
                "data": []
            }
        user = User.query.filter_by(id=user_id).first()
        records = user.exchange_money_records
        euids = [{"exchangeUid": record.exchange_number} for record in records if record.status == 0]
        return {
            "msg": "ok",
            "code": 200,
            "data": euids
        }


class GiftOrder(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("token", location="headers")

    def verify_login(self):
        self.parser.add_argument("token", location="headers")
        args = self.parser.parse_args()
        token = args.get("token")
        # token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NDkyNTQ0NTEsInVzZXJfaWQiOjEsIm9wZW5pZCI6Im9wUG9vd0ZYMnVsTkl1ZDdxbnVCT1RIRV83QlUifQ.UINfl6w8Um9v9C8PV6DkUyl0o4KAEezQSsoJtlDRbZ8"
        if not token:
            return False, {
                "msg": "请先登录!",
                "code": 201,
                "data": []
            }
        try:
            payload = verify_jwt(token)
        except Exception as e:
            return False, {
                "msg": "登录过期,请重新登录",
                "code": 201,
                "data": []
            }
        if not payload:
            return False, {
                "msg": "登录过期,请重新登录",
                "code": 201,
                "data": []
            }
        return True, payload

    def get(self):
        flag, res_login = self.verify_login()
        if not flag:
            return res_login
        payload = res_login
        user_id = payload["user_id"]
        user = User.query.filter_by(id=user_id).first()
        orders = user.order
        return_data = {
            "waitOrderList": [
                {"id": order.id, "order_number": order.order_number, "create_time": str(order.create_time),
                 "gift_title": Gift.query.filter_by(id=order.gift_id).first().gift_title,
                 "gift_price": Gift.query.filter_by(id=order.gift_id).first().price,
                 "gift_cover": Gift.query.filter_by(id=order.gift_id).first().banner.split(",")[0]} for order in orders
                if order.status == 0],
            "sendOrderList": [
                {"id": order.id, "order_number": order.order_number, "create_time": str(order.create_time),
                 "logistics_number": order.logistics_number,
                 "gift_title": Gift.query.filter_by(id=order.gift_id).first().gift_title,
                 "gift_price": Gift.query.filter_by(id=order.gift_id).first().price,
                 "gift_cover": Gift.query.filter_by(id=order.gift_id).first().banner.split(",")[0]} for order in orders
                if order.status == 1],
            "doneOrderList": [
                {"id": order.id, "order_number": order.order_number, "create_time": str(order.create_time),
                 "gift_title": Gift.query.filter_by(id=order.gift_id).first().gift_title,
                 "gift_price": Gift.query.filter_by(id=order.gift_id).first().price,
                 "gift_id": Gift.query.filter_by(id=order.gift_id).first().id,
                 "gift_cover": Gift.query.filter_by(id=order.gift_id).first().banner.split(",")[0]} for order in orders
                if order.status == 2]
        }
        return {
            "msg": "ok",
            "code": 200,
            "data": return_data
        }

    def delete(self):
        self.parser.add_argument("delOrderNumber", location="json")
        flag, res_login = self.verify_login()
        if not flag:
            return res_login
        payload = res_login
        user_id = payload["user_id"]

        args = self.parser.parse_args()
        delOrderNumber = args.get("delOrderNumber")
        order = Order.query.filter(
            and_(Order.user_id == user_id, Order.order_number == delOrderNumber, Order.status == 0)).first()
        if order:
            try:
                order.status = -1
                db.session.commit()
                user = User.query.filter_by(id=user_id).first()
                user.score = user.score + float(Gift.query.filter_by(id=order.gift_id).first().price)
                db.session.commit()
            except Exception as e:
                print(e)
                print("订单关闭失败")
            return {
                "msg": "订单关闭成功",
                "code": 200,
                "data": []
            }
        else:
            return {
                "msg": "订单关闭失败",
                "code": 202,
                "data": []
            }

    def post(self):
        self.parser.add_argument("got_gift_number", location="json")
        flag, res_login = self.verify_login()
        if not flag:
            return res_login
        payload = res_login
        user_id = payload["user_id"]

        args = self.parser.parse_args()
        got_gift_number = args.get("got_gift_number")
        order = Order.query.filter(
            and_(Order.user_id == user_id, Order.order_number == got_gift_number, Order.status == 1)).first()
        if order:
            try:
                order.status = 2
                db.session.commit()
            except Exception as e:
                print(e)
                print("收货失败")
            return {
                "msg": "收货成功",
                "code": 200,
                "data": []
            }
        else:
            return {
                "msg": "收货失败!",
                "code": 202,
                "data": []
            }


class IsLogin(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("token", location="headers")

    def get(self):
        self.parser.add_argument("token", location="headers")
        args = self.parser.parse_args()
        token = args.get("token")
        if not token:
            return False, {
                "msg": "请先登录!",
                "code": 201,
                "data": []
            }
        try:
            payload = verify_jwt(token)
        except Exception as e:
            return False, {
                "msg": "登录过期,请重新登录",
                "code": 201,
                "data": []
            }
        if not payload:
            return False, {
                "msg": "登录过期,请重新登录",
                "code": 201,
                "data": []
            }
        return {
            "msg": "ok",
            "code": 200,
            "data": []
        }


class InviteRecords(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("token", location="headers")

    def get(self):
        self.parser.add_argument("token", location="headers")
        args = self.parser.parse_args()
        token = args.get("token")
        if not token:
            return False, {
                "msg": "请先登录!",
                "code": 201,
                "data": []
            }
        try:
            payload = verify_jwt(token)
        except Exception as e:
            return False, {
                "msg": "登录过期,请重新登录",
                "code": 201,
                "data": []
            }
        if not payload:
            return False, {
                "msg": "登录过期,请重新登录",
                "code": 201,
                "data": []
            }
        invite_user_id = payload['user_id']
        invite_records = InviteReward.query.filter_by(user_id=invite_user_id).all()
        return_data = []
        for record in invite_records:
            invited_user_id = record.invited_user_id
            invited_user = User.query.filter_by(id=invited_user_id).first()
            msg = "您邀请%s成功, 获得%s枚金币" % (invited_user.nick_name, record.reward)
            return_data.append(msg)
        return {
            "msg": "ok",
            "code": 200,
            "data": return_data
        }
