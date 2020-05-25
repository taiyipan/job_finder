import json
# recursively obtain web element by going through methods available to the object passed in
# use method order associated with the class, and remember new orders if any occurs
class AdaptiveRecursor:
    # constructor takes in the object to be processed
    def __init__(self, object):
        self.object = object
        self.memory_path = '/home/taiyi/job_finder/memory/memory.json'
        self.memory = self.remember()
        self.new_order = list()

    # execute a generic method from the object to get something
    def get(self):
        return self.recurse(self.order(), 0)

    # read memory json into python dictionary
    def remember(self) -> dict:
        try:
            with open(self.memory_path, 'r') as file:
                memory = json.load(file)
        except:
            print('\nMemory file could not be found')
        return memory

    # extract method order from dictionary
    def order(self) -> list:
        return self.memory[type(self.object).__name__]

    # update memory file
    def memorize(self, order: list):
        # merge new_order list and leftover order list
        self.create_new_order(order)
        # update memory dictionary
        self.memory[type(self.object).__name__] = self.new_order
        # write memory dictionary to memory json file
        with open(self.memory_path, 'w') as file:
            json.dump(self.memory, file, indent = 4)
        print('Memory updated: {}'.format(type(self.object).__name__))

    # merge new_order list and leftover order list
    # most recently working method number comes first
    def create_new_order(self, order: list):
        # get most recently working method number
        num = self.new_order.pop()
        # insert num into placeholder list as first element
        self.new_order.insert(0, num)
        # add leftover order list to placeholder list
        if order:
            self.new_order.extend(order)

    # verify if object method exists
    def verify_method(self, method_name: str):
        return hasattr(self.object, method_name) and callable(getattr(self.object, method_name))

    # recursively determine the working method and remember it
    def recurse(self, order: list, max_i: int):
        # if order is not empty, pop first, update max
        if order:
            i = order.pop(0)
            max_i = max(max_i, i)
        # if order is empty, see if more methods exist
        # if not, return None
        else:
            if self.verify_method('method_{}'.format(max_i + 1)):
                max_i += 1
                i = max_i
            else:
                return None
        # add method number to new_order
        self.new_order.append(i)
        # attempt to obtain web element with object method
        try:
            element = eval('self.object.method_{}()'.format(i))
            # if an element other than the 1st element in order list is working,
            # memorize this new order
            if len(self.new_order) > 1:
                self.memorize(order)
            # stop condition, return element
            return element
        # if attempt fails, recurse
        except:
            print('{}: Method_{} failed, recurse'.format(type(self.object).__name__, i))
            # recursive functional call
            return self.recurse(order, max_i)
