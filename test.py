import docker

client = docker.from_env()

container_id = "5c8b693e61331ed6775174533c6f795fb2fed796e4b43502c3ceddbfa8083560"

container = client.containers.get(container_id)

container.update(
    restart_policy={"Name": "unless-stopped", "MaximumRetryCount": 0},
)
