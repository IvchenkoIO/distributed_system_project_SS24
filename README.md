
# Project: Containerized application with Google Kubernetes Engine

**Distributed Systems/Summer Semester 2024**

Develop a distributed account management system consisting of the following applications:
1. Client application (back end)
  
            ● Requests transactions regarding an account (deposit/withdrawal) to an associated account manager application (see below)
            ● Issues transaction requests at random times with randomly generated amounts (positive for deposit, negative for withdrawal)
            ● Runs in its own container
            ● At least 2 client containers in the same pod

2. Account manager application (back end)
   
            ● Performs transactions for one account as requested by client applications from the same pod
            ● Maintains the account balance
            ● During a run logs all transactions with time stamps
            ● Runs on the same pod as the client applications for that account
            
3. Accounts Monitor application (front end)

            ● Monitors multiple accounts on the same cluster
            ● Maintains a summary of accounts with current balance for each account
            ● Provides the user with various information about the accounts, including current balance and transaction logs
