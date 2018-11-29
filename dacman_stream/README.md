# Dacman-Stream Overview

Before we start our stream process, we have to prepare the environment correctly.

Note: We are going to use Docker through out our guide.

## Getting Started
### 1. Install [Redis](https://redis.io/topics/quickstart) or [Redis-Container](https://docs.docker.com/samples/library/redis/) on a server.
We are going to push our comparison data blocks and our comparison tasks to this Redis server. If you are going to user Docker to initiate a Redis container, don't forget to expose and link the right ports so you can connect to it from outside the server.

```
# dacman-redis is just a name, you can change it to however you want.
# redis is the public docker image we are going to use.

$ docker run --name dacman-redis -d redis
```

### 2. Build our Workers docker image.
We'll use the ```Dockerfile``` in ```mpi_worker_docker``` to build the workers docker image. All the files needed to run the image correctly, like ```config.py``` for example, are inside that directory.

```
# workers_manager is the name of the image we chose.
# Note: Docker will automatically look for Dockerfile
# in the mpi_worker_docker directory.

$ docker build -t workers_manager mpi_worker_docker/
```

### 3. Initiate our Workers Container.
Before we start running our container, let's not forget to link it to our Redis server. That way, our container will be able to connect to Redis directly.

Note: By linking, we mean to add the right IP address with the right alias to ```/etc/hosts```. The alias has to be ```redis``` in our case, as ```mpi_worker_docker/config.py``` already sets ```HOST="redis"```.

#### To link to Redis 
```
# If you have access on the redis container and are able to see it
# via the 'docker ps' command.

$ docker run --name workers_container --link dacman-redis:redis -d workers_manager
```
or
```
# To manually add to /etc/hosts, use the '--add-host' command.
# Make sure to add the correct IP address.

$ docker run -it --name workers_container --add-host redis:111.111.1.1 workers_manager
```

## Streaming

Now we are ready to start the streaming process.

### 1. Have the right configurations.
Set ```settings.py``` correctly. Make sure to set ```Host```, ```PORT``` and ```DATABASE``` to the right Redis settings.

```
###### Start of Redis Config Variables ######
HOST="[REDIS_SERVER]"
PORT="6379"
DATABASE=0

...
```

### 2. Start pushing data and tasks.
```
# This command is tested on an ALS use case with the
# 20160904_043848_CSPbI3_140DEG1_.h5 dataset

$ python dacman_stream.py <source_dir> <dataset(h5_file)> <output_dir>
```
