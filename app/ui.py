from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QWidget, QTableWidget, QTableWidgetItem, QMessageBox, QProgressBar, QGridLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QCoreApplication, QEvent, Qt
from typing import List
from requests import get, post, put, delete
from pydantic import BaseModel
import sys
import time
import threading


# FastAPI routes information
BASE_URL = "http://localhost:8000"
ITEMS_URL = f"{BASE_URL}/items"
UPDATE_PRICES_URL = f"{BASE_URL}/update"
ADD_ITEM_URL = f"{BASE_URL}/items/"


class InventoryItem(BaseModel):
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Steam Investment Manager')
        self.setGeometry(100, 100, 1260, 648)

        self.layout = QVBoxLayout()

        self.title_label = QLabel('Steam Investment Manager', self)
        self.title_label.setFont(QFont('Arial', 14, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)

        self.search_layout = QHBoxLayout()
        self.search_label = QLabel('Search:', self)
        self.text_input = QLineEdit(self)
        self.search_button = QPushButton('Search', self)
        self.clear_button = QPushButton('Clear', self)
        self.search_layout.addWidget(self.search_label)
        self.search_layout.addWidget(self.text_input)
        self.search_layout.addWidget(self.search_button)
        self.search_layout.addWidget(self.clear_button)

        self.table = QTableWidget(self)
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["Item Number", "Purchase Date", "Item Name", "Cost per Item",
                                              "Number of Items", "Total Cost", "Current Price", "Total Value",
                                              "Total Return Dollar"])

        self.stats_layout = QGridLayout()
        self.stats_layout.setHorizontalSpacing(10)  # Set horizontal spacing between columns

        self.stats_label = QLabel('Investment Statistics', self)
        self.stats_label.setFont(QFont('Arial', 9, QFont.Bold))
        self.total_cost_label = QLabel('Total Cost:', self)
        self.total_cost_value = QLabel('', self)
        self.total_value_label = QLabel('Total Value:', self)
        self.total_value_value = QLabel('', self)
        self.total_return_dollar_label = QLabel('Total Return Dollar:', self)
        self.total_return_dollar_value = QLabel('', self)
        self.total_return_percent_label = QLabel('Total Return Percent:', self)
        self.total_return_percent_value = QLabel('', self)

        self.stats_layout.addWidget(self.stats_label, 0, 0)  # Add stats_label to the grid layout
        self.stats_layout.addWidget(self.total_cost_label, 1, 0)
        self.stats_layout.addWidget(self.total_cost_value, 1, 1)
        self.stats_layout.addWidget(self.total_value_label, 2, 0)
        self.stats_layout.addWidget(self.total_value_value, 2, 1)
        self.stats_layout.addWidget(self.total_return_dollar_label, 3, 0)
        self.stats_layout.addWidget(self.total_return_dollar_value, 3, 1)
        self.stats_layout.addWidget(self.total_return_percent_label, 4, 0)
        self.stats_layout.addWidget(self.total_return_percent_value, 4, 1)

        # Add blank columns to the right
        self.stats_layout.setColumnStretch(2, 1)
        self.stats_layout.setColumnStretch(3, 1)

        self.action_label = QLabel('Select Action', self)
        self.action_label.setFont(QFont('Arial', 9, QFont.Bold))
        self.add_item_button = QPushButton('Add Item', self)
        self.update_item_button = QPushButton('Update Item', self)
        self.update_prices_button = QPushButton('Update Prices', self)
        self.delete_item_button = QPushButton('Delete Item', self)

        self.action_space_label = QLabel('', self)
        self.action_space_inputs = []

        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.add_item_button)
        self.button_layout.addWidget(self.update_item_button)
        self.button_layout.addWidget(self.update_prices_button)
        self.button_layout.addWidget(self.delete_item_button)

        self.layout.addWidget(self.title_label)
        self.layout.addLayout(self.search_layout)
        self.layout.addWidget(self.table)
        self.layout.addLayout(self.stats_layout)
        self.layout.addWidget(self.action_label)
        self.layout.addLayout(self.button_layout)
        self.layout.addWidget(self.action_space_label)

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        self.search_button.clicked.connect(self.search_items)
        self.clear_button.clicked.connect(self.clear_search)
        self.add_item_button.clicked.connect(self.open_add_item_window)
        self.update_item_button.clicked.connect(self.open_update_item_window)
        self.update_prices_button.clicked.connect(self.open_update_prices_window)
        self.delete_item_button.clicked.connect(self.open_delete_item_window)

        self.update_table()
        self.update_statistics()

    def search_items(self):
        keyword = self.text_input.text()
        response = get(f'{ITEMS_URL}/search?keyword={keyword}')
        if response.status_code == 200:
            items = response.json()

            self.table.setRowCount(len(items))

            for row, item in enumerate(items):
                self.table.setItem(row, 0, QTableWidgetItem(str(item['item_number'])))
                self.table.setItem(row, 1, QTableWidgetItem(item['purchase_date']))
                self.table.setItem(row, 2, QTableWidgetItem(item['item_name']))
                self.table.setItem(row, 3, QTableWidgetItem(str(item['cost_per_item'])))
                self.table.setItem(row, 4, QTableWidgetItem(str(item['number_of_items'])))
                self.table.setItem(row, 5, QTableWidgetItem(str(item['total_cost'])))
                self.table.setItem(row, 6, QTableWidgetItem(str(item['current_price'])))
                self.table.setItem(row, 7, QTableWidgetItem(str(item['total_value'])))
                self.table.setItem(row, 8, QTableWidgetItem(str(item['total_return_dollar'])))

            # Calculate updated statistics based on filtered items
            self.calculate_and_update_statistics(items)

        else:
            self.show_error_popup('Error', 'An error occurred while searching items.')

    def clear_search(self):
        self.text_input.clear()
        self.update_table()

    def update_table(self):
        response = get(ITEMS_URL)
        if response.status_code == 200:
            items = response.json()

            self.table.setRowCount(len(items))

            for row, item in enumerate(items):
                self.table.setItem(row, 0, QTableWidgetItem(str(item['item_number'])))
                self.table.setItem(row, 1, QTableWidgetItem(item['purchase_date']))
                self.table.setItem(row, 2, QTableWidgetItem(item['item_name']))
                self.table.setItem(row, 3, QTableWidgetItem(str(item['cost_per_item'])))
                self.table.setItem(row, 4, QTableWidgetItem(str(item['number_of_items'])))
                self.table.setItem(row, 5, QTableWidgetItem(str(item['total_cost'])))
                self.table.setItem(row, 6, QTableWidgetItem(str(item['current_price'])))
                self.table.setItem(row, 7, QTableWidgetItem(str(item['total_value'])))
                self.table.setItem(row, 8, QTableWidgetItem(str(item['total_return_dollar'])))

            # Calculate updated statistics based on all items
            self.calculate_and_update_statistics(items)

        else:
            self.show_error_popup('Error', 'An error occurred while fetching items.')

    def update_statistics(self):
        response = get(ITEMS_URL)
        if response.status_code == 200:
            items = response.json()

            total_cost = sum(item['total_cost'] for item in items)
            total_value = sum(item['total_value'] for item in items)
            total_return_dollar = sum(item['total_return_dollar'] for item in items)
            total_return_percent = (total_return_dollar / total_cost) * 100 if total_cost != 0 else 0

            self.total_cost_value.setText('${:,.2f}'.format(total_cost))
            self.total_value_value.setText('${:,.2f}'.format(total_value))
            self.total_return_dollar_value.setText('${:,.2f}'.format(total_return_dollar))
            self.total_return_percent_value.setText('{}%'.format(round(total_return_percent)))

        else:
            self.show_error_popup('Error', 'An error occurred while fetching statistics.')

    def calculate_and_update_statistics(self, items):
        total_cost = sum(item['total_cost'] for item in items)
        total_value = sum(item['total_value'] for item in items)
        total_return_dollar = sum(item['total_return_dollar'] for item in items)
        total_return_percent = (total_return_dollar / total_cost) * 100 if total_cost != 0 else 0

        self.total_cost_value.setText('${:,.2f}'.format(total_cost))
        self.total_value_value.setText('${:,.2f}'.format(total_value))
        self.total_return_dollar_value.setText('${:,.2f}'.format(total_return_dollar))
        self.total_return_percent_value.setText('{}%'.format(round(total_return_percent)))

    def open_add_item_window(self):
        add_item_window = AddItemWindow(self)
        add_item_window.show()

    def open_update_item_window(self):
        update_item_window = UpdateItemWindow(self)
        update_item_window.show()

    def open_update_prices_window(self):
        update_prices_window = UpdatePricesWindow(self)
        update_prices_window.show()

    def open_delete_item_window(self):
        delete_item_window = DeleteItemWindow(self)
        delete_item_window.show()

    def show_error_popup(self, title: str, message: str):
        QMessageBox.critical(self, title, message)


class AddItemWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Add Item')
        self.setGeometry(200, 200, 400, 200)

        self.central_widget = QWidget(self)

        self.item_link_label = QLabel('Item Link:', self.central_widget)
        self.item_link_input = QLineEdit(self.central_widget)

        self.number_of_items_label = QLabel('Number of Items:', self.central_widget)
        self.number_of_items_input = QLineEdit(self.central_widget)

        self.cost_per_item_label = QLabel('Cost per Item:', self.central_widget)
        self.cost_per_item_input = QLineEdit(self.central_widget)

        self.add_button = QPushButton('Add', self.central_widget)
        self.cancel_button = QPushButton('Cancel', self.central_widget)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.item_link_label)
        self.layout.addWidget(self.item_link_input)
        self.layout.addWidget(self.number_of_items_label)
        self.layout.addWidget(self.number_of_items_input)
        self.layout.addWidget(self.cost_per_item_label)
        self.layout.addWidget(self.cost_per_item_input)
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.cancel_button)

        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.add_button.clicked.connect(self.add_item)

    def add_item(self):
        item_link = self.item_link_input.text()
        number_of_items = self.number_of_items_input.text()
        cost_per_item = self.cost_per_item_input.text()

        payload = {
            "item_link": item_link,
            "number_of_items": int(number_of_items),
            "cost_per_item": float(cost_per_item)
        }

        response = post(ADD_ITEM_URL, json=payload)
        if response.status_code == 200:
            QMessageBox.information(self, 'Success', 'Item added successfully.')
            self.close()
            self.parent().update_table()
        else:
            self.show_error_popup('Error', 'An error occurred while adding the item.')

    def show_error_popup(self, title: str, message: str):
        QMessageBox.critical(self, title, message)


class UpdateItemWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.item_number = None

        self.setWindowTitle('Update Item')
        self.setGeometry(200, 200, 400, 250)

        self.central_widget = QWidget(self)

        self.item_number_label = QLabel('Item Number:', self.central_widget)
        self.item_number_input = QLineEdit(self.central_widget)

        self.item_name_label = QLabel('Item Name:', self.central_widget)
        self.item_name_input = QLineEdit(self.central_widget)

        self.number_of_items_label = QLabel('Number of Items:', self.central_widget)
        self.number_of_items_input = QLineEdit(self.central_widget)

        self.cost_per_item_label = QLabel('Cost per Item:', self.central_widget)
        self.cost_per_item_input = QLineEdit(self.central_widget)

        self.current_price_label = QLabel('Current Price:', self.central_widget)
        self.current_price_input = QLineEdit(self.central_widget)

        self.purchase_date_label = QLabel('Purchase Date (MM/DD/YYYY):', self.central_widget)
        self.purchase_date_input = QLineEdit(self.central_widget)

        self.update_button = QPushButton('Update', self.central_widget)
        self.cancel_button = QPushButton('Cancel', self.central_widget)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.item_number_label)
        self.layout.addWidget(self.item_number_input)
        self.layout.addWidget(self.item_name_label)
        self.layout.addWidget(self.item_name_input)
        self.layout.addWidget(self.number_of_items_label)
        self.layout.addWidget(self.number_of_items_input)
        self.layout.addWidget(self.cost_per_item_label)
        self.layout.addWidget(self.cost_per_item_input)
        self.layout.addWidget(self.current_price_label)
        self.layout.addWidget(self.current_price_input)
        self.layout.addWidget(self.purchase_date_label)
        self.layout.addWidget(self.purchase_date_input)
        self.layout.addWidget(self.update_button)
        self.layout.addWidget(self.cancel_button)

        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.update_button.clicked.connect(self.update_item)

    def update_item(self):
        item_number = self.item_number_input.text()
        item_name = self.item_name_input.text()
        number_of_items = self.number_of_items_input.text()
        cost_per_item = self.cost_per_item_input.text()
        current_price = self.current_price_input.text()
        purchase_date = self.purchase_date_input.text()

        payload = {}

        if item_name:
            payload["item_name"] = item_name

        if number_of_items:
            payload["number_of_items"] = int(number_of_items)

        if cost_per_item:
            payload["cost_per_item"] = float(cost_per_item)

        if current_price:
            payload["current_price"] = float(current_price)

        if purchase_date:
            payload["purchase_date"] = purchase_date

        response = put(f"http://127.0.0.1:8000/items/{item_number}", json=payload)
        if response.status_code == 200:
            QMessageBox.information(self, 'Success', 'Item updated successfully.')
            self.close()
            self.parent().update_table()
        else:
            self.show_error_popup('Error', 'An error occurred while updating the item.')


            response = post(f"http://127.0.0.1:8000/update/{item_number}", json=payload)
            if response.status_code == 200:
                QMessageBox.information(self, 'Success', 'Item updated successfully.')
                self.close()
                self.parent().update_table()
                self.parent().update_statistics()
            else:
                self.show_error_popup('Error', 'An error occurred while updating the item.')



    def show_error_popup(self, title: str, message: str):
        QMessageBox.critical(self, title, message)

