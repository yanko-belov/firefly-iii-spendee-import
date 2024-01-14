import csv
import os
from datetime import datetime, timedelta

exchange_rates = {
    "EUR-USD": 1.19,
    "USD-EUR": 0.84,
    "USD-BGN": 1.65,
    "BGN-USD": 0.61,
    "EUR-BGN": 1.96,
    "BGN-EUR": 0.51,
    "BGN-RUB": 36.27,
    "RUB-BGN": 0.0275709953129308,
    "BGN-GBP": 0.43,
    "GBP-BGN": 2.31,
    "GBP-USD": 1.39,
    "USD-GBP": 0.72,
    "GBP-EUR": 1.17,
    "EUR-GBP": 0.85,
    "RUB-USD": 0.014,
    "USD-RUB": 73.97,
    "RUB-EUR": 0.011,
    "EUR-RUB": 88.51,
    "RUB-GBP": 0.010,
    "GBP-RUB": 102.09,
}

# Find possible opposing transaction based on date, type and amount, from other csv files
def find_opposing_account_name(search_list, target_transaction):
    result = {}
    source_date = datetime.fromisoformat(target_transaction["Date"])
    source_transaction_type = target_transaction["Type"]
    source_amount = target_transaction["Amount"]
    source_currency = target_transaction["Currency"]

    if source_transaction_type == "Incoming Transfer":
        target_amount = source_amount * -1
        target_transaction_type = "Outgoing Transfer"
    else:
        target_amount = abs(source_amount)
        target_transaction_type = "Incoming Transfer"

    for file in search_list:
        for transaction in search_list[file]:
            transaction_amount = transaction["Amount"]
            if target_transaction_type != transaction["Type"] or (source_amount > 0 and target_amount > 0) or (
                    source_amount < 0 and target_amount < 0):
                continue

            transaction_currency = transaction["Currency"]
            transaction_date = datetime.fromisoformat(transaction["Date"])

            time_difference = abs(transaction_date - source_date)
            allowed_time_delta = timedelta(minutes=3)

            if source_currency != transaction_currency:
                exchange_rate = exchange_rates.get(f'{transaction_currency}-{source_currency}')
                transaction_amount_in_source_currency = abs(transaction_amount * exchange_rate)
                allowed_tolerance = transaction_amount_in_source_currency * 0.04
                amount_difference = abs(
                    transaction_amount_in_source_currency - abs(source_amount))

                if time_difference > allowed_time_delta or amount_difference > allowed_tolerance:
                    continue

                if result:
                    if result["time_difference"] > time_difference or result["amount_difference"] > amount_difference:
                        # if duplicate, only use transaction with the smallest delta
                        result = {
                            "transaction": transaction,
                            "time_difference": time_difference,
                            "amount_difference": amount_difference,
                        }
                else:
                    # new result
                    result = {
                        "transaction": transaction,
                        "time_difference": time_difference,
                        "amount_difference": amount_difference,
                    }

            else:
                if time_difference > allowed_time_delta or transaction_amount != target_amount:
                    continue

                if result:
                    if result["time_difference"] > time_difference:
                        # if duplicate, only use transaction with smallest delta
                        result = {
                            "transaction": transaction,
                            "time_difference": time_difference,
                            "amount_difference": 0,
                        }
                else:
                    # new result
                    result = {
                        "transaction": transaction,
                        "time_difference": time_difference,
                        "amount_difference": 0,
                    }

    if result:
        return result["transaction"]
    else:
        return {}


# Read CSV files and store data
files = {}
csv_files = os.listdir('csv')
for file in csv_files:
    with open(f'csv/{file}', 'r') as f:
        csvreader = csv.DictReader(f)
        data = []

        for row in csvreader:
            new_row = row.copy()
            new_row["Amount"] = float(row["Amount"])
            new_row["Note"] = row["Note"].replace(',', " ").replace('#', "")
            new_row["Labels"] = row["Labels"].replace(',', " ").replace('#', "")
            new_row["Author"] = ""
            data.append(new_row)

        files[f'csv/{file}'] = data

# Process transactions
final_transfer_csv_content = [
    'amount,currency_code,foreign_amount,foreign_currency,description,date,source_name,destination_name,category,tags']
final_expense_csv_content = ['amount,currency_code,description,date,source_name,category,tags']

for file in files:
    for transaction in files[file]:
        transaction_type = transaction["Type"]
        transaction_amount = transaction["Amount"]
        transaction_currency_code = transaction["Currency"]
        transaction_description = transaction["Note"]
        transaction_date = transaction["Date"]
        transaction_category = transaction["Category name"]
        transaction_tags = transaction["Labels"]
        transaction_source_name = transaction["Wallet"]

        transaction_foreign_amount = ""
        transaction_foreign_currency_code = ""
        transaction_destination_name = ""

        if transaction_type in ["Outgoing Transfer", "Incoming Transfer"]:
            search_list_files = files.copy()
            del search_list_files[file]

            potential_opposing_transaction = find_opposing_account_name(search_list_files, transaction)
            account_name = ""
            opposing_account_name = ""

            if potential_opposing_transaction:
                transaction_foreign_amount = potential_opposing_transaction["Amount"]
                transaction_foreign_currency_code = potential_opposing_transaction["Currency"]
                transaction_destination_name = potential_opposing_transaction["Wallet"]
                if transaction_type == "Incoming Transfer":
                    continue
            else:
                transaction_destination_name = "(cash)"

            final_transfer_csv_content.append(
                f'{transaction_amount},{transaction_currency_code},{transaction_foreign_amount},{transaction_foreign_currency_code},{transaction_description},{transaction_date},{transaction_source_name},{transaction_destination_name},{transaction_category},{transaction_tags}')

        else:
            final_expense_csv_content.append(
                f'{transaction_amount},{transaction_currency_code},{transaction_description},{transaction_date},{transaction_source_name},{transaction_category},{transaction_tags}')

f = open("final_expense.csv", "w")
f.write("\n".join(final_expense_csv_content))
f.close()

f = open("final_transfer.csv", "w")
f.write("\n".join(final_transfer_csv_content))
f.close()
