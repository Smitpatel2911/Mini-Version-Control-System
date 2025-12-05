import os
from config import SHARED_FILE
from data_structure import Stack
from exception import StackUnderFlowError

class BranchWorkspace: # Renamed to be more descriptive
    """
    Represents a single workspace and its independent file history.
    Each workspace has its own independent undo/redo history.
    """
    def __init__(self, name, initial_content=""): # Improved name
        self.name = name
        self.current_content = initial_content
        
        # LIFO Stack: Stores the history of edits for Undo
        self.history_stack = Stack() 
        self.history_stack.push(initial_content) # Base state is the first entry
        
        # LIFO Stack: Stores undone edits for Redo
        self.future_stack = Stack() 

class VersionControlSystem:
    """
    The central Manager for the entire VCS. It coordinates user sessions,
    branch workspaces, file I/O operations, and peer-to-peer announcements.
    """
    def __init__(self):
        self.official_repository_content = "" # Improved name for server file content
        self.connected_clients = []
        
        # Storage: { "branch_name": BranchWorkspaceObject }
        self.branch_registry = {} # Improved name
        
        # User Tracking: { "username": "current_branch_name" }
        self.user_sessions = {}
        
        self._load_from_disk() # Renamed to private helper method
        
        # Ensure the default 'master' branch is initialized
        if "master" not in self.branch_registry:
            self.branch_registry["master"] = BranchWorkspace("master", self.official_repository_content)

    # --- File I/O Operations ---
    def _load_from_disk(self):
        """Reads the official repository file from the disk."""
        if os.path.exists(SHARED_FILE):
            with open(SHARED_FILE, 'r') as f:
                self.official_repository_content = f.read()
        else:
            self.official_repository_content = ""

    def _save_to_disk(self): # Renamed to private helper method
        """Writes the current official memory state to the physical file."""
        try:
            with open(SHARED_FILE, 'w') as f:
                f.write(self.official_repository_content)
        except Exception as e:
            print(f"Error writing to disk: {e}")

    # --- User & Branch Management ---
    def register_user(self, username, connection_socket): # Improved name
        """Adds a new user and sets their initial branch to 'master'."""
        self.connected_clients.append(connection_socket)
        self.user_sessions[username] = "master"

    def get_active_branch(self, username):
        """Retrieves the BranchWorkspace object the user is currently checked out to."""
        branch_name = self.user_sessions.get(username, "master")
        return self.branch_registry.get(branch_name, self.branch_registry["master"]) # Safe retrieval

    def create_branch(self, username, new_branch_name):
        """Creates a new branch that is an exact copy of the user's current branch state."""
        if new_branch_name in self.branch_registry:
            return f"Error: Branch '{new_branch_name}' already exists."
        
        # Copy current state to the new branch
        current_branch = self.get_active_branch(username)
        self.branch_registry[new_branch_name] = BranchWorkspace(new_branch_name, current_branch.current_content)
        return f"Branch '{new_branch_name}' created successfully."

    def switch_branch(self, username, target_branch_name):
        """Checks out to a different branch, updating the user's session."""
        if target_branch_name not in self.branch_registry:
            return f"Error: Branch '{target_branch_name}' not found."
        
        self.user_sessions[username] = target_branch_name
        branch = self.branch_registry[target_branch_name]
        return f"Switched to branch '{target_branch_name}'. Content loaded."

    # --- The Core 3: Edit, Undo, Redo ---
    def edit(self, username, new_content):
        """Applies a new change to the active branch, saving the old state to history."""
        branch = self.get_active_branch(username)
        
        # 1. Update content
        branch.current_content = new_content
        # 2. Save new state to history stack
        branch.history_stack.push(new_content)
        # 3. Clear future stack (a new edit kills the ability to Redo prior undos)
        branch.future_stack.clear()
        
        return f"File updated on branch '{branch.name}'."

    def undo(self, username):
        """Reverts the current branch state to the previous recorded state."""
        branch = self.get_active_branch(username)
        try:
            # The current state is popped off the history stack...
            current_state = branch.history_stack.pop()
            
            # ...if the stack is now empty, we stop
            if branch.history_stack.is_empty():
                # Re-add the state we popped to prevent underflow
                branch.history_stack.push(current_state) 
                return "Nothing to undo (at base state of history)."
            
            # ...and the popped state is saved to the future stack for Redo
            branch.future_stack.push(current_state)
            
            # The new 'current' content is the state now on top of the history stack
            branch.current_content = branch.history_stack.peek()
            
            return "Undo successful."
        except StackUnderFlowError:
            return "Nothing to undo."

    def redo(self, username):
        """Re-applies the most recently undone state."""
        branch = self.get_active_branch(username)
        if branch.future_stack.is_empty():
            return "Nothing to redo."
        
        # 1. Take the state from the future stack...
        restored_state = branch.future_stack.pop()
        # 2. ...and put it back into the history stack
        branch.history_stack.push(restored_state)
        branch.current_content = restored_state
        return "Redo successful."

    def commit(self, username):
        """
        Promotes the user's current branch content to the official server repository,
        and saves it to the physical file.
        """
        # 1. Find the user's work
        branch = self.get_active_branch(username)
        
        # 2. Update the Server's Global State (The "Official" version)
        self.official_repository_content = branch.current_content
        
        # 3. Write to Hard Drive
        self._save_to_disk()
        
        # 4. Notify others
        msg = f"[COMMIT] User \'{username}\' has committed new changes from branch '{branch.name}'."
        self._broadcast_message(msg)
        
        return "Commit successful! Server repository updated."

    def merge(self, username, source_name):
        """
        Performs a simple merge (overwrite) of the source branch content 
        into the user's active branch.
        """
        target_branch = self.get_active_branch(username)
        
        if source_name not in self.branch_registry:
            return f"Error: Branch '{source_name}' not found."
            
        source_branch = self.branch_registry[source_name]
        
        # Check if merge is necessary
        if target_branch.current_content == source_branch.current_content:
            return f"Branch '{source_name}' is already up to date with '{target_branch.name}'."
        
        # 1. Update the content of the target branch (The Merge)
        new_content = source_branch.current_content
        target_branch.current_content = new_content
        
        # 2. Record the merge as a new state in history
        target_branch.history_stack.push(new_content)
        target_branch.future_stack.clear() 
        
        # 3. Announce the merge
        msg = f"[MERGE] User {username} merged branch '{source_name}' into '{target_branch.name}'."
        self._broadcast_message(msg)
        
        return f"Merge successful! '{source_name}' integrated into '{target_branch.name}'."

    def _broadcast_message(self, message):
        
        """
        FIX: Temporarily modifies the function to ONLY print to the server console 
        to prevent race conditions with the client's synchronous socket reads.
        """
        

        print(f"[SERVER BROADCAST DISABLED (Race Condition Fix)] {message}")
        for conn in self.connected_clients:
            try:
                conn.sendall(message.encode())
            except:
                pass


# Singleton Instance of the Version Control System
vcs = VersionControlSystem()