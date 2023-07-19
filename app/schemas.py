from pydantic import BaseModel, validator
from utils import name_finder, price_finder
from typing import Optional
from datetime import datetime
from fastapi import HTTPException

class NewItem(BaseModel):
    cost_per_item: float
    number_of_items: int
    item_link: str

    @property
    def item_name(self) -> str:
        return name_finder(self.item_link)

    @property
    def current_price(self) -> int:
        return price_finder(self.item_link)

    @property
    def total_cost(self) -> int:
        return round(self.cost_per_item * self.number_of_items,2)

    @property
    def total_value(self) -> int:
        return round(self.number_of_items * self.current_price,2)

    @property
    def total_return_dollar(self) -> int:
        return round(self.total_value - self.total_cost, 2)
    
    @property
    def total_return_percent(self) -> int:
        return round((self.total_return_dollar / self.total_cost) * 100, 2)

    @property
    def purchase_date(self) -> str:
        return datetime.now().strftime("%m/%d/%Y")
    
class InventoryResponse(BaseModel):
    item_number: int    
    purchase_date: str
    item_name: str
    cost_per_item: float
    number_of_items: int
    total_cost: float
    current_price: float
    total_value: float
    total_return_dollar: float
    total_return_percent: float
    item_link: str

class UpdateItem(BaseModel):
    item_name: Optional[str] = None
    cost_per_item: Optional[float] = None
    number_of_items: Optional[int] = None
    current_price: Optional[float] = None
    purchase_date: Optional[str] = None

    @validator('purchase_date')
    def validate_purchase_date(cls, value):
        if value is not None:
            try:
                # Check if the value can be parsed as a valid date
                datetime.strptime(value, "%m/%d/%Y")
            except ValueError:
                # Raise an HTTPException if the format is invalid
                raise HTTPException(status_code=400, detail="Invalid purchase date format. Use 'MM/DD/YYYY' format.")
        return value
