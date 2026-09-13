from datetime import datetime, timezone
from models import db

class ShoppingList(db.Model):
    __tablename__ = 'shopping_lists'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    items = db.relationship('ShoppingItem', backref='shopping_list', cascade='all, delete-orphan', lazy='dynamic')
    history_records = db.relationship('ShoppingHistory', backref='shopping_list', lazy='dynamic')

    @property
    def total_items_count(self) -> int:
        return self.items.count()

    @property
    def pending_items_count(self) -> int:
        return self.items.filter_by(completed=False).count()

    @property
    def completed_items_count(self) -> int:
        return self.items.filter_by(completed=True).count()

    @property
    def is_completed(self) -> bool:
        return self.total_items_count > 0 and self.pending_items_count == 0

    @property
    def estimated_total(self) -> float:
        total = 0.0
        for item in self.items:
            total += item.total_estimated_price
        return round(total, 2)

    @property
    def actual_total(self) -> float:
        total = 0.0
        for item in self.items:
            if item.completed and item.actual_price is not None:
                total += float(item.actual_price)
        return round(total, 2)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else '',
            'total_items': self.total_items_count,
            'pending_items': self.pending_items_count,
            'completed_items': self.completed_items_count,
            'estimated_total': self.estimated_total,
            'actual_total': self.actual_total
        }

    def __repr__(self):
        return f"<ShoppingList id={self.id} title='{self.title}' user_id={self.user_id}>"
