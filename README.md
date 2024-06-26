# Setup Instructions

## Prerequisites

Before setting up the project, ensure you have the following software installed:

1. **Python 3.12.\***
2. **Node.js 20.10.0**
3. **RabbitMQ**

### Step 1: Install Python

1. Download Python 3.12.\* from the [official Python website](https://www.python.org/downloads/).
2. Follow the installation instructions to install Python on your system.

### Step 2: Install Node.js

1. Download Node.js version 20.14.0 LTS from the [official Node.js website](https://nodejs.org/en/download/).
2. Follow the installation instructions to install Node.js on your system.

### Step 3: Install RabbitMQ

1. Download RabbitMQ from the [official RabbitMQ website](https://www.rabbitmq.com/docs/install-windows).
2. Navigate to "Direct Downloads" and download the Windows executable file.
3. During the RabbitMQ installation, you will be prompted to install Erlang. Follow the link provided by the RabbitMQ installer to download and install Erlang.

### Step 4: Set Up and Run the Project

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Ensure dependencies are set up as per the instructions above.

#### For Unix-like systems

1. Start RabbitMQ Service:

    ```sh
    rabbitmq.sh start
    ```

    Run below command to find out all options.

    ```sh
    rabbitmq.sh help
    ```

2. Run the setup script to setup virtual envieronment and installing python and node dependencies:

    ```sh
    ./setup.sh
    ```

3. Run the run script to start fastapi, node and RabbitMQ workers:

    ```sh
    ./run.sh
    ```

#### For Windows

1. Start RabbitMQ Service:

    ```bat
    rabbitmq.bat start
    ```

    Run below command to find out all options.

    ```bat
    rabbitmq.bat help
    ```

2. Run the setup script to setup virtual envieronment and installing python and node dependencies:

    ```bat
    setup.bat
    ```

3. Run the run script to start fastapi, node and RabbitMQ workers:

    ```bat
    run.bat
    ```

#### Verify RabbitMQ Installation Manually if RabbitMQ service startup fails(Optional)

1. After installation, navigate to the RabbitMQ installation directory:

    ```plaintext
    C:\Program Files\RabbitMQ Server\rabbitmq_server-3.13.3\sbin
    ```

2. Open the command prompt as administrator to Start RabbitMQ service:

    ```cmd
    rabbitmq-service.bat start
    ```

3. Start the RabbitMQ server:

    ```cmd
    rabbitmqctl start_app
    ```

4. Open a command prompt and check the status of RabbitMQ:

    ```cmd
    rabbitmqctl status
    ```

5. If the server does not start, follow these steps:

    1. By default, RabbitMQ uses the cookie file located in the home directory of the user running the RabbitMQ service.
    2. For the RabbitMQ service, this file is usually found at:

        ```plaintext
        C:\Windows\system32\config\systemprofile\.erlang.cookie
        ```

    3. The Erlang cookie file is named `.erlang.cookie` and is typically located in the user's home directory:

        ```plaintext
        C:\Users\<YourUsername>\.erlang.cookie
        ```

    4. Open both cookie files in a text editor and ensure that the contents are identical.
    5. If they are not, copy the content from the RabbitMQ server's cookie file (`C:\Windows\system32\config\systemprofile\.erlang.cookie`) to the CLI tool's cookie file (`C:\Users\<YourUsername>\.erlang.cookie`).
    6. Repeat from step 1.

This will start the frontend development server, the FastAPI server, and multiple instances of `worker.py` with different arguments in separate terminal windows.

---

More setup instructions will follow. Please complete the above steps first.
