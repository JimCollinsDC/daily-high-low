# Daily High Low Stock Analysis

A Python-based stock analysis tool that identifies local highs and lows in
stock price data using yfinance. The application runs both locally and as an
AWS Lambda function with EventBridge and SNS integration.

## Features

- **Local High Detection**: Identifies when previous day's high > max(today's
  high, 2-days-ago high)
- **Local Low Detection**: Identifies when previous day's low < min(today's
  low, 2-days-ago low)
- **Dual Analysis Types**: Tracks both price-based and extreme-based metrics
- **Browser Simulation**: Uses curl_cffi to avoid rate limiting
- **AWS Integration**: EventBridge triggers and SNS notifications
- **Attractive Output**: Formatted console display (not JSON dumps)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/daily-high-low.git
cd daily-high-low
```

1. Create and activate virtual environment:

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac
```

1. Install dependencies:

```bash
pip install -r requirements.txt
```

## Local Usage

1. Edit `stock_symbols.csv` to include your desired stock symbols:

```csv
symbol,name
AAPL,Apple Inc.
MSFT,Microsoft Corporation
GOOGL,Alphabet Inc.
```

1. Run the analysis:

```bash
python app.py
```

Example output:

```text
🚀 Daily High Low Stock Analysis
================================
🔍 Analyzing 10 stock symbols...
  [1/10] Processing AAPL... 📈 ✓
  [2/10] Processing MSFT... ➖ ✓
  [3/10] Processing GOOGL... 📉 ✓

================================================================================
📈 DAILY HIGH LOW STOCK ANALYSIS RESULTS
================================================================================

🔺 LOCAL HIGHS:
--------------------------------------------------
  AAPL   | 2025-10-06 | Close: $  225.67 | High: $  227.89
         | Types: Close Higher, High Higher

🔻 LOCAL LOWS:
--------------------------------------------------
  GOOGL  | 2025-10-06 | Close: $  138.45 | Low: $  137.23
         | Types: Close Lower, Low Lower

================================================================================
📊 Summary: 1 local highs, 1 local lows detected
```

## AWS Lambda Deployment

### Prerequisites

- AWS CLI configured
- IAM role with EventBridge and SNS permissions

### Deployment Steps

1. Package the application:

```bash
pip install -t package -r requirements.txt
cp app.py package/
cd package && zip -r ../daily-high-low.zip . && cd ..
```

1. Create Lambda function:

```bash
aws lambda create-function \
  --function-name daily-high-low \
  --runtime python3.9 \
  --role arn:aws:iam::YOUR-ACCOUNT:role/lambda-execution-role \
  --handler app.lambda_handler \
  --zip-file fileb://daily-high-low.zip \
  --timeout 60 \
  --memory-size 256
```

1. Set environment variables:

```bash
aws lambda update-function-configuration \
  --function-name daily-high-low \
  --environment Variables='{SNS_TOPIC_ARN=arn:aws:sns:region:account:topic-name}'
```

### EventBridge Integration

Create an EventBridge rule to trigger the Lambda:

```json
{
  "symbols": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
}
```

The Lambda will process these symbols and publish results to the configured
SNS topic.

## Algorithm Details

### Local High Detection

A local high occurs when:

- Previous day's high > max(today's high, 2-days-ago high)

### Local Low Detection

A local low occurs when:

- Previous day's low < min(today's low, 2-days-ago low)

### Analysis Types

For each detected pattern, the tool reports two metrics:

1. **Close-based**: Whether closing price is higher/lower than comparison
   points
2. **Extreme-based**: Whether the high/low value itself is higher/lower than
   comparison points

## Error Handling

- Graceful handling of yfinance API failures
- Browser simulation using curl_cffi to avoid blocking
- Rate limiting with configurable delays
- Comprehensive error messages for debugging
- Retry logic for transient network errors

## Configuration

### Request Delays

Modify the delay between requests in `app.py`:

```python
add_request_delay(0.5)  # 0.5 second delay
```

### Data Range

Adjust the number of days analyzed:

```python
data = get_stock_data(symbol, days=3)  # 3 days of data
```

## Dependencies

- `yfinance>=0.2.28` - Stock data API
- `curl-cffi>=0.6.2` - Browser simulation
- `boto3>=1.34.0` - AWS SDK
- `pandas>=2.0.0` - Data manipulation
- `numpy>=1.24.0` - Numerical computing

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Troubleshooting

### Common Issues

#### No data available for symbol

- Check if symbol is valid and trades on major exchanges
- Verify market is open (weekends/holidays may have no recent data)

#### Rate limiting errors

- Increase delay between requests
- Check if yfinance is blocking requests (curl_cffi should help)

#### Lambda timeout

- Reduce number of symbols per invocation
- Increase Lambda timeout setting
- Consider using Lambda layers for dependencies

#### SNS publish failures

- Verify SNS topic ARN is correct
- Check IAM permissions for SNS publish
- Ensure topic exists in same region as Lambda
