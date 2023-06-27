import logging

from rest_framework import serializers

from base.serializer import ICBaseModelSerializer, ICBaseSerializer
from dockers.models.main import DockerContainerMode


class DockerContainerModelSerializer(ICBaseModelSerializer):
    class Meta:
        model = DockerContainerMode
        fields = "__all__"


class DockerStatsSerializer(ICBaseSerializer):
    id = serializers.CharField(help_text="container id")
    name = serializers.CharField(help_text="container name")
    read = serializers.DateTimeField(help_text="read time")
    preread = serializers.DateTimeField(help_text="preread time")
    num_procs = serializers.IntegerField(help_text="num procs")
    pids_stats = serializers.DictField(help_text="pids stats")
    cpu_stats = serializers.DictField(help_text="cpu stats")
    precpu_stats = serializers.DictField(help_text="precpu stats")
    memory_stats = serializers.DictField(help_text="memory stats")
    blkio_stats = serializers.DictField(help_text="blkio stats")
    storage_stats = serializers.DictField(help_text="storage stats")
    networks = serializers.DictField(help_text="networks")


class DockerContainerRestartPolicySerializer(ICBaseSerializer):
    name = serializers.CharField(help_text="restart policy name")
    maximum_retry_count = serializers.IntegerField(help_text="maximum retry count")


