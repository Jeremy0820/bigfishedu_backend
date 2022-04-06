from flask import Blueprint
from flask_restful import Api
from edubackend.resources.gift_bpt.gift_bpt_view import GiftList, GiftDetail, GiftCollect, GiftCollection, GiftExchange

gift_bpt = Blueprint("gift_bpt", __name__)
api = Api(gift_bpt)

api.add_resource(GiftList, "/api/giftslist")
api.add_resource(GiftDetail, "/api/giftdetail")
api.add_resource(GiftCollect, "/api/gift/collect")
api.add_resource(GiftCollection, "/api/gift/collection")
api.add_resource(GiftExchange, "/api/gift/exchage")