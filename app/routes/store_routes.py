"""
식당 관련 API 엔드포인트
"""
from flask import Blueprint, jsonify, request
from app.services.congestion_service import CongestionService
from app.repositories.store_repository import StoreRepository
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('stores', __name__)

congestion_service = CongestionService()
store_repo = StoreRepository()


@bp.route('/stores', methods=['GET'])
def get_stores():
    """
    식당 목록 조회

    Query params:
        - latitude: 현재 위도
        - longitude: 현재 경도
        - radius: 검색 반경 (km, 기본값 1.0)
    """
    try:
        lat = request.args.get('latitude', type=float)
        lon = request.args.get('longitude', type=float)
        radius = request.args.get('radius', default=1.0, type=float)

        if lat and lon:
            stores = store_repo.find_nearby(lat, lon, radius)
        else:
            stores = store_repo.find_all()

        return jsonify({
            'success': True,
            'data': [store.to_dict() for store in stores],
            'count': len(stores)
        }), 200

    except Exception as e:
        logger.error(f"식당 목록 조회 실패: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '서버 오류가 발생했습니다.'
            }
        }), 500


@bp.route('/stores/', methods=['GET'])
def get_store(store_id):
    """식당 상세 정보 조회"""
    try:
        store = store_repo.find_by_id(store_id)

        if not store:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'STORE_NOT_FOUND',
                    'message': '존재하지 않는 식당입니다.',
                    'details': {'store_id': store_id}
                }
            }), 404

        return jsonify({
            'success': True,
            'data': store.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"식당 상세 조회 실패: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '서버 오류가 발생했습니다.'
            }
        }), 500


@bp.route('/stores//congestion', methods=['GET'])
def get_congestion(store_id):
    """
    식당 혼잡도 조회 (F-1, F-2)

    Query params:
        - target_time: 조회 시점 (ISO format, 선택)
    """
    try:
        from datetime import datetime

        target_time_str = request.args.get('target_time')
        target_time = None

        if target_time_str:
            try:
                target_time = datetime.fromisoformat(target_time_str)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'INVALID_TIME_FORMAT',
                        'message': 'target_time은 ISO 8601 형식이어야 합니다.'
                    }
                }), 400

        congestion_data = congestion_service.get_store_congestion(
            store_id, target_time
        )

        return jsonify({
            'success': True,
            'data': congestion_data
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'STORE_NOT_FOUND',
                'message': str(e)
            }
        }), 404

    except Exception as e:
        logger.error(f"혼잡도 조회 실패: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '서버 오류가 발생했습니다.'
            }
        }), 500


@bp.route('/stores//peak-times', methods=['GET'])
def get_peak_times(store_id):
    """가게별 피크 시간대 조회"""
    try:
        store = store_repo.find_by_id(store_id)

        if not store:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'STORE_NOT_FOUND',
                    'message': '존재하지 않는 식당입니다.'
                }
            }), 404

        peak_times = store_repo.get_peak_times(store.place_id)

        return jsonify({
            'success': True,
            'data': [pt.to_dict() for pt in peak_times]
        }), 200

    except Exception as e:
        logger.error(f"피크 시간대 조회 실패: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '서버 오류가 발생했습니다.'
            }
        }), 500