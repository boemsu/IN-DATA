"""
식당 관련 데이터 모델
"""
from app import db
from datetime import datetime


class Store(db.Model):
    """식당 기본 정보"""
    __tablename__ = 'stores'

    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(500))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    opening_hours = db.Column(db.JSON)  # {"월": "09:00-22:00", ...}
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """JSON 직렬화"""
        return {
            'id': self.id,
            'place_id': self.place_id,
            'name': self.name,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'category': self.category,
            'opening_hours': self.opening_hours,
            'phone': self.phone
        }


class StoreCongestionPattern(db.Model):
    """R 모델 분석 결과 저장"""
    __tablename__ = 'store_congestion_patterns'

    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    store_name = db.Column(db.String(200))
    cluster = db.Column(db.Integer)  # K-means 클러스터 번호
    avg_pop_all = db.Column(db.Float)
    max_pop = db.Column(db.Float)
    avg_lunch = db.Column(db.Float)
    avg_dinner = db.Column(db.Float)
    avg_weekday = db.Column(db.Float)
    avg_weekend = db.Column(db.Float)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'place_id': self.place_id,
            'store_name': self.store_name,
            'cluster': self.cluster,
            'avg_pop_all': self.avg_pop_all,
            'max_pop': self.max_pop,
            'avg_lunch': self.avg_lunch,
            'avg_dinner': self.avg_dinner,
            'avg_weekday': self.avg_weekday,
            'avg_weekend': self.avg_weekend
        }


class StorePeakTime(db.Model):
    """가게별 피크 시간대"""
    __tablename__ = 'store_peak_times'

    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.String(50), nullable=False, index=True)
    weekday = db.Column(db.String(10), nullable=False)  # '월', '화', ...
    peak_hour = db.Column(db.Integer, nullable=False)
    peak_congestion = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'place_id': self.place_id,
            'weekday': self.weekday,
            'peak_hour': self.peak_hour,
            'peak_congestion': self.peak_congestion
        }