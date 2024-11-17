from models.warehouse import Warehouse
from models.eventemmiter import EventEmitter
from models.storage import Storage

import random

random.seed(10)

ee = EventEmitter()
a = Warehouse((4, 4, 3), ee)

s1 = Storage((0, 0, 0))
s2 = Storage((0, 0, 1))

a.attach_storage(s1)
a.attach_storage(s2)

a.seed_objects(1)
a.seed_agents(2)

print(a.map[0])

while not a.is_sorted():
    a.step()

print(a.map[0])
