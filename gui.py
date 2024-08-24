from tkinter import *
from tkinter import ttk, messagebox
import random
import threading
from bubbleSort import bubble_sort
from selectionSort import selection_sort

root = Tk()
root.title("Sorting Algorithms Visualization")
root.maxsize(900, 600)
root.config(bg="#021526")

selected_alg = StringVar()
data = []
stop_signal = threading.Event()
current_thread = None

def draw_data(data, color_list):
    if not stop_signal.is_set() and root.winfo_exists():
            try:
                canvas.delete("all")
                canvas_height = canvas.winfo_height()
                canvas_width = canvas.winfo_width()
                bar_width = canvas_width / (len(data) + 1)
                margin = 20
                gap = 5
                scaled_data = [value / max(data) for value in data]
                for index, value in enumerate(scaled_data):
                    left_x = index * bar_width + margin + gap
                    top_y = canvas_height - value * (canvas_height - 40)
                    right_x = (index + 1) * bar_width + margin
                    bottom_y = canvas_height
                    canvas.create_rectangle(left_x, top_y, right_x, bottom_y, fill=color_list[index])
                    canvas.create_text(left_x + 2, top_y, anchor="sw", text=str(data[index]))
                root.update_idletasks()
            except Exception as e:
                print(f"Error in visualize_data: {e}")

def generate():
    global data, current_thread, stop_signal
    if current_thread and current_thread.is_alive():
        stop_signal.set()
        current_thread.join()
        stop_signal.clear()

    minVal = int(minEntry.get())
    maxVal = int(maxEntry.get())
    size = int(sizeEntry.get())
    data = [random.randrange(minVal, maxVal + 1) for _ in range(size)]
    draw_data(data, ['#FF204E' for _ in range(len(data))])
    startButton.config(state="normal")

def startAlgorithm():
    """Start the selected sorting algorithm in a new thread."""
    startButton.config(state="disabled")
    global data, current_thread, stop_signal
    if current_thread and current_thread.is_alive():
        stop_signal.set()
        current_thread.join()
        stop_signal.clear()

    if algorithMenu.get() == "Bubble Sort":
        stop_signal = threading.Event()
        current_thread = threading.Thread(target=bubble_sort, args=(data, draw_data, speedScale.get(), stop_signal))
        current_thread.start()
    elif algorithMenu.get() == "Selection Sort":
        stop_signal = threading.Event()
        current_thread = threading.Thread(target=selection_sort, args=(data, draw_data, speedScale.get(), stop_signal))
        current_thread.start()
    elif algorithMenu.get() == "Quick Sort":
        stop_signal = threading.Event()
        current_thread = threading.Thread(target=bubble_sort, args=(data, draw_data, speedScale.get(), stop_signal))
        current_thread.start()

def on_closing():
    """Handle closing of the window."""
    global current_thread, stop_signal
    if current_thread and current_thread.is_alive():
        if messagebox.askyesno("Quit", "Sorting is still running! Do you really want to quit?"):
            stop_signal.set()
            current_thread.join()
            root.destroy()
    else:
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Frame and UI setup
UI_frame = Frame(root, bg='#6EACDA')
UI_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

canvas = Canvas(root, bg="#03346E")
canvas.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

# User Interface
Label(UI_frame, text="Algorithm:", bg="#6EACDA").grid(row=0, column=0, padx=5, pady=5, sticky=W)
algorithMenu = ttk.Combobox(UI_frame, textvariable=selected_alg, values=["Bubble Sort","Selection Sort","Merge Sort"])
algorithMenu.grid(row=0, column=1, padx=5, pady=5)
algorithMenu.current(0)

speedScale = Scale(UI_frame, from_=0.1, to=2.0, length=200, digits=2, resolution=0.2, orient=HORIZONTAL, label="Select speed")
speedScale.grid(row=0, column=2, padx=5, pady=5)
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
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
UI_frame.grid_rowconfigure(0, weight=1)
UI_frame.grid_columnconfigure([0, 1, 2, 3], weight=1)

root.mainloop()
