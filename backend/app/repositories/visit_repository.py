"""
방문 데이터 접근 레이어
"""
from typing import List, Optional
from datetime import datetime, timedelta
from app import db
from app.models.visit import VisitIntention, ActualVisit


class VisitRepository:
    """방문 Repository"""

    @staticmethod
    def save_intention(intention: VisitIntention) -> VisitIntention:
        """방문 의사 저장"""
        db.session.add(intention)
        db.session.commit()
        return intention

    @staticmethod
    def get_active_intentions_by_store(
        store_id: int,
        time_window_minutes: int = 30
    ) -> List[VisitIntention]:
        """
        특정 식당의 활성 방문 의사 조회
        현재 시간 ±time_window_minutes 내의 의사만 반환
        """
        now = datetime.utcnow()
        time_start = now - timedelta(minutes=time_window_minutes)
        time_end = now + timedelta(minutes=time_window_minutes)

        return VisitIntention.query.filter(
            VisitIntention.store_id == store_id,
            VisitIntention.is_active == True,
            VisitIntention.intended_time.between(time_start, time_end)
        ).all()

    @staticmethod
    def save_actual_visit(visit: ActualVisit) -> ActualVisit:
        """실제 방문 저장"""
        db.session.add(visit)
        db.session.commit()
        return visit

    @staticmethod
    def get_current_visitors(store_id: int) -> List[ActualVisit]:
        """현재 매장에 체류 중인 방문 기록 조회"""
        return ActualVisit.query.filter(
            ActualVisit.store_id == store_id,
            ActualVisit.actual_exit_time.is_(None),
            ActualVisit.is_valid_visit == True
        ).all()

    @staticmethod
    def update_visit_exit(visit_id: int, exit_time: datetime) -> Optional[ActualVisit]:
        """방문 종료 시간 업데이트"""
        visit = ActualVisit.query.get(visit_id)
        if visit:
            visit.actual_exit_time = exit_time
            db.session.commit()
        return visit

    @staticmethod
    def find_active_visit_by_user_and_store(
        user_id: str,
        store_id: int
    ) -> Optional[ActualVisit]:
        """사용자의 특정 식당 활성 방문 조회"""
        return ActualVisit.query.filter(
            ActualVisit.user_id == user_id,
            ActualVisit.store_id == store_id,
            ActualVisit.actual_exit_time.is_(None)
        ).first()