import re
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colormaps

# Define the log file
log_file = "wrk_test_results.log"

# Initialize data storage
threads = []
connections = []
latencies = []
throughputs = []

# Parse the log file
with open(log_file, "r") as file:
    for line in file:
        # Extract threads and connections
        if "Testing with" in line:
            match = re.search(r"Testing with (\d+) threads and (\d+) connections", line)
            if match:
                t, c = int(match.group(1)), int(match.group(2))
                threads.append(t)
                connections.append(c)
        # Extract average latency
        elif "Latency" in line:
            match = re.search(r"Latency\s+([\d.]+)\s*ms", line)
            if match:
                latencies.append(float(match.group(1)))
        # Extract throughput
        elif "Requests/sec" in line:
            match = re.search(r"Requests/sec:\s+([\d.]+)", line)
            if match:
                throughputs.append(float(match.group(1)))

# Debugging: Print lengths of parsed data
print("Parsed Data Lengths:")
print(f"Threads: {len(threads)}")
print(f"Connections: {len(connections)}")
print(f"Latencies: {len(latencies)}")
print(f"Throughputs: {len(throughputs)}")

# Ensure consistent lengths
min_length = min(len(threads), len(connections), len(latencies), len(throughputs))
if len(threads) != min_length:
    print("Warning: Trimming threads data to match the shortest list.")
    threads = threads[:min_length]
if len(connections) != min_length:
    print("Warning: Trimming connections data to match the shortest list.")
    connections = connections[:min_length]
if len(latencies) != min_length:
    print("Warning: Trimming latencies data to match the shortest list.")
    latencies = latencies[:min_length]
if len(throughputs) != min_length:
    print("Warning: Trimming throughputs data to match the shortest list.")
    throughputs = throughputs[:min_length]

# Convert data to numpy arrays for easier manipulation
threads = np.array(threads)
connections = np.array(connections)
latencies = np.array(latencies)
throughputs = np.array(throughputs)

# Get a colormap with enough distinct colors
cmap = colormaps.get_cmap("tab10")

# Plot Latency vs Connections
plt.figure(figsize=(12, 6))
unique_threads = np.unique(threads)

for i, thread in enumerate(unique_threads):
    mask = threads == thread
    sorted_indices = np.argsort(connections[mask])
    plt.plot(
        connections[mask][sorted_indices],
        latencies[mask][sorted_indices],
        color=cmap(i % 10),
        marker="o",
        linestyle="-",
        label=f"Thread {thread}",
    )
    avg_latency = np.mean(latencies[mask])
    plt.axhline(
        y=avg_latency, color=cmap(i % 10), linestyle="--", alpha=0.7, 
        label=f"Avg Latency (Thread {thread})"
    )

plt.title("Latency vs Connections")
plt.xlabel("Connections")
plt.ylabel("Latency (ms)")
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()
plt.show()

# Plot Throughput vs Connections
plt.figure(figsize=(12, 6))

for i, thread in enumerate(unique_threads):
    mask = threads == thread
    sorted_indices = np.argsort(connections[mask])
    plt.plot(
        connections[mask][sorted_indices],
        throughputs[mask][sorted_indices],
        color=cmap(i % 10),
        marker="o",
        linestyle="-",
        label=f"Thread {thread}",
    )
    avg_throughput = np.mean(throughputs[mask])
    plt.axhline(
        y=avg_throughput, color=cmap(i % 10), linestyle="--", alpha=0.7, 
        label=f"Avg Throughput (Thread {thread})"
    )

plt.title("Throughput vs Connections")
plt.xlabel("Connections")
plt.ylabel("Requests/sec")
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()
plt.show()