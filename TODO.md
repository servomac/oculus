TODO List
---------

> Still not a real project; you can open github issues, but there no exists a team working on it, just a pet project (by now). This list is more a mixture of whishlist and pointers to damn bad code or poor architectural solutions introduced while prototyping.

1. to return the last hour of data, a hardcoded '''for minutes in range(60)''' is placed at run.py. This must mean a barenuckle punch in the face for me. World is unfair. Solution: a granularity selector, time picker.
2. How to deal with data not introduced in the backend? (None values returned by redis; by the moment are just not returned by the view using a value != None..)
3. the javascript in container.js must be in a external file. How to handle the jinja templating? Also, my JS sucks. How to avoid the concats? => Solution: Use 3c.js capacity to handle json files. http://c3js.org/samples/data_json.html
4. redis connection pool instead of opening/closing connections
5. Added a /containers/ view listing currently running containers. This acoplates acadock front with docker-py for an specific DOCKER_BASE_URL. (a) rethink the architecture (b) allow to configure more that just one DOCKER_BASE_URL (c not-so-related) add auth for the docker api
6. CPU is not being returned by acadock. The Network throughtput also shows errors (negative values).
7. Better integration of errors in the overview template. A panel inside the grid is just horrible. How to present the error messages?
