class Config:
    DEBUG = True
    SECRET_KEY = 'your-secret-key'
    MYSQL_USERNAME = 'root'
    MYSQL_PASSWORD = '123456'
    MYSQL_HOST = 'localhost'
    MYSQL_DB = 'anti_database'
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SERVER = 'localhost'
    PORT = 5000
    JWT_SECRET_KEY = '8d576d31d18256c58f15ea7714e7ecf39f140dfcd9f5de87dbdad2632bf6d98d'
    JWT_ACCESS_TOKEN_EXPIRES = 3600
