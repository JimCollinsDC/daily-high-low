# Copilot Instructions for Daily High Low Stock Analysis

## Project Overview
This is a Python-based stock analysis tool that identifies local highs and lows in stock price data using yfinance. The application is designed to run both locally and as an AWS Lambda function with EventBridge and SNS integration.

## Key Architecture Decisions

### Dual Environment Design
- **Local Mode**: Prints analysis results to console with attractive formatting (not JSON dumps)
- **Lambda Mode**: Integrates with AWS EventBridge and SNS for event-driven processing
- Use environment detection (e.g., `AWS_LAMBDA_FUNCTION_NAME` env var) to determine execution context

### Web Scraping Strategy
- Use `curl_cffi` to fake Chrome browser requests to yfinance
- Implement delays between requests to avoid rate limiting
- Handle potential blocking/throttling gracefully

### Core Algorithm
The application analyzes each stock symbol to identify:
1. **Local Extreme High**: Yesterday's high > max(today's high, 2-days-ago high)
2. **Local Close High**: Yesterday's close > max(today's close, 2-days-ago close)
3. **Local Extreme Low**: Yesterday's low < min(today's low, 2-days-ago low)
4. **Local Close Low**: Yesterday's close < min(today's close, 2-days-ago close)

### Data Analysis Types
For each local high/low, track two distinct metrics:
- **Close-based Analysis**: Whether yesterday's close is higher/lower than comparison points
- **Extreme-based Analysis**: Whether yesterday's high/low value itself is higher/lower than comparison points

## Development Patterns

### File Structure
```
app.py                 # Main application entry point
requirements.txt       # curl_cffi, yfinance, boto3, other dependencies
README.md             # Usage instructions and deployment guide
stock_symbols.csv     # CSV format stock symbol list
tests/                # Unit tests for analysis logic
```

### Core Functions to Implement
```python
def get_stock_data(symbol, days=3)         # Fetch yfinance data with curl_cffi (3-day analysis)
def add_request_delay()                    # Rate limiting between requests
def analyze_local_extreme_highs(data)      # Identify local extreme high patterns
def analyze_local_close_highs(data)        # Identify local close high patterns
def analyze_local_extreme_lows(data)       # Identify local extreme low patterns
def analyze_local_close_lows(data)         # Identify local close low patterns
def format_results_pretty(results)         # Attractive console output formatting
def format_results_json(results)           # JSON for Lambda/SNS
def publish_to_sns(results)                # SNS integration for Lambda
def lambda_handler(event, context)         # AWS Lambda entry point with EventBridge
def main()                                 # Local execution entry point
```

### Stock Symbol Input
- **Local Mode**: Read from CSV file (stock_symbols.csv)
- **Lambda Mode**: Accept symbols via EventBridge event payload
- CSV format should include symbol and optionally company name
- Validate CSV format and stock symbol validity

### Error Handling Patterns
- Handle yfinance API failures gracefully with specific error messages
- Implement retry logic for transient network errors
- Use curl_cffi error handling for browser simulation failures
- Return meaningful error messages in both execution modes
- Log failures for debugging without crashing entire analysis

## Dependencies & Environment

### Python Environment
- Use virtual environment (`python -m venv venv`)
- Python 3.8+ compatibility for Lambda runtime
- Include `curl_cffi` for browser simulation
- Include `yfinance` as primary data source

### AWS Lambda Considerations
- Keep package size under 50MB unzipped
- Use Lambda layers for large dependencies if needed
- Set appropriate timeout (30-60 seconds for multiple stock lookups)
- Configure memory based on symbol count (128-512MB typical)

## Testing Strategy
- Mock yfinance responses for unit tests
- Test both extreme and close-based high/low detection algorithms
- Verify dual-mode output formatting
- Test edge cases: weekends, holidays, insufficient data
- Test curl_cffi browser simulation and rate limiting
- Ensure flake8 compliance for all Python code
- Validate markdownlint compliance for documentation

## Development Workflow
1. Start with local-only implementation and testing
2. Add Lambda handler wrapper around core logic
3. Test locally using CSV file with stock symbols
4. Package and deploy to Lambda for integration testing
5. Configure EventBridge and SNS integration
6. Ensure flake8 compliance for all Python code
7. Validate markdownlint compliance for all documentation

## Key Files to Reference
- `.github/project.md`: Original requirements specification
- `app.py`: Core implementation (when created)
- `requirements.txt`: Dependency management

## Common Pitfalls to Avoid
- Don't fetch more historical data than needed (performance)
- Handle market closure scenarios (weekends, holidays)
- Ensure timezone consistency in date calculations
- Validate stock symbols before processing