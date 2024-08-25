import time
import threading

def bubble_sort(data, draw_data, timeTick, stop_signal, data_lock=None):
    n = len(data)
    for i in range(n - 1):
        swapped = False
        for j in range(n - i - 1):
            if stop_signal.is_set():  # Check if stop signal is set
                return  # Exit the function if stop signal is set

            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
                swapped = True

            # Optionally throttle UI updates to reduce load
            # Draw less frequently for large datasets
            draw_data(data, ['green' if x == j or x == j + 1 else '#FF204E' for x in range(n)])
            time.sleep(timeTick)  # Throttle speed based on user settings

        if not swapped:
            break  # Early exit if no swaps occurred

    # Final draw to ensure the sorted list is shown with thread safety

    draw_data(data, ['green' for _ in range(n)])
 
