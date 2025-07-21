import argparse
from scipy.stats import truncnorm
import statistics

def parse_events(file_name) -> dict:
    events = {}
    with open(file_name, 'r') as file:
        try:
            num_events = int(file.readline().strip())
        except ValueError:
            raise ValueError("Error: The first line should specify an integer number of events")

        lines_read = 0
        for _ in range(num_events):
            line = file.readline().strip()
            attributes = line.split(":")
            event_name = attributes[0]
            event_type = attributes[1]
            min_value = float(attributes[2]) if attributes[2] else 0.0
            max_value = float(attributes[3]) if attributes[3] else 0.0
            if min_value >= max_value:
                raise ValueError("Error: min_value expected to be lower than max_value")
            weight = int(attributes[4]) if attributes[4] else 1
            if weight <= 0:
                raise ValueError("Error: Non-zero positive integer expected for weight")
            events[event_name] = {
                "type": event_type,
                "min": min_value,
                "max": max_value,
                "weight": weight
            }
            lines_read += 1

        if lines_read != num_events:
            raise ValueError(f"Expected {num_events} events, but found {lines_read} in the file")
        
    return events

def parse_stats(file_name) -> dict:
    stats = {}
    with open(file_name, 'r') as file:
        try:
            num_events = int(file.readline().strip())
        except ValueError:
            raise ValueError("Error: The first line should specify an integer number of events")

        lines_read = 0
        for _ in range(num_events):
            line = file.readline().strip()
            attributes = line.split(":")
            event_name = attributes[0]
            mean = float(attributes[1]) if attributes[1] else 0.0
            standard_deviation = float(attributes[2]) if attributes[2] else 0.0
            stats[event_name] = {
                "mean": mean,
                "standard_deviation": standard_deviation
            }
            lines_read += 1

        if lines_read != num_events:
            raise ValueError(f"Expected {num_events} events, but found {lines_read} in the file")
        
        return stats

def generate_event(event_type, min_value, max_value, mean, stddev) -> float:
    lower_bounds = (min_value - mean) / stddev
    upper_bounds = (max_value - mean) / stddev

    value = truncnorm.rvs(lower_bounds, upper_bounds, loc=mean, scale=stddev)

    if event_type == "D":
        value = int(value)
    elif event_type == "C":
        value = round(value, 2)
    else:
        raise ValueError(f"Error: Invalid event type {event_type}. Expected 'C' for continuous or 'D' for discrete")
    
    return value

def generate_events(events, stats, days) -> dict:
    logs = []
    for day in range(1, days + 1):
        daily_log = {}
        
        for event, attributes in events.items():
            event_name = event
            event_type = attributes["type"]
            min_value = attributes["min"]
            max_value = attributes["max"]

            mean = stats[event]["mean"]
            stddev = stats[event]["standard_deviation"]
            
            value = generate_event(event_type, min_value, max_value, mean, stddev)
            daily_log[event_name] = value

        logs.append(daily_log)
    return logs

