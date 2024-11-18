from models.warehouse import Warehouse
from models.eventemmiter import EventEmitter, MockEmitter
from models.storage import Storage

import time
import random

random.seed(10)

DELTA_TIME = 1

ee = EventEmitter()
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

a.seed_objects(18)
a.seed_agents(5)

print(a.map[0])

while not a.is_sorted():
    time.sleep(DELTA_TIME)
    a.step()

print(a.map[0])

ee.close()
