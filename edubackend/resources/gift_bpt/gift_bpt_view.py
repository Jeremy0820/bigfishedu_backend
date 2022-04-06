import uuid
from random import randint
from flask_restful import reqparse
from flask_restful import Resource
from common.models.models import Gift, Order
from common.utils.user_auth import verify_jwt
from common.models import db
from common.models.models import User, Gift


class GiftList(Resource):
    """
    礼物列表接口
    """
    def get(self):
        gifts = Gift.query.all()
        return_data = []
        for gift in gifts:
            return_data.append({
                "id": gift.id,
                "img": gift.banner.split(',')[0],
                "title": gift.gift_title,
                "littleTitle": "xxxxxxxxxxx",
                "amount": str(gift.price) + "积分",
                "amountRemark": "已有%s人兑换" % randint(105, 500),
                "label": "包邮"
            })
        return {
            "msg": "ok",
            "code": 200,
            "data": return_data
        }


class GiftDetail(Resource):
    """
    礼物详情接口
    """
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("giftId", location="args")

    def get(self):
        args = self.parser.parse_args()
        gift_id = args.get("giftId")
        if not gift_id:
            return {
                'msg': "params error",
                'code': 203,
                'data': []
            }
        gift = Gift.query.filter_by(id=gift_id).first()
        collection_num = len(gift.users)
        swiperList = [{"id": gift.banner.split(',').index(item), "img": item} for item in gift.banner.split(',')]
        imgs = [item for item in gift.pics.split(',')]
        return_data = {
            "msg": "ok",
            "code": 200,
            "data": {
                "id": gift.id,
                "swiperList": swiperList,
                "title": gift.gift_title,
                "price": gift.price,
                "brief": 'yyyyy',
                "imgs": imgs,
                "notice": gift.notice,
                "collection_num": collection_num
            }
        }
        return return_data


class GiftCollect(Resource):
    """
    收藏礼物接口
    """
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("token", location="headers")
        self.parser.add_argument("gift_id", location="args")

    def get(self):
        args = self.parser.parse_args()
        token = args.get("token")

        payload = None
        msg = "ok"
        if not token:
            msg = "未登录状态, 请进行登录"
        try:
            payload = verify_jwt(token)
        except:
            msg = "登录态过期, 请重新登录"
        if not payload:
            msg = "登录态过期, 请重新登录"
        if msg != "ok":
            return {
                "msg": "收藏失败, 请先登录!",
                "code": 201,
                "data": []
            }
        user_id = payload["user_id"]
        gift_id = args.get("gift_id")
        print("礼物收藏接口: userid: ", user_id, "礼物收藏接口: giftid:", gift_id)
        user = User.query.filter_by(id=user_id).first()
        gift = Gift.query.filter_by(id=gift_id).first()
        collections = user.giftcollections
        if gift in collections:
            return {
                "msg": "该礼物已被收藏过!",
                "code": 202,
                "data": []
            }
        if user and gift:
            user.giftcollections.append(gift)
            db.session.add(user)
            db.session.commit()
        return {
            "msg": "收藏成功!",
            "code": 200,
            "data": []
        }


class GiftCollection(Resource):
    """
    礼物收藏接口
    """
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("token")

    def get(self):
        args = self.parser.parse_args()
        token = args.get("token")
        msg = "ok"
        payload = None
        if not token:
            msg = "未登录, 请进行登录!"
        try:
            payload = verify_jwt(token)
        except:
            msg = "登录态过去, 请进行登录!"
        if not payload:
            return {
                "msg": msg,
                "code": 201,
                "data": []
            }
        user_id = payload["user_id"]
        user = User.query.filter_by(id=user_id)
        collections = user.giftcollections
        # for gift in collections:
        #
        collections_list = [{"id":gift.id, "gift_title":gift.gift_title, "price": gift.price, "date": "2022-03-28"} for gift in collections]
        return {
            "msg": "ok",
            "code": 200,
            "data":collections_list
        }


class GiftExchange(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("token", location="headers")
        self.parser.add_argument("gid", location="json")
        self.parser.add_argument("address_id", location="json")

    def post(self):
        args = self.parser.parse_args()
        token = args.get("token")
        gid = args.get("gid")
        address_id = args.get("address_id")
        # 参数检查
        if not all([token, gid, address_id]):
            return {
                "msg": "兑换出错啦!",
                "code": 202,
                "data":[]
            }

        # 用户确认
        try:
            payload = verify_jwt(token)
            user_id = payload.get("user_id")
        except Exception as e:
            print(e)
            return {
                "msg": "请先登录!",
                "code": 201,
                "data": []
            }
        user = User.query.filter_by(id=user_id).first()
        gift = Gift.query.filter_by(id=gid).first()
        if user and gift and user.score>=gift.price:
            order_num = str(uuid.uuid1())
            order = Order(order_number=order_num, user_id = user.id, gift_id=gift.id, status=0)
            db.session.add(order)
            db.session.commit()
            return {
                "msg": "兑换成功!",
                "code": 200,
                "data":[]
            }
        else:
            return {
                "msg": "积分不足,无法兑换!",
                "code": 200,
                "data": []
            }