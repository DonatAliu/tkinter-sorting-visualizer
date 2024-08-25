import time
import threading

def selection_sort(data, draw_data, timeTick, stop_signal):
    n = len(data)
    
    for i in range(n):
        min_idx = i
        # Initially, color the current index as yellow (assumed smallest value)
        draw_data(data, ['yellow' if x == min_idx else '#FF204E' for x in range(n)])
        time.sleep(timeTick)

        # Inner loop to find the minimum element in the remaining unsorted array
        for j in range(i + 1, n):
            if stop_signal.is_set():  # Check if stop signal is set
                return  # Exit the function if stop signal is set
            
            # Highlight the current element being examined in green
            #color_array = ['yellow' if x == min_idx else ('green' if x == j else '#FF204E') for x in range(n)]
            #draw_data(data, color_array)
            #time.sleep(timeTick)
            
            # Compare the current value with the smallest found so far
            if data[j] < data[min_idx]:
                min_idx = j

                # Update color to mark the new minimum element as yellow
            color_array = ['yellow' if x == min_idx else ('green' if x == j else '#FF204E') for x in range(n)]
            draw_data(data, color_array)
            time.sleep(timeTick)

        # Swap the found minimum element with the first element of the unsorted part
        data[i], data[min_idx] = data[min_idx], data[i]

        # Mark the swapped element (which is now in its correct place) as green
       # draw_data(data, ['green' if x <= i else '#FF204E' for x in range(n)])
        #time.sleep(timeTick)

        # Early exit if stop_signal is set
        if stop_signal.is_set():
            return
    
    # Final pass: Mark the entire array as sorted (green)
    draw_data(data, ['green' for _ in range(n)])
