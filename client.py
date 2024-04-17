import requests
from server import app
from config import Config
from sqlalchemy.orm import sessionmaker
from flask import Flask, request, jsonify
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String


# 构造基础模型类
Base = declarative_base()
SessionLocal = None
# 定义本地用户模型
class LocalUser(Base):
    __tablename__ = 'local_user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    sex = Column(String)
    phone = Column(String)
    face_url = Column(String)

#初始化数据库会话
def init_db():
    global SessionLocal
    DATABASE_URI = Config._decrypt(Config.LOCAL_DATABASE_URI)
    engine_local = create_engine(DATABASE_URI)
    SessionLocal = sessionmaker(bind=engine_local)

# 从配置文件中读取本地数据库链接（解密后的）
# DATABASE_URI = Config.LOCAL_DATABASE_URI
DATABASE_URI = Config._decrypt(Config.LOCAL_DATABASE_URI)
engine_local = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(bind=engine_local)

#local_user与college_user同步
def sync_user_data(user_id, college_user_data):
    with SessionLocal() as session:
        # 开始事务
        transaction = session.begin()
        try:
            local_user = session.query(LocalUser).filter_by(id=user_id).first()

            if college_user_data and not local_user:
                # 1、远程存在，本地不存在，创建新用户
                new_user = LocalUser(**college_user_data)
                session.add(new_user)
                return "这是新用户，数据存储完成！"
            elif not college_user_data and local_user:
                # 2、远程不存在，本地存在，删除本地用户
                session.delete(local_user)
            elif college_user_data and local_user:
                # 3、远程和本地存在，检查数据是否一致，不一致则更新
                update_needed = False
                for key, value in college_user_data.items():
                    if getattr(local_user, key) != value:
                        setattr(local_user, key, value)
                        update_needed = True
                if update_needed:
                    session.merge(local_user)
                else:
                    return "用户数据已存在，无需存储"
            transaction.commit()
            return "用户数据更新完成，数据已存储。"
        except Exception as e:
            transaction.rollback()
            return f"用户数据同步失败：{e}"

# 存储用户数据到本地local_data
# def store_user_dataToLocal(user_data):
#     with SessionLocal() as session:
#         # 使用集合操作来检查是否存在具有相同姓名、性别、电话的用户
#         # 现实情况一般使用用户的 ‘身份证号码’ 作为校验字段
#         try:
#             existing_user = session.query(LocalUser).filter(
#                 LocalUser.name == user_data['name'],
#                 LocalUser.sex == user_data['sex'],
#                 LocalUser.phone == user_data['phone']
#             ).first()
#             if existing_user:
#                 # 如果用户已存在，则不重复存储
#                 return False, "用户数据已存在，无需重复存储。"
#             new_user = LocalUser(
#                 name=user_data['name'],
#                 sex=user_data['sex'],
#                 phone=user_data['phone'],
#                 face_url=user_data['face_url']
#             )
#             session.add(new_user)
#             session.commit()
#             # 返回成功存储的信息
#             return True, "用户数据已成功存储。"
#         except Exception as e:
#             # 发生存储过程异常时回滚事务
#             session.rollback()
#             return False, str(e)


# 接口 2
@app.route('/insert_user', methods=['GET'])
def insert_user():
    user_id = request.args.get('id')
    # 验证用户ID参数是否存在且为有效整数
    if not user_id or not user_id.isdigit():
        return jsonify({'error': '用户ID参数必须提供且为有效整数'}), 400

    # 接口1的URL地址
    server_url = Config.SERVER_URL
    # print("1:url is:"+server_url)
    # 对数据库会话进行初始化
    init_db()
    try:
        # 向服务器发送请求以获取用户数据（查询id）
        response = requests.get(f'{server_url}/query_user', params={'id': user_id})
        response.raise_for_status()  # 如果响应状态码不是200，将抛出HTTPError异常
        user_data = response.json()
        # print(user_data)
        # 检查返回的用户数据是否完整
        if not all(key in user_data for key in ['name', 'sex', 'phone', 'face_url']):
            return jsonify({'error': '获取的用户数据不完整，请联系college运维人员'}), 400
        # 存储用户数据到本地数据库，并获取存储结果和信息
        # stored, msg = sync_user_data(user_data)
        sync_message = sync_user_data(user_id, user_data)
        return jsonify({'message': sync_message}), 200
    except requests.HTTPError as e:
        # 请求失败，则返回具体的HTTP错误信息
        if e.response.status_code == 404:
            return jsonify({'error': e.response.json().get('error', '用户不存在或ID错误')}), 404
        else:
            return jsonify(
            {'error': f'请求失败: 状态码 {e.response.status_code} - 原因 {e.response.reason}'}), e.response.status_code
    except requests.RequestException as e:
        # 请求异常（如网络问题），返回通用错误信息
        return jsonify({'error': f'请求失败: {e}'}), 500
    except ValueError as e:
        # 响应异常（例如，无法将字符串转换为整数），返回错误信息
        return jsonify({'error': f'响应错误: {e}'}), 400
    except Exception as e:
        # 其他异常，记录错误并返回通用错误信息
        return jsonify({'error': '处理失败', 'message': str(e)}), 500


# 启动 Flask 应用
if __name__ == '__main__':
    app.run(host=Config.CLIENT_HOST, port=Config.CLIENT_PORT, debug=Config.DEBUG)