class DockerInpectSerializer(ICBaseSerializer):
    """{
        "id": "9505f78242a87e69415e506558a4274aaa8a53c1e0550d9d83bb644ad2f33525",
        "created": "2023-05-03T12:25:03.392136607Z",
        "path": "/bin/sh",
        "args": [
            "-c",
            "subconverter"
        ],
        "state": {
            "status": "running",
            "running": true,
            "paused": false,
            "restarting": false,
            "oOMKilled": false,
            "dead": false,
            "pid": 2516486,
            "exitCode": 0,
            "error": "",
            "startedAt": "2023-06-01T03:00:21.831596677Z",
            "finishedAt": "2023-06-01T03:00:20.670337057Z"
        },
        "image": "sha256:4a48bbff469bec8061d57ce87cd0e7d65adf36748cb28151fa5f0fc9e8a8305d",
        "resolvConfPath": "/var/lib/docker/containers/9505f78242a87e69415e506558a4274aaa8a53c1e0550d9d83bb644ad2f33525/resolv.conf",
        "hostnamePath": "/var/lib/docker/containers/9505f78242a87e69415e506558a4274aaa8a53c1e0550d9d83bb644ad2f33525/hostname",
        "hostsPath": "/var/lib/docker/containers/9505f78242a87e69415e506558a4274aaa8a53c1e0550d9d83bb644ad2f33525/hosts",
        "logPath": "/var/lib/docker/containers/9505f78242a87e69415e506558a4274aaa8a53c1e0550d9d83bb644ad2f33525/9505f78242a87e69415e506558a4274aaa8a53c1e0550d9d83bb644ad2f33525-json.log",
        "name": "/charming_cartwright",
        "restartCount": 0,
        "driver": "overlay2",
        "platform": "linux",
        "mountLabel": "",
        "processLabel": "",
        "appArmorProfile": "docker-default",
        "execIDs": null,
        "hostConfig": {
            "binds": null,
            "containerIDFile": "",
            "logConfig": {
                "type": "json-file",
                "config": {}
            },
            "networkMode": "default",
            "portBindings": {
                "25500/tcp": [
                    {
                        "hostIp": "",
                        "hostPort": "25500"
                    }
                ]
            },
            "restartPolicy": {
                "name": "always",
                "maximumRetryCount": 0
            },
            "autoRemove": false,
            "volumeDriver": "",
            "volumesFrom": null,
            "consoleSize": [
                30,
                120
            ],
            "capAdd": null,
            "capDrop": null,
            "cgroupnsMode": "private",
            "dns": [],
            "dnsOptions": [],
            "dnsSearch": [],
            "extraHosts": null,
            "groupAdd": null,
            "ipcMode": "private",
            "cgroup": "",
            "links": null,
            "oomScoreAdj": 0,
            "pidMode": "",
            "privileged": false,
            "publishAllPorts": false,
            "readonlyRootfs": false,
            "securityOpt": null,
            "uTSMode": "",
            "usernsMode": "",
            "shmSize": 67108864,
            "runtime": "runc",
            "isolation": "",
            "cpuShares": 0,
            "memory": 0,
            "nanoCpus": 0,
            "cgroupParent": "",
            "blkioWeight": 0,
            "blkioWeightDevice": [],
            "blkioDeviceReadBps": [],
            "blkioDeviceWriteBps": [],
            "blkioDeviceReadIOps": [],
            "blkioDeviceWriteIOps": [],
            "cpuPeriod": 0,
            "cpuQuota": 0,
            "cpuRealtimePeriod": 0,
            "cpuRealtimeRuntime": 0,
            "cpusetCpus": "",
            "cpusetMems": "",
            "devices": [],
            "deviceCgroupRules": null,
            "deviceRequests": null,
            "memoryReservation": 0,
            "memorySwap": 0,
            "memorySwappiness": null,
            "oomKillDisable": null,
            "pidsLimit": null,
            "ulimits": null,
            "cpuCount": 0,
            "cpuPercent": 0,
            "iOMaximumIOps": 0,
            "iOMaximumBandwidth": 0,
            "maskedPaths": [
                "/proc/asound",
                "/proc/acpi",
                "/proc/kcore",
                "/proc/keys",
                "/proc/latency_stats",
                "/proc/timer_list",
                "/proc/timer_stats",
                "/proc/sched_debug",
                "/proc/scsi",
                "/sys/firmware"
            ],
            "readonlyPaths": [
                "/proc/bus",
                "/proc/fs",
                "/proc/irq",
                "/proc/sys",
                "/proc/sysrq-trigger"
            ]
        },
        "graphDriver": {
            "data": {
                "lowerDir": "/var/lib/docker/overlay2/f3f2de9a14e24a1e84d21f87610e7ce4af75597b02042ca2c03d0532c63479f4-init/diff:/var/lib/docker/overlay2/c78322b125a98df7916ef7aa85928eb6a901e2d0eb3922c386960fc07f5d3dbe/diff:/var/lib/docker/overlay2/fdf6f8e2abc4df8487c23c5439b7064c0526df443892a8352bcda49bdb1d0c87/diff:/var/lib/docker/overlay2/4b1756009dc5d9ca5a4284d8457ffe9dbdb0609eeadf74fc2b2244e16ec65fcf/diff",
                "mergedDir": "/var/lib/docker/overlay2/f3f2de9a14e24a1e84d21f87610e7ce4af75597b02042ca2c03d0532c63479f4/merged",
                "upperDir": "/var/lib/docker/overlay2/f3f2de9a14e24a1e84d21f87610e7ce4af75597b02042ca2c03d0532c63479f4/diff",
                "workDir": "/var/lib/docker/overlay2/f3f2de9a14e24a1e84d21f87610e7ce4af75597b02042ca2c03d0532c63479f4/work"
            },
            "name": "overlay2"
        },
        "mounts": [],
        "config": {
            "hostname": "9505f78242a8",
            "domainname": "",
            "user": "",
            "attachStdin": false,
            "attachStdout": false,
            "attachStderr": false,
            "exposedPorts": {
                "25500/tcp": {}
            },
            "tty": false,
            "openStdin": false,
            "stdinOnce": false,
            "env": [
                "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
            ],
            "cmd": [
                "/bin/sh",
                "-c",
                "subconverter"
            ],
            "image": "tindy2013/subconverter:latest",
            "volumes": null,
            "workingDir": "/base",
            "entrypoint": null,
            "onBuild": null,
            "labels": {
                "maintainer": "tindy.it@gmail.com"
            }
        },
        "networkSettings": {
            "bridge": "",
            "sandboxID": "44207bf59e3a40af7ad76d91e22ee4351021632d752a80886e7d582173a6c326",
            "hairpinMode": false,
            "linkLocalIPv6Address": "",
            "linkLocalIPv6PrefixLen": 0,
            "ports": {
                "25500/tcp": [
                    {
                        "hostIp": "0.0.0.0",
                        "hostPort": "25500"
                    },
                    {
                        "hostIp": "::",
                        "hostPort": "25500"
                    }
                ]
            },
            "sandboxKey": "/var/run/docker/netns/44207bf59e3a",
            "secondaryIPAddresses": null,
            "secondaryIPv6Addresses": null,
            "endpointID": "53a91e022d6646a40e346b21788b5329aa7507c2e69d9ad04d9e45e22ecd710d",
            "gateway": "172.17.0.1",
            "globalIPv6Address": "",
            "globalIPv6PrefixLen": 0,
            "iPAddress": "172.17.0.2",
            "iPPrefixLen": 16,
            "iPv6Gateway": "",
            "macAddress": "02:42:ac:11:00:02",
            "networks": {
                "bridge": {
                    "iPAMConfig": null,
                    "links": null,
                    "aliases": null,
                    "networkID": "d01bde6f0ba6dd12c041a6d05567353b5c9439b38c4dc239d490ef8516c69f1d",
                    "endpointID": "53a91e022d6646a40e346b21788b5329aa7507c2e69d9ad04d9e45e22ecd710d",
                    "gateway": "172.17.0.1",
                    "iPAddress": "172.17.0.2",
                    "iPPrefixLen": 16,
                    "iPv6Gateway": "",
                    "globalIPv6Address": "",
                    "globalIPv6PrefixLen": 0,
                    "macAddress": "02:42:ac:11:00:02",
                    "driverOpts": null
                }
            }
        }
    }"""

    id = serializers.CharField(max_length=255, label="id", help_text="container id")
    name = serializers.CharField(
        max_length=255, label="name", help_text="container name"
    )
    image = serializers.CharField(
        max_length=255, label="image", help_text="nginx:latest"
    )
    status = serializers.CharField(max_length=255, label="status", help_text="running")
    ports = serializers.JSONField(
        label="ports",
        required=False,
        help_text="[{'80/tcp': [{'HostIp': '', 'HostPort': '80'}]}]",  # noqa
    )
    mounts = serializers.JSONField(label="mounts", required=False, help_text="[]")
    created = serializers.IntegerField(label="created", help_text="created time")
    command = serializers.CharField(
        max_length=255, label="command", help_text="command"
    )
    environment = serializers.JSONField(
        label="environment", required=False, help_text='{"FOO": "BAR"}'
    )
    host_config = serializers.JSONField(
        label="host_config", required=False, help_text="host_config"
    )
    network_settings = serializers.JSONField(
        label="network_settings", required=False, help_text="network_settings"
    )


