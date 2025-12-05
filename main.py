from client import start_client

if __name__ == "__main__":
    print("Initializing Distributed Version Control System...")
    print("------------------------------------------------")

    # Start the Client
    # We run this in the main thread so it can accept keyboard input.
    start_client()