import os
import time
import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import numpy as np
from scipy import stats

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class BenchmarkApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pipelined System Performance Benchmark")
        self.geometry("1300x850")
        self.minsize(1100, 700)

        # Apply modern TTK styling
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self._configure_styles()

        self._build_layout()
        self._init_empty_charts()
        self.refresh_telemetry()

    def _configure_styles(self):
        self.configure(bg="#f8fafc")
        self.style.configure(".", font=("Segoe UI", 10), background="#f8fafc", foreground="#0f172a")
        self.style.configure("Header.TFrame", background="#0f172a")
        self.style.configure("Header.TLabel", background="#0f172a", foreground="#ffffff", font=("Segoe UI", 14, "bold"))
        self.style.configure("Card.TFrame", background="#ffffff", relief="solid", borderwidth=1)
        self.style.configure("CardTitle.TLabel", font=("Segoe UI", 11, "bold"), foreground="#1e293b", background="#ffffff")
        self.style.configure("Metric.TLabel", font=("Segoe UI", 9), background="#ffffff", foreground="#334155")
        self.style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), background="#2563eb", foreground="#ffffff")
        self.style.map("Action.TButton", background=[("active", "#1d4ed8")])

        # Treeview formatting for metrics table
        self.style.configure("Treeview", rowheight=26, font=("Segoe UI", 9))
        self.style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#e2e8f0")

    def _build_layout(self):
        # Top Header & Controls Bar
        header_frame = ttk.Frame(self, style="Header.TFrame", padding=(16, 12))
        header_frame.pack(fill=tk.X, side=tk.TOP)

        title_lbl = ttk.Label(header_frame, text="⚡ System Telemetry & Benchmark Dashboard", style="Header.TLabel")
        title_lbl.pack(side=tk.LEFT)

        ctrl_frame = ttk.Frame(header_frame, style="Header.TFrame")
        ctrl_frame.pack(side=tk.RIGHT)

        ttk.Label(ctrl_frame, text="Iterations:", style="Header.TLabel", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=6)
        self.iter_var = tk.StringVar(value="100")
        self.iter_entry = ttk.Entry(ctrl_frame, textvariable=self.iter_var, width=6, font=("Segoe UI", 10))
        self.iter_entry.pack(side=tk.LEFT, padx=6)

        self.btn_run = ttk.Button(ctrl_frame, text="Run Benchmark", style="Action.TButton", command=self.on_run_benchmark)
        self.btn_run.pack(side=tk.LEFT, padx=10)

        # Main Workspace Container
        main_container = ttk.Frame(self, padding=12)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Left Sidebar (Telemetry + Statistical Results Table)
        left_sidebar = ttk.Frame(main_container, width=380)
        left_sidebar.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))

        # Hardware Telemetry Card
        telemetry_card = ttk.Frame(left_sidebar, style="Card.TFrame", padding=12)
        telemetry_card.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(telemetry_card, text="🖥 Hardware Telemetry", style="CardTitle.TLabel").pack(anchor=tk.W, pady=(0, 8))
        self.lbl_cpu = ttk.Label(telemetry_card, text="CPU Usage: -- %", style="Metric.TLabel")
        self.lbl_cpu.pack(anchor=tk.W, pady=2)
        self.lbl_ram = ttk.Label(telemetry_card, text="RAM Usage: -- %", style="Metric.TLabel")
        self.lbl_ram.pack(anchor=tk.W, pady=2)
        self.lbl_proc_mem = ttk.Label(telemetry_card, text="Process Memory: -- MB", style="Metric.TLabel")
        self.lbl_proc_mem.pack(anchor=tk.W, pady=2)
        self.lbl_threads = ttk.Label(telemetry_card, text="Active Threads: --", style="Metric.TLabel")
        self.lbl_threads.pack(anchor=tk.W, pady=2)

        # Benchmark Summary Metrics Card (Table)
        results_card = ttk.Frame(left_sidebar, style="Card.TFrame", padding=12)
        results_card.pack(fill=tk.BOTH, expand=True)

        ttk.Label(results_card, text="📊 Benchmark Metrics Summary", style="CardTitle.TLabel").pack(anchor=tk.W, pady=(0, 8))
        
        self.tree = ttk.Treeview(results_card, columns=("Metric", "Value"), show="headings", height=10)
        self.tree.heading("Metric", text="Benchmark Metric", anchor=tk.W)
        self.tree.heading("Value", text="Value", anchor=tk.E)
        self.tree.column("Metric", width=220, anchor=tk.W)
        self.tree.column("Value", width=110, anchor=tk.E)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Right Area (Embedded Dashboard Visualizer)
        right_area = ttk.Frame(main_container, style="Card.TFrame", padding=8)
        right_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.fig = Figure(figsize=(8, 6), dpi=100, facecolor="#ffffff")
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_area)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def refresh_telemetry(self):
        """Fetches system metrics and updates telemetry labels."""
        process = psutil.Process(os.getpid())
        sys_mem = psutil.virtual_memory()

        cpu_p = psutil.cpu_percent(interval=None)
        ram_p = sys_mem.percent
        proc_mb = process.memory_info().rss / (1024**2)
        threads = process.num_threads()

        self.lbl_cpu.config(text=f"CPU Usage: {cpu_p:.1f}%")
        self.lbl_ram.config(text=f"RAM Usage: {ram_p:.1f}% ({sys_mem.used / (1024**3):.1f}/{sys_mem.total / (1024**3):.1f} GB)")
        self.lbl_proc_mem.config(text=f"Process Memory: {proc_mb:.1f} MB")
        self.lbl_threads.config(text=f"Active Threads: {threads}")

        self.after(2000, self.refresh_telemetry)

    def _init_empty_charts(self):
        """Draws initial placeholder text on embedded canvas."""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.text(0.5, 0.5, "Click 'Run Benchmark' to execute workload pipeline", 
                ha="center", va="center", fontsize=12, color="#64748b")
        ax.axis("off")
        self.canvas.draw()

    def run_benchmark_logic(self, iterations):
        stage_latencies = {"Stage 1 (Gen)": [], "Stage 2 (Transform)": [], "Stage 3 (Reduce)": []}
        total_latencies, throughputs = [], []

        for _ in range(iterations):
            t_start = time.perf_counter()
            t0 = time.perf_counter()
            d1 = np.random.rand(300, 300)
            t1 = time.perf_counter()

            d2 = np.dot(d1, d1.T)
            t2 = time.perf_counter()

            _ = np.linalg.eigvals(d2)
            t3 = time.perf_counter()

            stage_latencies["Stage 1 (Gen)"].append(t1 - t0)
            stage_latencies["Stage 2 (Transform)"].append(t2 - t1)
            stage_latencies["Stage 3 (Reduce)"].append(t3 - t2)

            total_time = t3 - t_start
            total_latencies.append(total_time)
            throughputs.append(1.0 / total_time)

        lat_arr = np.array(total_latencies)
        tp_arr = np.array(throughputs)

        tendency = {
            "Throughput Harmonic Mean": stats.hmean(tp_arr),
            "Throughput Arithmetic Mean": np.mean(tp_arr),
            "Latency Arithmetic Mean": np.mean(lat_arr),
            "Latency Median (p50)": np.median(lat_arr),
            "Latency Geometric Mean": stats.gmean(lat_arr),
            "Latency Harmonic Mean": stats.hmean(lat_arr),
        }

        return stage_latencies, lat_arr, tp_arr, tendency

    def on_run_benchmark(self):
        try:
            iterations = int(self.iter_var.get())
            if iterations <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a positive integer for iterations.")
            return

        self.btn_run.config(state=tk.DISABLED)
        self.update_idletasks()

        # Run pipeline benchmark
        stage_lat, lat_arr, tp_arr, tendency = self.run_benchmark_logic(iterations)

        # Update Treeview Table
        for row in self.tree.get_children():
            self.tree.delete(row)

        self.tree.insert("", tk.END, values=("Throughput (Harmonic)", f"{tendency['Throughput Harmonic Mean']:.2f} Ops/s"))
        self.tree.insert("", tk.END, values=("Throughput (Arithmetic)", f"{tendency['Throughput Arithmetic Mean']:.2f} Ops/s"))
        self.tree.insert("", tk.END, values=("Latency Mean", f"{tendency['Latency Arithmetic Mean']*1000:.2f} ms"))
        self.tree.insert("", tk.END, values=("Latency Median (p50)", f"{tendency['Latency Median (p50)']*1000:.2f} ms"))
        self.tree.insert("", tk.END, values=("Latency GeoMean", f"{tendency['Latency Geometric Mean']*1000:.2f} ms"))
        self.tree.insert("", tk.END, values=("Latency HarMean", f"{tendency['Latency Harmonic Mean']*1000:.2f} ms"))

        # Render Charts on Embedded Matplotlib Canvas
        self.render_embedded_dashboard(stage_lat, tp_arr, tendency)

        self.btn_run.config(state=tk.NORMAL)

    def render_embedded_dashboard(self, stage_lat, tp_arr, tendency):
        self.fig.clear()
        
        c_primary, c_secondary, c_success, c_danger, c_warning = "#2563eb", "#7c3aed", "#059669", "#e11d48", "#d97706"

        # Subplot 1: Pipeline Breakdown
        ax1 = self.fig.add_subplot(221)
        stages = list(stage_lat.keys())
        stage_means = [np.mean(stage_lat[s]) * 1000 for s in stages]
        ax1.bar(stages, stage_means, color=["#38bdf8", "#fb923c", "#a78bfa"], width=0.5)
        ax1.set_ylabel("Latency (ms)", fontsize=8)
        ax1.set_title("Pipeline Stage Breakdown", fontweight="bold", fontsize=10)
        ax1.grid(axis="y", linestyle="--", alpha=0.5)
        ax1.tick_params(axis="both", labelsize=8)

        # Subplot 2: Latency Measures
        ax2 = self.fig.add_subplot(222)
        metrics = ["Arithmetic", "Median", "Geometric", "Harmonic"]
        lat_vals = [
            tendency["Latency Arithmetic Mean"] * 1000,
            tendency["Latency Median (p50)"] * 1000,
            tendency["Latency Geometric Mean"] * 1000,
            tendency["Latency Harmonic Mean"] * 1000,
        ]
        ax2.bar(metrics, lat_vals, color=[c_danger, c_success, c_warning, "#0d9488"], width=0.5)
        ax2.set_ylabel("Latency (ms)", fontsize=8)
        ax2.set_title("Latency Central Tendencies", fontweight="bold", fontsize=10)
        ax2.grid(axis="y", linestyle="--", alpha=0.5)
        ax2.tick_params(axis="both", labelsize=8)

        # Subplot 3: Throughput Distribution
        ax3 = self.fig.add_subplot(212)
        ax3.hist(tp_arr, bins=16, color="#64748b", edgecolor="#ffffff", alpha=0.75)
        ax3.set_xlabel("Throughput (Operations / Second)", fontsize=8)
        ax3.set_ylabel("Frequency", fontsize=8)
        ax3.set_title("Throughput Rate Distribution (Harmonic vs Arithmetic)", fontweight="bold", fontsize=10)
        ax3.grid(axis="y", linestyle="--", alpha=0.5)
        ax3.tick_params(axis="both", labelsize=8)

        h_mean = tendency["Throughput Harmonic Mean"]
        a_mean = tendency["Throughput Arithmetic Mean"]
        ax3.axvline(h_mean, color=c_success, linestyle="--", linewidth=1.8, label=f"Harmonic Mean: {h_mean:.1f} Ops/s")
        ax3.axvline(a_mean, color=c_danger, linestyle=":", linewidth=1.8, label=f"Arithmetic Mean: {a_mean:.1f} Ops/s")
        ax3.legend(fontsize=8, loc="upper right")

        self.fig.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    app = BenchmarkApp()
    app.mainloop()
