# Distributed Version Control System (DVCS) in Python

A custom, socket-based Version Control System that implements core VCS features such as branching, merging, commits, and history navigation (Undo/Redo) using a Client-Server architecture.

## 📂 Project Structure

- **`server.py`**: The multi-threaded server that manages client connections and the central repository.
- **`client.py`**: The client application that handles user input and communicates with the server.
- **`main.py`**: The entry point to launch the client application.
- **`vcs_core.py`**: The core logic engine. It handles branch management, the singleton pattern, and file I/O operations.
- **`data_structure.py`**: Custom Stack implementation used for Undo/Redo history.
- **`protocol.py`**: Routes string-based commands from the client to specific VCS functions.
- **`config.py`**: Contains global configuration for IP addresses, ports, and buffer sizes.
- **`utils.py`**: Contains GUI utilities (Tkinter) for displaying the official server content.

## 🚀 Getting Started

### Prerequisites
- Python 3.x
- Tkinter (Usually included with Python; required for the `SHOW` command).

### Configuration
Before running, check `config.py`:
1. Ensure `SRVR_HOST` is set to `'0.0.0.0'` to allow connections.
2. Set `PORT` to your desired port (default: `5050`).

### Installation & Run

**Step 1: Start the Server**
Run the server script to start listening. The server persists the official repository to `server_repo.txt`.

```bash
python server.py
```

### Step 2: Start the Client
Open a new terminal (or multiple terminals for multiple users) and run the main entry point.

```bash
python main.py
```

## 🎮 Usage & Commands

Once connected, you will be prompted to enter a username. You are automatically assigned to the `master` branch.



[Image of version control system branching and merging workflow]


| Command | Description |
| :--- | :--- |
| **`EDIT`** | Triggers a multi-line input mode to modify the file content of your current branch. Type `--END` to finish editing. |
| **`UNDO`** | Reverts the last change in your current branch (Stack-based history). |
| **`REDO`** | Re-applies a change that was previously undone. |
| **`BRANCH:[name]`** | Creates a new branch copying the state of your current branch. |
| **`CHECKOUT:[name]`** | Switches your active workspace to the specified branch. |
| **`MERGE:[name]`** | Merges the content of `[name]` into your current branch. |
| **`COMMIT`** | Pushes your current branch's content to the official server repository. |
| **`PEEK`** | Displays the current local draft of your active branch. |
| **`SHOW`** | Opens a graphical window (GUI) showing the official server repository content. |
| **`EXIT`** | Disconnects from the server and closes the client. |

## 🧠 Architecture Highlights



- **Concurrency**
  The server uses `threading.Thread` to handle multiple clients simultaneously without blocking.

- **Data Structures**
  A custom **LIFO (Last-In, First-Out) Stack** is used to manage edit history, enabling granular Undo/Redo capabilities within every branch.

- **Persistence**
  The `server_repo.txt` file acts as the hard-disk storage for the committed repository state, ensuring data is saved between restarts.

- **Robustness**
  The server includes exception handling to prevent a single client's bad request (e.g., a malformed commit) from crashing the entire system.
