"""
Flask 애플리케이션 초기화
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import redis
import logging
from config import config

# 전역 객체 선언
db = SQLAlchemy()
redis_client = None

def create_app(config_name='default'):
    """애플리케이션 팩토리 패턴"""
    app = Flask(__name__)

    # 설정 로드
    app.config.from_object(config[config_name])

    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO if not app.config['DEBUG'] else logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )

    # 데이터베이스 초기화
    db.init_app(app)

    # Redis 초기화
    global redis_client
    redis_client = redis.Redis(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
        db=app.config['REDIS_DB'],
        password=app.config['REDIS_PASSWORD'],
        decode_responses=True
    )

    # CORS 설정
    CORS(app, origins=app.config['CORS_ORIGINS'])

    # 블루프린트 등록
    from app.routes import store_routes, visit_routes, health_routes

    app.register_blueprint(store_routes.bp, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(visit_routes.bp, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(health_routes.bp)

    # 데이터베이스 테이블 생성
    with app.app_context():
        db.create_all()

    return app