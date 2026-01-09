# Start ci container
```
docker container create --name ci-mtml-py --env MTHREADS_VISIBLE_DEVICES=all --env MTHREADS_DRIVER_CAPABILITIES=all  -v $PWD:/app/test -it  registry.cn-hangzhou.aliyuncs.com/fishingfly/mthreads-ml-py-ci:latest bash
```