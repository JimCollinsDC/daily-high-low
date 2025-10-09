import os
import time
import json
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import yfinance as yf
import pandas as pd
from curl_cffi import requests
import boto3
from botocore.exceptions import ClientError


def add_request_delay(delay_seconds: float = 1.0) -> None:
    """Add delay between requests to avoid rate limiting."""
    time.sleep(delay_seconds)


def get_stock_data(symbol: str, days: int = 3) -> Optional[pd.DataFrame]:
    """
    Fetch stock data using yfinance with curl_cffi for browser simulation.

    Args:
        symbol: Stock symbol (e.g., 'AAPL')
        days: Number of days of data to fetch (default 3 for algorithm)

    Returns:
        DataFrame with stock data or None if failed
    """
    try:
        # Use curl_cffi session to simulate Chrome browser
        session = requests.Session(impersonate="chrome110")

        # Create yfinance ticker with custom session
        ticker = yf.Ticker(symbol)
        ticker.session = session

        # Calculate date range
        end_date = datetime.now()
        # Extra days for weekends
        start_date = end_date - timedelta(days=days + 5)

        # Fetch historical data
        data = ticker.history(start=start_date, end=end_date)

        if data.empty:
            print(f"❌ No data available for {symbol}")
            return None

        # Get the most recent trading days
        recent_data = data.tail(days)

        if len(recent_data) < days:
            print(f"⚠️ Insufficient data for {symbol}: "
                  f"only {len(recent_data)} days available")
            return recent_data if len(recent_data) >= 3 else None

        return recent_data

    except Exception as e:
        print(f"❌ Error fetching data for {symbol}: {str(e)}")
        return None


def analyze_local_extreme_highs(
    data: pd.DataFrame
) -> Optional[Dict[str, Any]]:
    """
    Analyze if previous day shows a local extreme high pattern.
    Local Extreme High: Yesterday's high > max(today's high, 2-days-ago high)

    Returns:
        Dict with analysis results or None if insufficient data
    """
    if len(data) < 3:
        return None

    # Get the last 3 days (today, yesterday, 2 days ago)
    recent_days = data.tail(3)

    today_high = recent_days.iloc[-1]['High']
    yesterday_high = recent_days.iloc[-2]['High']
    two_days_ago_high = recent_days.iloc[-3]['High']
    yesterday_close = recent_days.iloc[-2]['Close']

    # Check local extreme high condition
    is_local_extreme_high = yesterday_high > max(today_high, two_days_ago_high)

    if not is_local_extreme_high:
        return None

    return {
        'type': 'local_extreme_high',
        'close_price': yesterday_close,
        'high_price': yesterday_high,
        'date': recent_days.index[-2].strftime('%Y-%m-%d')
    }


