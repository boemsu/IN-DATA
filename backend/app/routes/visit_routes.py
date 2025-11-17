"""
방문 관련 API 엔드포인트
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from app.services.visit_tracking_service import VisitTrackingService
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('visits', __name__)

visit_service = VisitTrackingService()


@bp.route('/visits/intentions', methods=['POST'])
def register_intention():
    """
    방문 의사 등록 (F-3)

    Request body:
        {
            "user_id": "user_12345",
            "store_id": 42,
            "intended_time": "2025-11-14T12:30:00",
            "intended_people": 3
        }
    """
    try:
        data = request.get_json()

        # 필수 필드 검증
        required_fields = ['user_id', 'store_id', 'intended_time', 'intended_people']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'MISSING_FIELD',
                        'message': f'{field} 필드는 필수입니다.'
                    }
                }), 400

        # 시간 파싱
        try:
            intended_time = datetime.fromisoformat(data['intended_time'])
        except ValueError:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_TIME_FORMAT',
                    'message': 'intended_time은 ISO 8601 형식이어야 합니다.'
                }
            }), 400

        # 방문 의사 등록
        result = visit_service.register_visit_intention(
            user_id=data['user_id'],
            store_id=data['store_id'],
            intended_time=intended_time,
            intended_people=data['intended_people']
        )

        return jsonify({
            'success': True,
            'data': result
        }), 201

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400

    except Exception as e:
        logger.error(f"방문 의사 등록 실패: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '서버 오류가 발생했습니다.'
            }
        }), 500


@bp.route('/visits/actual', methods=['POST'])
def record_visit():
    """
    실제 방문 기록 (F-4 - 지오펜스 진입)

    Request body:
        {
            "user_id": "user_12345",
            "store_id": 42,
            "entry_time": "2025-11-14T12:35:00",
            "intended_people": 3
        }
    """
    try:
        data = request.get_json()

        # 필수 필드 검증
        required_fields = ['user_id', 'store_id', 'entry_time', 'intended_people']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'MISSING_FIELD',
                        'message': f'{field} 필드는 필수입니다.'
                    }
                }), 400

        # 시간 파싱
        try:
            entry_time = datetime.fromisoformat(data['entry_time'])
        except ValueError:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_TIME_FORMAT',
                    'message': 'entry_time은 ISO 8601 형식이어야 합니다.'
                }
            }), 400

        # 방문 기록
        result = visit_service.record_geofence_entry(
            user_id=data['user_id'],
            store_id=data['store_id'],
            entry_time=entry_time,
            intended_people=data['intended_people']
        )

        return jsonify({
            'success': True,
            'data': result
        }), 201

    except Exception as e:
        logger.error(f"실제 방문 기록 실패: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '서버 오류가 발생했습니다.'
            }
        }), 500


@bp.route('/visits/actual/exit', methods=['POST'])
def record_exit():
    """
    방문 종료 기록 (F-4 - 지오펜스 이탈)

    Request body:
        {
            "user_id": "user_12345",
            "store_id": 42,
            "exit_time": "2025-11-14T13:10:00"
        }
    """
    try:
        data = request.get_json()

        # 필수 필드 검증
        required_fields = ['user_id', 'store_id', 'exit_time']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'MISSING_FIELD',
                        'message': f'{field} 필드는 필수입니다.'
                    }
                }), 400

        # 시간 파싱
        try:
            exit_time = datetime.fromisoformat(data['exit_time'])
        except ValueError:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_TIME_FORMAT',
                    'message': 'exit_time은 ISO 8601 형식이어야 합니다.'
                }
            }), 400

        # 이탈 기록
        result = visit_service.record_geofence_exit(
            user_id=data['user_id'],
            store_id=data['store_id'],
            exit_time=exit_time
        )

        return jsonify({
            'success': True,
            'data': result
        }), 200

    except Exception as e:
        logger.error(f"방문 종료 기록 실패: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '서버 오류가 발생했습니다.'
            }
        }), 500