from flask import Blueprint
from flask_restful import Api
from edubackend.resources.user_profile_bpt.user_profile_bpt_view import Login, CoinAndScore, FaqView, MoneyHelpView, BusinessData, MyData, SpiritView, NoticeView
from edubackend.resources.user_profile_bpt.user_profile_bpt_view import CoinExchangeRule, CoinExchangeTip, CoinToScore, GiftCollections, InviteCode, InviteFriendSure, InviteTip
from edubackend.resources.user_profile_bpt.user_profile_bpt_view import ScoreExchangeMoney, ScoreToMoneyTip, ScoreExchangeMoneyRecords, AddressView, GiftOrder, IsLogin, InviteRecords

user_profile_bpt = Blueprint("user_profile_bpt", __name__)
api = Api(user_profile_bpt)

# 推荐课程列表接口
api.add_resource(Login, "/api/login")
api.add_resource(CoinAndScore, "/api/user/coinscore")
api.add_resource(FaqView, "/api/faq")
api.add_resource(MoneyHelpView, "/api/user/moneyhelp")
api.add_resource(BusinessData, "/api/user/business")
api.add_resource(MyData, "/api/user/mydata")
api.add_resource(SpiritView, "/api/spirit")
api.add_resource(NoticeView, "/api/notice")
api.add_resource(CoinExchangeRule, "/api/user/coinexchangerule")
api.add_resource(CoinExchangeTip, "/api/user/coinexchangetip")
api.add_resource(CoinToScore, "/api/user/cointoscore")
api.add_resource(GiftCollections, "/api/user/giftcollections")
api.add_resource(InviteCode, "/api/user/invitecode")
api.add_resource(InviteFriendSure, "/api/user/sureinvite")
api.add_resource(InviteTip, "/api/user/invitetip")
api.add_resource(ScoreToMoneyTip, "/api/user/scoretomoneytip")
api.add_resource(ScoreExchangeMoney, "/api/user/scoretomoney")
api.add_resource(ScoreExchangeMoneyRecords, "/api/user/scoretomoneyrecords")
api.add_resource(AddressView, "/api/user/address")
api.add_resource(GiftOrder, "/api/user/orders")
api.add_resource(IsLogin, "/api/user/islogin")
api.add_resource(InviteRecords, "/api/user/inviterecords")
