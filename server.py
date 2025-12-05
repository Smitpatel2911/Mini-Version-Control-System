from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread, active_count
from config import SRVR_HOST, PORT, BUFFER_SIZE
from protocol import process_client_request # Renamed
from vcs_core import vcs

# add: safe broadcast helper
def broadcast_to_all(message, exclude=None):
    """Best-effort broadcast to all registered client sockets."""
    for client_sock in list(getattr(vcs, "connected_clients", [])):
        if exclude is not None and client_sock is exclude:
            continue
        try:
            client_sock.sendall(message.encode())
        except Exception:
            # remove dead sockets quietly
            try:
                vcs.connected_clients.remove(client_sock)
                client_sock.close()
            except Exception:
                pass

def handle_client_connection(client_socket, client_address): # Improved names
    """
    Runs in a dedicated thread for each connected client. Manages the 
    handshake, main communication loop, and connection cleanup.
    
    Args:
        client_socket (socket.socket): The socket connection to the client.
        client_address (tuple): The IP address and port of the client.
    """
    print(f"[NEW CONNECTION] {client_address} connected.")
    username = "Unknown"
    
    try:
        # 1. Handshake: Receive the Username
        username_data = client_socket.recv(BUFFER_SIZE).decode().strip()
        username = username_data if username_data else "Guest"
        
        # Register user with the Core VCS Manager
        vcs.register_user(username, client_socket)
        
        # Send a welcome message with current branch info
        welcome_msg = f"Welcome {username}! You are currently on branch 'master'. Type HELP for commands."
        client_socket.sendall(welcome_msg.encode())

        # 2. Main Communication Loop
        while True:
            # Wait for a command from the client
            client_command = client_socket.recv(BUFFER_SIZE).decode()
            
            if not client_command:
                # Client disconnected gracefully (sent empty data)
                break
            
            print(f"[{username}] Command received: {client_command.splitlines()[0]}...")
            
            # Detect COMMIT and handle it safely so server doesn't go down
            if client_command.strip().upper().startswith("COMMIT"):
                # protect against protocol code that might raise SystemExit or other fatal signals
                try:
                    response = process_client_request(username, client_command)
                except SystemExit as se:
                    # prevent process exit; report and continue
                    response = f"[ERROR] Commit handler attempted to exit: {se}"
                    print(response)
                except KeyboardInterrupt as ki:
                    response = "[ERROR] Commit handler interrupted."
                    print(response)
                except Exception as e:
                    response = f"[ERROR] Commit failed: {e}"
                    print(response)
                
                # send response to the client that issued the commit
                try:
                    client_socket.sendall(response.encode())
                except Exception:
                    pass

                # broadcast commit notice to everyone (best-effort)
                commit_notice = f"[BROADCAST] {username} performed COMMIT: {client_command.strip()[6:].strip() or 'no message'}"
                broadcast_to_all(commit_notice, exclude=None)
                # continue processing further commands
                continue

            # Non-commit normal processing (also protected)
            try:
                response = process_client_request(username, client_command)
            except Exception as e:
                response = f"[ERROR] Command processing failed: {e}"
                print(f"[ERROR] while handling command from {username}: {e}")
            
            # Send the response back to the client
            try:
                client_socket.sendall(response.encode())
            except Exception:
                # If sending fails, close connection loop gracefully
                break

    except Exception as e:
        print(f"[ERROR] Connection with {username} ({client_address}) failed: {e}")
        
    finally:
        # 3. Connection Cleanup
        print(f"[DISCONNECT] {username} has left.")
        if client_socket in getattr(vcs, "connected_clients", []):
            try:
                vcs.connected_clients.remove(client_socket)
            except Exception:
                pass
        try:
            client_socket.close()
        except Exception:
            pass

def start_vcs_server(): # Improved name
    """
    The main entry point for the VCS Server. Initializes the socket and 
    listens for incoming client connections indefinitely.
    """
    server_socket = socket(AF_INET, SOCK_STREAM)
    
    # Enables quick restart by releasing the port immediately
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((SRVR_HOST, PORT))
        server_socket.listen(5) # Max 5 queued connections
        print(f"--- 🚀 Distributed VCS Server Running on {SRVR_HOST}:{PORT} ---")
        print("Waiting for client connections...")
        
        while True:
            try:
                # Blocking call: waits for a new client to connect
                client_conn, client_addr = server_socket.accept()
                
                # Hand off the connection to a new dedicated thread
                thread = Thread(target=handle_client_connection, 
                                args=(client_conn, client_addr), 
                                daemon=True)
                thread.start()
                print(f"[ACTIVE CONNECTIONS] {active_count() - 1}")
            except Exception as e:
                # log and continue accepting new connections
                print(f"[ERROR] Accept/dispatch error: {e}")
                continue
            
    except Exception as e:
        print(f"[FATAL ERROR] Server failed to start: {e}")
        
start_vcs_server()