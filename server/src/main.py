from models.warehouse import Warehouse
from models.eventemmiter import EventEmitter
from models.storage import Storage

ee = EventEmitter()
a = Warehouse((6, 5, 3), ee)

s1 = Storage((0, 0, 0))
s2 = Storage((0, 0, 1))

a.attach_storage(s1)
a.attach_storage(s2)

a.seed_objects(3)
a.seed_agents(2)

print(a.map[0])

a.step()

