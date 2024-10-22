dname=$(dirname ${BASH_SOURCE[0]})
if [ "$#" -ne 2 ]; then
    echo "Usage: ./run_client <server_name> <port>"
    exit 1
fi
echo "Running client.py with server: $1 and port: $2"
python3 $dname/client.py $1 $2