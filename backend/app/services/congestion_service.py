"""
혼잡도 계산 서비스 (핵심 비즈니스 로직)
"""
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from app import redis_client
from app.repositories.store_repository import StoreRepository
from app.repositories.visit_repository import VisitRepository
from flask import current_app

logger = logging.getLogger(__name__)


class CongestionService:
    """혼잡도 계산 및 제공 서비스"""

    def __init__(self):
        self.store_repo = StoreRepository()
        self.visit_repo = VisitRepository()

    def get_store_congestion(
        self,
        store_id: int,
        target_time: Optional[datetime] = None
    ) -> Dict:
        """
        식당의 혼잡도 정보 조회
        R 모델 기반 예측 + 실시간 방문 데이터 결합

        Args:
            store_id: 식당 ID
            target_time: 조회 시점 (None이면 현재 시간)

        Returns:
            혼잡도 정보 딕셔너리
        """
        if target_time is None:
            target_time = datetime.utcnow()

        # 1. 식당 기본 정보 조회
        store = self.store_repo.find_by_id(store_id)
        if not store:
            raise ValueError(f"존재하지 않는 식당 ID: {store_id}")

        # 2. R 모델 기반 예측 혼잡도
        base_congestion = self._get_base_congestion_from_r_model(
            store.place_id,
            target_time.weekday(),
            target_time.hour
        )

        # 3. 실시간 방문 의사 데이터
        expected_visitors = self._get_expected_visitors(store_id, target_time)

        # 4. 현재 체류 중인 방문자 수
        current_visitors = self._get_current_visitors_count(store_id)

        # 5. 최종 혼잡도 계산
        realtime_congestion = self._calculate_final_congestion(
            base_congestion,
            expected_visitors,
            current_visitors
        )

        return {
            'store_id': store_id,
            'store_name': store.name,
            'predicted_congestion': base_congestion,
            'realtime_congestion': realtime_congestion,
            'current_visitors': current_visitors,
            'expected_visitors': expected_visitors,
            'timestamp': target_time.isoformat(),
            'congestion_level': self._get_congestion_level(realtime_congestion)
        }

    def _get_base_congestion_from_r_model(
        self,
        place_id: str,
        weekday: int,
        hour: int
    ) -> int:
        """
        R 모델 기반 기본 혼잡도 조회

        Args:
            place_id: 식당 Place ID
            weekday: 요일 (0=월요일, 6=일요일)
            hour: 시간 (0-23)

        Returns:
            기본 혼잡도 (0-100)
        """
        # 캐시 확인
        cache_key = f"r_model:congestion:{place_id}:{weekday}:{hour}"
        cached = redis_client.get(cache_key)

        if cached:
            return int(cached)

        # DB에서 R 모델 결과 조회
        pattern = self.store_repo.get_congestion_pattern(place_id)

        if not pattern:
            logger.warning(f"R 모델 데이터 없음: {place_id}, 기본값 반환")
            return 50  # 기본값

        # 시간대별 혼잡도 계산
        base = self._calculate_base_by_time(pattern, weekday, hour)

        # 캐시 저장
        ttl = current_app.config['CACHE_TTL_CONGESTION']
        redis_client.setex(cache_key, ttl, int(base))

        return int(base)

    def _calculate_base_by_time(self, pattern, weekday: int, hour: int) -> float:
        """
        시간대별 기본 혼잡도 계산
        R 모델의 avg_lunch, avg_dinner 등을 활용
        """
        # 점심 시간대 (11-14시)
        if 11 <= hour <= 14:
            return pattern.avg_lunch or pattern.avg_pop_all

        # 저녁 시간대 (18-21시)
        elif 18 <= hour <= 21:
            return pattern.avg_dinner or pattern.avg_pop_all

        # 주말 (토=5, 일=6)
        elif weekday >= 5:
            return pattern.avg_weekend or pattern.avg_pop_all

        # 평일
        else:
            return pattern.avg_weekday or pattern.avg_pop_all

    def _get_expected_visitors(self, store_id: int, target_time: datetime) -> int:
        """
        방문 예정 인원 수 계산
        target_time ±30분 내 방문 의사 합산
        """
        window = current_app.config['VISIT_INTENTION_WINDOW_MINUTES']
        intentions = self.visit_repo.get_active_intentions_by_store(
            store_id,
            window
        )

        total_people = sum(intention.intended_people for intention in intentions)
        return total_people

    def _get_current_visitors_count(self, store_id: int) -> int:
        """현재 매장 내 체류 중인 인원 수"""
        active_visits = self.visit_repo.get_current_visitors(store_id)

        total_people = sum(
            visit.intended_people or 1
            for visit in active_visits
        )
        return total_people

    def _calculate_final_congestion(
        self,
        base: float,
        expected: int,
        current: int
    ) -> int:
        """
        최종 혼잡도 계산

        Args:
            base: R 모델 기반 예측값 (0-100)
            expected: 방문 예정 인원
            current: 현재 체류 인원

        Returns:
            최종 혼잡도 (0-100)
        """
        # 간단한 가중치 계산
        # 실제로는 더 정교한 공식 필요 (매장 크기, 수용 인원 등 고려)
        adjustment = (expected + current) * 2  # 1명당 2% 증가

        final = base + adjustment

        # 0-100 범위로 제한
        return max(0, min(100, int(final)))

    def _get_congestion_level(self, congestion: int) -> str:
        """
        혼잡도 레벨 문자열 반환

        Args:
            congestion: 혼잡도 (0-100)

        Returns:
            '여유', '보통', '혼잡', '매우혼잡'
        """
        if congestion < 30:
            return '여유'
        elif congestion < 60:
            return '보통'
        elif congestion < 80:
            return '혼잡'
        else:
            return '매우혼잡'

    def invalidate_cache(self, store_id: int) -> None:
        """
        특정 식당의 혼잡도 캐시 무효화
        실시간 데이터 변경 시 호출
        """
        store = self.store_repo.find_by_id(store_id)
        if not store:
            return

        # 해당 식당의 모든 시간대 캐시 삭제
        pattern = f"r_model:congestion:{store.place_id}:*"
        keys = redis_client.keys(pattern)

        if keys:
            redis_client.delete(*keys)
            logger.info(f"캐시 무효화: {len(keys)}개 키 삭제 (store_id={store_id})")