import re
import random
import time
from dataclasses import dataclass
from typing import Generator, Optional, Tuple, List, Dict, Set

import tkinter as tk
from tkinter import ttk, messagebox


# ----------------------------- Event Model -----------------------------

@dataclass(frozen=True)
class Event:
    type: str
    i: Optional[int] = None
    j: Optional[int] = None
    value: Optional[int] = None
    indices: Optional[Tuple[int, ...]] = None


def ev_compare(i: int, j: int) -> Event:
    return Event(type="compare", i=i, j=j)


def ev_swap(i: int, j: int) -> Event:
    return Event(type="swap", i=i, j=j)


def ev_pivot(p: int) -> Event:
    return Event(type="pivot", i=p)


def ev_select_min(i: int) -> Event:
    return Event(type="select_min", i=i)


def ev_write(i: int, value: int) -> Event:
    return Event(type="write", i=i, value=value)


def ev_mark_sorted(i: int) -> Event:
    return Event(type="mark_sorted", i=i)


def ev_done() -> Event:
    return Event(type="done")


# ----------------------------- Sorting Generators -----------------------------

def bubble_sort_events(a: List[int]) -> Generator[Event, None, None]:
    n = len(a)
    if n <= 1:
        if n == 1:
            yield ev_mark_sorted(0)
        yield ev_done()
        return

    for end in range(n - 1, -1, -1):
        for j in range(0, end):
            yield ev_compare(j, j + 1)
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                yield ev_swap(j, j + 1)
        yield ev_mark_sorted(end)
    yield ev_done()


def selection_sort_events(a: List[int]) -> Generator[Event, None, None]:
    n = len(a)
    if n <= 1:
        if n == 1:
            yield ev_mark_sorted(0)
        yield ev_done()
        return

    for i in range(n):
        min_idx = i
        yield ev_select_min(min_idx)
        for j in range(i + 1, n):
            yield ev_compare(min_idx, j)
            if a[j] < a[min_idx]:
                min_idx = j
                yield ev_select_min(min_idx)
        if min_idx != i:
            a[i], a[min_idx] = a[min_idx], a[i]
            yield ev_swap(i, min_idx)
        yield ev_mark_sorted(i)
    yield ev_done()


def merge_sort_events(a: List[int]) -> Generator[Event, None, None]:
    n = len(a)

    def sort(lo: int, hi: int) -> Generator[Event, None, None]:
        if hi - lo <= 1:
            return
        mid = (lo + hi) // 2
        yield from sort(lo, mid)
        yield from sort(mid, hi)

        left = a[lo:mid]
        right = a[mid:hi]
        i = 0
        j = 0
        k = lo

        while i < len(left) and j < len(right):
            yield ev_compare(lo + i, mid + j)
            if left[i] <= right[j]:
                val = left[i]
                i += 1
            else:
                val = right[j]
                j += 1
            a[k] = val
            yield ev_write(k, val)
            k += 1

        while i < len(left):
            val = left[i]
            i += 1
            a[k] = val
            yield ev_write(k, val)
            k += 1

        while j < len(right):
            val = right[j]
            j += 1
            a[k] = val
            yield ev_write(k, val)
            k += 1

    if n <= 1:
        if n == 1:
            yield ev_mark_sorted(0)
        yield ev_done()
        return

    yield from sort(0, n)
    for idx in range(n):
        yield ev_mark_sorted(idx)
    yield ev_done()


def quick_sort_lomuto_events(a: List[int]) -> Generator[Event, None, None]:
    n = len(a)

    def qs(lo: int, hi: int) -> Generator[Event, None, None]:
        if hi - lo <= 1:
            if hi - lo == 1:
                yield ev_mark_sorted(lo)
            return

        pivot_idx = hi - 1
        pivot_val = a[pivot_idx]
        yield ev_pivot(pivot_idx)

        i = lo
        for j in range(lo, hi - 1):
            yield ev_compare(j, pivot_idx)
            if a[j] <= pivot_val:
                if i != j:
                    a[i], a[j] = a[j], a[i]
                    yield ev_swap(i, j)
                i += 1

        if i != pivot_idx:
            a[i], a[pivot_idx] = a[pivot_idx], a[i]
            yield ev_swap(i, pivot_idx)

        yield ev_mark_sorted(i)
        yield from qs(lo, i)
        yield from qs(i + 1, hi)

    if n <= 1:
        if n == 1:
            yield ev_mark_sorted(0)
        yield ev_done()
        return

    yield from qs(0, n)
    yield ev_done()


