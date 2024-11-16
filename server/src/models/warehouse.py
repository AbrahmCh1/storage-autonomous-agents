import random

from enum import Enum
from typing import Any
from copy import copy

from models.storage import Storage
from models.eventemmiter import EventEmitter
from models.object import Object

class InsufficientStorage(Exception):
    pass

class InvalidHeight(Exception):
    pass

class SpaceState(Enum):
    FREE_SPACE = 1
    OUT_OF_BOUNDS = 2

class Warehouse():
    def __init__(self, dimensions: tuple[int, int, int], ee: EventEmitter):
        self.dimensions = dimensions
        x, y, z = dimensions
        self.capacity = 0
        self.ee = ee
        self.agents: list[Agent] = []
        self.step_n = 0

        # generate an empty map. may contain none, storage or object
        # to access a given floor map, use self.map[level]
        # to access a given position, use self.map[level][x][y]
        self.map: list[list[list[SpaceState | Storage | Object]]] = [[[SpaceState.FREE_SPACE for _ in range(y)] for _ in range(x)] for _ in range(z)]

        # generate a static map that will never be modified. This
        # is what is going to be handed out to the agents initially
        self.static_map: list[list[list[SpaceState | Storage | Object]]] = [[[SpaceState.FREE_SPACE for _ in range(y)] for _ in range(x)] for _ in range(z)]
        
        # emit an event to notify client of
        # warehouse being attached
        self.ee.send_event("warehouse_attached", {
            "warehouse_id": "some-id",
            "dimensions": { "x": x, "y": y, "z": z },
        })

    # Attaches a storage to it's specified location
    # and keeps capacity information up to date
    def attach_storage(self, s: Storage):
        x, y, z = s.location

        # if we are going to overwrite, subtract capacity
        if self.map[z][x][y] != SpaceState.FREE_SPACE:
            self.capacity -= self.map[z][x][y].capacity

        # add storage to the map and update capacity
        self.update_maps((x, y, z), s)
        self.capacity += s.capacity

        # emit an event to notify client of storage being
        # attached
        self.ee.send_event("storage_attached", {
            "storage_id": "some-id",
            "position": { "x": x, "y": y, "z": z },
        })

    # Method to seed a certain amount of objects
    # makes sure that there is enough capacity to
    # store given objects
    def seed_objects(self, object_count: int):
        # make sure we can actually fit all of the objects we
        # are seeding with our current capacity
        if object_count > self.capacity:
            raise InsufficientStorage(f"Make sure to attach more storage with attach_storage before seeding")

        # the sources to the images 
        object_srcs = ["src_1", "src_2", "src_3"]
        x, y, _ = self.dimensions

        # generate random positions for the objects in z = 0
        for _ in range(object_count):
            xrandom = random.choice(range(x))
            yrandom = random.choice(range(y))

            # keep trying combinations if some are busy
            while self.map[0][xrandom][yrandom] != SpaceState.FREE_SPACE:
                xrandom = random.choice(range(x))
                yrandom = random.choice(range(y))

            self.update_maps((xrandom, yrandom, 0), Object((xrandom, yrandom, 0), random.choice(object_srcs)))
            
            # emit an event to notify the client of a
            # random object being placed
            self.ee.send_event("object_attached", {
                "object_id": "some-id",
                "position": { "x": x, "y": y, "z": 0 },
            })

    def seed_agents(self, agent_count: int):
        x, y, _ = self.dimensions

        for i in range(agent_count):
            xrandom = random.choice(range(x))
            yrandom = random.choice(range(x))

            while self.map[0][xrandom][yrandom] != SpaceState.FREE_SPACE:
                xrandom = random.choice(range(x))
                yrandom = random.choice(range(x))

            agent = Agent(self, (xrandom, yrandom, 0), i)
            
            self.agents.append(agent)
            self.map[0][xrandom][yrandom] = agent

            # emit an event to notify the client of a
            # random object being placed
            self.ee.send_event("agent_attached", {
                "agent_id": i,
                "position": { "x": x, "y": y, "z": 0 },
            })

    def get_surroundings(self, position: tuple[int, int, int]):
        x, y, _ = position
        x_space, y_space, z_space = self.dimensions

        if z_space > len(self.map):
            raise InvalidHeight("Provided height was higher than map height")
        
        # each array represents the columns of things around the position
        # there can be instances of 'Object', 'Storage' a 0 representing a
        # wall/limit and a 1 representing empty floor
        left = [self.map[z][x - 1][y] for z in range(z_space)] if x - 1 > 0 and x - 1 < x_space else [SpaceState.OUT_OF_BOUNDS for _ in range(z_space)]
        right = [self.map[z][x + 1][y] for z in range(z_space)] if x + 1 > 0 and x + 1 < x_space else [SpaceState.OUT_OF_BOUNDS for _ in range(z_space)]
        front = [self.map[z][x][y + 1] for z in range(z_space)] if y + 1 > 0 and y + 1 < y_space else [SpaceState.OUT_OF_BOUNDS for _ in range(z_space)]
        back = [self.map[z][x][y - 1] for z in range(z_space)] if y - 1 > 0 and y - 1 < y_space else [SpaceState.OUT_OF_BOUNDS for _ in range(z_space)]

        return {
            "front": front,
            "back": back,
            "left": left,
            "right": right
        }
    
    # advance the warehouse simulation by one step
    def step(self):
        for agent in self.agents:
            surroundings = self.get_surroundings(agent.position)

            agent.perceive(surroundings) # perceive the relevant part of the map
            agent.plan() # decide what to do
            agent.step() # execute the last decision made

        # emit an event to notify the client of
        # a step being completed
        self.ee.send_event("step_completed", {
            "step_number": self.step_n
        })

        self.step_n += 1

    def update_maps(self, position: tuple[int, int, int], v: Any):
        x, y, z = position
        self.static_map[z][x][y] = v
        self.map[z][x][y] = v
        



