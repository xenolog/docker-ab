# ab-to-json

`ab-to-json` is a tool for parsing output of the `ab` (Apache HTTP server
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
$ ab -n 100 -c 10 http://ipinfo.io/ 2>&1 | python ab-to-json.py > result.json
```

To get formatted JSON output for pretty-printing:

```bash
ab -n 100 -c 10 http://ipinfo.io/ 2>&1 | python ab-to-json.py | python -m json.tool > result.json
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
```
{
    "result_details": [
        {
            "name": "Time taken for tests, seconds",
            "value": "2.428"
        },
        {
            "name": "Complete requests",
            "value": "100"
        },
        {
            "name": "Failed requests",
            "value": "0"
        },
        {
            "name": "Non-2xx responses",
            "value": "100"
        },
        {
            "name": "Total transferred, bytes",
            "value": "34933"
        },
        {
            "name": "HTML transferred, bytes",
            "value": "4000"
        },
        {
            "name": "Time per request, ms",
            "value": "24.278"
        },
        {
            "name": "Requests per second, #/sec",
            "value": "41.19"
        },
        {
            "name": "Transfer rate, Kbytes/sec",
            "value": "14.05"
        }
    ],
    "test_errors": [],
    "test_parameters": [
        {
            "name": "Server Software",
            "value": "nginx"
            },
        {
            "name": "Server Hostname",
            "value": "ipinfo.io"
        },
        {
            "name": "Server Port",
            "value": "80"
        },
        {
            "name": "Document Path",
            "value": "/"
        },
        {
            "name": "Document Length, bytes",
            "value": "40"
        },
        {
            "name": "Concurrency Level",
            "value": "10"
        }
    ]
}
```