def generate_logs_file(event_logs, file_name):
    counter = 0
    try:
        with open(file_name, "w") as f:
            counter = 0

            for log in event_logs:
                counter += 1
                f.write(f"Day:{counter}\n")
                for curr_event, curr_value in log.items():
                    f.write(f"{curr_event}:{curr_value}\n")
                f.write("\n")

    except FileNotFoundError:
        print("Error: Could not open logs.txt for writing. Please check the file path and try again.")
    except IOError:
        print("Error: An I/O error occurred while writing to logs.txt.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def accumulate_events(logs_file):
    event_data = {}
    day_counter = 0

    with open(logs_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith("Day"):
                day_counter += 1
            elif ":" in line:
                key, value = line.split(":")
                value = float(value)

                if key in event_data:
                    event_data[key].append(value)
                else:
                    event_data[key] = [value]

    event_data["Day"] = day_counter
    return event_data

def generate_baseline_file(accumulated_events):
    try:
        with open("baseline.txt", "w") as f:
            f.write("Total Statistics\n")
            f.write("===========\n")
            
            for key, values in accumulated_events.items():
                if key == "Day":
                    f.write(f"{key}:{values}\n")
                else:
                    values_str = ", ".join(map(str, values))
                    f.write(f"{key}: {values_str}\n")
                            
    except FileNotFoundError:
        print("Error: Could not open baseline.txt for writing. Please check the file path and try again.")
    except IOError:
        print("Error: An I/O error occurred while writing to baseline.txt")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def compute_statistics(baseline_file):
    # Dictionary to store event data across days
    event_values = {}

    try:
        # Read the data from the file, line by line
        with open(baseline_file, "r") as f:
            for line in f:
                line = line.strip()
                
                # Skip headers or empty lines
                if not line or line in ["Total Statistics", "==========="]:
                    continue

                # Split the line into key and values (values e.g.: 4, 2, 5, 2, 1)
                key, value = line.split(":")
                key = key.strip()
                
                if key != "Day":  # Exclude "Day" from the statistics
                    # Convert comma-separated values to a list of floats
                    values = [float(v.strip()) for v in value.split(",") if v.strip()]
                    
                    # Log missing data if values list is empty
                    if not values:
                        print(f"Warning: Missing data for event '{key}' in {baseline_file}.")
                    else:
                        event_values[key] = values

        # Calculate mean and standard deviation for each event and write output
        with open("baseline_statistics.txt", "w") as f_statistics:
            # Write the number of events at the top
            f_statistics.write(f"{len(event_values)}\n")

            for key, values in event_values.items():
                if values:
                    mean = round(statistics.mean(values), 2)
                    stddev = round(statistics.stdev(values), 2) if len(values) > 1 else 0.0
                    # Format the output as Event:mean:standard_deviation:
                    f_statistics.write(f"{key}:{mean}:{stddev}:\n")
                else:
                    # Log fallback if there is no data for a given event
                    f_statistics.write(f"{key}:Data missing:Data missing:\n")

    except FileNotFoundError:
        print("Error: Could not open data file. Please check the file path and try again.")
    except IOError:
        print("Error: An I/O error occurred while accessing the data file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def load_new_stats(stats_file):
    print("Loading new statistics...")
    return parse_stats(stats_file)

def generate_live_data(events, new_stats, days):
    print(f"Generating live data for {days} days...")
    return generate_events(events, new_stats, days)

def accumulate_live_events(live_data_logs):
    print(f"Accumulating live events...")
    return accumulate_events(live_data_logs)

def calculate_daily_anomaly_score(accumulated_events, original_stats, event_weights):
    daily_anomaly_scores = []

    num_days = accumulated_events["Day"]
    for day in range(num_days):
        anomaly_score = 0

        # Calculate anomaly score for each event on that day
        for event, values in accumulated_events.items():
            if event == "Day":
                continue

            # Get the day's value, baseline mean, and stddev
            daily_value = values[day]
            baseline_mean = original_stats[event]["mean"]
            baseline_stddev = original_stats[event]["standard_deviation"]
            weight = event_weights.get(event, 1)

            # Calculate the deviation (number of std deviations from mean)
            if baseline_stddev > 0:
                deviation = abs(daily_value - baseline_mean) / baseline_stddev
            else:
                deviation = 0  # If stddev is zero, deviation is zero

            # Add weighted deviation to the anomaly score
            anomaly_score += deviation * weight

        daily_anomaly_scores.append(round(anomaly_score, 2))

    return daily_anomaly_scores

def alert_engine(events, baseline_stats, event_weights):
    while True:
        # Step 1: Load New Stats File
        while True:
            stats_file = input("Enter the new stats file for live data analysis (or 'q' to quit): ")
            if stats_file.lower() == 'q':
                return

            try:
                # Attempt to load the new statistics file
                new_stats = load_new_stats(stats_file)
                break  # If successful, exit the loop
            except FileNotFoundError:
                print("Error: The specified file was not found. Please enter a valid file name.")
            except IOError:
                print("Error: An I/O error occurred while trying to read the file. Please try again.")
            except KeyboardInterrupt:
                print("Error: KeyboardInterrupt, closing program.")
                return
            except Exception as e:
                print(f"An unexpected error occurred: {e}")


        # Step 2: Get Number of Days
        while True:
            try:
                days = int(input("Enter the number of days for live data generation: "))
                break
            except ValueError:
                print("Error: Expected integer for number of days")
            except KeyboardInterrupt:
                print("Error: KeyboardInterrupt, closing program.")
                return

        # Step 3: Generate live data
        live_data_logs = generate_live_data(events, new_stats, days)
        generate_logs_file(live_data_logs, "live_logs.txt")
        accumulated_live = accumulate_live_events("live_logs.txt")

        print("")

        # Step 4: Calculate Anomaly Scores for each day
        print("Calculating anomaly scores for live data...")
        daily_anomaly_scores = calculate_daily_anomaly_score(accumulated_live, baseline_stats, event_weights)

        print("")

        # Step 5: Define threshold and determine alert status
        threshold = 2 * sum(event_weights.values())
        print("==========================================================================")
        print("Daily Reports")
        print(f"Anomaly Detection Threshold: {threshold}")
        print("==========================================================================")

        for day, anomaly_score in enumerate(daily_anomaly_scores, start=1):
            if anomaly_score >= threshold:
                print(f"Day {day}: ALERT - Anomaly Score = {anomaly_score}")
            else:
                print(f"Day {day}: OK - Anomaly Score = {anomaly_score}")
        print("==========================================================================")


def main(eventsFile, statsFile, days):
    days = int(days)
    logs_file = "logs.txt"
    baseline_file = "baseline.txt"

    print("==========================================================================")
    print("Initializing Events and Statistics...")
    events = parse_events(eventsFile)
    stats = parse_stats(statsFile)
    if len(events) != len(stats):
        print("Error: Inconsistent number between Events and Statistics.")
        return
    print("Initialization success!")
    print("==========================================================================")
    print("EVENTS DATA")
    print("==========================================================================")

    for event, attr in events.items():
        print(f"{event:<15}: {attr}")

    print("==========================================================================")
    print("STATISTICS DATA")
    print("==========================================================================")

    for stat, attr in stats.items():
        print(f"{stat:<15}: {attr}")

    print("==========================================================================")
    print("Activity Engine and the Logs")
    print("==========================================================================")

    print("Generating events...")
    event_logs = generate_events(events, stats, days)
    print(f"Generated {days} days of events!")

    print("")

    print("Generating Logs File...")
    generate_logs_file(event_logs, "logs.txt")
    print("Event logs written successfully to logs.txt!")

    print("")

    print("Accumulating daily totals...")
    accumulated_events = accumulate_events(logs_file)
    print("Calculations Complete!")

    print("==========================================================================")
    print("Analysis Engine")
    print("==========================================================================")

    print("Generating Data File...")
    generate_baseline_file(accumulated_events)
    print("Data successfully written to baseline.txt!")

    print("")

    print("Calculating statistics...")
    compute_statistics(baseline_file)
    print("Statistics successfully written to baseline_statistics.txt...")

    print("==========================================================================")
    print("Alert Engine")
    print("==========================================================================")
    
    # Obtain dictionary of event weights from Events.txt
    event_weights = {event: attributes["weight"] for event, attributes in events.items()}
    # Obtain statistics from baseline data
    baseline_stats = parse_stats("baseline_statistics.txt")

    alert_engine(events, baseline_stats, event_weights)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IDS CLI Application")
    parser.add_argument("eventsFile", type=str, help="Enter Events File Name")
    parser.add_argument("statsFile", type=str, help="Enter Stats File Name")
    parser.add_argument("days", type=str, help="Enter days")

    args = parser.parse_args()
    
    main(args.eventsFile, args.statsFile, args.days)