# ----------------------------- Tkinter App -----------------------------

class SortingVisualizerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Sorting Algorithms Visualizer (Tkinter)")
        self.geometry("1200x720")
        self.minsize(980, 620)

        # Color palette (8 distinct hex colors)
        self.COLORS = {
            "default": "#3B82F6",     # blue
            "comparing": "#F59E0B",   # amber
            "swapping": "#EF4444",    # red
            "pivot": "#A855F7",       # purple
            "selected_min": "#22C55E",# green
            "writing": "#06B6D4",     # cyan
            "sorted": "#10B981",      # emerald
            "finished": "#111827",    # near-black
        }

        # State machine
        self.state = "Idle"  # Idle / Running / Paused / Finished
        self._after_id: Optional[str] = None

        # Dataset & flags
        self.data: List[int] = []
        self.original_data: List[int] = []       # snapshot for Reset restore (last loaded)
        self.dataset_loaded: bool = False
        self.dataset_source: Optional[str] = None  # "manual" / "random" / None
        self.manual_locked_until_reset: bool = False  # if manual dataset loaded, Random must refuse until Reset

        # Sorting engine
        self._gen: Optional[Generator[Event, None, None]] = None
        self._algo_local: List[int] = []  # local copy used by generators (kept in sync by events)
        self.sorted_indices: Set[int] = set()
        self._pivot_index: Optional[int] = None

        # Metrics
        self.comparisons = 0
        self.swaps_or_writes = 0
        self._start_perf: Optional[float] = None
        self._elapsed_before_pause: float = 0.0

        # UI variables
        self.var_algo = tk.StringVar(value="Bubble Sort")
        self.var_speed = tk.IntVar(value=25)  # ms
        self.var_size = tk.IntVar(value=30)   # 1..100

        self.var_input = tk.StringVar(value="")
        self.var_min = tk.StringVar(value="0")
        self.var_max = tk.StringVar(value="100")

        self.var_status = tk.StringVar(value="Idle")
        self.var_algo_name = tk.StringVar(value=self.var_algo.get())
        self.var_comparisons = tk.StringVar(value="0")
        self.var_swaps = tk.StringVar(value="0")
        self.var_elapsed = tk.StringVar(value="0.000 s")
        self.var_message = tk.StringVar(value="")

        # Build UI
        self._build_ui()
        self._redraw()

        # Bindings
        self.canvas.bind("<Configure>", lambda _e: self._redraw())
        self.entry_input.bind("<KeyRelease>", self._on_input_edited)

    # ----------------------------- UI Construction -----------------------------

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        main = ttk.Frame(self, padding=10)
        main.grid(row=0, column=0, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(0, weight=1)

        # Canvas
        self.canvas = tk.Canvas(main, bg="white", highlightthickness=1, highlightbackground="#D1D5DB")
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Right side controls
        side = ttk.Frame(main)
        side.grid(row=0, column=1, sticky="ns")
        side.columnconfigure(0, weight=1)

        # Algorithm selector
        ttk.Label(side, text="Algorithm").grid(row=0, column=0, sticky="w")
        self.combo_algo = ttk.Combobox(
            side,
            textvariable=self.var_algo,
            values=["Bubble Sort", "Selection Sort", "Merge Sort (Top-Down)", "Quick Sort (Lomuto)"],
            state="readonly",
            width=28,
        )
        self.combo_algo.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # Speed slider
        ttk.Label(side, text="Speed (delay ms)").grid(row=2, column=0, sticky="w")
        self.scale_speed = ttk.Scale(
            side, from_=1, to=250, orient="horizontal",
            variable=self.var_speed
        )
        self.scale_speed.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        # Data size slider
        ttk.Label(side, text="Data Size (1..100)").grid(row=4, column=0, sticky="w")
        self.scale_size = ttk.Scale(
            side, from_=1, to=100, orient="horizontal",
            variable=self.var_size
        )
        self.scale_size.grid(row=5, column=0, sticky="ew", pady=(0, 10))

        # Manual input
        ttk.Label(side, text="Manual Input (non-negative integers)").grid(row=6, column=0, sticky="w")
        self.entry_input = ttk.Entry(side, textvariable=self.var_input, width=30)
        self.entry_input.grid(row=7, column=0, sticky="ew", pady=(0, 8))

        # Random controls
        rand_box = ttk.LabelFrame(side, text="Random Generation", padding=8)
        rand_box.grid(row=8, column=0, sticky="ew", pady=(0, 10))
        rand_box.columnconfigure(1, weight=1)

        ttk.Label(rand_box, text="Min").grid(row=0, column=0, sticky="w")
        self.entry_min = ttk.Entry(rand_box, textvariable=self.var_min, width=10)
        self.entry_min.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=2)

        ttk.Label(rand_box, text="Max").grid(row=1, column=0, sticky="w")
        self.entry_max = ttk.Entry(rand_box, textvariable=self.var_max, width=10)
        self.entry_max.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=2)

        self.btn_random = ttk.Button(rand_box, text="Random", command=self.on_random)
        self.btn_random.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(6, 0))

        # Buttons
        btns = ttk.Frame(side)
        btns.grid(row=9, column=0, sticky="ew", pady=(0, 10))
        for c in range(5):
            btns.columnconfigure(c, weight=1)

        self.btn_play = ttk.Button(btns, text="Play", command=self.on_play)
        self.btn_pause = ttk.Button(btns, text="Pause", command=self.on_pause)
        self.btn_step = ttk.Button(btns, text="Step", command=self.on_step)
        self.btn_reset = ttk.Button(btns, text="Reset", command=self.on_reset)
        self.btn_help = ttk.Button(btns, text="Help", command=self.on_help)

        self.btn_play.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.btn_pause.grid(row=0, column=1, sticky="ew", padx=(0, 6))
        self.btn_step.grid(row=0, column=2, sticky="ew", padx=(0, 6))
        self.btn_reset.grid(row=0, column=3, sticky="ew", padx=(0, 6))
        self.btn_help.grid(row=0, column=4, sticky="ew")

        # Metrics
        metrics = ttk.LabelFrame(side, text="Metrics", padding=8)
        metrics.grid(row=10, column=0, sticky="ew")
        metrics.columnconfigure(1, weight=1)

        ttk.Label(metrics, text="Algorithm:").grid(row=0, column=0, sticky="w")
        ttk.Label(metrics, textvariable=self.var_algo_name).grid(row=0, column=1, sticky="w")

        ttk.Label(metrics, text="State:").grid(row=1, column=0, sticky="w")
        ttk.Label(metrics, textvariable=self.var_status).grid(row=1, column=1, sticky="w")

        ttk.Label(metrics, text="Comparisons:").grid(row=2, column=0, sticky="w")
        ttk.Label(metrics, textvariable=self.var_comparisons).grid(row=2, column=1, sticky="w")

        ttk.Label(metrics, text="Swaps/Writes:").grid(row=3, column=0, sticky="w")
        ttk.Label(metrics, textvariable=self.var_swaps).grid(row=3, column=1, sticky="w")

        ttk.Label(metrics, text="Elapsed:").grid(row=4, column=0, sticky="w")
        ttk.Label(metrics, textvariable=self.var_elapsed).grid(row=4, column=1, sticky="w")

        # Message area
        msg = ttk.Label(side, textvariable=self.var_message, foreground="#B91C1C", wraplength=280, justify="left")
        msg.grid(row=11, column=0, sticky="ew", pady=(10, 0))

        self._update_buttons()

    # ----------------------------- Parsing & Validation -----------------------------

    @staticmethod
    def _parse_int_list(text: str) -> Optional[List[int]]:
        s = text.strip()
        if not s:
            return None
        parts = [p for p in re.split(r"[,\s]+", s) if p.strip() != ""]
        if not parts:
            return None
        out: List[int] = []
        for p in parts:
            if not re.fullmatch(r"\d+", p):
                return None
            val = int(p)
            if val < 0:
                return None
            out.append(val)
        return out

    @staticmethod
    def _parse_nonneg_int(text: str) -> Optional[int]:
        t = text.strip()
        if not re.fullmatch(r"\d+", t):
            return None
        v = int(t)
        if v < 0:
            return None
        return v

    def _on_input_edited(self, _event=None) -> None:
        self._set_message("")

    # ----------------------------- Dataset / Engine Setup -----------------------------

    def _set_message(self, msg: str) -> None:
        self.var_message.set(msg)

    def _set_state(self, new_state: str) -> None:
        self.state = new_state
        self.var_status.set(new_state)
        self._update_buttons()

    def _lock_controls(self, locked: bool) -> None:
        combo_state = "disabled" if locked else "readonly"
        entry_state = "disabled" if locked else "normal"
        btn_state = "disabled" if locked else "normal"

        self.combo_algo.configure(state=combo_state)
        self.entry_input.configure(state=entry_state)
        self.entry_min.configure(state=entry_state)
        self.entry_max.configure(state=entry_state)
        self.btn_random.configure(state=btn_state)

        if locked:
            self.scale_speed.state(["disabled"])
            self.scale_size.state(["disabled"])
        else:
            self.scale_speed.state(["!disabled"])
            self.scale_size.state(["!disabled"])

    def _update_buttons(self) -> None:
        if self.state == "Idle":
            self.btn_play.configure(state="normal")
            self.btn_pause.configure(state="disabled")
            self.btn_step.configure(state="normal")
            self.btn_reset.configure(state="normal")
        elif self.state == "Running":
            self.btn_play.configure(state="disabled")
            self.btn_pause.configure(state="normal")
            self.btn_step.configure(state="disabled")
            self.btn_reset.configure(state="normal")
        elif self.state == "Paused":
            self.btn_play.configure(state="normal")
            self.btn_pause.configure(state="disabled")
            self.btn_step.configure(state="normal")
            self.btn_reset.configure(state="normal")
        elif self.state == "Finished":
            self.btn_play.configure(state="disabled")
            self.btn_pause.configure(state="disabled")
            self.btn_step.configure(state="disabled")
            self.btn_reset.configure(state="normal")
        else:
            self.btn_play.configure(state="normal")
            self.btn_pause.configure(state="disabled")
            self.btn_step.configure(state="normal")
            self.btn_reset.configure(state="normal")

        self.btn_help.configure(state="normal")

    def _reset_metrics_and_visuals(self) -> None:
        self.comparisons = 0
        self.swaps_or_writes = 0
        self.sorted_indices.clear()
        self._pivot_index = None

        self._start_perf = None
        self._elapsed_before_pause = 0.0

        self.var_comparisons.set("0")
        self.var_swaps.set("0")
        self.var_elapsed.set("0.000 s")
        self.var_algo_name.set(self.var_algo.get())

    def _cancel_schedule(self) -> None:
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _ensure_dataset_exists_or_message(self) -> bool:
        if not self.dataset_loaded or not self.data:
            self._set_message("Enter data or press Random.")
            return False
        return True

    def _init_sorting_generator(self) -> None:
        self._algo_local = list(self.data)
        algo = self.var_algo.get()
        self.var_algo_name.set(algo)

        if algo == "Bubble Sort":
            self._gen = bubble_sort_events(self._algo_local)
        elif algo == "Selection Sort":
            self._gen = selection_sort_events(self._algo_local)
        elif algo == "Merge Sort (Top-Down)":
            self._gen = merge_sort_events(self._algo_local)
        elif algo == "Quick Sort (Lomuto)":
            self._gen = quick_sort_lomuto_events(self._algo_local)
        else:
            self._gen = bubble_sort_events(self._algo_local)

    # ----------------------------- Drawing -----------------------------

    def _compute_colors_for_tick(self, highlights: Dict[int, str]) -> Dict[int, str]:
        colors: Dict[int, str] = {}
        n = len(self.data)

        for idx in range(n):
            if self.state == "Finished":
                colors[idx] = self.COLORS["finished"]
            elif idx in self.sorted_indices:
                colors[idx] = self.COLORS["sorted"]
            else:
                colors[idx] = self.COLORS["default"]

        if self.state != "Finished":
            if self._pivot_index is not None and 0 <= self._pivot_index < n:
                colors[self._pivot_index] = self.COLORS["pivot"]
            for idx, col in highlights.items():
                if 0 <= idx < n:
                    colors[idx] = col

        return colors

    def _redraw(self, highlights: Optional[Dict[int, str]] = None) -> None:
        self.canvas.delete("all")
        if not self.data:
            self.canvas.create_text(
                10, 10, anchor="nw",
                text="No dataset loaded. Enter data and press Play, or press Random.",
                fill="#6B7280", font=("Segoe UI", 12)
            )
            return

        highlights = highlights or {}
        colors = self._compute_colors_for_tick(highlights)

        w = max(1, self.canvas.winfo_width())
        h = max(1, self.canvas.winfo_height())

        top_pad = 20
        bottom_pad = 60
        left_pad = 20
        right_pad = 20

        usable_w = max(1, w - left_pad - right_pad)
        usable_h = max(1, h - top_pad - bottom_pad)

        n = len(self.data)
        max_val = max(self.data) if self.data else 1
        max_val = max(max_val, 1)

        bar_w = usable_w / n
        font_size = 8 if n > 60 else 9 if n > 40 else 10
        value_font = ("Segoe UI", font_size)

        for i, val in enumerate(self.data):
            x0 = left_pad + i * bar_w + 1
            x1 = left_pad + (i + 1) * bar_w - 1
            bar_h = (val / max_val) * usable_h
            y1 = top_pad + usable_h
            y0 = y1 - bar_h

            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                fill=colors.get(i, self.COLORS["default"]),
                outline="#111827" if n <= 60 else ""
            )

            tx = (x0 + x1) / 2
            ty = y1 + 16
            self.canvas.create_text(
                tx, ty,
                text=str(val),
                font=value_font,
                fill="#111827"
            )

        legend_y = 6
        lx = 10
        items = [
            ("default", "Default"),
            ("comparing", "Compare"),
            ("swapping", "Swap"),
            ("pivot", "Pivot"),
            ("selected_min", "Min"),
            ("writing", "Write"),
            ("sorted", "Sorted"),
            ("finished", "Finished"),
        ]
        for key, label in items:
            self.canvas.create_rectangle(lx, legend_y, lx + 12, legend_y + 12, fill=self.COLORS[key], outline="")
            self.canvas.create_text(lx + 16, legend_y + 6, anchor="w", text=label, fill="#374151", font=("Segoe UI", 9))
            lx += 80

    # ----------------------------- Metrics -----------------------------

    def _elapsed_seconds(self) -> float:
        if self._start_perf is None:
            return self._elapsed_before_pause
        return self._elapsed_before_pause + (time.perf_counter() - self._start_perf)

    def _update_metrics_labels(self) -> None:
        self.var_comparisons.set(str(self.comparisons))
        self.var_swaps.set(str(self.swaps_or_writes))
        self.var_elapsed.set(f"{self._elapsed_seconds():.3f} s")

    # ----------------------------- Event Application -----------------------------

    def _apply_event(self, event: Event) -> Dict[int, str]:
        highlights: Dict[int, str] = {}
        et = event.type

        if et == "compare":
            if event.i is not None and event.j is not None:
                highlights[event.i] = self.COLORS["comparing"]
                highlights[event.j] = self.COLORS["comparing"]
            self.comparisons += 1

        elif et == "swap":
            i, j = event.i, event.j
            if i is not None and j is not None and 0 <= i < len(self.data) and 0 <= j < len(self.data):
                highlights[i] = self.COLORS["swapping"]
                highlights[j] = self.COLORS["swapping"]
                self.data[i], self.data[j] = self.data[j], self.data[i]
            self.swaps_or_writes += 1

        elif et == "pivot":
            if event.i is not None:
                self._pivot_index = event.i
                highlights[event.i] = self.COLORS["pivot"]

        elif et == "select_min":
            if event.i is not None:
                highlights[event.i] = self.COLORS["selected_min"]

        elif et == "write":
            i = event.i
            if i is not None and event.value is not None and 0 <= i < len(self.data):
                highlights[i] = self.COLORS["writing"]
                self.data[i] = event.value
            self.swaps_or_writes += 1

        elif et == "mark_sorted":
            if event.i is not None:
                self.sorted_indices.add(event.i)

        return highlights

    # ----------------------------- Animation Loop -----------------------------

    def _tick(self) -> None:
        if self.state != "Running":
            self._after_id = None
            return

        if self._gen is None:
            self._finish_sort()
            return

        try:
            event = next(self._gen)
        except StopIteration:
            self._finish_sort()
            return

        if event.type == "done":
            self._finish_sort()
            return

        highlights = self._apply_event(event)
        self._update_metrics_labels()
        self._redraw(highlights)

        if self.state == "Running":
            delay = max(1, int(self.var_speed.get()))
            self._after_id = self.after(delay, self._tick)

    def _finish_sort(self) -> None:
        self._cancel_schedule()
        self._pivot_index = None

        self.sorted_indices = set(range(len(self.data)))
        self._set_state("Finished")

        if self._start_perf is not None:
            self._elapsed_before_pause = self._elapsed_seconds()
            self._start_perf = None

        self._update_metrics_labels()
        self._lock_controls(False)
        self._redraw()

    # ----------------------------- Commands -----------------------------

    def on_random(self) -> None:
        self._set_message("")
        if self.state == "Running":
            self._set_message("Pause or Reset before generating Random data.")
            return

        if self.manual_locked_until_reset:
            self._set_message("Random is disabled because a manual dataset is loaded. Press Reset first.")
            return

        min_v = self._parse_nonneg_int(self.var_min.get())
        max_v = self._parse_nonneg_int(self.var_max.get())
        if min_v is None or max_v is None:
            self._set_message("Random Min/Max must be non-negative integers.")
            return
        if max_v < min_v:
            self._set_message("Random Max must be >= Min.")
            return

        size = int(round(float(self.var_size.get())))
        size = max(1, min(100, size))

        self.data = [random.randint(min_v, max_v) for _ in range(size)]
        self.original_data = list(self.data)
        self.dataset_loaded = True
        self.dataset_source = "random"
        self.manual_locked_until_reset = False

        self._reset_metrics_and_visuals()
        self._set_state("Idle")
        self._gen = None
        self._lock_controls(False)
        self._redraw()

    def _load_manual_if_valid(self) -> bool:
        parsed = self._parse_int_list(self.var_input.get())
        if parsed is None:
            self._set_message("Invalid input. Use e.g. '1, 2 3' (non-negative integers only).")
            return False
        if len(parsed) < 1 or len(parsed) > 100:
            self._set_message("Manual input must contain 1..100 numbers.")
            return False

        self.data = list(parsed)
        self.original_data = list(self.data)
        self.dataset_loaded = True
        self.dataset_source = "manual"
        self.manual_locked_until_reset = True
        return True

    def on_play(self) -> None:
        self._set_message("")

        if self.state == "Finished":
            return
        if self.state == "Paused":
            self._set_state("Running")
            self._start_perf = time.perf_counter()
            self._cancel_schedule()
            self._after_id = self.after(max(1, int(self.var_speed.get())), self._tick)
            return
        if self.state == "Running":
            return

        # Idle: load manual input if present; otherwise require an existing dataset (Random)
        input_text = self.var_input.get().strip()
        if input_text:
            if not self._load_manual_if_valid():
                return
        else:
            if not self.dataset_loaded:
                self._set_message("Enter data or press Random.")
                return

        self._cancel_schedule()
        self._reset_metrics_and_visuals()
        self._init_sorting_generator()
        self._lock_controls(True)

        self._set_state("Running")
        self._start_perf = time.perf_counter()

        self._after_id = self.after(max(1, int(self.var_speed.get())), self._tick)

    def on_pause(self) -> None:
        self._set_message("")
        if self.state != "Running":
            return
        self._cancel_schedule()
        if self._start_perf is not None:
            self._elapsed_before_pause = self._elapsed_seconds()
            self._start_perf = None
        self._set_state("Paused")
        self._update_metrics_labels()
        self._redraw()

    def on_step(self) -> None:
        self._set_message("")
        if self.state == "Finished":
            return

        if self.state == "Idle":
            if not self._ensure_dataset_exists_or_message():
                return
            self._cancel_schedule()
            self._reset_metrics_and_visuals()
            self._init_sorting_generator()
            self._lock_controls(True)
            self._set_state("Paused")

        if self.state != "Paused":
            return
        if self._gen is None:
            self._set_message("No active sort generator. Press Reset then Play, or Step from Idle with a dataset.")
            return

        try:
            event = next(self._gen)
        except StopIteration:
            self._finish_sort()
            return

        if event.type == "done":
            self._finish_sort()
            return

        if self._start_perf is None:
            self._start_perf = time.perf_counter()

        highlights = self._apply_event(event)
        self._update_metrics_labels()
        self._redraw(highlights)

    def on_reset(self) -> None:
        self._set_message("")
        self._cancel_schedule()

        if self.dataset_loaded:
            self.data = list(self.original_data)
        else:
            self.data = []

        self._gen = None
        self._algo_local = []
        self._pivot_index = None

        self._reset_metrics_and_visuals()
        self._lock_controls(False)
        self._set_state("Idle")

        # After reset, Random is allowed again
        self.manual_locked_until_reset = False

        self._redraw()

    def on_help(self) -> None:
        win = tk.Toplevel(self)
        win.title("Help - Sorting Visualizer")
        win.geometry("720x520")
        win.minsize(640, 420)

        text = tk.Text(win, wrap="word", font=("Segoe UI", 10))
        text.pack(fill="both", expand=True, padx=10, pady=10)

        help_content = f"""ACCEPTED INPUT FORMATS
- Commas and/or whitespace in any mixture:
  • 1,2,3
  • 1 2 3
  • 1, 2 , 3,    4   5 6 20
- Only NON-NEGATIVE integers (0, 1, 2, ...). Duplicates are allowed.
- Manual list length must be 1..100.

BUTTONS
- Play:
  • From Idle: starts sorting (loads Manual Input if provided and valid).
  • From Paused: resumes animation.
  • Disabled when Finished (press Reset).
- Pause:
  • Stops scheduling immediately (no further .after ticks).
- Step:
  • From Idle: performs exactly ONE yielded event (only if a dataset already exists).
  • From Paused: performs exactly ONE yielded event.
  • Never auto-schedules; stays Paused.
- Reset:
  • Stops any running schedule.
  • Clears highlights, metrics, and restores the last loaded dataset (manual or random).
  • Unlocks controls.
- Random:
  • Generates a dataset using Min/Max and Data Size.
  • Allowed only when no manual dataset is currently loaded OR after Reset.
  • If a manual dataset is loaded, press Reset to enable Random again.

SLIDERS
- Speed (delay ms):
  • Controls the delay between visualization events.
  • Locked when sorting starts; unlocked only on Reset or when done.
- Data Size (1..100):
  • Used when generating Random data.
  • Locked when sorting starts; unlocked only on Reset or when done.

COLOR LEGEND
- Default: {self.COLORS["default"]}
- Comparing: {self.COLORS["comparing"]}
- Swapping: {self.COLORS["swapping"]}
- Pivot (Quick Sort): {self.COLORS["pivot"]}
- Selected Minimum (Selection Sort): {self.COLORS["selected_min"]}
- Writing/Merging (Merge Sort writes): {self.COLORS["writing"]}
- Sorted (final position / sorted portion): {self.COLORS["sorted"]}
- Finished (all sorted): {self.COLORS["finished"]}
"""
        text.insert("1.0", help_content)
        text.configure(state="disabled")

    def run(self) -> None:
        self.mainloop()


def main() -> None:
    app = SortingVisualizerApp()
    app.run()


if __name__ == "__main__":
    main()