# Daily High Low Stock Analysis Project

1. create a git account on github. "daily high low",
2. create and initialize a venv
3. create a python project, app.py that I can run locally and will also run as an aws lambda function. The aws version will integrate with eventbridge and SNS.
4. app.py should read in a list of stock symbols in csv format, and for each one, use yfinance data to determine if the previous days high is a local close high, or a local extreme high.
5. a local extreme high is defined as: yesterday's high (one day ago) is higher than both today's high and the high two days ago. example : 3, 4,3.
6. a local close high is defined as: yesterday's close (one day ago) is higher than both today's close and the close two days ago. example : 3, 4,3.
7. use curl_cffi to fake coming from chrome. add a delay between requests.
8. do the same as (4), except with lows.
9. if running locally, print out a list of stocks with local highs and local lows. give the type (local high/low), the closing price, and the type of local high/low. make it look nice, not just a json dump.
10. there are two types, if the close is higher/lower, and if the low/high is higher/lower.
11. error handling. if yfinance fails generate an error message.
12. generate a requirements.txt
13. generate a readme.md
14. make all python code flake8 compatible
15. make all markdown code markdownlint compatible
