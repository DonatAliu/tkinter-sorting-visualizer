from tkinter import *
from tkinter import ttk
import random
import threading
from bubbleSort import bubble_sort

root = Tk()
root.title("Sorting Algorithms Visualization")
root.maxsize(900, 600)
root.config(bg="#021526")

selected_alg = StringVar()
data = []
stop_signal = threading.Event()
current_thread = None

def drawData(data, colorArray):
    """Draw the data on the canvas."""
    if not stop_signal.is_set() and root.winfo_exists():  # Ensure the window exists before drawing
        canvas.delete("all")
        c_height = canvas.winfo_height()  # Dynamic height based on canvas size
        c_width = canvas.winfo_width()  # Dynamic width based on canvas size
        x_width = c_width / (len(data) + 1)
        offset = 20
        spacing = 5
        normalizedData = [i / max(data) for i in data]
        for i, height in enumerate(normalizedData):
            x0 = i * x_width + offset + spacing
            y0 = c_height - height * (c_height - 40)
            x1 = (i + 1) * x_width + offset
            y1 = c_height
            canvas.create_rectangle(x0, y0, x1, y1, fill=colorArray[i])
            canvas.create_text(x0 + 2, y0, anchor=SW, text=str(data[i]))
        root.update_idletasks()

def generate():
    """Generate random data for sorting."""
    global data, current_thread, stop_signal
    if current_thread and current_thread.is_alive():
        stop_signal.set()  # Set the stop signal to stop the sorting thread
        current_thread.join()  # Wait for the thread to stop
        stop_signal.clear()  # Clear the stop signal for the new operation

    minVal = int(minEntry.get())
    maxVal = int(maxEntry.get())
    size = int(sizeEntry.get())
    data = [random.randrange(minVal, maxVal + 1) for _ in range(size)]
    drawData(data, ['#FF204E' for _ in range(len(data))])
    startButton.config(state="normal")  # Enable the Start button


def startAlgorithm():
    """Start the selected sorting algorithm in a new thread."""
    startButton.config(state="disabled")  # Enable the Start button
    global data, current_thread, stop_signal
    if current_thread and current_thread.is_alive():
        stop_signal.set()  # Set the stop signal to stop the sorting thread
        current_thread.join()  # Wait for the thread to stop
        stop_signal.clear()  # Clear the stop signal for the new operation

    if algorithMenu.get() == "Bubble Sort":
        stop_signal = threading.Event()  # Create a new stop signal
        current_thread = threading.Thread(target=bubble_sort, args=(data, drawData, speedScale.get(), stop_signal))
        current_thread.start()

def on_closing():
    """Handle closing of the window."""
    global current_thread, stop_signal
    if current_thread and current_thread.is_alive():
        stop_signal.set()  # Signal the thread to stop
        current_thread.join()  # Wait for the thread to stop
    root.destroy()  # Destroy the main window

root.protocol("WM_DELETE_WINDOW", on_closing)

# Frame and UI setup
UI_frame = Frame(root, bg='#6EACDA')
UI_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

canvas = Canvas(root, bg="#03346E")
canvas.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

# User Interface
Label(UI_frame, text="Algorithm:", bg="#6EACDA").grid(row=0, column=0, padx=5, pady=5, sticky=W)
algorithMenu = ttk.Combobox(UI_frame, textvariable=selected_alg, values=["Bubble Sort"])
algorithMenu.grid(row=0, column=1, padx=5, pady=5)
algorithMenu.current(0)

speedScale = Scale(UI_frame, from_=0.1, to=2.0, length=200, digits=2, resolution=0.2, orient=HORIZONTAL, label="Select speed")
speedScale.grid(row=0, column=2, padx=5, pady=5)
#startButton=Button(UI_frame, text="Start", command=startAlgorithm, bg="#508C9B").grid(row=0, column=3, padx=5, pady=5)
startButton = Button(UI_frame, text="Start", command=startAlgorithm, bg="#508C9B")
startButton.grid(row=0, column=3, padx=5, pady=5)
sizeEntry = Scale(UI_frame, from_=3, to=25, resolution=1, orient=HORIZONTAL, label="Select size")
sizeEntry.grid(row=1, column=0, padx=5, pady=5)
sizeEntry.set(15)

minEntry = Scale(UI_frame, from_=0, to=10, resolution=1, orient=HORIZONTAL, label="Min value")
minEntry.grid(row=1, column=1, padx=5, pady=5)

maxEntry = Scale(UI_frame, from_=10, to=100, resolution=1, orient=HORIZONTAL, label="Max value")
maxEntry.grid(row=1, column=2, padx=5, pady=5)
maxEntry.set(100)
Button(UI_frame, text="Generate", command=generate, bg="white").grid(row=1, column=3, padx=5, pady=5)

# Make the UI responsive
root.grid_rowconfigure(1, weight=1)  # Make row 1 (canvas) expandable
root.grid_columnconfigure(0, weight=1)  # Make column 0 (main content) expandable
UI_frame.grid_rowconfigure(0, weight=1)  # Allow UI_frame's rows to expand
UI_frame.grid_columnconfigure([0, 1, 2, 3], weight=1)  # Make all columns in UI_frame expandable

root.mainloop()
