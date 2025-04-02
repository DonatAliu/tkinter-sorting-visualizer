from tkinter import *
from tkinter import ttk, messagebox
import random
import time
import threading
from bubbleSort import bubble_sort
from mergeSort import merge_sort
from quickSort import quick_sort
from selectionSort import selection_sort
#yellow is F9D689
root = Tk()
root.title("Sorting Algorithms Visualization")
root.maxsize(1500, 1000)
root.config(bg="#021526")

selected_alg = StringVar()
data = []
stop_signal = threading.Event()
current_thread = None
data_lock = threading.Lock()  # New lock for thread synchronization


def draw_data(data, color_list):
    if not stop_signal.is_set() and root.winfo_exists():
        try:
            canvas.delete("all")
            canvas_height = canvas.winfo_height()
            canvas_width = canvas.winfo_width()
            bar_width = canvas_width / (len(data) + 1)
            margin = 5
            gap = 0
            scaled_data = [value / max(data) for value in data]
            for index, value in enumerate(scaled_data):
                left_x = index * bar_width + margin + gap
                top_y = canvas_height - value * (canvas_height - 40)
                right_x = (index + 1) * bar_width + margin
                bottom_y = canvas_height
                canvas.create_rectangle(left_x, top_y, right_x, bottom_y, fill=color_list[index])
                canvas.create_text(left_x + 2, top_y-2, anchor="sw", text=str(data[index]))
            root.update_idletasks()
        except Exception as e:
            print(f"Error in visualize_data: {e}")


def generate():
    global data, current_thread, stop_signal
   # generateButton.config(state="disabled")
    # Acquire lock to safely access shared resources
    try:
        with data_lock:
            if current_thread and current_thread.is_alive():
                stop_signal.set()
                current_thread.join()  # Wait for the current thread to stop
                stop_signal.clear()

            # Generate new data
            minVal = int(minEntry.get())
            maxVal = int(maxEntry.get())
            size = int(sizeEntry.get())
            data = [random.randrange(minVal, maxVal + 1) for _ in range(size)]
            draw_data(data, ['#E1D7B7' for _ in range(len(data))])
            startButton.config(state="normal")
           # root.after(size*100, lambda: generateButton.config(state="normal"))
    except Exception as e:
        print(f"Error in generating: {e}")


def startAlgorithm():
    """Start the selected sorting algorithm in a new thread."""
    global data, current_thread, stop_signal

    startButton.config(state="disabled")

    # Acquire lock to safely access shared resources
    try:
        with data_lock:
            if current_thread and current_thread.is_alive():
                stop_signal.set()
                current_thread.join()  # Wait for the previous sorting thread to finish
                stop_signal.clear()

            # Start a new sorting algorithm thread
            stop_signal = threading.Event()
            algorithm = algorithm_selector.get()

            if algorithm == "Bubble Sort":
                current_thread = threading.Thread(target=bubble_sort, args=(data, safe_draw_data, speedScale.get(), stop_signal))
            elif algorithm == "Selection Sort":
                current_thread = threading.Thread(target=selection_sort, args=(data, safe_draw_data, speedScale.get(), stop_signal))
            elif algorithm == "Merge Sort":
                current_thread = threading.Thread(target=merge_sort, args=(data, safe_draw_data, speedScale.get(), stop_signal))
            elif algorithm == "Quick Sort":
                current_thread = threading.Thread(target=quick_sort, args=(data, safe_draw_data, speedScale.get(), stop_signal))
            
            current_thread.start()
    except Exception as e:
        print(f"Error in starting algorithm: {e}")


def safe_draw_data(data, color_list):
    root.after(0, draw_data, data, color_list)


def on_closing():
    global current_thread, stop_signal

    with data_lock:
        if current_thread and current_thread.is_alive():
            if messagebox.askyesno("Quit", "Sorting is still running! Do you really want to quit?"):
                stop_signal.set()  # Signal the sorting thread to stop
                while current_thread.is_alive():
                    time.sleep(0.05)  # Wait in small increments for the thread to finish

                root.destroy()  # Close the application
        else:
            root.destroy()  # Close the application directly if no thread is running



root.protocol("WM_DELETE_WINDOW", on_closing)

# Frame and UI setup
UI_frame = Frame(root, bg='#6EACDA')
UI_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

canvas = Canvas(root, bg="#1A4870")
canvas.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

# User Interface
Label(UI_frame, text="Algorithm:", bg="#6EACDA").grid(row=0, column=0, padx=5, pady=5, sticky=W)
algorithm_selector = ttk.Combobox(UI_frame, textvariable=selected_alg, values=["Bubble Sort", "Selection Sort", "Merge Sort","Quick Sort"])
algorithm_selector.grid(row=0, column=1, padx=5, pady=5)
algorithm_selector.current(0)

speedScale = Scale(UI_frame, from_=0.1, to=2.0, length=200, digits=2, resolution=0.2, orient=HORIZONTAL, label="Select speed", bg="#3282B8")
speedScale.grid(row=0, column=2, padx=5, pady=5)

startButton = Button(UI_frame, text="Start", command=startAlgorithm, bg="#3282B8")
startButton.grid(row=0, column=3, padx=5, pady=5)

sizeEntry = Scale(UI_frame, from_=3, to=100, resolution=1, orient=HORIZONTAL, label="Select size", bg="#3282B8")
sizeEntry.grid(row=1, column=1, padx=5, pady=5)
sizeEntry.set(15)

minEntry = Scale(UI_frame, from_=0, to=10, resolution=1, orient=HORIZONTAL, label="Min value", bg="#3282B8")
minEntry.grid(row=1, column=2, padx=5, pady=5)

maxEntry = Scale(UI_frame, from_=10, to=100, resolution=1, orient=HORIZONTAL, label="Max value", bg="#3282B8")
maxEntry.grid(row=1, column=3, padx=5, pady=5)
maxEntry.set(100)

generateButton=Button(UI_frame, text="Generate", command=generate, bg="#3282B8")
generateButton.grid(row=1, column=0, padx=5, pady=5)

# Make the UI responsive
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
UI_frame.grid_rowconfigure(0, weight=1)
UI_frame.grid_columnconfigure([0, 1, 2, 3], weight=1)

root.mainloop()
