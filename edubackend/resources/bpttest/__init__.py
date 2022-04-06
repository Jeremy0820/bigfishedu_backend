from flask import Blueprint
from flask_restful import Api
from edubackend.resources.bpttest.bpt import TestResource

tbp = Blueprint('tbp', __name__)
api = Api(tbp)
api.add_resource(TestResource, '/test')