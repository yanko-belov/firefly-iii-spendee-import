"""
Copyright (c) 2023 Wendy Liga. Licensed under the MIT license, as follows:

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import csv
import os
from datetime import datetime
from datetime import timedelta

# find possible opposing transaction based on date, type and amount, from other csv files
def find_opposing_account_name(search_list, target_transaction):
  result = {}

  source_date = datetime.fromisoformat(target_transaction["Date"])
  source_transaction_type = target_transaction["Type"]
  source_amount = target_transaction["Amount"]
  
  # adjust target transaction amount and type based
  # we will inverse the amount and change the type based on the source transaction type
  target_amount = 0.0
  target_transaction_type = ""
  if source_transaction_type == "Incoming Transfer":
    target_amount = source_amount * -1
    target_transaction_type = "Outgoing Transfer"
  else:
    target_amount = abs(source_amount)
    target_transaction_type = "Incoming Transfer"

  for file in search_list:
    for transaction in search_list[file]:
      transaction_type = transaction["Type"]
      transaction_amount = transaction["Amount"]
      transaction_date = datetime.fromisoformat(transaction["Date"])
      
      difference = abs(transaction_date - source_date)
      allowed_delta = timedelta(minutes=3)
      
      if difference < allowed_delta and transaction_type == target_transaction_type and transaction_amount == target_amount :
        if result:
          if result["delta"] > difference:
            # if duplicate, only use transaction with smallest delta
            result = {
              "transaction": transaction,
              "delta": difference
            }
        else:
          # new result
          result = {
            "transaction": transaction,
            "delta": difference
          }

  if result:
    return result["transaction"]
  else:
    return {}

# calculate delta between two transaction dates
def transaction_date_delta(first_transaction, second_transcation):
  first = datetime.fromisoformat(first_transaction)
  second = datetime.fromisoformat(second_transcation)
  return abs(first - second)  

files = {}
csv_files = os.listdir('csv')

for file in csv_files:
  with open(f'csv/{file}', 'r') as f:
    csvreader = csv.DictReader(f)
    data = []

    for row in csvreader:
      new_row = row.copy()
      new_row["Amount"] = float(row["Amount"])
      # replace comma and hash, so csv can be parsed correctly
      new_row["Note"] = row["Note"].replace(',', " ").replace('#', "")
      # replace comma and hash, so csv can be parsed correctly
      new_row["Labels"] = row["Labels"].replace(',', " ").replace('#', "")
      new_row["Author"] = ""

      data.append(new_row)

    files[f'csv/{file}'] = data

final_transfer_csv_content = ['Date,Wallet,Type,"Category name",Amount,Currency,Note,Labels,Author,"Account Name","Opposing Account Name"']
final_expense_csv_content = ['Date,Wallet,Type,"Category name",Amount,Currency,Note,Labels,Author']
for file in files:
  for transaction in files[file]:
    transaction_date = transaction["Date"]
    transaction_type = transaction["Type"]
    transaction_amount = abs(transaction["Amount"])

    if transaction_type == "Outgoing Transfer":
      search_list_files = files.copy()
      del search_list_files[file]
      
      # search potential opposing transaction
      potential_opposing_transaction = find_opposing_account_name(search_list_files, transaction)

      account_name = ""
      opposing_account_name = ""

      if potential_opposing_transaction:
        account_name = potential_opposing_transaction["Wallet"]
        opposing_account_name = transaction["Wallet"]
      else:
        account_name = "Deleted Account"
        opposing_account_name = transaction["Wallet"]

      final_transfer_csv_content.append(f'{transaction_date},{transaction["Wallet"]},{transaction["Type"]},{transaction["Category name"]},{transaction_amount},{transaction["Currency"]},{transaction["Note"]},{transaction["Labels"]},{transaction["Author"]},{account_name},{opposing_account_name}')
    elif transaction_type == "Incoming Transfer":
      search_list_files = files.copy()
      del search_list_files[file]
      
      potential_opposing_transaction = find_opposing_account_name(search_list_files, transaction)

      # we will only add new transfer transcation if it is coming from "Out of Spendee" account
      # because if not, we will create 2 transfer that will cancel each other.
      if len(potential_opposing_transaction) == 0:
        opposing_account_name = "Deleted Account"
        account_name = transaction["Wallet"]
        final_transfer_csv_content.append(f'{transaction_date},{transaction["Wallet"]},{transaction["Type"]},{transaction["Category name"]},{transaction_amount},{transaction["Currency"]},{transaction["Note"]},{transaction["Labels"]},{transaction["Author"]},{account_name},{opposing_account_name}')

    elif transaction_type == "Income" or transaction_type == "Expense":
      final_expense_csv_content.append(f'{transaction_date},{transaction["Wallet"]},{transaction["Type"]},{transaction["Category name"]},{transaction["Amount"]},{transaction["Currency"]},{transaction["Note"]},{transaction["Labels"]},{transaction["Author"]}')

f = open("final_expense.csv", "w")
f.write("\n".join(final_expense_csv_content))
f.close()

f = open("final_transfer.csv", "w")
f.write("\n".join(final_transfer_csv_content))
f.close()
