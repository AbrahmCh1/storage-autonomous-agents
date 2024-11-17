from models.warehouse import Warehouse
from models.eventemmiter import EventEmitter
from models.storage import Storage

import random

random.seed(5)

ee = EventEmitter()
a = Warehouse((4, 6, 3), ee)

s1 = Storage((0, 0, 0))
s2 = Storage((0, 0, 1))
s3 = Storage((0, 0, 2))
s4 = Storage((1, 0, 0))

a.attach_storage(s1)
a.attach_storage(s2)
a.attach_storage(s3)
a.attach_storage(s4)

a.seed_objects(8)

print(a.map[0])

while not a.is_sorted():
    a.step()

print(a.map[0])

ee.close()
