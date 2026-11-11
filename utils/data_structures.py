class Stack:
    def __init__(self):
        self.__items = []
        self.__size = 0
        
    def __len__(self):
        return self.__size
    
    def __str__(self):
        return str(self.__items)
    
    def __repr__(self):
        return f"Stack({self.__items})"
    
    def __contains__(self, item):
        return item in self.__items

    def push(self, item):
        self.__items.append(item)
        self.__size += 1

    def pop(self):
        if not self.is_empty():
            self.__size -= 1
            return self.__items.pop()
        raise IndexError("pop from empty stack")

    def peek(self):
        if not self.is_empty():
            return self.__items[-1]
        raise IndexError("peek from empty stack")

    def is_empty(self):
        return self.__size == 0
    
    def to_list(self):
        return self.__items.copy()

    @property
    def size(self):
        return self.__size
    
class Queue:
    def __init__(self):
        self.__items = []
        self.__size = 0
        
    def __len__(self):
        return self.__size
    
    def __str__(self):
        return str(self.__items)
    
    def __repr__(self):
        return f"Queue({self.__items})"
    
    def __contains__(self, item):
        return item in self.__items

    def push(self, item):
        self.__items.append(item)
        self.__size += 1

    def pop(self):
        if not self.is_empty():
            self.__size -= 1
            return self.__items.pop(0)
        raise IndexError("dequeue from empty queue")

    def peek(self):
        if not self.is_empty():
            return self.__items[0]
        raise IndexError("peek from empty queue")

    def is_empty(self):
        return self.__size == 0
    
    def to_list(self):
        return self.__items.copy()
    
    def set_from_list(self, items:list):
        self.__items = items[:]
        self.__size = len(items)

    @property
    def size(self):
        return self.__size
    
class PriorityQueue:
    def __init__(self, sorting_function:callable):
        self.__items = []
        self.__size = 0
        self.__sorting_function = sorting_function
        
    def __len__(self):
        return self.__size
    
    def __str__(self):
        return str(self.__items)
    
    def __repr__(self):
        return f"PriorityQueue({self.__items})"
    
    def __contains__(self, item):
        return item in self.__items

    def push(self, item):
        self.__items.append(item)
        self.__size += 1
        self.__items.sort(key=self.__sorting_function)

    def pop(self):
        if not self.is_empty():
            self.__size -= 1
            return self.__items.pop(0)
        raise IndexError("pop from empty priority queue")

    def peek(self):
        if not self.is_empty():
            return self.__items[0]
        raise IndexError("peek from empty priority queue")

    def is_empty(self):
        return self.__size == 0
    
    def to_list(self):
        return self.__items.copy()

    @property
    def size(self):
        return self.__size