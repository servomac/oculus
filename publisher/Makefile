build:
	docker build -t servomac/stats_poller .

push:
	docker push servomac/stats_poller

run:
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock --link redis:db --name oculus_poller servomac/stats_poller	

bash:
	docker exec -it oculus_poller /bin/bash

rm:
	docker rm oculus_poller

stop:
	docker stop oculus_poller

start:
	docker start oculus_poller
