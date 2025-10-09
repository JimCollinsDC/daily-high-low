1. create a git account on github. "daily high low"
2. create and initialize a venv
3. create a python project, app.py that I cat run locally and will also run as an aws lambda function. The aws version will integrare with eventvridge and SNS.
4. app.py shoud read in a list of stock symbols in csv format, and for each one, use yfinance data to detemine if the previous days high is a local close high, or a local extreme high.
5. a local extreme high is defined as: yesterdays high (one day ago) is higher than both todays high and the high two days ago. example : 3, 4,3.
6. a local close high is defined as: yesterdays close (one day ago) is higher than both todays close and the close two days ago. example : 3, 4,3.
7. use curl_cffi to fake coming from chrome. add a delay between requests.
8. do the same as (4), except with lows.
9. if running locally, print out a list of stocks with local highs and local lows. give the type (local high/low), the closing price, and the tpe of local high/low. make it look nice, not just a json dump.
10. there are two types, if the close is higher/lower, and if the low/high is higher/lower.
11. error handing. if yfinace fails generate an error message.
12. generate a requirements.txt
13. generate a readme.md
14. make all python code flake8 compatible
15. make all markdown code markdownlint compatible
