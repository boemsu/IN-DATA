"""
헬스 체크 엔드포인트
"""
from flask import Blueprint, jsonify
from app import db, redis_client
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('health', __name__)


@bp.route('/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    try:
        # DB 연결 확인
        db.session.execute('SELECT 1')
        db_status = 'ok'
    except Exception as e:
        logger.error(f"DB 연결 실패: {e}")
        db_status = 'error'

    try:
        # Redis 연결 확인
        redis_client.ping()
        redis_status = 'ok'
    except Exception as e:
        logger.error(f"Redis 연결 실패: {e}")
        redis_status = 'error'

    status_code = 200 if db_status == 'ok' and redis_status == 'ok' else 503

    return jsonify({
        'status': 'healthy' if status_code == 200 else 'unhealthy',
        'database': db_status,
        'redis': redis_status
    }), status_code