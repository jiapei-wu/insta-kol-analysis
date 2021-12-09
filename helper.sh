# 1. build image
docker build -f src/python-dev/Dockerfile-dev -t python-image-dev:v1 .

# 2. run docker container
docker run --rm \
    -d \
    -it \
    -p 8888:8888 \
    --name python-dev-env \
    --mount type=bind,source="$(pwd)",target=/home/jovyan \
    -e GRANT_SUDO=yes \
    python-image-dev:v1

echo "Please type mysql/postgres to launch your database:"
read db_name

if [ $db_name == "postgres" ]; then
    # postgres
    docker run \
        --name yc-postgres \
        -e POSTGRES_PASSWORD=123 \
        --rm \
        -d \
        -p 5432:5432 \
        postgres:10

elif [ $db_name == "mysql" ]; then
    # launch mysql
    docker run \
        --name yc-mysql \
        -e MYSQL_ROOT_PASSWORD=123 \
        --rm \
        -d \
        -p 3306:3306 \
        mysql:8.0
    echo "Your username is set to root; password is set to 123"
    docker exec -it yc-mysql mysql -uroot -p123

else
    echo "Current only support postgres or mysql, please type one of them"
fi