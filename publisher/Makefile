build:
	docker build -t oculus/publisher .


run:
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock --link redis:db --name oculus_publisher oculus/publisher	

rm:
	docker rm oculus_publisher

stop:
	docker stop oculus_publisher

start:
	docker start oculus_publisher
