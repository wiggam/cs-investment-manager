from datetime import datetime
from sqlalchemy.orm import Session
from models import Inventory
from schemas import NewItem
from typing import Optional
from utils import price_finder
import time
from fastapi import HTTPException, status
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import Qt


def create_item(db: Session, item: NewItem):
    item_data = Inventory(
        # purchase_date=datetime.utcnow(),
        purchase_date=datetime.strptime(item.purchase_date, "%m/%d/%Y").strftime("%m/%d/%Y"),
        item_name=item.item_name,
        cost_per_item=str(item.cost_per_item),
        number_of_items=item.number_of_items,
        total_cost=str(item.total_cost),
        current_price=str(item.current_price),
        total_value=str(item.total_value),
        total_return_dollar=str(item.total_return_dollar),
        total_return_percent=str(item.total_return_percent),
        item_link=item.item_link
    )
    db.add(item_data)
    db.commit()
    db.refresh(item_data)
    return item_data

def get_item_or_404(db: Session, item_id: int) -> Inventory:
    item = get_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


def get_item(db: Session, item_number: Optional[int] = None):
    if item_number is not None:
        return db.query(Inventory).filter(Inventory.item_number == item_number).first()
    else:
        return db.query(Inventory).all()
    

def update_calculated_fields(item: Inventory):
    current_price = float(item.current_price)
    number_of_items = float(item.number_of_items)
    cost_per_item = float(item.cost_per_item)

    item.total_value = "{:.2f}".format(round(number_of_items * current_price, 2))
    item.total_cost = "{:.2f}".format(round(number_of_items * cost_per_item, 2))
    item.total_return_dollar = "{:.2f}".format(round(float(item.total_value) - float(item.total_cost), 2))
    item.total_return_percent = "{:.2f}".format(round((float(item.total_return_dollar) / float(item.total_cost)) * 100, 2))


def delete_item_by_id(db: Session, item_number: int):
    item = get_item(db, item_number)
    if item:
        db.delete(item)
        db.commit()
    return item


def update_current_prices(db: Session):
    items = db.query(Inventory).all()
    total_items = len(items)

    for i, item in enumerate(items):
        current_price = price_finder(item.item_link)

        # Update current_price
        item.current_price = current_price

        # Update other calculated fields
        update_calculated_fields(item)

        # Print message to indicate progress
        print(f"Updated current price and calculated fields for Item {item.item_number}")

        # Yield the progress status
        yield {
            "progress": i + 1,
            "total_items": total_items,
            "message": f"Updated current price and calculated fields for Item {item.item_number}"
        }

        # Delay between requests to avoid timing out
        time.sleep(3.5)

    db.commit()

def update_current_price(item_number: int, db: Session):
    item = get_item(db, item_number)
    current_price = price_finder(item.item_link)
    item.current_price = current_price
    update_calculated_fields(item)
    db.commit()
    