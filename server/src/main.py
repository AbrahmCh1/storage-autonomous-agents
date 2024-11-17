from models.warehouse import Warehouse
from models.eventemmiter import EventEmitter
from models.storage import Storage

import random

random.seed(5)

ee = EventEmitter()
a = Warehouse((4, 6, 3), ee)

storages = [
    Storage((1, 1, 0)),
    Storage((2, 1, 0)),
]

for storage in storages:
    a.attach_storage(storage)

a.seed_objects(3)
a.seed_agents(2)

print(a.map[0])

while not a.is_sorted():
    a.step()

print(a.map[0])

ee.close()
