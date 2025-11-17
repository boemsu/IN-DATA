"""
방문 추적 서비스
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from app.models.visit import VisitIntention, ActualVisit
from app.repositories.visit_repository import VisitRepository
from app.services.congestion_service import CongestionService
from flask import current_app

logger = logging.getLogger(__name__)


class VisitTrackingService:
    """방문 의사 및 실제 방문 추적 서비스"""

    def __init__(self):
        self.visit_repo = VisitRepository()
        self.congestion_service = CongestionService()

    def register_visit_intention(
        self,
        user_id: str,
        store_id: int,
        intended_time: datetime,
        intended_people: int
    ) -> Dict:
        """
        방문 의사 등록 (F-3)

        Args:
            user_id: 사용자 ID
            store_id: 식당 ID
            intended_time: 방문 예정 시간
            intended_people: 방문 인원

        Returns:
            등록된 방문 의사 정보
        """
        # 유효성 검증
        if intended_people < 1:
            raise ValueError("방문 인원은 1명 이상이어야 합니다.")

        if intended_time < datetime.utcnow():
            raise ValueError("방문 예정 시간은 현재 시간 이후여야 합니다.")

        # 방문 의사 생성
        intention = VisitIntention(
            user_id=user_id,
            store_id=store_id,
            intended_time=intended_time,
            intended_people=intended_people,
            is_active=True
        )

        # 저장
        saved = self.visit_repo.save_intention(intention)

        # 혼잡도 캐시 무효화
        self.congestion_service.invalidate_cache(store_id)

        logger.info(
            f"방문 의사 등록: user={user_id}, store={store_id}, "
            f"time={intended_time}, people={intended_people}"
        )

        return {
            'intention_id': saved.id,
            'tracking_started': True,
            'message': '위치 추적이 시작되었습니다.'
        }

    def record_geofence_entry(
        self,
        user_id: str,
        store_id: int,
        entry_time: datetime,
        intended_people: int
    ) -> Dict:
        """
        지오펜스 진입 기록 (F-4)

        Args:
            user_id: 사용자 ID
            store_id: 식당 ID
            entry_time: 진입 시간
            intended_people: 방문 인원

        Returns:
            기록된 방문 정보
        """
        # 중복 방문 체크 (5분 이내 재진입 방지)
        existing = self.visit_repo.find_active_visit_by_user_and_store(
            user_id, store_id
        )

        if existing:
            logger.warning(f"이미 활성 방문 존재: user={user_id}, store={store_id}")
            return {
                'visit_id': existing.id,
                'is_duplicate': True
            }

        # 실제 방문 기록 생성
        visit = ActualVisit(
            user_id=user_id,
            store_id=store_id,
            actual_entry_time=entry_time,
            intended_people=intended_people,
            is_valid_visit=True
        )

        # 저장
        saved = self.visit_repo.save_actual_visit(visit)

        # 혼잡도 캐시 무효화
        self.congestion_service.invalidate_cache(store_id)

        logger.info(
            f"지오펜스 진입 기록: user={user_id}, store={store_id}, "
            f"time={entry_time}, people={intended_people}"
        )

        return {
            'visit_id': saved.id,
            'is_duplicate': False,
            'message': '방문이 기록되었습니다.'
        }

    def record_geofence_exit(
        self,
        user_id: str,
        store_id: int,
        exit_time: datetime
    ) -> Dict:
        """
        지오펜스 이탈 기록

        Args:
            user_id: 사용자 ID
            store_id: 식당 ID
            exit_time: 이탈 시간

        Returns:
            업데이트된 방문 정보
        """
        # 활성 방문 조회
        visit = self.visit_repo.find_active_visit_by_user_and_store(
            user_id, store_id
        )

        if not visit:
            logger.warning(f"활성 방문 없음: user={user_id}, store={store_id}")
            return {
                'success': False,
                'message': '진입 기록이 없습니다.'
            }

        # 이탈 시간 업데이트
        visit = self.visit_repo.update_visit_exit(visit.id, exit_time)

        # 체류 시간 계산
        stay_time = visit.calculate_stay_time()
        min_stay = current_app.config['MIN_STAY_TIME_MINUTES']

        # 최소 체류 시간 미달 시 유효하지 않은 방문으로 처리
        if stay_time and stay_time < min_stay:
            visit.is_valid_visit = False
            logger.info(f"유효하지 않은 방문 (체류 시간 부족): {stay_time}분 < {min_stay}분")

        # 혼잡도 캐시 무효화
        self.congestion_service.invalidate_cache(store_id)

        logger.info(
            f"지오펜스 이탈 기록: user={user_id}, store={store_id}, "
            f"stay_time={stay_time}분, valid={visit.is_valid_visit}"
        )

        return {
            'visit_id': visit.id,
            'stay_time_minutes': stay_time,
            'is_valid_visit': visit.is_valid_visit,
            'message': '방문 종료가 기록되었습니다.'
        }