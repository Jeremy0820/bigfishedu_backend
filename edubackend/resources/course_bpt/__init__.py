from flask import Blueprint
from flask_restful import Api
from edubackend.resources.course_bpt.course_bpt_view import RecommendCourseList, Banner, Search, CourseList, CourseInfo, CollectCourse, CourseCollection, CourseVideo


course_bpt = Blueprint("course_bpt", __name__)
api = Api(course_bpt)

# 推荐课程列表接口
api.add_resource(RecommendCourseList, "/api/recommend")
api.add_resource(Banner, "/api/banner")
api.add_resource(Search, "/api/search")
api.add_resource(CourseList, "/api/course")
api.add_resource(CourseInfo, "/api/courseinfo")
api.add_resource(CollectCourse, "/api/course/collect")
api.add_resource(CourseCollection, "/api/collection")
api.add_resource(CourseVideo, "/api/course/video")