def analyze_local_close_highs(data: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """
    Analyze if previous day shows a local close high pattern.
    Local Close High: Yesterday's close > max(today's close, 2-days-ago close)

    Returns:
        Dict with analysis results or None if insufficient data
    """
    if len(data) < 3:
        return None

    # Get the last 3 days (today, yesterday, 2 days ago)
    recent_days = data.tail(3)

    today_close = recent_days.iloc[-1]['Close']
    yesterday_close = recent_days.iloc[-2]['Close']
    two_days_ago_close = recent_days.iloc[-3]['Close']

    # Check local close high condition
    is_local_close_high = yesterday_close > max(
        today_close, two_days_ago_close
    )

    if not is_local_close_high:
        return None

    return {
        'type': 'local_close_high',
        'close_price': yesterday_close,
        'date': recent_days.index[-2].strftime('%Y-%m-%d')
    }


def analyze_local_extreme_lows(data: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """
    Analyze if previous day shows a local extreme low pattern.
    Local Extreme Low: Yesterday's low < min(today's low, 2-days-ago low)

    Returns:
        Dict with analysis results or None if insufficient data
    """
    if len(data) < 3:
        return None

    # Get the last 3 days (today, yesterday, 2 days ago)
    recent_days = data.tail(3)

    today_low = recent_days.iloc[-1]['Low']
    yesterday_low = recent_days.iloc[-2]['Low']
    two_days_ago_low = recent_days.iloc[-3]['Low']
    yesterday_close = recent_days.iloc[-2]['Close']

    # Check local extreme low condition
    is_local_extreme_low = yesterday_low < min(today_low, two_days_ago_low)

    if not is_local_extreme_low:
        return None

    return {
        'type': 'local_extreme_low',
        'close_price': yesterday_close,
        'low_price': yesterday_low,
        'date': recent_days.index[-2].strftime('%Y-%m-%d')
    }


def analyze_local_close_lows(data: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """
    Analyze if previous day shows a local close low pattern.
    Local Close Low: Yesterday's close < min(today's close, 2-days-ago close)

    Returns:
        Dict with analysis results or None if insufficient data
    """
    if len(data) < 3:
        return None

    # Get the last 3 days (today, yesterday, 2 days ago)
    recent_days = data.tail(3)

    today_close = recent_days.iloc[-1]['Close']
    yesterday_close = recent_days.iloc[-2]['Close']
    two_days_ago_close = recent_days.iloc[-3]['Close']

    # Check local close low condition
    is_local_close_low = yesterday_close < min(today_close, two_days_ago_close)

    if not is_local_close_low:
        return None

    return {
        'type': 'local_close_low',
        'close_price': yesterday_close,
        'date': recent_days.index[-2].strftime('%Y-%m-%d')
    }


def read_stock_symbols_csv(file_path: str = 'stock_symbols.csv') -> List[str]:
    """Read stock symbols from CSV file."""
    symbols = []
    try:
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if 'symbol' in row:
                    symbols.append(row['symbol'].strip().upper())
        return symbols
    except FileNotFoundError:
        print(f"❌ Stock symbols file not found: {file_path}")
        return []
    except Exception as e:
        print(f"❌ Error reading stock symbols: {str(e)}")
        return []


def format_results_pretty(results: List[Dict[str, Any]]) -> None:
    """Format and print results in an attractive console format."""
    if not results:
        print("📊 No local highs or lows detected today.")
        return

    print("\n" + "=" * 80)
    print("📈 DAILY HIGH LOW STOCK ANALYSIS RESULTS")
    print("=" * 80)

    extreme_highs = [r for r in results if r['type'] == 'local_extreme_high']
    close_highs = [r for r in results if r['type'] == 'local_close_high']
    extreme_lows = [r for r in results if r['type'] == 'local_extreme_low']
    close_lows = [r for r in results if r['type'] == 'local_close_low']

    if extreme_highs:
        print("\n🔺 LOCAL EXTREME HIGHS:")
        print("-" * 50)
        for result in extreme_highs:
            symbol = result['symbol']
            close = result['close_price']
            high = result['high_price']
            date = result['date']

            print(f"  {symbol:6} | {date} | Close: ${close:8.2f} | "
                  f"High: ${high:8.2f}")
            print("         | Type: Yesterday's high > max(today, 2-days-ago)")
            print()

    if close_highs:
        print("\n📊 LOCAL CLOSE HIGHS:")
        print("-" * 50)
        for result in close_highs:
            symbol = result['symbol']
            close = result['close_price']
            date = result['date']

            print(f"  {symbol:6} | {date} | Close: ${close:8.2f}")
            print("         | Type: Yesterday's close > max(today, "
                  "2-days-ago)")
            print()

    if extreme_lows:
        print("\n🔻 LOCAL EXTREME LOWS:")
        print("-" * 50)
        for result in extreme_lows:
            symbol = result['symbol']
            close = result['close_price']
            low = result['low_price']
            date = result['date']

            print(f"  {symbol:6} | {date} | Close: ${close:8.2f} | "
                  f"Low: ${low:8.2f}")
            print("         | Type: Yesterday's low < min(today, 2-days-ago)")
            print()

    if close_lows:
        print("\n📉 LOCAL CLOSE LOWS:")
        print("-" * 50)
        for result in close_lows:
            symbol = result['symbol']
            close = result['close_price']
            date = result['date']

            print(f"  {symbol:6} | {date} | Close: ${close:8.2f}")
            print("         | Type: Yesterday's close < min(today, "
                  "2-days-ago)")
            print()

    print("=" * 80)
    total_patterns = (len(extreme_highs) + len(close_highs)
                      + len(extreme_lows) + len(close_lows))
    print(f"📊 Summary: {len(extreme_highs)} extreme highs, "
          f"{len(close_highs)} close highs, "
          f"{len(extreme_lows)} extreme lows, {len(close_lows)} close lows")
    print(f"📊 Total patterns detected: {total_patterns}")


def format_results_json(results: List[Dict[str, Any]]) -> str:
    """Format results as JSON for Lambda/SNS output."""
    extreme_highs = [r for r in results if r['type'] == 'local_extreme_high']
    close_highs = [r for r in results if r['type'] == 'local_close_high']
    extreme_lows = [r for r in results if r['type'] == 'local_extreme_low']
    close_lows = [r for r in results if r['type'] == 'local_close_low']

    return json.dumps({
        'timestamp': datetime.now().isoformat(),
        'total_symbols_analyzed': len(set(r['symbol'] for r in results)),
        'local_extreme_highs': extreme_highs,
        'local_close_highs': close_highs,
        'local_extreme_lows': extreme_lows,
        'local_close_lows': close_lows,
        'summary': {
            'extreme_highs_count': len(extreme_highs),
            'close_highs_count': len(close_highs),
            'extreme_lows_count': len(extreme_lows),
            'close_lows_count': len(close_lows),
            'total_patterns': len(results)
        }
    }, indent=2)


def publish_to_sns(results: List[Dict[str, Any]], topic_arn: str) -> bool:
    """Publish results to SNS topic."""
    try:
        sns = boto3.client('sns')
        message = format_results_json(results)

        response = sns.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject='Daily High Low Stock Analysis Results'
        )

        print(f"✅ Published to SNS: {response['MessageId']}")
        return True

    except ClientError as e:
        print(f"❌ SNS publish error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error publishing to SNS: {e}")
        return False


def analyze_stocks(symbols: List[str]) -> List[Dict[str, Any]]:
    """Analyze a list of stock symbols for local highs and lows."""
    results = []
    total_symbols = len(symbols)

    print(f"🔍 Analyzing {total_symbols} stock symbols...")

    for i, symbol in enumerate(symbols, 1):
        print(f"  [{i}/{total_symbols}] Processing {symbol}...", end=" ")

        # Fetch stock data
        data = get_stock_data(symbol)
        if data is None:
            continue

        has_pattern = False

        # Check for local extreme high
        extreme_high_result = analyze_local_extreme_highs(data)
        if extreme_high_result:
            extreme_high_result['symbol'] = symbol
            results.append(extreme_high_result)
            print("📈E", end=" ")
            has_pattern = True

        # Check for local close high
        close_high_result = analyze_local_close_highs(data)
        if close_high_result:
            close_high_result['symbol'] = symbol
            results.append(close_high_result)
            print("📈C", end=" ")
            has_pattern = True

        # Check for local extreme low
        extreme_low_result = analyze_local_extreme_lows(data)
        if extreme_low_result:
            extreme_low_result['symbol'] = symbol
            results.append(extreme_low_result)
            print("📉E", end=" ")
            has_pattern = True

        # Check for local close low
        close_low_result = analyze_local_close_lows(data)
        if close_low_result:
            close_low_result['symbol'] = symbol
            results.append(close_low_result)
            print("📉C", end=" ")
            has_pattern = True

        if not has_pattern:
            print("➖", end=" ")

        print("✓")

        # Add delay between requests
        if i < total_symbols:
            add_request_delay(0.5)

    return results


def lambda_handler(event, context):
    """AWS Lambda entry point with EventBridge integration."""
    try:
        # Get symbols from EventBridge event
        symbols = event.get('symbols', [])

        if not symbols:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No symbols provided in event'})
            }

        # Analyze stocks
        results = analyze_stocks(symbols)

        # Publish to SNS if topic ARN provided
        sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')
        if sns_topic_arn:
            publish_to_sns(results, sns_topic_arn)

        # Return results
        return {
            'statusCode': 200,
            'body': format_results_json(results)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def main():
    """Local execution entry point."""
    print("🚀 Daily High Low Stock Analysis")
    print("================================")

    # Read stock symbols from CSV
    symbols = read_stock_symbols_csv()

    if not symbols:
        print("❌ No stock symbols to analyze. "
              "Please check stock_symbols.csv file.")
        return

    # Analyze stocks
    results = analyze_stocks(symbols)

    # Display results
    format_results_pretty(results)


if __name__ == "__main__":
    # Check if running in AWS Lambda
    if os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
        # This would be handled by Lambda runtime
        pass
    else:
        # Run locally
        main()
