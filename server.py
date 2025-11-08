import grpc
import json
from concurrent import futures
from pymongo import MongoClient, errors
from generated.db import db_pb2, db_pb2_grpc
import jwt
from jwt import InvalidTokenError
from dotenv import load_dotenv
import os

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET", "your_secret_key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

def create_jwt(payload):
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except InvalidTokenError:
        return None
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "local")
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[MONGO_DB]
    print("✅ Connected to MongoDB successfully.")
except errors.ServerSelectionTimeoutError as e:
    print(f"❌ Failed to connect to MongoDB: {e}")
    exit(1)

class MongoService(db_pb2_grpc.MongoServiceServicer):
    def InsertDocument(self, request, context):
        # JWT validation
        token = dict(context.invocation_metadata()).get('authorization')
        if not token or not decode_jwt(token):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("Invalid or missing JWT token.")
            return db_pb2.InsertResponse(message="❌ Unauthorized.")
        try:
            collection = db[request.collection]
            document = json.loads(request.document)
            result = collection.insert_one(document)
            return db_pb2.InsertResponse(
                message=f"✅ Inserted document with ID: {result.inserted_id}"
            )
        except json.JSONDecodeError:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Invalid JSON in insert request.")
            return db_pb2.InsertResponse(message="❌ Invalid JSON format.")
        except errors.PyMongoError as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Database error: {str(e)}")
            return db_pb2.InsertResponse(message=f"❌ Database error: {e}")
        except Exception as e:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details(str(e))
            return db_pb2.InsertResponse(message=f"❌ Unexpected error: {e}")

    def FindDocument(self, request, context):
        # JWT validation
        token = dict(context.invocation_metadata()).get('authorization')
        if not token or not decode_jwt(token):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("Invalid or missing JWT token.")
            yield db_pb2.FindResponse()
            return
        try:
            collection = db[request.collection]
            query = json.loads(request.query)
            cursor = collection.find(query)
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                yield db_pb2.FindResponse(documents=json.dumps([doc]))
        except json.JSONDecodeError:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Invalid JSON in find request.")
            yield db_pb2.FindResponse()
        except errors.PyMongoError as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Database error: {str(e)}")
            yield db_pb2.FindResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details(str(e))
            yield db_pb2.FindResponse()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    db_pb2_grpc.add_MongoServiceServicer_to_server(MongoService(), server)
    server.add_insecure_port("[::]:50051")

    print("🚀 Server is running on port 50051...")
    try:
        server.start()
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped manually.")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    serve()
