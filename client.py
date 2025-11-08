import grpc
import json
from generated.db import db_pb2, db_pb2_grpc
import jwt

from dotenv import load_dotenv
import os

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET", "your_secret_key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

def create_jwt(payload):
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def insert_document(stub):
    collection = "user"
    name = input("Enter name: ")
    age = int(input("Enter age: "))

    document = {"name": name, "age": age}
    request = db_pb2.InsertRequest(
        collection=collection,
        document=json.dumps(document)
    )
    # Create JWT token (in real use, payload should be user info, etc.)
    token = create_jwt({"user": "testuser"})
    metadata = [("authorization", token)]
    try:
        response = stub.InsertDocument(request, metadata=metadata)
        print(f"✅ Insert response: {response.message}")
    except grpc.RpcError as e:
        print(f"❌ gRPC error: {e.details()}")

def find_documents(stub):
    collection = "user"
    name = input("Enter name to search: ")

    query = {"name": {"$regex": name, "$options": "i"}}
    request = db_pb2.FindRequest(
        collection=collection,
        query=json.dumps(query)
    )
    # Create JWT token
    token = create_jwt({"user": "testuser"})
    metadata = [("authorization", token)]
    try:
        print("📦 Found documents:")
        for response in stub.FindDocument(request, metadata=metadata):
            response_doc = response.documents
            print(json.loads(response_doc))
    except grpc.RpcError as e:
        print(f"❌ gRPC error: {e.details()}")

def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = db_pb2_grpc.MongoServiceStub(channel)

        while True:
            print("\n=== MongoDB gRPC CLI ===")
            print("1. Insert Document")
            print("2. Search Documents")
            print("3. Exit")

            choice = input("Select an option: ").strip()
            if choice == "1":
                insert_document(stub)
            elif choice == "2":
                find_documents(stub)
            elif choice == "3":
                print("👋 Exiting...")
                break
            else:
                print("⚠️ Invalid choice. Please try again.")

if __name__ == "__main__":
    run()
