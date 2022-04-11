from flask_restful import Resource
from flask_restful import reqparse
from sqlalchemy import or_, and_
from common.models import db
from common.models.models import Course, Chapter, Section, course_collections, User
from common.utils.user_auth import verify_jwt


class RecommendCourseList(Resource):
    """
    推荐课程列表数据接口
    """

    def get(self):
        recommend_course_data_meta = Course.query.filter(and_(Course.recommend == 1, Course.status == 1)).all()
        return_data = [
            {"id": item.id,
             "image": item.cover,
             "course_title": item.course_title
             } for item in recommend_course_data_meta]
        return {
            "msg": "ok",
            "code": 200,
            "data": return_data
        }


class Banner(Resource):
    """
    首页banner列表数据接口
    """

    def get(self):
        banner_data = Course.query.filter(and_(Course.status == 1, Course.is_banner == 1)).all()
        return_data = [
            {
                "id": item.id,
                "image": item.cover,
                "course_title": item.course_title,
                "wid": item.id
            } for item in banner_data]
        return {
            "msg": "ok",
            "code": 200,
            "data": return_data
        }


class Search(Resource):
    """
    模糊搜索接口
    """
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("keyword", location='args')

    def get(self):
        args = self.parser.parse_args()
        keyword = args.get("keyword") if args.get("keyword") else ""
        course_search = Course.query.filter(or_(
            Course.course_title.like('%' + keyword + '%'),
            Course.grade.like('%' + keyword + '%'),
            Course.uod.like('%' + keyword + '%'),
            Course.version.like('%' + keyword + '%'))).all()
        if course_search:
            return_data = [{"id": item.id, "image": item.cover, "course_title": item.course_title, "wid": item.id} for item
                       in course_search]
            msg = "ok"
        else:
            recommend_course_data_meta = Course.query.filter(and_(Course.recommend == 1, Course.status == 1)).all()
            msg = "搜索无果, 已展示推荐课程!"
            return_data = [
                {"id": item.id,
                 "image": item.cover,
                 "course_title": item.course_title
                 } for item in recommend_course_data_meta]
        return {
            "msg": msg,
            "code": 200,
            "data": return_data
        }


class CourseList(Resource):
    """
    分类课程列表接口
    """
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("categroy", location='args')

    def get(self):
        args = self.parser.parse_args()
        category = args.get("categroy") if args.get("categroy") else "高一"
        cate_course_list = Course.query.filter_by(grade=category).all()
        return_data = [
            {
                "id": item.id,
                "image": item.cover,
                "course_title": item.course_title
            } for item in cate_course_list]
        return {"msg": "ok", "code": 200, "data": return_data}


class CourseInfo(Resource):
    """
    课程详情接口
    """
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("courseId", location='args')

    def get(self):
        args = self.parser.parse_args()
        course_id = args.get("courseId")
        course = Course.query.get(course_id)
        collect_num = len(course.users)
        chapters = Chapter.query.filter_by(course_id=course.id).order_by(Chapter.id.asc())
        content = []
        for chapter in chapters:
            sections = Section.query.filter_by(chapter_id=chapter.id).order_by(Section.id.asc())
            chapter_child = [{"id": section.id, "title": section.section_title} for section in sections]
            content.append({"id": chapter.id, "chapter_name": chapter.chapter_title, "chapter_child": chapter_child})

        return_data = {
            "course_name": course.course_title,
            "course_version": course.version,
            "course_grade": course.grade,
            "collect_num": collect_num,
            "content": content,
            "course_source": course.source
        }
        return {
            "msg": "ok",
            "code": 200,
            "data": return_data
        }


class CollectCourse(Resource):
    """
    收藏课程接口
    """
    def __init__(self):
        self.parse = reqparse.RequestParser()
        self.parse.add_argument("courseId", location="args")
        self.parse.add_argument("token", location="headers")

    def get(self):
        args = self.parse.parse_args()
        course_id = args.get("courseId")  # 获取课程id
        token = args.get("token")  # 获取token

        # 登录态校验
        try:
            payload = verify_jwt(token)
            if not payload:
                return {
                    "msg": "收藏课程失败, 请先登录!",
                    "code": 201,
                    "data": []
                }
        except:
            return {
                "msg": "登录过期, 请重新登录!",
                "code": 201,
                "data": []
            }
        user_id = payload.get("user_id")

        # 获取课程与用户
        course = Course.query.filter_by(id=course_id).first()
        user = User.query.filter_by(id=user_id).first()

        # 收藏逻辑处理
        collections = user.coursecollections
        if course in collections:
            return {
                "msg": "该课程已被收藏过!",
                "code": 202,
                "data": []
            }
        if user and course:
            user.coursecollections.append(course)
            db.session.add(user)
            db.session.commit()
            return {
                "msg": "收藏成功!",
                "code": 200,
                "data": []
            }
        return {
            "msg": "收藏失败!",
            "code": 203,
            "data": []
        }


class CourseCollection(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("token", location="headers")

    def get(self):
        args = self.parser.parse_args()
        token = args.get("token")
        if not token:
            return {
                'msg': "not login",
                "code": 201,
                'data': []
            }
        try:
            payload = verify_jwt(token)
            user = User.query.filter_by(id=payload['user_id']).first()
            course_collections = user.coursecollections
            data = []
            msg = "ok"
            for course in course_collections:
                id = course.id
                course_title = course.course_title
                image = course.cover
                collect = len(course.users)
                date = str(course.create_time)
                data.append({"id": id, "course_title": course_title, "image": image, "collect": collect, "date": date})
        except:
            msg = "获取收藏失败!"
            data = []
        return {
            'msg': msg,
            "code": 200,
            'data': data
        }


class CourseVideo(Resource):
    """
    获取视频链接接口
    """

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("token", location="headers")
        self.parser.add_argument("chapter_id", location="args")

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
        if payload:
            user_id = payload["user_id"]
        else:
            return {
                "msg": "请登录!",
                "code": 201,
                "data": []
            }
        section_id = args.get("chapter_id")
        section_url = Section.query.filter_by(id=section_id).first().video_url
        print("视频链接: ", section_url)
        user = User.query.filter_by(id=user_id).first()
        if user.coin >= 100:
            user.coin = user.coin - 100
            db.session.add(user)
            db.session.commit()
        else:
            return {
                "msg": "积分不足!",
                "code": 203,
                "data": []
            }
        return {
            "msg": "OK",
            "code": 200,
            "data": {
                "vurl": section_url
            }
        }
