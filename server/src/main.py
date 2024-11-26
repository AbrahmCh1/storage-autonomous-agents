from models.warehouse import Warehouse
from models.eventemmiter import EventEmitter, MockEmitter
from models.storage import Storage

from handlers.camera_handler import CameraHandler


import base64
import os
from datetime import datetime
import time
import random

random.seed(10)

DELTA_TIME = 0

ee = EventEmitter()
ch = CameraHandler()

a = Warehouse((12, 8, 3), ee)

storages = [
    Storage((2, 5, 0)),
    Storage((2, 5, 1)),
    Storage((3, 5, 0)),
    Storage((3, 5, 1)),
    Storage((4, 5, 0)),
    Storage((4, 5, 1)),
    Storage((7, 2, 0)),
    Storage((7, 2, 1)),
    Storage((8, 2, 0)),
    Storage((8, 2, 1)),
    Storage((9, 2, 0)),
    Storage((9, 2, 1)),
]

for storage in storages:
    a.attach_storage(storage)

a.seed_objects(5)
a.seed_agents(2)

print(a.map[0])

while not a.is_sorted():
    time.sleep(DELTA_TIME)
    a.step()
    ee.register_handler("camera_capture", ch.handle_camera_capture)



print(a.map[0])

a.create_stats_graph()

ee.close()
