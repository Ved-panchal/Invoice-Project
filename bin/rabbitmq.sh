#!/bin/bash

# Determine the current directory of the script
SCRIPT_PATH="$(dirname "$(realpath "$0")")"

# Check if the script is run as root
if [[ $EUID -ne 0 ]]; then
    echo "This script requires administrative privileges."
    echo "Please run the script as root."
    exit 1
fi

# Main script logic
case "$1" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    status)
        status_service
        ;;
    help)
        echo "start - To start RabbitMQ service and app"
        echo "stop - To stop RabbitMQ service and app"
        echo "status - To show RabbitMQ status"
        ;;
    *)
        echo "Invalid argument. Please use one of the following:"
        echo "start - To start RabbitMQ service and app"
        echo "stop - To stop RabbitMQ service and app"
        echo "status - To show RabbitMQ status"
        ;;
esac
exit 0

# Function to start RabbitMQ service
start_service() {
    echo "Checking RabbitMQ service status..."
    if systemctl is-active --quiet rabbitmq-server; then
        echo "RabbitMQ service is already running."
    else
        echo "Starting RabbitMQ service..."
        systemctl start rabbitmq-server
        echo "Verifying cookies..."
        cp -f /var/lib/rabbitmq/.erlang.cookie /root/.erlang.cookie
        echo "Cookies verified."
        echo "Starting RabbitMQ app..."
        rabbitmqctl start_app
        echo "Startup successful."
    fi
}

# Function to stop RabbitMQ service
stop_service() {
    echo "Checking RabbitMQ service status..."
    if systemctl is-active --quiet rabbitmq-server; then
        echo "Stopping RabbitMQ service..."
        rabbitmqctl stop_app
        systemctl stop rabbitmq-server
        if [[ $? -eq 0 ]]; then
            echo "RabbitMQ service stopped successfully."
        else
            echo "Failed to stop RabbitMQ service."
        fi
    else
        echo "RabbitMQ service is not running."
    fi
}

# Function to show RabbitMQ status
status_service() {
    echo "Showing RabbitMQ status..."
    output=$(rabbitmqctl status 2>&1)
    if [[ "$output" == *"Error"* ]]; then
        echo "RabbitMQ service is not running. Use rabbitmq.sh start command to start the service."
    elif [[ "$output" == *"Status"* ]]; then
        echo "RabbitMQ service is up and running."
    else
        echo "Unknown error occurred, contact administrator..."
    fi
}

cd "$SCRIPT_PATH"
