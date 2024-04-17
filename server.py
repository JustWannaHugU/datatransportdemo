import logging
from typing import Tuple, Union
from config import Config
from sqlalchemy.orm import sessionmaker
from flask import Flask, jsonify, request, abort
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String
import re  # 导入正则表达式模块

# 配置标准分级日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# 构造基础模型类
Base = declarative_base()


# 定义用户模型，映射数据库中的 'college_user' 表
class User(Base):
    __tablename__ = 'college_user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    sex = Column(String)
    phone = Column(String)
    face_url = Column(String)


# 创建 Flask 应用实例
app = Flask(__name__)
# 从配置文件中读取数据库 URI
# DATABASE_URI = Config.COLLEGE_DATABASE_URI
DATABASE_URI = Config._decrypt(Config.COLLEGE_DATABASE_URI)
# print(DATABASE_URI)

# 创建数据库引擎
engine = create_engine(DATABASE_URI)
# 创建 Session 类
Session = sessionmaker(bind=engine)


# 函数用于查询用户并返回结果
def get_user_by_id(user_id: str) -> Union[Tuple[dict, int], Tuple[dict, int, bool]]:
    # 创建数据库会话
    with Session() as session:
        try:
            # 验证用户ID是否为整数
            if not re.match(r'^\d+$', user_id):
                return {'error': '用户 id 必须是整数'}, 400

            # 查询用户信息
            user = session.query(User).filter_by(id=int(user_id)).first()
            if user is None:
                return {'error': '用户不存在,请核实后输入单个id进行查询'}, 404
            return {'name': user.name, 'sex': user.sex, 'phone': user.phone,
                    'face_url': user.face_url}, 200
        except ValueError as e:
            logging.error(f'用户 id 转换错误: {e}')
            return {'error': '无效的用户ID'}, 400
        except SQLAlchemyError as e:
            logging.error(f'数据库错误: {e}')
            return {'error': '数据库查询失败'}, 500

# 查询用户的路由处理函数
@app.route('/query_user', methods=['GET'])
def query_user():
    user_id = request.args.get('id')
    if not user_id:
        return abort(400, description='缺少用户 id 参数')
    return get_user_by_id(user_id)


# 启动 Flask 应用
if __name__ == '__main__':
    # config = Config()
    app.run(host=Config.SERVER_HOST, port=Config.SERVER_PORT, debug=Config.DEBUG)