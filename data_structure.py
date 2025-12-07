from exception import StackUnderFlowError

class Stack:
    """
    A LIFO (Last-In-First-Out) Data Structure.
    Think of it like a stack of plates.
    """
    def __init__(self):
        self.items = []

    def push(self, item):
        """Add item to the top."""
        self.items.append(item)

    def pop(self):
        """Remove and return the top item."""
        if self.is_empty():
            raise StackUnderFlowError("Cannot pop: Stack is empty.")
        return self.items.pop()

    def peek(self):
        """Look at the top item without removing it."""
        if self.is_empty():
            return None
        return self.items[-1]

    def is_empty(self):
        return (len(self.items) == 0)

    def clear(self):
        """Remove all items."""
        self.items = []