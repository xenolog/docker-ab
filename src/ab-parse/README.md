# ab2json

`ab2json` is a tool for parsing output of the `ab` (Apache HTTP server
benchmarking) tool. It gets the results from stdin, parses it, converts it
into a JSON structure and writes it to stdout. It does not format the output
for pretty-printing. It parses error and warning messages.

## Parsing of error and warning messages

There are three categories of such messages are distinguished:

Error messages like the following:
```
ERROR: The median and mean for the initial connection time are more than twice the standard
       deviation apart. These results are NOT reliable.
```
are saved to `Error` dictionary.

Error messages like the following:
```
apr_pollset_poll: The timeout specified has expired (70007)
```
are saved to `Fatal` list. It was called "Fatal" as such errors interrupt the
testing by default. These (and only these) messages go to `stderr` so you need
to capture `stderr` to have them processed.

Warning messages like the following:
```
WARNING: The median and mean for the total time are not within a normal deviation
        These results are probably not that reliable.
```
are saved to `Warning` dictionary.

## Usage examples

To get non-formatted JSON output:

```bash
$ ab -n 100 -c 10 http://ipinfo.io/ 2>&1 | python ab2json.py > result.json
```

To get formatted JSON output for pretty-printing:

```bash
ab -n 100 -c 10 http://ipinfo.io/ 2>&1 | python ab2json.py | python -m json.tool > result.json
```

Output example (formatted):

```json
{
    "Complete requests": {
        "value": "100"
    },
    "Concurrency Level": {
        "value": "10"
    },
    "Connection Times (ms)": {
        "Connect": {
            "avg": "23",
            "max": "28",
            "mean": "24",
            "min": "23",
            "sd": "1.2"
        },
        "Processing": {
            "avg": "170",
            "max": "737",
            "mean": "185",
            "min": "169",
            "sd": "68.4"
        },
        "Total": {
            "avg": "194",
            "max": "764",
            "mean": "209",
            "min": "192",
            "sd": "68.6"
        },
        "Waiting": {
            "avg": "170",
            "max": "737",
            "mean": "184",
            "min": "169",
            "sd": "67.2"
        }
    },
    "Document Length": {
        "units": "bytes",
        "value": "40"
    },
    "Document Path": {
        "value": "/"
    },
    "Error": {},
    "Failed requests": {
        "value": "0"
    },
    "Fatal": [],
    "HTML transferred": {
        "units": "bytes",
        "value": "4000"
    },
    "Non-2xx responses": {
        "value": "100"
    },
    "Percentile vs Time (ms)": {
        "100": "764",
        "50": "194",
        "66": "196",
        "75": "197",
        "80": "199",
        "90": "208",
        "95": "271",
        "98": "519",
        "99": "764"
    },
    "Requests per second": {
        "note": "(mean)",
        "units": "#/sec",
        "value": "46.05"
    },
    "Server Hostname": {
        "value": "ipinfo.io"
    },
    "Server Port": {
        "value": "80"
    },
    "Server Software": {
        "value": "nginx"
    },
    "Time per request": {
        "note": "(mean, across all concurrent requests)",
        "units": "ms",
        "value": "21.716"
    },
    "Time taken for tests": {
        "units": "seconds",
        "value": "2.172"
    },
    "Total transferred": {
        "units": "bytes",
        "value": "34938"
    },
    "Transfer rate": {
        "note": "received",
        "units": "Kbytes/sec",
        "value": "15.71"
    },
    "Warning": {
        "Response code not 2xx (302)": 100
    }
}
```

'--generic' CLI option can be specified to get JSON in generic format.
Generic format is the one defined for storing test results in ElasticSearch.

Example of JSON in generic format:

```json
{
    "result_details": {
        "Complete requests": "20",
        "Failed requests": "0",
        "HTML transferred, bytes": "800",
        "Non-2xx responses": "20",
        "Requests per second, #/sec": "50.76",
        "Response code not 2xx (302)": 20,
        "TC_Connect_avg, ms": "23",
        "TC_Connect_max, ms": "24",
        "TC_Connect_sd, ms": "0.1",
        "TC_Processing_avg, ms": "167",
        "TC_Processing_max, ms": "178",
        "TC_Processing_sd, ms": "3.0",
        "TC_Total_avg, ms": "190",
        "TC_Total_max, ms": "201",
        "TC_Total_sd, ms": "2.9",
        "TC_Waiting_avg, ms": "166",
        "TC_Waiting_max, ms": "178",
        "TC_Waiting_sd, ms": "2.9",
        "Time per request, ms": "19.702",
        "Time taken for tests, seconds": "0.394",
        "Total transferred, bytes": "7147",
        "Transfer rate, Kbytes/sec": "17.71"
    },
    "test_errors": {},
    "test_parameters": {
        "Server Software": "nginx",
        "Server Hostname": "ipinfo.io",
        "Server Port": "80",
        "Document Path": "/",
        "Document Length, bytes": "40",
        "Concurrency Level": "10"
    }
}
```

