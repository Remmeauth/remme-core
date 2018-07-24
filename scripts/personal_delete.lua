wrk.method = "DELETE"
wrk.body   = string.format("{\"name\": \"%s\"}", os.time(os.date("!*t")))
wrk.headers["Content-Type"] = "application/json"