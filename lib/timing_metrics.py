import time
from collections import defaultdict

class TimingMetrics:
    def __init__(self):
        self.data = defaultdict(lambda: defaultdict(float))  # filename -> phase -> duration
        self.phase_data = defaultdict(list)  # phase -> [durations]
        self.current_starts = {}  # (filename, phase) -> start_time

    def start(self, filename, phase):
        key = (filename, phase)
        self.current_starts[key] = time.time()

    def stop(self, filename, phase):
        key = (filename, phase)
        if key in self.current_starts:
            duration = time.time() - self.current_starts[key]
            self.data[filename][phase] = duration
            self.phase_data[phase].append(duration)
            print(f"{filename} completed {phase} in {duration:.2f}s")
            del self.current_starts[key]

    def print_stats(self, filename=None, phase=None):
        if filename and phase:
            # Print specific phase for specific file
            if filename in self.data and phase in self.data[filename]:
                print(f"{filename} {phase}: {self.data[filename][phase]:.2f}s")
        elif filename:
            # Print all phases for file + total
            if filename in self.data:
                total = 0
                for ph, dur in self.data[filename].items():
                    print(f"{filename} {ph}: {dur:.2f}s")
                    total += dur
                print(f"{filename} total: {total:.2f}s")
        elif phase:
            # Print min/max/avg for phase
            if phase in self.phase_data and self.phase_data[phase]:
                times = self.phase_data[phase]
                min_t = min(times)
                max_t = max(times)
                avg_t = sum(times) / len(times)
                print(f"Phase {phase}: min={min_t:.2f}s, max={max_t:.2f}s, avg={avg_t:.2f}s")
        else:
            # Print overall stats in table format
            print("\n=== Overall Statistics ===")
            
            # Phase statistics table
            if self.phase_data:
                print("Phase Statistics:")
                print("Phase Name".ljust(20) + "| Min".ljust(10) + "| Max".ljust(10) + "| Avg".ljust(10))
                print("-" * 55)
                for ph in sorted(self.phase_data.keys()):
                    times = self.phase_data[ph]
                    if times:
                        min_t = min(times)
                        max_t = max(times)
                        avg_t = sum(times) / len(times)
                        print(f"{ph:<20}| {min_t:>8.2f}s | {max_t:>8.2f}s | {avg_t:>8.2f}s")
            
            # File statistics
            if self.data:
                file_totals = []
                for fname, phases in self.data.items():
                    total = sum(phases.values())
                    file_totals.append(total)
                num_files = len(file_totals)
                if file_totals:
                    min_t = min(file_totals)
                    max_t = max(file_totals)
                    avg_t = sum(file_totals) / len(file_totals)
                    print(f"\nProcessed {num_files} file{'s' if num_files != 1 else ''}: min={min_t:.2f}s, max={max_t:.2f}s, avg={avg_t:.2f}s")