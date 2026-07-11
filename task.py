# regex for log parsing
# sys for managing input file and error
# counter for finding 10 top end points
import re
import sys
from collections import Counter

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
    print("\n--- Top 10 endpoints ---")
    for i, (endpoint, count) in enumerate(top_endpoints, 1):
        print(f"{i:2}. {endpoint[:40]:40} {count:8,} requests")
    print("="*50 + "\n")


if __name__ == "__main__":
    main()