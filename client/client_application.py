
import time
import random
import requests
import json
import threading



def generate_transaction():
    #account_id = acc_data.acc_id
    amount = round(random.uniform(-1000, 1000), 2)


    operation = 'D' if amount > 0 else 'W'

    info = json.dumps({"description": f"{'Deposit' if operation == 'D' else 'Withdrawal'} of ${amount}"})

    transaction_data = {
        'operation': operation,
        'amount': amount,
        'info': info
    }

    return transaction_data , True


def send_transaction(i):
    while True:
        transaction_data , flag= generate_transaction()
        if flag:
            try:
                url = "http://localhost:3000/"
                json_data = json.dumps(transaction_data)
                response = requests.post(url, data=json_data, headers={'Content-Type': 'application/json'})
                print(f"Sent transaction: {transaction_data}")
                print("with node - ",i)
                if response.status_code == 200:
                    print(f"Sent transaction successfully: {transaction_data}")
                else:
                    print(f"Failed to send transaction. Status code: {response.status_code}, Response: {response.text}")
            except Exception as e:
                print(f"Error sending transaction: {e}")

        time.sleep(random.uniform(1, 5))  # Random delay between 1 to 5 seconds


if __name__ == "__main__":
    #get_manager_conn()
    num_of_instances=random.randint(1,5)
    threads=[]
    for i in range (0,num_of_instances):
        thread=threading.Thread(target=lambda i=i: send_transaction(i))
        print("created")
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
