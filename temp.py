import csv
import os
import subprocess

import matplotlib.pyplot as plt
import pandas as pd

# === CONFIGURATION ===

omp_threads = [1, 2, 3, 4, 5, 6, 7, 8]  # Threads for OpenMP
mpi_procs = [1, 2, 3, 4, 5, 6, 7, 8]  # Processes for MPI
base_size = 10000000  # Base input size
output_strong = "logs/strong_scaling.csv"
output_weak = "logs/weak_scaling.csv"

# === HELPERS ===


def run_command(cmd, env=None):
    """Run a shell command and return stdout, stderr."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
    return result.stdout.strip(), result.stderr.strip()


def extract_time(output):
    """Parse output to find execution time line."""
    for line in output.splitlines():
        if "Time:" in line or "Elapsed time:" in line:
            try:
                return float(line.strip().split()[-1])
            except ValueError:
                return None
    return None


def write_csv(filename, header, rows):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


# === CLEAN + BUILD ===
# print("🛠️ Cleaning and building...")
subprocess.run("make fclean && make all", shell=True, check=True)

# === STRONG SCALING TESTS ===
print("📊 Running strong scaling benchmarks...")

strong_data = []

# Baseline single-threaded
print("→ project (sequential)")
out, err = run_command(f"./project {base_size}")
t_seq = extract_time(out)

if t_seq is None:
    print("❌ Failed to extract time from sequential output:\n", out)
    exit(1)

strong_data.append(["project", 1, base_size, t_seq])
print(f"   Time: {t_seq:.4f}s")

# OpenMP
for nth in omp_threads:
    print(f"→ project_omp with {nth} threads")
    out, err = run_command(f"./project_omp {base_size} {nth}")
    t = extract_time(out)
    if t is None:
        print(f"❌ Failed to extract time from project_omp with {nth} threads:\n", out)
        exit(1)
    strong_data.append(["project_omp", nth, base_size, t])
    print(f"   Time: {t:.4f}s")

# MPI
for np in mpi_procs:
    print(f"→ project_mpi with {np} processes")
    out, err = run_command(f"mpirun -np {np} ./project_mpi {base_size}")
    t = extract_time(out)
    if t is None:
        print(f"❌ Failed to extract time from project_mpi with {np} processes:\n", out)
        exit(1)
    strong_data.append(["project_mpi", np, base_size, t])
    print(f"   Time: {t:.4f}s")

write_csv(
output_strong,
["exec_type", "procs/threads", "vector_size", "time_sec"],
strong_data,
)

# === WEAK SCALING TESTS ===
print("📊 Running weak scaling benchmarks...")

weak_data = []

# OpenMP
for nth in omp_threads:
    size = base_size * nth
    print(f"→ project_omp with {nth} threads and size {size}")
    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = str(nth)
    out, err = run_command(f"./project_omp {size} {nth}")
    t = extract_time(out)
    if t is None:
        print(f"❌ Failed to extract time from project_omp with {nth} threads:\n", out)
        exit(1)
    weak_data.append(["project_omp", nth, size, t])
    print(f"   Time: {t:.4f}s")

# MPI
for np in mpi_procs:
    size = base_size * np
    print(f"→ project_mpi with {np} processes and size {size}")
    out, err = run_command(f"mpirun -np {np} ./project_mpi {size}")
    t = extract_time(out)
    if t is None:
        print(f"❌ Failed to extract time from project_mpi with {np} processes:\n", out)
        exit(1)
    weak_data.append(["project_mpi", np, size, t])
    print(f"   Time: {t:.4f}s")

write_csv(
    output_weak, ["exec_type", "procs/threads", "vector_size", "time_sec"], weak_data
)

print("\n✅ Benchmarking complete.")
print(f"→ Strong scaling data saved to: {output_strong}")
print(f"→ Weak scaling data saved to:   {output_weak}")


# === STRONG SCALING ===
def plot_strong_scaling():
    _, ax = plt.subplots()
    # Load data
    strong_df = pd.read_csv(output_strong)

    # Separate data
    mpi_strong = strong_df[strong_df["exec_type"] == "project_mpi"]
    omp_strong = strong_df[strong_df["exec_type"] == "project_omp"]

    # Compute speedup for strong scaling
    mpi_baseline = mpi_strong[mpi_strong["procs/threads"] == 1]["time_sec"].values[0]
    omp_baseline = omp_strong[omp_strong["procs/threads"] == 1]["time_sec"].values[0]

    mpi_strong = mpi_strong.copy()
    omp_strong = omp_strong.copy()
    mpi_strong["speedup"] = mpi_baseline / mpi_strong["time_sec"]
    omp_strong["speedup"] = omp_baseline / omp_strong["time_sec"]

    # --- Left: Strong scaling ---
    # Compute the dynamic y-limit for strong scaling
    max_speedup = max(
        mpi_strong["speedup"].max(),
        omp_strong["speedup"].max()
    )

    ideal_limit = mpi_strong["procs/threads"].max()  # in case we want to match ideal line
    y_upper = max_speedup * 1.1  # give a bit of headroom

    # --- Left: Strong scaling ---
    ax.plot(mpi_strong["procs/threads"], mpi_strong["speedup"], label="MPI", color="green")
    ax.fill_between(mpi_strong["procs/threads"], mpi_strong["speedup"]*0.95, mpi_strong["speedup"]*1.05, alpha=0.2, color="green")

    ax.plot(omp_strong["procs/threads"], omp_strong["speedup"], label="OpenMP", color="blue")
    ax.fill_between(omp_strong["procs/threads"], omp_strong["speedup"]*0.95, omp_strong["speedup"]*1.05, alpha=0.2, color="blue")

    ax.plot([1, ideal_limit], [1, ideal_limit], 'k--', label="Ideal")

    ax.set_xlabel("# cores")
    ax.set_ylabel("speedup")
    ax.set_title("Strong Scaling (Amdahl's law)")
    ax.set_ylim(0, y_upper)  # ← LIMIT ADJUSTED HERE
    ax.legend()
    plt.tight_layout()
    plt.savefig("plots/strong_scaling.png")
    print("📈 Saved: plots/strong_scaling.png")


# === WEAK SCALING ===
def plot_weak_scaling():
    weak_df = pd.read_csv(output_weak)

    # Separate data
    mpi_weak = weak_df[weak_df["exec_type"] == "project_mpi"]
    omp_weak = weak_df[weak_df["exec_type"] == "project_omp"]

    # Compute speedup for strong scaling
    _, ax = plt.subplots()
    ax.plot(
        mpi_weak["procs/threads"], mpi_weak["time_sec"], label="MPI", color="green"
    )
    ax.fill_between(
        mpi_weak["procs/threads"],
        mpi_weak["time_sec"] * 0.95,
        mpi_weak["time_sec"] * 1.05,
        alpha=0.2,
        color="green",
    )

    ax.plot(
        omp_weak["procs/threads"], omp_weak["time_sec"], label="OpenMP", color="blue"
    )
    ax.fill_between(
        omp_weak["procs/threads"],
        omp_weak["time_sec"] * 0.95,
        omp_weak["time_sec"] * 1.05,
        alpha=0.2,
        color="blue",
    )

    ax.set_xlabel("# cores")
    ax.set_ylabel("time [s]")
    ax.set_title("Weak Scaling (Gustafson's law)")
    ax.legend()
    plt.tight_layout()
    plt.savefig("plots/weak_scaling.png")
    print("📈 Saved: weak_scaling.png")


# === RUN ===
plot_strong_scaling()
plot_weak_scaling()


# Load data
strong_df = pd.read_csv(output_strong)
weak_df = pd.read_csv(output_weak)

# Separate data
mpi_strong = strong_df[strong_df["exec_type"] == "project_mpi"]
mpi_weak = weak_df[weak_df["exec_type"] == "project_mpi"]
omp_strong = strong_df[strong_df["exec_type"] == "project_omp"]
omp_weak = weak_df[weak_df["exec_type"] == "project_omp"]

# Compute speedup for strong scaling
mpi_baseline = mpi_strong[mpi_strong["procs/threads"] == 1]["time_sec"].values[0]
omp_baseline = omp_strong[omp_strong["procs/threads"] == 1]["time_sec"].values[0]

mpi_strong = mpi_strong.copy()
omp_strong = omp_strong.copy()
mpi_strong["speedup"] = mpi_baseline / mpi_strong["time_sec"]
omp_strong["speedup"] = omp_baseline / omp_strong["time_sec"]

# Plot
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# --- Left: Strong scaling ---
# Compute the dynamic y-limit for strong scaling
max_speedup = max(
    mpi_strong["speedup"].max(),
    omp_strong["speedup"].max()
)

ideal_limit = mpi_strong["procs/threads"].max()  # in case we want to match ideal line
y_upper = max_speedup * 1.1  # give a bit of headroom

# --- Left: Strong scaling ---
axes[0].plot(mpi_strong["procs/threads"], mpi_strong["speedup"], label="MPI", color="green")
axes[0].fill_between(mpi_strong["procs/threads"], mpi_strong["speedup"]*0.95, mpi_strong["speedup"]*1.05, alpha=0.2, color="green")

axes[0].plot(omp_strong["procs/threads"], omp_strong["speedup"], label="OpenMP", color="blue")
axes[0].fill_between(omp_strong["procs/threads"], omp_strong["speedup"]*0.95, omp_strong["speedup"]*1.05, alpha=0.2, color="blue")

axes[0].plot([1, ideal_limit], [1, ideal_limit], 'k--', label="Ideal")

axes[0].set_xlabel("# cores")
axes[0].set_ylabel("speedup")
axes[0].set_title("Strong Scaling (Amdahl's law)")
axes[0].set_ylim(0, y_upper)  # ← LIMIT ADJUSTED HERE
axes[0].legend()


# --- Right: Weak scaling ---
axes[1].plot(
    mpi_weak["procs/threads"], mpi_weak["time_sec"], label="MPI", color="green"
)
axes[1].fill_between(
    mpi_weak["procs/threads"],
    mpi_weak["time_sec"] * 0.95,
    mpi_weak["time_sec"] * 1.05,
    alpha=0.2,
    color="green",
)

axes[1].plot(
    omp_weak["procs/threads"], omp_weak["time_sec"], label="OpenMP", color="blue"
)
axes[1].fill_between(
    omp_weak["procs/threads"],
    omp_weak["time_sec"] * 0.95,
    omp_weak["time_sec"] * 1.05,
    alpha=0.2,
    color="blue",
)

axes[1].set_xlabel("# cores")
axes[1].set_ylabel("time [s]")
axes[1].set_title("Weak Scaling (Gustafson's law)")
axes[1].legend()

# Final formatting
plt.tight_layout()
plt.figtext(
    0.5,
    -0.05,
    "Fig. 2. Left: strong scaling (Amdahl's law). Right: weak scaling (Gustafson's law). Both plots compare MPI and OpenMP performance on the OCCAM HPC center (24 cores).",
    wrap=True,
    horizontalalignment="center",
    fontsize=9,
)
plt.savefig("plots/comparison.png")


# === CLEAN + BUILD ===
# print("🛠️ Rewritte the report with the good images...")
# subprocess.run("make report", shell=True, check=True)