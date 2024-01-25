# Process logs into a dict (for key/value pairs) and a list (for regular messages)
import os


def process_logs(logs):
    logs_dict = {}
    log_statements = []
    for log in logs:
        log_data = log[33:].strip().split(" = ")  # Ignore timestamp info at start of log entry
        # Handle regular log message (DB connection, training start, error statements)
        if len(log_data) == 1:
            log_statements.append(log_data)
        else:  # For logs with format 'key = value', put log values into dict
            logs_dict[log_data[0]] = log_data[1]
    return logs_dict, log_statements


# Find log file for a user's particular run with a particular dataset
def get_log_file(path, user_id, dataset, run):
    # List index mappings (only for log files)
    file_type = 0
    dataset_found = 1
    time = 3
    user = 4

    logs_found = {}
    for root, directories, files in os.walk(path):
        for filename in files:
            name_data = filename.split("_")
            if name_data[file_type] == 'log' and name_data[dataset_found] == dataset\
                    and name_data[user] == user_id:
                logs_found[int(name_data[time])] = filename

    if logs_found:
        sorted_logs = dict(sorted(logs_found.items()))
        found_log = sorted_logs[list(sorted_logs)[run-1]]
        return os.path.join(root, found_log)
