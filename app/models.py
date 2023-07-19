from sqlalchemy import DateTime, Column, Integer, String, Numeric
from datetime import datetime

from database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    item_number = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    # purchase_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    purchase_date = Column(String(10))
    item_name = Column(String, nullable=False)
    cost_per_item = Column(String, nullable=False)
    number_of_items = Column(String, nullable=False)
    total_cost = Column(String, nullable=False)
    current_price = Column(String, nullable=False)
    total_value = Column(String, nullable=False)
    total_return_dollar = Column(String, nullable=False)
    total_return_percent = Column(String, nullable=False)
    item_link = Column(String, nullable=False)
    
