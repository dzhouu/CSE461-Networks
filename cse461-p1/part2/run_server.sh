dname=$(dirname ${BASH_SOURCE[0]})
if [ "$#" -ne 2 ]; then
    echo "Usage: ./run_server <server_name> <port>"
    exit 1
fi
echo "Running server.py on server: $1 and port: $2"
python3 $dname/server.py $1 $2