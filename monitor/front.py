from flask import Flask, render_template, jsonify, request, Response
import psycopg2
import time
import datetime
import pytz
from psycopg2 import pool


db_pool = None

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

def postgre_q_tr():
    #conn = get_db_connection()
    #cursor = conn.cursor()
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                     SELECT log_id,date, account_id, operation, amount, info
                     FROM logs
                     ORDER BY date DESC
                     """)

            rows = cursor.fetchall()

        # Convert rows to a list of dictionaries
            logs = []
            for row in rows:
                log = {
                    'log_id':row[0],
                    'date': row[1],
                    'account_id': row[2],
                    'operation': row[3],
                    'amount': row[4],
                    'info': row[5]
                }
                logs.append(log)
            return logs
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        db_pool.putconn(conn)

def postgre_q_a():
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
             SELECT first_name, last_name, balance, acc_id
             FROM accounts
             """)

            rows = cursor.fetchall()

    # Convert rows to a list of dictionaries
            logs = []
            for row in rows:
                log = {
                    'fname': row[0],
                    'lname': row[1],
                    'balance': row[2],
                    'account_id': row[3],
                }
                logs.append(log)

            cursor.close()
            conn.close()
            return logs
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        db_pool.putconn(conn)



def fetch_accounts(fname=None, lname=None, start_date=None, end_date=None):
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cursor:

            base_query = """
        SELECT acc_id, first_name, last_name, balance
        FROM accounts
    """
            filters = []
            if fname:
                filters.append(f"first_name LIKE '%{fname}%'")
            if lname:
                filters.append(f"last_name LIKE '%{lname}%'")

            if filters:
                query = base_query + " WHERE " + " AND ".join(filters)
            else:
                query = base_query

            cursor.execute(query)
            rows = cursor.fetchall()
            print(rows)
            # Convert rows to a list of dictionaries
            accounts = []
            for row in rows:
                account = {
                    'account_id': row[0],
                    'fname': row[1],
                    'lname': row[2],
                    'balance': row[3],
                }
                accounts.append(account)


            return accounts
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        db_pool.putconn(conn)

def create_app():
    app = Flask(__name__)
    init_db_pool()
    @app.route('/monitor_t', methods=['GET'])
    def monitor_transactions():
        while True:
            try:
                logs=postgre_q_tr()
                #logs = mysql_q_tr()
                #time.sleep(5)
                return render_template('tr_logs.html', tr_logs=logs)

            except Exception as e:
                print(f"Error: {e}")
                return jsonify({"error": str(e)}), 500


    def fetch_tr_logs(start_date=None, end_date=None,acc_id=None):
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                base_query="""
            SELECT log_id, date, account_id, operation, amount, info
            FROM logs
        """
                filters = []
                if start_date:
                    filters.append(f"date >= '{start_date}'")
                if end_date:
                    filters.append(f"date <= '{end_date}'")
                if acc_id:
                    filters.append(f"account_id = '{str(acc_id)}'")

                if filters:
                    query = base_query + " WHERE " + " AND ".join(filters) + " ORDER BY date DESC"
                else:
                    query = base_query + " ORDER BY date DESC"

                cursor.execute(query)
                rows = cursor.fetchall()

                # Convert rows to a list of dictionaries
                logs = []
                for row in rows:
                    log = {
                        'log_id':row[0],
                        'date': row[1],
                        'account_id': row[2],
                        'operation': row[3],
                        'amount': row[4],
                        'info': row[5]
                    }
                    logs.append(log)

                return logs
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            db_pool.putconn(conn)

    @app.route('/search_t', methods=['POST'])
    def search_t():
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        if start_date:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=pytz.utc)
        else:
            start_date = None

        if end_date:
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d') + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)
            end_date = end_date.replace(tzinfo=pytz.utc)
        else:
            end_date = None
        acc_id=request.form.get('account_id')
        print(acc_id)
        tr_logs = fetch_tr_logs(start_date, end_date,acc_id)
        return render_template('tr_logs.html', tr_logs=tr_logs,account_id=acc_id)


    @app.route('/', methods=['GET'])
    def monitor_accounts():
        try:
            logs=postgre_q_a()
            # logs = mysql_q_a()
            return render_template('a_logs.html', logs=logs)

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/', methods=['POST'])
    def display_a():
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        print(fname,lname)
        accounts = fetch_accounts(fname, lname)
        return render_template('a_logs.html', logs=accounts)


    return app




if __name__ == "__main__":
    app=create_app()
    app.run(host='0.0.0.0', port=5000)
