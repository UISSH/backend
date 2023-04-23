# https://blog.jeanbruenn.info/2021/08/21/systemd-multi-instance-redis/

if [ $(id -u) != "0" ]; then
    echo "Error: You must be root to run this script, please use root to install redis"
    exit 1
fi

apt install lsb-release -y

# delete old key
rm /usr/share/keyrings/redis-archive-keyring.gpg

# install new key
curl -fsSL https://packages.redis.io/gpg | gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg

# add source
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/redis.list

# install redis
apt-get update -y && apt-get install redis -y
