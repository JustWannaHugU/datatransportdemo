import os
from cryptography.fernet import Fernet

class Config:
    #敏感信息，加密处理
    COLLEGE_DATABASE_URI = 'gAAAAABmHGuXxiNYGZB9XQBqtiAJpGyRr_vlE3YM84Q0ENI_j7hCcONGPXCXquN5bzYOETYL6bYzl6wRM_UkSMS9_NuxKQkMoWZoD2Tf86PqslHLHBVbUlgNhWzJY9j_2nmYsX4F7vwf90flcfMNR0eKJFMlKRhqSW1GlRvEalx9yKs4dcqFIck='
    LOCAL_DATABASE_URI = 'gAAAAABmHGuXwevu6Ir_E3oJgcNaVlRuWTlsVwthVfYG_RLZO0CcEM9Jv1JcacDtDpXrpr5-1_2cZdjpbh1IFZj1982O6MJnltruGmyCbmK4SS_uvReIDyrfc9cerQtlPDXObxUygaNa5y3-HRzxP6rDxnhrHc5UqKioNExpnPUKVWLlYeEREfM='
    #非敏感数据
    DEBUG = False
    SERVER_HOST = '0.0.0.0'
    CLIENT_HOST = '0.0.0.0'
    SERVER_PORT = 9090
    CLIENT_PORT = 9091
    #接口1 地址
    SERVER_URL = 'http://localhost:9090'

    def _decrypt(encrypted_data):
        #从环境变量中获取密钥 key 用来解密
        key = os.getenv('FERNET_KEY')
        # 使用密钥解密数据
        fernet = Fernet(key)
        return fernet.decrypt(encrypted_data.encode()).decode()


# 从环境变量中得到 key
# config 中显示的是 database 的密文地址
# 可在链接时调用 decrypt 中的 decode 方法对密文进行解密
# 运行时才进行解密
if __name__ == '__main__':
    config = Config()
    # 敏感数据需要加密
    # college_data_url = 'mysql+pymysql://root:my_password@localhost:3306/college_data?charset=utf8'
    # local_data_url = 'mysql+pymysql://root:my_password@localhost:3306/local_data?charset=utf8'
    college_data = 'gAAAAABmHGuXxiNYGZB9XQBqtiAJpGyRr_vlE3YM84Q0ENI_j7hCcONGPXCXquN5bzYOETYL6bYzl6wRM_UkSMS9_NuxKQkMoWZoD2Tf86PqslHLHBVbUlgNhWzJY9j_2nmYsX4F7vwf90flcfMNR0eKJFMlKRhqSW1GlRvEalx9yKs4dcqFIck='
    local_data = 'gAAAAABmHGuXwevu6Ir_E3oJgcNaVlRuWTlsVwthVfYG_RLZO0CcEM9Jv1JcacDtDpXrpr5-1_2cZdjpbh1IFZj1982O6MJnltruGmyCbmK4SS_uvReIDyrfc9cerQtlPDXObxUygaNa5y3-HRzxP6rDxnhrHc5UqKioNExpnPUKVWLlYeEREfM='


    #
    decrypted_college_data = Config._decrypt(college_data, config._fernet)
    print("college解密后:", Config._decrypt(college_data, config._fernet))
    print("local解密后", Config._decrypt(local_data, config._fernet))