# Define the custom event class
class UpdateCompleteEvent(QEvent):
    def __init__(self):
        super().__init__(QEvent.User)

class UpdatePricesWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Update Prices')
        self.setGeometry(200, 200, 400, 200)

        self.central_widget = QWidget(self)

        self.progress_bar = QProgressBar(self.central_widget)
        self.progress_bar.setGeometry(30, 40, 340, 25)

        self.update_button = QPushButton('Update', self.central_widget)


        self.layout = QVBoxLayout()
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.update_button)
        

        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)
        

        self.update_button.clicked.connect(self.execute_update_prices)
    

    def execute_update_prices(self):
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(100)

        response = get(ITEMS_URL)
        if response.status_code == 200:
            items = response.json()
            total_items = len(items)
            if total_items > 0:
                increment = 100 / total_items
                thread = threading.Thread(target=self.update_prices_thread, args=(items, increment))
                thread.start()
            else:
                QMessageBox.information(self, 'No Items', 'No items to update.')
        else:
            self.show_error_popup('Error', 'An error occurred while updating prices.')

    def update_prices_thread(self, items, increment):
        for index, item in enumerate(items):
            # Update progress bar
            self.progress_bar.setValue(int((index + 1) * increment))

            # Update item price
            item_id = item['item_number']  # Adjust the key name if needed
            response = post(f'http://127.0.0.1:8000/update/{item_id}')
            if response.status_code != 200:
                self.show_error_popup('Error', f'Failed to update price for item: {item_id}')

            # Delay before the next request
            time.sleep(3.5)

        QCoreApplication.postEvent(self, UpdateCompleteEvent())

    def customEvent(self, event):
        if isinstance(event, UpdateCompleteEvent):
            self.update_complete()

    def update_complete(self):
        # Perform actions when the update process is complete
        QMessageBox.information(self, 'Update Complete', 'Prices updated successfully.')
        self.close()
        self.parent().update_table()

    def show_error_popup(self, title: str, message: str):
        QMessageBox.critical(self, title, message)

class DeleteItemWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.item_number = None

        self.setWindowTitle('Delete Item')
        self.setGeometry(200, 200, 400, 150)

        self.central_widget = QWidget(self)

        self.item_number_label = QLabel('Item Number:', self.central_widget)
        self.item_number_input = QLineEdit(self.central_widget)

        self.delete_button = QPushButton('Delete', self.central_widget)
        self.cancel_button = QPushButton('Cancel', self.central_widget)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.item_number_label)
        self.layout.addWidget(self.item_number_input)
        self.layout.addWidget(self.delete_button)
        self.layout.addWidget(self.cancel_button)

        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.delete_button.clicked.connect(self.delete_item)

    def delete_item(self):
        item_number = self.item_number_input.text()

        response = delete(f"{ITEMS_URL}/{item_number}")
        if response.status_code == 200:
            QMessageBox.information(self, 'Success', 'Item deleted successfully.')
            self.close()
            self.parent().update_table()
        else:
            self.show_error_popup('Error', 'An error occurred while deleting the item.')

    def show_error_popup(self, title: str, message: str):
        QMessageBox.critical(self, title, message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

  