class AgentState(Enum):
    STANDBY = 1
    MOVING_TO_OBJECT = 2
    CARRYING_OBJECT = 3

class AgentAction(Enum):
    MOVE_FORWARD = 1
    MOVE_BACKWARD = 2
    MOVE_LEFT = 3
    MOVE_RIGHT = 4
    ROTATE = 5
    WAIT = 6
    PICK_UP = 7
    STORE = 8
    CHANGE_STATE = 9

class Direction(Enum):
    FORWARD = 1
    RIGHT = 2
    BACKWARD = 3
    LEFT = 4

class Step():
    def __init__(self, action: AgentAction, params: dict[str, Any]):
        self.action = action
        self.params = params

class Agent():
    def __init__(self, warehouse: Warehouse, initial_position: tuple[int, int, int], n: int):
        self.map = copy(warehouse.static_map)
        self.initial_position = initial_position
        self.position = initial_position
        self.warehouse = warehouse
        self.state = AgentState.STANDBY
        self.planned_steps: list[Step] = []
        self.direction = Direction.FORWARD
        self.inventory: Object | None = None
        self.id = n

    # get the current perception at a given position, based on the 
    # current map the agent has
    def get_current_perception(self, position: tuple[int, int, int]):
        x, y, _ = position
        x_space, y_space, z_space = self.warehouse.dimensions

        if z_space > len(self.map):
            raise InvalidHeight("Provided height was higher than map height")
        
        # each array represents the columns of things around the position
        # there can be instances of 'Object', 'Storage' a 0 representing a
        # wall/limit and a 1 representing empty floor
        left = [self.map[z][x - 1][y] for z in range(z_space)] if x - 1 > 0 and x - 1 < x_space else [SpaceState.OUT_OF_BOUNDS for _ in range(z_space)]
        right = [self.map[z][x + 1][y] for z in range(z_space)] if x + 1 > 0 and x + 1 < x_space else [SpaceState.OUT_OF_BOUNDS for _ in range(z_space)]
        front = [self.map[z][x][y + 1] for z in range(z_space)] if y + 1 > 0 and y + 1 < y_space else [SpaceState.OUT_OF_BOUNDS for _ in range(z_space)]
        back = [self.map[z][x][y - 1] for z in range(z_space)] if y - 1 > 0 and y - 1 < y_space else [SpaceState.OUT_OF_BOUNDS for _ in range(z_space)]

        return {
            "front": front,
            "back": back,
            "left": left,
            "right": right
        }

    # given new sensor data, compare the sensor data with expected data,
    # and update the map to match sensor data
    def perceive(self, surroundings: dict[str, list[SpaceState | Storage | Object]]):
        prev_surroundings = self.get_current_perception(self.position)

        current_left, previous_left = surroundings["left"], prev_surroundings["left"]
        current_right, previous_right = surroundings["right"], prev_surroundings["right"]
        current_front, previous_front = surroundings["front"], prev_surroundings["front"]
        current_back, previous_back = surroundings["back"], prev_surroundings["back"]

        _, _, z_space = self.warehouse.dimensions
        x, y, _ = self.position

        if current_left != previous_left:
            # we need to fix our perception at the left!
            for z in range(z_space):
                if current_left[z] != previous_left[z]:
                    # there should be no way this is out of bounds
                    if current_left[z] == SpaceState.OUT_OF_BOUNDS:
                        raise Exception("Unexpected out of bounds")
                    
                    # now we are absolutely sure, we update the map to the left
                    self.map[z][x - 1][y] = current_left[z]


        if current_right != previous_right:
            # we need to fix our perception at the right!
            for z in range(z_space):
                if current_right[z] != previous_right[z]:
                    # there should be no way this is out of bounds
                    if current_right[z] == SpaceState.OUT_OF_BOUNDS:
                        raise Exception("Unexpected out of bounds")
                    
                    # now we are absolutely sure, we update the map to the right
                    self.map[z][x + 1][y] = current_right[z]

        if current_front != previous_front:
            # we need to fix our perception at the front!
            for z in range(z_space):
                if current_front[z] != previous_front[z]:
                    # there should be no way this is out of bounds
                    if current_front[z] == SpaceState.OUT_OF_BOUNDS:
                        raise Exception("Unexpected out of bounds")
                    
                    # now we are absolutely sure, we update the map to the front
                    self.map[z][x][y + 1] = current_front[z]

        if current_back != previous_back:
            # we need to fix our perception at the back!
            for z in range(z_space):
                if current_back[z] != previous_back[z]:
                    # there should be no way this is out of bounds
                    if current_back[z] == SpaceState.OUT_OF_BOUNDS:
                        raise Exception("Unexpected out of bounds")
                    
                    # now we are absolutely sure, we update the map to the back
                    self.map[z][x][y - 1] = current_back[z]

        # at this point, all perceptions are fixed, and
        # map is up to date

    def plan(self):
        # this will use the available information
        # to make a plan or decision on what to do
        # this will depend on the current state of the agent
        print("Agent is planning...")

        # if there are no planned steps
        if len(self.planned_steps) == 0:
            if self.state == AgentState.STANDBY:
                path, object = self.get_path_to_object()

                print("planning to go to object", object)
                print("path: ", path)

                initial_steps = [Step(AgentAction.CHANGE_STATE, { "new_state": AgentState.MOVING_TO_OBJECT })]
                movement_steps = self.path_to_movement(path)
                pickup_steps = [
                    Step(AgentAction.PICK_UP, { "object": object }), # pick up the object
                    Step(AgentAction.CHANGE_STATE, { "new_state": AgentState.CARRYING_OBJECT }) # change agent state to carrying object
                ]
                
                # set plan to be the combination of these steps
                # 1. change state to move to object
                # 2. move to object
                # 3. pickup object and set state to MOVING_OBJECT
                self.planned_steps = initial_steps + movement_steps + pickup_steps
            
            if self.state == AgentState.MOVING_TO_OBJECT:
                raise Exception("Invalid state. Agent should have at least one step if on this state")

            if self.state == AgentState.CARRYING_OBJECT:
                # check if path must be modified
                if self.inventory is None:
                    raise Exception("Invalid state. Agent should have an object in the inventory if on this state")

                path, storage = self.get_path_to_storage(self.inventory)
                movement_steps = self.path_to_movement(path)
                store_steps = [
                    Step(AgentAction.STORE, { "storage": storage }),
                    Step(AgentAction.CHANGE_STATE, { "new_state": AgentState.STANDBY })
                ]

                # set the plan to be the combination of these steps
                # 1. Move to selected storage
                # 2. Store object and set new state to standby
                self.planned_steps = movement_steps + store_steps

            return # we have created an initial plan
    
        # this means there are planned steps, so we need to evaluate the next one
        # and make sure it is still possible
        next_step = self.planned_steps[0]
        
        if next_step.action == AgentAction.MOVE_RIGHT:
            feasible, reason = self.is_move_feasible(Direction.RIGHT)
            if feasible: return

        if next_step.action == AgentAction.MOVE_LEFT:
            feasible, reason = self.is_move_feasible(Direction.LEFT)
            if feasible: return
        
        if next_step.action == AgentAction.MOVE_FORWARD:
            feasible, reason = self.is_move_feasible(Direction.FORWARD)
            if feasible: return
        
        if next_step.action == AgentAction.MOVE_BACKWARD:
            feasible, reason = self.is_move_feasible(Direction.BACKWARD)
            if feasible: return
        
        if next_step.action == AgentAction.PICK_UP:
            _, reason = self.is_move_feasible(Direction.FORWARD)
            if reason == next_step.params["object"]: return
        
        if next_step.action == AgentAction.STORE:
            target_storage: Storage = next_step.params["storage"]
            _, reason = self.is_move_feasible(Direction.FORWARD, target_storage.location[2])
            if target_storage == reason and not target_storage.is_full(): return

        if next_step.action == AgentAction.ROTATE:
            return # rotate is always possible
        
        if next_step.action == AgentAction.WAIT:
            return # wait is always possible

        if next_step.action == AgentAction.CHANGE_STATE:
            return # change state is always possible

    def step(self):
        # this will execute the action at the top
        # of the agent's plan
        print("CURRENT PLAN")

        for i, step in enumerate(self.planned_steps):
            print(f"s{i + 1}: {step.action.name} - {step.params}")

    ## From here on out, all of these methods might be 
    ## specific to the actions that can be executed in step
    
    # function that finds a path to an object
    def get_path_to_object(self) -> tuple[list[tuple[int, int, int]], Object]:
        queue = []
        visited = set()
        
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up

        initial_x, initial_y, _ = self.position
        initial_position = (initial_x, initial_y)

        queue.append(initial_position)
        visited.add(initial_position)

        floor_map = self.map[0]
        n, m, _ = self.warehouse.dimensions
        parents = {}

        def reconstruct_path(end: tuple[int, int]):
            path: list[tuple[int, int, int]] = []
            start = initial_position
            current = end
            while current != start:
                path.append((current[0], current[1], 0))
                current = parents[current]

            path.append((start[0], start[1], 0))  # Add the start position
            path.reverse()  # Reverse the path to go from start to end
            return path

        while queue:
            x, y = queue.pop(0)

            if isinstance(floor_map[x][y], Object):
                path = reconstruct_path((x, y))
                return path, floor_map[x][y]

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < n and 0 <= ny < m and (nx, ny) not in visited:
                    # if floor_map[nx][ny] == SpaceState.FREE_SPACE:
                    queue.append((nx, ny))
                    visited.add((nx, ny))
                    parents[(nx, ny)] = (x, y)

        raise Exception("Path not found")

    def path_to_movement(self, path: list[tuple[int, int, int]]) -> list[Step]:
        current_rotation = 0
        steps: list[Step] = []

        def calculate_rotation(dir: Direction):
            rotations = {
                Direction.FORWARD: 0,
                Direction.RIGHT: 90,
                Direction.BACKWARD: 180,
                Direction.LEFT: 270, 
            }

            # TODO: Consider if (n + 720) % 360 trick is needed
            return rotations[dir] - current_rotation

        for i in range(len(path) - 1):
            a1, a2, _ = path[i + 1]
            b1, b2, _ = path[i]

            direction_delta = a1 - b1, a2 - b2

            delta_to_direction = {
                (1, 0): Direction.RIGHT,
                (-1, 0): Direction.LEFT,
                (0, 1): Direction.FORWARD,
                (0, -1): Direction.BACKWARD
            }

            if not direction_delta in delta_to_direction:
                raise Exception("Unexpected error while handling step generation")
            
            direction = delta_to_direction[direction_delta]
            rotation = calculate_rotation(direction)

            current_rotation = rotation

            if rotation != 0:
                steps.append(Step(AgentAction.ROTATE, { "degrees": rotation }))

            if i + 1 != len(path) - 1: # last iteration must not move forward
                steps.append(Step(AgentAction.MOVE_FORWARD, None))

        return steps


    # function that finds a path to the place to store that object
    def get_path_to_storage(self, object: Object) -> tuple[list[tuple[int, int, int]], Storage]:
        pass

    def is_move_feasible(self, move: Direction, z = 0):
        x, y, _ = self.position
        x_space, y_space, _ = self.warehouse.dimensions

        map = self.map[z]

        dx = 1 if move == Direction.RIGHT else -1 if move == Direction.LEFT else 0
        dy = 1 if move == Direction.FORWARD else -1 if move == Direction.BACKWARD else 0

        new_x, new_y = x + dx, y + dy

        if new_x > 0 and new_x < x_space and new_y > 0 and new_y < y_space:
            return map[new_x][new_y] == SpaceState.FREE_SPACE, map[new_x][new_y]

        return False, SpaceState.OUT_OF_BOUNDS
    