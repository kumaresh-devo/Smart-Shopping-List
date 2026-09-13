from datetime import datetime, timezone
from models import db

class ShoppingHistory(db.Model):
    __tablename__ = 'shopping_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    list_id = db.Column(db.Integer, db.ForeignKey('shopping_lists.id', ondelete='SET NULL'), nullable=True, index=True)
    item_name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=1.0)
    actual_price = db.Column(db.Numeric(10, 2), nullable=False)
    purchase_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    @property
    def total_cost(self) -> float:
        return round(float(self.actual_price), 2)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'list_id': self.list_id,
            'list_title': self.shopping_list.title if self.shopping_list else 'Deleted / General',
            'item_name': self.item_name,
            'category': self.category,
            'quantity': float(self.quantity),
            'actual_price': float(self.actual_price),
            'total_cost': self.total_cost,
            'purchase_date': self.purchase_date.strftime('%Y-%m-%d %H:%M:%S') if self.purchase_date else ''
        }

    def __repr__(self):
        return f"<ShoppingHistory id={self.id} item='{self.item_name}' actual_price={self.actual_price}>"
