from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from config import HOST, PORT, BUFFER_SIZE
from utils import display_server_content
from vcs_core import vcs





# The asynchronous listener is removed to fix the race condition and hang.
# All socket reads now happen synchronously in the main loop.

def start_client():
    """
    Main function to initialize the client application and handle user input.
    """
    try:
        # Establish TCP/IP connection
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("❌ Error: Could not connect to server. Please ensure the server is running.")
        return
    
    # 1. Authentication Handshake
    username = input("Enter your Username: ").strip()
    sock.sendall(username.encode())


    # 2. Receive initial welcome message and display commands
    try:
        # Receive initial welcome message (blocking call)
        welcome_msg = sock.recv(BUFFER_SIZE).decode()
        print("\n" + "=" * 60)
        print(welcome_msg)
        print("\n--- AVAILABLE COMMANDS ---")
        print("  EDIT -> Modify your current branch's file content.")
        print("  UNDO -> Revert the last change in your current branch.")
        print("  REDO -> Re-apply an undone change.")
        print("  BRANCH:[name] -> Create a new branch from current state.")
        print("  CHECKOUT:[name] -> Switch your active branch.")
        print("  MERGE:[name] -> Merge a named branch into your current branch.")
        print("  COMMIT -> Save your branch content as the official server file.")
        print("  PEEK -> View your current branch's draft content.")
        print("  SHOW -> View the current official server file content (opens new window).")
        print("  EXIT -> Disconnect and quit.")
        print("=" * 60)
    except Exception:
        print("Server disconnected during initial connection.")
        return
    
    
        

    # (Synchronous Request-Response)
    while True:
        
        try:
            print("Command > ", end="", flush=True)
            cmd = input().strip()
            
            if cmd.upper() == 'EXIT':
                break
            
            if not cmd:

                #########################
                sock.settimeout(0.1)
                try:
                    incoming = sock.recv(BUFFER_SIZE).decode()
                    if incoming:
                        print(f"\n{incoming}")
                except:
                    pass
                finally:
                    sock.settimeout(None)
                ###################
                continue


                    
            # Special handling for EDIT: prompt user for multi-line content
            if cmd.upper() == 'EDIT':
                print("--- Enter New File Content (Type '--END' on a new line when done) ---")
                content_lines = []
                while True:
                    line = input()
                    if line.upper() == '--END':
                        break
                    content_lines.append(line)
                
                # Format the command for the server: EDIT:full_content
                full_content = "\n".join(content_lines)
                command_to_send = f"EDIT:{full_content}"
                
            else:
                command_to_send = cmd

            # Send the command to the server
            sock.sendall(command_to_send.encode())
            
            # Receive and Process Server Response (Blocking) 
            response = sock.recv(BUFFER_SIZE).decode()
            
            if not response:
                # Server disconnected
                print("\nServer has shut down.")
                break

            # Check for the SHOW command prefix
            if response.startswith("SHOW_CONTENT:"):
                # Extract content by removing the prefix
                content = response[14:].strip() 
                
                # Run the blocking GUI in a NEW THREAD so the main loop can continue
                gui_thread = Thread(target=display_server_content, args=(content,), daemon=True)
                gui_thread.start()
                
                print("✅ SHOW command successful! The official content is displayed in a new window.")
                
            else:
                # Handle all other command responses (EDIT, COMMIT, UNDO, etc.)
                print("\n" + "-" * 30)
                print(response)
                print("-" * 30)
                
        except KeyboardInterrupt:
            print("\nInterrupt detected.")
            break
        except Exception as e:
            print(f"A communication error occurred: {e}")
            break
            
    
    sock.close()
    print("\nDisconnected from VCS Server.")