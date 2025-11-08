# MongoDB Microservices with gRPC

This repository contains a Python-based microservices server that uses gRPC for communication and MongoDB as the database. The server allows clients to insert and query documents in MongoDB via gRPC.

## Features

- **gRPC-based communication**: Efficient and scalable communication between client and server.
- **MongoDB integration**: Perform Create and Read operations on MongoDB collections.
    - Can be enhanced further as required.
- **Protobuf definitions**: Define service contracts using `.proto` files.

---

## Prerequisites

- Python 3.8+
- MongoDB installed and running locally
- `pip` for dependency management

---

## Installation

1. Clone the repository:
    ```
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Create and activate a virtual environment:
    ```
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install Dependencies:
    ```
    pip install -r requirements.txt
    ```

4. Generate gRPC code from the .proto file:
    ```
    python -m grpc_tools.protoc -I. --python_out=./generated --grpc_python_out=./generated proto/db.proto
    ```

## Usage

### Start The Server

1. Ensure MongoDB is running locally
2. Run the gRPC server:
    ```
    python server.py
    ```

### Test with the client
1. Open a new terminal and activate the virtual environment.
2. Run the gRPC client
    ```
    python client.py
    ```

## Project Structure
    ```
    ├── proto/
    │   └── db.proto          # Protobuf definition file
    ├── generated/            # Generated gRPC code
    ├── server.py             # gRPC server implementation
    ├── client.py             # gRPC client for testing
    ├── requirements.txt      # Python dependencies
    └── README.md             # Project documentation
    ```

## Dependencies
* grpcio
* grpcio-tools
* protobuf
* pymongo