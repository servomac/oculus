
###########
# acadock #
###########

API_URL = 'http://127.0.0.1:4244'
container_id = '396e7635c892'

##########
# docker #
##########

DOCKER_BASE_URL = 'unix://var/run/docker.sock'

#########
# redis #
#########

REDIS_HOST='localhost'
REDIS_PORT=6379
REDIS_DB=8

REDIS_KEY = "{timestamp}:{container_id}:{resource}"
REDIS_KEY_TIMESTAMP='%Y%m%d%H%M'
REDIS_EXPIRE_TIME=3600              # expire time in seconds
