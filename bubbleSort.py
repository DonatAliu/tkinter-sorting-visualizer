import time
import threading

def bubble_sort(data, drawData, timeTick, stop_signal):
    n = len(data)
    for i in range(n-1):
        swapped = False
        for j in range(n-i-1):
            if stop_signal.is_set():  # Check if stop signal is set
                return  # Exit the function if stop signal is set
            if data[j] > data[j+1]:
                data[j], data[j+1] = data[j+1], data[j]
                swapped = True
                drawData(data, ['green' if x == j or x == j+1 else '#FF204E' for x in range(n)])
                time.sleep(timeTick)
        if not swapped:
            break  # Early exit if no swaps occurred
    drawData(data, ['green' for _ in range(n)])
