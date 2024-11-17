from models.object import Object
import uuid

class PositionFilled(Exception):
    pass

class PositionNonExistent(Exception):
    pass

class StorageFull(Exception):
    pass

class Storage():
    def __init__(self, location: tuple[int, int, int], capacity: int = 5):
        self.location = location
        self.capacity = capacity
        self.count = 0
        self.position_map: list[Object | None] = [None] * capacity
        self.id = str(uuid.uuid4())

    def check_position(self, n: int):
        if n < len(self.position_map):
            return self.position_map[n]
        else:
            raise PositionNonExistent()
    
    def store_position(self, n: int, o: Object):
        curr = self.check_position(n)

        if curr is None:
            self.position_map[n] = o
            self.count += 1
        else:
            raise PositionFilled()
        
    def store(self, o: Object):
        if self.is_full():
            raise StorageFull()
        
        for i in range(len(self.position_map)):
            if self.position_map[i] is None:
                self.position_map[i] = o
                self.count += 1
                break

    def is_full(self):
        return self.count == self.capacity
