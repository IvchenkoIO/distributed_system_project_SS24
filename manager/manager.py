
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from socketserver import ThreadingMixIn
import psycopg2
from psycopg2 import sql
import random
from datetime import datetime
from psycopg2 import pool
import pytz
from decimal import Decimal
import uuid
import traceback
from dotenv import load_dotenv
import os

load_dotenv()

client_id = uuid.UUID(os.getenv('ACCOUNT_ID'))

db_pool = None

def generate_logs_id(acc_id):
    return uuid.UUID(f'{acc_id.hex[:16]}{uuid.uuid4().hex[:16]}')


def init_db_pool():
    global db_pool
    db_pool = psycopg2.pool.ThreadedConnectionPool(
        minconn=10,
        maxconn=50,
        user='admin',
        password='password',
        host='postgresql.default.svc.cluster.local',
        port='5432',
        database='ds_proj_db'
    )

def create_account(client_id):
    first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "Diana"]
    last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis"]
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cursor:
            insert_query = sql.SQL("""
                INSERT INTO accounts (first_name, last_name, balance, acc_id)
                VALUES (%s, %s, %s, %s)
            """)
            data = (random.choice(first_names), random.choice(last_names), random.uniform(0, 10000), str(client_id))
            cursor.execute(insert_query, data)
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        db_pool.putconn(conn)

def find_acc():
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cursor:
            search_query = sql.SQL("SELECT * FROM accounts WHERE acc_id = %s")
            cursor.execute(search_query, (str(client_id),))
            result = cursor.fetchone()
            if not result:
                print("creating acc")
                create_account(str(client_id))
    except Exception as e:
        raise e
    finally:
        db_pool.putconn(conn)

def update_balance(client_id, amount):
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cursor:
            conn.autocommit = False
            cursor.execute("""
                UPDATE accounts 
                SET balance = balance + %s
                WHERE acc_id = %s
            """, (amount, str(client_id)))
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        db_pool.putconn(conn)

def log_tr(client_id, data):
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cursor:
            conn.autocommit = False
            log_id=generate_logs_id(client_id)
            cursor.execute("""
                INSERT INTO logs (log_id,date, account_id, operation, amount, info)
                VALUES (%s,%s, %s, %s, %s, %s)
            """, (str(log_id),datetime.now(pytz.utc).astimezone(pytz.timezone('Europe/Vienna')), str(client_id), data["operation"], data["amount"], json.dumps(data),))
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        db_pool.putconn(conn)

def check_balance(client_id, amount):
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT balance FROM accounts WHERE acc_id = %s FOR UPDATE", (str(client_id),))
            result = cursor.fetchone()
            if result and (result[0] + Decimal(amount) >= 0):
                return True
            return False
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        db_pool.putconn(conn)

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data)
            print(f"Received JSON data: {data}")
            #find_acc(client_id)
            if check_balance(str(client_id), data["amount"]):
                update_balance(str(client_id), data["amount"])
                log_tr(client_id, data)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'message': 'Transaction processed successfully'}
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'error': 'Insufficient funds'}
                self.wfile.write(json.dumps(response).encode())
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'error': 'Invalid JSON'}
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            print(traceback.print_exc(e))
            response = {'error': str(e)}
            self.wfile.write(json.dumps(response).encode())

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

def run(server_class=ThreadingHTTPServer, handler_class=RequestHandler, port=3000):
    init_db_pool()
    find_acc()
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Server running on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
