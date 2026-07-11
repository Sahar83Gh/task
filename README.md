# Log Analyzer CLI

A lightweight command‑line tool that reads a log in **Combined Log Format** and extracts useful statistics without loading the entire file into memory.
---

## How to Run

### Requirements
- Python 3.8 or higher
- No external dependencies (only the Python standard library is used)

### Command
```bash
python task.py <path-to-log-file>
```

## Standard Libraries
- re (regex) for log parsing
- sys for managing input file and error
- counter for finding 10 top end points
- datetime for extracting hour


## Features
- Line‑by‑line processing – works with huge log files without memory issues.
- Malformed or incomplete lines are counted and skipped, never causing a crash.
- Key metrics:
 - Total valid requests
 - Number of malformed lines
 - Unique IP addresses
 - Error rate (percentage of 4xx and 5xx responses)
 - Top 10 endpoints – the most frequently requested paths.

## Important Design Decisions
1. Standard Library Only
I used only Python’s built‑in modules (re, sys, collections, datetime) so that the tool runs anywhere without installing extra packages.

2. Streaming (Line‑by‑Line)
The file is iterated directly with for line in input:. This avoids reading the whole file into memory, which is essential for large production logs.

3. Custom Regex Parser
A hand‑crafted regular expression extracts each field. This gives full control over the parsing logic and lets me handle edge cases precisely, while external log‑parsing libraries are prohibited by the task.

4. Error Recovery
Whenever a line doesn’t match the expected format, it is counted as bad_lines and skipped. The program continues processing the rest of the file without interruption.

## The Problem
Real‑world log files sometimes contain lines that match the overall regex pattern, but the timestamp field is malformed (e.g., wrong date format, missing timezone, or extra characters). When I tried to convert such a timestamp with datetime.strptime(), it raised a ValueError and crashed the program.

### The Solution
I isolated the timestamp conversion into a separate function extract_hour(timestamp_str). Inside it, I wrapped the strptime call in a try‑except block:

- If the conversion succeeds, the function returns the hour.
- If it fails, the function catches the exception and returns None.

In the main loop, I check the return value:

- If hour is not None, I update the hourly statistics.
- If hour is None, I treat that line as bad (decrement total_requests and increment bad_lines).

## Sample Output

```bash
PS C:\Users\Lenovo\Desktop> python task.py access.log

==================================================
LOG ANALYSIS REPORT
==================================================
Total valid requests: 495,044
Malformed lines: 4,956
Unique IP addresses: 4,001
Error rate (4xx/5xx): 10.32%

--- Top 10 endpoints ---
 1. /                                         146,302 requests
 2. /products                                  87,685 requests
 3. /api/search                                48,842 requests
 4. /cart                                      34,181 requests
 5. /login                                     31,658 requests
 6. /static/app.js                             29,249 requests
 7. /static/style.css                          24,299 requests
 8. /health                                    14,549 requests
 9. /api/checkout                               9,807 requests
10. /products/9820                                 20 requests
00:00 - 01:00  51,026  ▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨
01:00 - 02:00  50,971  ▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨
02:00 - 03:00  50,975  ▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨
03:00 - 04:00  50,705  ▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨
04:00 - 05:00  50,847  ▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨
05:00 - 06:00  51,002  ▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨
06:00 - 07:00  50,809  ▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨
07:00 - 08:00  50,844  ▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨
08:00 - 09:00  50,912  ▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨▨
09:00 - 10:00  36,953  ▨▨▨▨▨▨▨▨▨▨▨▨▨▨
10:00 - 11:00       0
11:00 - 12:00       0
12:00 - 13:00       0
13:00 - 14:00       0
14:00 - 15:00       0
15:00 - 16:00       0
16:00 - 17:00       0
17:00 - 18:00       0
18:00 - 19:00       0
19:00 - 20:00       0
20:00 - 21:00       0
21:00 - 22:00       0
22:00 - 23:00       0
23:00 - 24:00       0
==================================================
```
