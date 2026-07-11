# regex for log parsing
# sys for managing input file and error
# counter for finding 10 top end points
# datetime for extracting hour
import re
import sys
from collections import Counter
from datetime import datetime

# Regular expression for log format
# Example line:
# 203.0.113.42 - - [01/Jun/2026:09:14:22 +0000] "GET /products/1877 HTTP/1.1" 200 5324 "-" "Mozilla/5.0 ..."

# ?P<name> is for group matching
# r'...' means raw string 
# ^ means it must start with that and $ means must end with that
# \d{1,3} -> digit (at least one digit and at most 3 digits) 
# \S -> except space 
# ?: non capturing group
# [^"] except "

LOG_PATTERN = re.compile(
    r'^(?P<ip>\d{1,3}(?:\.\d{1,3}){3}) - - \[(?P<timestamp>[^\]]+)\] '
    r'"(?P<method>[A-Z]+) (?P<path>\S+) HTTP/(?P<protocol>[^"]+)" '
    r'(?P<status>\d{3}) (?P<bytes>\d+) '
    r'"(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"$'
)

def parse_line(line):
    """
    Parse a single log line using the regex pattern.
    Returns a dict with fields if the line matches, otherwise None.
    """
    # remove additional spaces and \n
    line = line.strip()
    if not line:
        return None
    match = LOG_PATTERN.match(line)
    if not match:
        return None
    # convert status code and bytes to int
    data = match.groupdict()
    data['status'] = int(data['status'])
    data['bytes'] = int(data['bytes'])

    return data

def extract_hour(timestamp_str):
    """
    Extract the hour (0-23) from the timestamp string.
    Timestamp format: [01/Jun/2026:09:14:22 +0000]
    Returns hour as integer, or None if parsing fails.
    """
    try:
        # split timestamp and parse the date/time part (we don't need timezone part)
        dt_part = timestamp_str.split()[0]  # "01/Jun/2026:09:14:22"
        # datetime.strptime for parsing
        # %d day zero-padded
        # %b abbreviated month name
        # %Y year with century
        # %H hour (24-hour clock) zero-padded
        # %M minute zero-padded
        # %S second zero-padded
        dt = datetime.strptime(dt_part, "%d/%b/%Y:%H:%M:%S")
        return dt.hour
    except Exception:
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python task.py <logfile>")
        sys.exit(1)

    logfile = sys.argv[1]

    # Statistics (we use set for unique ips)
    total_requests = 0
    bad_lines = 0
    unique_ips = set()
    endpoint_counter = Counter()
    status_codes = []
    hourly_counter = Counter()

    try:
        with open(logfile, 'r', encoding='utf-8') as input:
            for line in input:
                parsed = parse_line(line)
                # count not matched lines
                if parsed is None:
                    bad_lines += 1
                    continue

                # Extract fields
                ip = parsed['ip']
                path = parsed['path']
                status = parsed['status']
                timestamp = parsed['timestamp']

                # Update statistics
                total_requests += 1
                unique_ips.add(ip)
                endpoint_counter[path] += 1
                status_codes.append(status)

                # Hourly distribution
                hour = extract_hour(timestamp)
                if hour is not None:
                    hourly_counter[hour] += 1
                else:
                    # If timestamp is invalid, treat this line as bad
                    total_requests -= 1
                    bad_lines += 1

    except FileNotFoundError:
        print(f"Error: File '{logfile}' not found.", file=sys.stderr)
        sys.exit(1)

    # calculate error rate (4xx and 5xx)
    error_count = sum(1 for s in status_codes if s >= 400)
    if total_requests > 0:
        error_rate = (error_count / total_requests * 100)  
    else: 
        error_rate = 0.0

    # Top 10 endpoints
    top_endpoints = endpoint_counter.most_common(10)

    # Print results
    print("\n" + "="*50)
    print("LOG ANALYSIS REPORT")
    print("="*50)
    print(f"Total valid requests: {total_requests:,}")
    print(f"Malformed lines: {bad_lines:,}")
    print(f"Unique IP addresses: {len(unique_ips):,}")
    print(f"Error rate (4xx/5xx): {error_rate:.2f}%")
    # {count:8,} means that print count in 8 characters and with thousands separator
    print("\n--- Top 10 endpoints ---")
    for i, (endpoint, count) in enumerate(top_endpoints, 1):
        print(f"{i:2}. {endpoint[:40]:40} {count:8,} requests")
    # Display a simple histogram
    if hourly_counter:
        max_count = max(hourly_counter.values()) if hourly_counter else 1
        for hour in range(24):
            # count default zero
            count = hourly_counter.get(hour, 0)
            bar_len = int(20 * count / max_count)
            bar = '▨' * bar_len
            print(f"{hour:02}:00 - {hour+1:02}:00  {count:6,}  {bar}")
    else:
        print("No hourly data available.")
    print("="*50 + "\n")


if __name__ == "__main__":
    main()