class CreateDockerContainerSerializer(ICBaseSerializer):
    name = serializers.CharField(
        max_length=255,
        label="name",
        required=False,
        help_text="container name, default is random",
    )
    image = serializers.CharField(
        max_length=255, label="image", help_text="nginx:latest"
    )
    port_bindings = serializers.JSONField(
        label="port_bindings", required=False, help_text="{80: 80, 443: 443}"
    )
    binds = serializers.JSONField(
        label="binds", required=False, help_text='{"/home/user1/": "/mnt/vol2"}'
    )
    environment = serializers.JSONField(
        label="environment", required=False, help_text='{"FOO": "BAR"}'
    )

    def create(self, validated_data):
        return validated_data


class DockerContainerSerializer(ICBaseSerializer):
    command = serializers.CharField(max_length=255, label="command")
    created = serializers.IntegerField(label="created")
    host_config = serializers.JSONField(label="host_config")
    id = serializers.CharField(max_length=255, label="id")
    image = serializers.CharField(max_length=255, label="image")
    image_id = serializers.CharField(max_length=255, label="image_id")
    labels = serializers.JSONField(label="labels")
    mounts = serializers.JSONField(label="mounts")
    names = serializers.JSONField(label="names")
    network_settings = serializers.JSONField(label="network_settings")
    ports = serializers.JSONField(label="ports")
    state = serializers.CharField(max_length=255, label="state")
    status = serializers.CharField(max_length=255, label="status")


class DockerContainerListSerializer(ICBaseSerializer):
    containers = DockerContainerSerializer(many=True, label="containers")
