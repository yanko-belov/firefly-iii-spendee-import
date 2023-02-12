# Import Spendee to Firefly III

This is a helper script to help transform [Spendee](https://www.spendee.com/) csv exports into [Firefly III](https://www.firefly-iii.org/).

First you need to convert spendee csv into csv that is compatible for Firefly III.

# How to generate Firefly III csv

- Export all your account on spendee, you will get email shortly after.

- Place all your csv on csv directory beside compose.py

```
firefly-iii-spendee-import/
├─ compose.py
├─ csv/
│  ├─ transactions_export_cash.csv
│  ├─ transactions_export_bank.csv
```
- Run `python3 compose.py` on terminal
- You will get `final_expense.csv` and `final_transfer.csv`

# How to import

You will need `fidi` or `Firefly III Data Importer documentation` to be able to import csv into Firefly III

Once you have the csv, then open your fidi page. learn more about fidi(https://docs.firefly-iii.org/data-importer/).

Choose `import from file`, then choose `final_expense.csv` and `config_expense.json` to import your expense and `final_transfer.csv` and `config_transfer.csv` for transfer.

<img width="1179" alt="Screenshot 2023-02-12 at 22 17 33" src="https://user-images.githubusercontent.com/16457495/218319753-54ea989f-6fe8-4731-8412-880b573f1116.png">

And Continue the fidi process.

# License

Copyright (c) 2023 Wendy Liga. Licensed under the MIT license, as follows:

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
