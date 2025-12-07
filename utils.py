from tkinter import Tk, Label, Canvas
from tkinter.scrolledtext import ScrolledText 

def display_server_content(content):
    """
    Creates and displays a new Tkinter window with the current server repository content.
    Uses ScrolledText for a better display experience, especially for large content.
    
    Args:
        content (str): The content of the server repository file.
    """
    # Create the main window
    vcs_window = Tk()
    vcs_window.title("VCS Repository Content")

    # Title label
    Label(vcs_window, text="Official Server Content", font=("Arial", 15, "bold")).pack(pady=10)
    
    # Separator
    canva = Canvas(vcs_window, width=400, height=20)
    canva.create_line(10, 10, 390, 10, fill="Black")
    canva.pack()
    
    # Content display using ScrolledText
    text_area = ScrolledText(
        master=vcs_window,
        wrap='word', # Wrap lines at word boundaries
        width=60,    # Width in characters
        height=20,   # Height in lines
        font=("Courier", 11),
        borderwidth=3,
        relief="sunken"
    )
    text_area.insert('1.0', content) # Insert content at the beginning
    text_area.config(state='disabled') # Make it read-only
    text_area.pack(padx=20, pady=10)

    vcs_window.mainloop()