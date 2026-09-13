# Benchmarking_Dashboard_Using_Tendency_Measures
  A_System benchmarking dasboard using the scalling of task manager and through pipelining.

**Workload Pipeline Stages
  Each iteration executes three distinct compute profiles to simulate real-world data processing:

  [ Stage 1: Gen ] ---> [ Stage 2: Transform ] ---> [ Stage 3: Reduce ]
  (np.random.rand)      (np.dot matrix mult)        (np.linalg.eigvals)**

GUI & Visualization Interface
  The interface is constructed using Python's tkinter with ttk widget styling, embedding custom Matplotlib figures via FigureCanvasTkAgg:

  Asynchronous Telemetry: Polling routines update hardware usage labels without locking main event loops.

  Embedded Analytics Canvas: A 4-panel figure visualizes pipeline stage latencies, latency central tendencies, and the throughput rate distribution (highlighting the gap between Arithmetic     and Harmonic means).

  Summary Data Table: A structured ttk.Treeview presents computed metrics immediately upon benchmark completion.
