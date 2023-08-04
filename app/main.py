from fastapi import FastAPI
from routers import router
from models import Inventory
from database import engine

from ui import MainWindow
import sys
from PyQt5.QtWidgets import QApplication
from multiprocessing import Process, Event  


app = FastAPI()

# Add the router to the app
app.include_router(router)

# Create the database tables (if needed)
Inventory.metadata.create_all(bind=engine)

def run_fastapi(stop_event):
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True, lifespan="on")
    stop_event.set()


def run_ui(stop_event):
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.destroyed.connect(stop_event.set)
    sys.exit(app.exec_())


if __name__ == '__main__':
    stop_event = Event()

    fastapi_process = Process(target=run_fastapi, args=(stop_event,))
    fastapi_process.start()

    ui_process = Process(target=run_ui, args=(stop_event,))
    ui_process.start()

    stop_event.wait()  # Wait for either the UI or FastAPI to be closed
    fastapi_process.terminate()
    ui_process.terminate()