from datetime import datetime, timezone
from models import db

class ShoppingItem(db.Model):
    __tablename__ = 'shopping_items'

    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('shopping_lists.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    item_name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=1.0)
    unit = db.Column(db.String(50), nullable=False, default='pcs')
    estimated_price = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    actual_price = db.Column(db.Numeric(10, 2), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    @property
    def total_estimated_price(self) -> float:
        return round(float(self.estimated_price or 0.0), 2)

    @property
    def total_actual_price(self) -> float:
        if self.actual_price is not None:
            return round(float(self.actual_price), 2)
        return 0.0

    def to_dict(self):
        return {
            'id': self.id,
            'list_id': self.list_id,
            'user_id': self.user_id,
            'item_name': self.item_name,
            'category': self.category,
            'quantity': float(self.quantity),
            'unit': self.unit,
            'estimated_price': float(self.estimated_price) if self.estimated_price is not None else 0.0,
            'actual_price': float(self.actual_price) if self.actual_price is not None else None,
            'total_estimated_price': self.total_estimated_price,
            'total_actual_price': self.total_actual_price,
            'notes': self.notes or '',
            'completed': self.completed,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else ''
        }

    def __repr__(self):
        return f"<ShoppingItem id={self.id} item_name='{self.item_name}' list_id={self.list_id} completed={self.completed}>"
