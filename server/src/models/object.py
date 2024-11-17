import uuid

class Object():
    def __init__(self, location: tuple[int, int, int], image_src: str):
        self.id = str(uuid.uuid4())
        self.location = location
        self.image_src = image_src
