class StackError(Exception):
    """Base class for stack errors."""
    pass

class StackUnderFlowError(StackError):
    """Raised when trying to pop from an empty stack."""
    pass

class BranchError(Exception):
    """Raised when a branch operation fails (e.g., branch not found)."""
    pass