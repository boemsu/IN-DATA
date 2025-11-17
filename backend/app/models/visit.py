"""
방문 관련 데이터 모델
"""
from app import db
from datetime import datetime


class VisitIntention(db.Model):
    """방문 의사 데이터 (F-3)"""
    __tablename__ = 'visit_intentions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False, index=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    intended_time = db.Column(db.DateTime, nullable=False)
    intended_people = db.Column(db.Integer, nullable=False)
    intention_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)  # 추적 중인지 여부

    # 관계
    store = db.relationship('Store', backref='visit_intentions')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'store_id': self.store_id,
            'intended_time': self.intended_time.isoformat(),
            'intended_people': self.intended_people,
            'intention_timestamp': self.intention_timestamp.isoformat(),
            'is_active': self.is_active
        }


class ActualVisit(db.Model):
    """실제 방문 데이터 (F-4)"""
    __tablename__ = 'actual_visits'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False, index=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    actual_entry_time = db.Column(db.DateTime, nullable=False)
    actual_exit_time = db.Column(db.DateTime)
    intended_people = db.Column(db.Integer)
    is_valid_visit = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 관계
    store = db.relationship('Store', backref='actual_visits')

    def calculate_stay_time(self):
        """체류 시간 계산 (분)"""
        if self.actual_exit_time:
            delta = self.actual_exit_time - self.actual_entry_time
            return int(delta.total_seconds() / 60)
        return None

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'store_id': self.store_id,
            'actual_entry_time': self.actual_entry_time.isoformat(),
            'actual_exit_time': self.actual_exit_time.isoformat() if self.actual_exit_time else None,
            'intended_people': self.intended_people,
            'stay_time_minutes': self.calculate_stay_time(),
            'is_valid_visit': self.is_valid_visit
        }