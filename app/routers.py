from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from models import Inventory
from schemas import NewItem, InventoryResponse, UpdateItem
from services import create_item, get_item, delete_item_by_id, update_current_prices, update_current_price, update_calculated_fields, get_item_or_404
from database import get_db

router = APIRouter()

@router.get("/")
def read_root():
    # Redirect to the desired route or return the main template
    return RedirectResponse(url="/items")


@router.get("/items", response_model=List[InventoryResponse])
def get_items_route(db: Session = Depends(get_db)):
    items = get_item(db)
    return items


@router.get("/items/search", response_model=List[InventoryResponse])
def search_items(keyword: str, db: Session = Depends(get_db)):
    items = db.query(Inventory).filter(Inventory.item_name.ilike(f"%{keyword}%")).all()
    return items


@router.get("/items/{item_number}", response_model=InventoryResponse)
def read_item(item_number: int, db: Session = Depends(get_db)):
    item = get_item_or_404(db, item_number)
    return item


@router.post("/items/")
async def new_item(item: NewItem, db: Session = Depends(get_db)):
    new_item = create_item(db, item)
    return {"message": "Item created successfully"}


@router.put("/items/{item_id}", response_model=InventoryResponse)
def update_item_route(item_id: int, item: UpdateItem, db: Session = Depends(get_db)):
    # Check if the item exists
    existing_item = get_item_or_404(db, item_id)

    # Update the item's properties based on the changes in the UpdateItem object
    if item.item_name is not None:
        existing_item.item_name = item.item_name

    if item.cost_per_item is not None:
        existing_item.cost_per_item = str(item.cost_per_item)

    if item.number_of_items is not None:
        existing_item.number_of_items = str(item.number_of_items)

    if item.current_price is not None:
        existing_item.current_price = str(item.current_price)

    if item.purchase_date is not None:
        existing_item.purchase_date = datetime.strptime(item.purchase_date, "%m/%d/%Y").strftime("%m/%d/%Y")

    # Update the calculated fields
    update_calculated_fields(existing_item)

    db.commit()

    return existing_item


@router.delete("/items/{item_id}")
def delete_item_route(item_id: int, db: Session = Depends(get_db)):
    item = get_item_or_404(db, item_id)
    delete_item_by_id(db, item_id)
    return {"message": "Item deleted successfully."}


@router.post("/update/{item_id}")
def execute_update_prices(item_id: int, db: Session = Depends(get_db)):
    update_current_price(item_id, db)
    return {"message": "Current price updated successfully."}