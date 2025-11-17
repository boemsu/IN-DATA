"""
식당 데이터 접근 레이어
"""
from typing import List, Optional
from app import db
from app.models.store import Store, StoreCongestionPattern, StorePeakTime


class StoreRepository:
    """식당 Repository"""

    @staticmethod
    def find_by_id(store_id: int) -> Optional[Store]:
        """ID로 식당 조회"""
        return Store.query.get(store_id)

    @staticmethod
    def find_by_place_id(place_id: str) -> Optional[Store]:
        """Place ID로 식당 조회"""
        return Store.query.filter_by(place_id=place_id).first()

    @staticmethod
    def find_all() -> List[Store]:
        """모든 식당 조회"""
        return Store.query.all()

    @staticmethod
    def find_nearby(latitude: float, longitude: float, radius_km: float = 1.0) -> List[Store]:
        """
        주변 식당 조회 (간단한 거리 계산)
        실제로는 PostGIS 등을 사용하는 것이 좋음
        """
        # 위도/경도 1도 ≈ 111km
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / (111.0 * abs(latitude))

        return Store.query.filter(
            Store.latitude.between(latitude - lat_delta, latitude + lat_delta),
            Store.longitude.between(longitude - lon_delta, longitude + lon_delta)
        ).all()

    @staticmethod
    def get_congestion_pattern(place_id: str) -> Optional[StoreCongestionPattern]:
        """R 모델 분석 결과 조회"""
        return StoreCongestionPattern.query.filter_by(place_id=place_id).first()

    @staticmethod
    def get_peak_times(place_id: str) -> List[StorePeakTime]:
        """피크 시간대 조회"""
        return StorePeakTime.query.filter_by(place_id=place_id).all()

    @staticmethod
    def save(store: Store) -> Store:
        """식당 저장"""
        db.session.add(store)
        db.session.commit()
        return store