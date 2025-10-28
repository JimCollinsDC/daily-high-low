import time
import csv
import json
import argparse
from datetime import datetime, timedelta
from typing import List, Optional
import yfinance as yf
import pandas as pd
from curl_cffi import requests
import numpy as np
from dataclasses import dataclass


@dataclass
class BacktestResult:
    """Results from backtesting a single stock."""
    symbol: str
    total_return: float
    win_rate: float
    total_trades: int
    profitable_trades: int
    avg_return_per_trade: float
    max_drawdown: float
    sharpe_ratio: float
    volatility: float
    analysis_days: int


def add_request_delay(delay_seconds: float = 1.0) -> None:
    """Add delay between requests to avoid rate limiting."""
    time.sleep(delay_seconds)


def get_historical_stock_data(symbol: str, days: int = 252) -> Optional[pd.DataFrame]:
    """
    Fetch extended historical stock data for backtesting.
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL')
        days: Number of days of historical data (default 252 = ~1 year)
        
    Returns:
        DataFrame with historical stock data or None if failed
    """
    try:
        # Use curl_cffi session to simulate Chrome browser
        session = requests.Session(impersonate="chrome110")
        
        # Create yfinance ticker with custom session
        ticker = yf.Ticker(symbol)
        ticker.session = session
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days + 10)
        
        # Fetch historical data
        data = ticker.history(start=start_date, end=end_date)
        
        if data.empty:
            print(f"❌ No historical data available for {symbol}")
            return None
            
        # Dynamic minimum based on requested period
        min_required = max(10, int(days * 0.4))  # At least 40% of requested days
        if len(data) < min_required:
            print(f"⚠️ Insufficient historical data for {symbol}: "
                  f"only {len(data)} days (need {min_required})")
            return None
            
        return data
        
    except Exception as e:
        print(f"❌ Error fetching historical data for {symbol}: {str(e)}")
        return None


def has_extreme_price_movement(data: pd.DataFrame, index: int, 
                               threshold: float = 0.25) -> bool:
    """
    Check if a day has extreme price movement that should be filtered out.
    
    Args:
        data: Historical stock data
        index: Index of the day to check
        threshold: Price movement threshold (default 0.25 = 25%)
        
    Returns:
        True if extreme movement detected (should be filtered out)
    """
    if index < 1 or index >= len(data):
        return False
    
    current_close = data.iloc[index]['Close']
    previous_close = data.iloc[index - 1]['Close']
    
    # Calculate daily price change percentage
    price_change_pct = abs(current_close - previous_close) / previous_close
    
    return price_change_pct >= threshold


def filter_extreme_events(data: pd.DataFrame, 
                          threshold: float = 0.25) -> pd.DataFrame:
    """
    Filter out days with extreme price movements and surrounding days.
    
    Args:
        data: Historical stock data
        threshold: Price movement threshold (default 0.25 = 25%)
        
    Returns:
        Filtered DataFrame with extreme events removed
    """
    if len(data) < 5:  # Need minimum data for filtering
        return data
    
    # Identify extreme movement days
    extreme_days = []
    for i in range(1, len(data)):
        if has_extreme_price_movement(data, i, threshold):
            extreme_days.append(i)
    
    if not extreme_days:
        return data  # No extreme events found
    
    # Create mask to exclude extreme days and buffer days around them
    exclude_indices = set()
    buffer_days = 2  # Exclude 2 days before and after extreme events
    
    for extreme_day in extreme_days:
        for offset in range(-buffer_days, buffer_days + 1):
            exclude_idx = extreme_day + offset
            if 0 <= exclude_idx < len(data):
                exclude_indices.add(exclude_idx)
    
    # Filter out extreme events and surrounding days
    filtered_data = data.iloc[[i for i in range(len(data)) 
                               if i not in exclude_indices]]
    
    print(f"   📊 Filtered out {len(exclude_indices)} days with extreme "
          f"events (>{threshold*100:.0f}% moves)")
    
    return filtered_data.reset_index(drop=True) if not filtered_data.empty else data


def detect_local_extreme_high_historical(data: pd.DataFrame, 
                                          index: int) -> bool:
    """
    Check if a specific day had a local extreme high.
    
    Args:
        data: Historical stock data
        index: Index of the day to check (must be >= 1 and < len-1)
        
    Returns:
        True if local extreme high detected
    """
    if index < 1 or index >= len(data) - 1:
        return False
    
    yesterday_high = data.iloc[index]['High']
    today_high = data.iloc[index + 1]['High']
    two_days_ago_high = data.iloc[index - 1]['High']
    
    return yesterday_high > max(today_high, two_days_ago_high)


def detect_local_extreme_low_historical(data: pd.DataFrame, 
                                         index: int) -> bool:
    """
    Check if a specific day had a local extreme low.
    
    Args:
        data: Historical stock data
        index: Index of the day to check (must be >= 1 and < len-1)
        
    Returns:
        True if local extreme low detected
    """
    if index < 1 or index >= len(data) - 1:
        return False
    
    yesterday_low = data.iloc[index]['Low']
    today_low = data.iloc[index + 1]['Low']
    two_days_ago_low = data.iloc[index - 1]['Low']
    
    return yesterday_low < min(today_low, two_days_ago_low)


def detect_local_close_high_historical(data: pd.DataFrame, 
                                        index: int) -> bool:
    """
    Check if a specific day had a local close high.
    
    Args:
        data: Historical stock data
        index: Index of the day to check (must be >= 1 and < len-1)
        
    Returns:
        True if local close high detected
    """
    if index < 1 or index >= len(data) - 1:
        return False
    
    yesterday_close = data.iloc[index]['Close']
    today_close = data.iloc[index + 1]['Close']
    two_days_ago_close = data.iloc[index - 1]['Close']
    
    return yesterday_close > max(today_close, two_days_ago_close)


def detect_local_close_low_historical(data: pd.DataFrame, 
                                       index: int) -> bool:
    """
    Check if a specific day had a local close low.
    
    Args:
        data: Historical stock data
        index: Index of the day to check (must be >= 1 and < len-1)
        
    Returns:
        True if local close low detected
    """
    if index < 1 or index >= len(data) - 1:
        return False
    
    yesterday_close = data.iloc[index]['Close']
    today_close = data.iloc[index + 1]['Close']
    two_days_ago_close = data.iloc[index - 1]['Close']
    
    return yesterday_close < min(today_close, two_days_ago_close)


def simulate_trading_strategy(data: pd.DataFrame, symbol: str, 
                              filter_extremes: bool = True, 
                              extreme_threshold: float = 0.25,
                              requested_days: int = 252) -> BacktestResult:
    """
    Simulate trading strategy based on local high/low signals.
    
    Strategy:
    - Buy on local extreme low signals
    - Sell on local extreme high signals
    - Hold period: until opposite signal or max 10 days
    - Filter out extreme price movement days to avoid outliers
    
    Args:
        data: Historical stock data
        symbol: Stock symbol
        filter_extremes: Whether to filter out extreme price movements
        extreme_threshold: Threshold for extreme movements (default 0.25 = 25%)
        requested_days: Original requested analysis period for validation
        
    Returns:
        BacktestResult with performance metrics
    """
    # Apply extreme event filtering if requested
    if filter_extremes:
        original_days = len(data)
        data = filter_extreme_events(data, extreme_threshold)
        filtered_days = len(data)
        
        if filtered_days < original_days:
            print(f"   🔍 Analysis period reduced from {original_days} to "
                  f"{filtered_days} days after filtering")
    
    # Dynamic minimum based on requested period and filtering
    min_required_after_filter = max(5, int(requested_days * 0.2))  # At least 20% of requested
    
    # Ensure we still have enough data after filtering
    if len(data) < min_required_after_filter:
        print(f"   ⚠️ Insufficient data after filtering for {symbol}: "
              f"only {len(data)} days (need {min_required_after_filter})")
        return BacktestResult(
            symbol=symbol,
            total_return=0.0,
            win_rate=0.0,
            total_trades=0,
            profitable_trades=0,
            avg_return_per_trade=0.0,
            max_drawdown=0.0,
            sharpe_ratio=0.0,
            volatility=0.0,
            analysis_days=len(data)
        )
    
    trades = []
    position = None  # None, 'long', or 'short'
    position_entry_price = 0
    position_entry_date = None
    position_days_held = 0
    max_hold_days = 10
    
    # Track portfolio value over time for drawdown calculation
    portfolio_values = []
    initial_capital = 10000
    current_capital = initial_capital
    
    for i in range(1, len(data) - 1):
        current_price = data.iloc[i + 1]['Close']
        current_date = data.index[i + 1]
        
        # Check for signals
        extreme_high = detect_local_extreme_high_historical(data, i)
        extreme_low = detect_local_extreme_low_historical(data, i)
        close_high = detect_local_close_high_historical(data, i)
        close_low = detect_local_close_low_historical(data, i)
        
        # Exit position if held too long
        if position and position_days_held >= max_hold_days:
            if position == 'long':
                return_pct = (current_price - position_entry_price) / position_entry_price
                current_capital *= (1 + return_pct)
                trades.append({
                    'entry_date': position_entry_date,
                    'exit_date': current_date,
                    'entry_price': position_entry_price,
                    'exit_price': current_price,
                    'position': position,
                    'return_pct': return_pct,
                    'reason': 'max_hold_exceeded'
                })
            position = None
            position_days_held = 0
        
        # Trading logic
        if position is None:
            # Look for entry signals
            if extreme_low or close_low:
                # Enter long position (buy)
                position = 'long'
                position_entry_price = current_price
                position_entry_date = current_date
                position_days_held = 0
        else:
            position_days_held += 1
            
            # Look for exit signals
            if position == 'long' and (extreme_high or close_high):
                # Exit long position (sell)
                return_pct = (current_price - position_entry_price) / position_entry_price
                current_capital *= (1 + return_pct)
                trades.append({
                    'entry_date': position_entry_date,
                    'exit_date': current_date,
                    'entry_price': position_entry_price,
                    'exit_price': current_price,
                    'position': position,
                    'return_pct': return_pct,
                    'reason': 'signal_exit'
                })
                position = None
                position_days_held = 0
        
        portfolio_values.append(current_capital)
    
    # Calculate performance metrics
    if not trades:
        return BacktestResult(
            symbol=symbol,
            total_return=0.0,
            win_rate=0.0,
            total_trades=0,
            profitable_trades=0,
            avg_return_per_trade=0.0,
            max_drawdown=0.0,
            sharpe_ratio=0.0,
            volatility=0.0,
            analysis_days=len(data)
        )
    
    total_return = (current_capital - initial_capital) / initial_capital
    profitable_trades = sum(1 for trade in trades if trade['return_pct'] > 0)
    win_rate = profitable_trades / len(trades) if trades else 0
    avg_return_per_trade = float(np.mean([trade['return_pct'] for trade in trades]))
    
    # Calculate max drawdown
    peak = initial_capital
    max_drawdown = 0
    for value in portfolio_values:
        if value > peak:
            peak = value
        drawdown = (peak - value) / peak
        max_drawdown = max(max_drawdown, drawdown)
    
    # Calculate Sharpe ratio (simplified)
    returns = [trade['return_pct'] for trade in trades]
    if returns:
        volatility = float(np.std(returns))
        sharpe_ratio = avg_return_per_trade / volatility if volatility > 0 else 0
    else:
        volatility = 0
        sharpe_ratio = 0
    
    return BacktestResult(
        symbol=symbol,
        total_return=total_return,
        win_rate=win_rate,
        total_trades=len(trades),
        profitable_trades=profitable_trades,
        avg_return_per_trade=avg_return_per_trade,
        max_drawdown=max_drawdown,
        sharpe_ratio=float(sharpe_ratio),
        volatility=volatility,
        analysis_days=len(data)
    )


def read_candidate_stocks_csv(file_path: str = 'candidate_stocks.csv') -> List[str]:
    """Read candidate stock symbols from CSV file."""
    symbols = []
    try:
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Handle different CSV formats
            if 'Stock Symbol' in reader.fieldnames:
                # CBOE format: "Stock Symbol,Company Name"
                for row in reader:
                    symbol = row['Stock Symbol'].strip().upper()
                    if symbol and not symbol.startswith('#'):  # Skip comments
                        symbols.append(symbol)
            elif 'symbol' in reader.fieldnames:
                # Standard format: "symbol,name"
                for row in reader:
                    symbol = row['symbol'].strip().upper()
                    if symbol and not symbol.startswith('#'):  # Skip comments
                        symbols.append(symbol)
            else:
                # Try first column
                first_col = reader.fieldnames[0] if reader.fieldnames else None
                if first_col:
                    for row in reader:
                        symbol = row[first_col].strip().upper()
                        if symbol and not symbol.startswith('#'):
                            symbols.append(symbol)
        
        return symbols
    except FileNotFoundError:
        print(f"❌ Candidate stocks file not found: {file_path}")
        print("Creating example file...")
        create_example_candidate_stocks_file(file_path)
        return []
    except Exception as e:
        print(f"❌ Error reading candidate stocks: {str(e)}")
        return []


def read_cboe_symbols_csv(file_path: str = 'cboesymboldirweeklys.csv') -> List[str]:
    """Read CBOE weekly options symbols from CSV file."""
    symbols = []
    try:
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if 'Stock Symbol' in row:
                    symbol = row['Stock Symbol'].strip().upper()
                    # Filter out ETFs and complex instruments for basic analysis
                    if (symbol and 
                        not symbol.startswith('#') and 
                        len(symbol) <= 5 and  # Basic stock symbols
                        not any(x in row['Company Name'].upper() for x in 
                               ['ETF', 'FUTURES', 'VIX', 'BITCOIN', 'ETHER'])):
                        symbols.append(symbol)
        
        print(f"📊 Loaded {len(symbols)} filtered stock symbols from CBOE file")
        return symbols
    except FileNotFoundError:
        print(f"❌ CBOE symbols file not found: {file_path}")
        return []
    except Exception as e:
        print(f"❌ Error reading CBOE symbols: {str(e)}")
        return []


def create_example_candidate_stocks_file(file_path: str) -> None:
    """Create an example candidate stocks CSV file."""
    example_stocks = [
        {'symbol': 'AAPL', 'name': 'Apple Inc.'},
        {'symbol': 'MSFT', 'name': 'Microsoft Corporation'},
        {'symbol': 'GOOGL', 'name': 'Alphabet Inc.'},
        {'symbol': 'AMZN', 'name': 'Amazon.com Inc.'},
        {'symbol': 'TSLA', 'name': 'Tesla Inc.'},
        {'symbol': 'NVDA', 'name': 'NVIDIA Corporation'},
        {'symbol': 'META', 'name': 'Meta Platforms Inc.'},
        {'symbol': 'NFLX', 'name': 'Netflix Inc.'},
        {'symbol': 'JPM', 'name': 'JPMorgan Chase & Co.'},
        {'symbol': 'JNJ', 'name': 'Johnson & Johnson'},
        {'symbol': 'V', 'name': 'Visa Inc.'},
        {'symbol': 'PG', 'name': 'Procter & Gamble'},
        {'symbol': 'UNH', 'name': 'UnitedHealth Group'},
        {'symbol': 'HD', 'name': 'Home Depot'},
        {'symbol': 'MA', 'name': 'Mastercard Inc.'},
    ]
    
    try:
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['symbol', 'name'])
            writer.writeheader()
            writer.writerows(example_stocks)
        print(f"✅ Created example file: {file_path}")
    except Exception as e:
        print(f"❌ Error creating example file: {str(e)}")


def format_profitability_results(results: List[BacktestResult]) -> None:
    """Format and display profitability analysis results."""
    if not results:
        print("📊 No profitability results to display.")
        return
    
    # Sort by total return (descending)
    results.sort(key=lambda x: x.total_return, reverse=True)
    
    print("\n" + "=" * 100)
    print("📊 STOCK PROFITABILITY ANALYSIS RESULTS")
    print("=" * 100)
    print(f"{'Rank':<4} {'Symbol':<8} {'Total Return':<12} {'Win Rate':<10} "
          f"{'Trades':<8} {'Avg/Trade':<12} {'Sharpe':<8} {'Max DD':<10}")
    print("-" * 100)
    
    for i, result in enumerate(results, 1):
        print(f"{i:<4} {result.symbol:<8} "
              f"{result.total_return:+7.1%}     "
              f"{result.win_rate:6.1%}     "
              f"{result.total_trades:<8} "
              f"{result.avg_return_per_trade:+7.1%}     "
              f"{result.sharpe_ratio:6.2f}  "
              f"{result.max_drawdown:6.1%}")
    
    print("-" * 100)
    print(f"📈 Best performer: {results[0].symbol} "
          f"({results[0].total_return:+.1%} return)")
    if len(results) > 1:
        print(f"📉 Worst performer: {results[-1].symbol} "
              f"({results[-1].total_return:+.1%} return)")
    
    # Show statistics
    positive_returns = [r for r in results if r.total_return > 0]
    print(f"\n📊 Summary Statistics:")
    print(f"   • Profitable stocks: {len(positive_returns)}/{len(results)} "
          f"({len(positive_returns)/len(results)*100:.1f}%)")
    if results:
        avg_return = sum(r.total_return for r in results) / len(results)
        print(f"   • Average return: {avg_return:+.1%}")


def save_results_to_json(results: List[BacktestResult]) -> None:
    """Save results to JSON file for further analysis."""
    if not results:
        return
    
    # Convert results to dictionary format
    results_dict = []
    for result in results:
        results_dict.append({
            'symbol': result.symbol,
            'total_return': result.total_return,
            'win_rate': result.win_rate,
            'total_trades': result.total_trades,
            'profitable_trades': result.profitable_trades,
            'avg_return_per_trade': result.avg_return_per_trade,
            'max_drawdown': result.max_drawdown,
            'sharpe_ratio': result.sharpe_ratio,
            'volatility': result.volatility,
            'analysis_days': result.analysis_days
        })
    
    # Sort by total return
    results_dict.sort(key=lambda x: x['total_return'], reverse=True)
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"profitability_results_{timestamp}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(results_dict, f, indent=2)
        print(f"💾 Results saved to: {filename}")
    except Exception as e:
        print(f"❌ Error saving results: {str(e)}")


def main(filter_extremes: bool = True, extreme_threshold: float = 0.25,
         use_cboe: bool = False, symbol_file: str = None, max_symbols: int = None,
         lookback_days: int = 252):
    """
    Main function for profitability analysis.
    
    Args:
        filter_extremes: Whether to filter out extreme price movements
        extreme_threshold: Threshold for extreme movements (default 0.25 = 25%)
        use_cboe: Whether to use CBOE symbols file
        symbol_file: Custom symbol file path
        max_symbols: Maximum number of symbols to analyze (for testing)
        lookback_days: Number of days of historical data (default 252 = 1 year)
    """
    print("🚀 Stock Profitability Analysis Tool")
    print("=====================================")
    print("Analyzing which stocks are most profitable using "
          "local high/low detection strategy")
    
    print(f"📅 Analysis period: {lookback_days} trading days "
          f"(~{lookback_days/252:.1f} years)")
    
    if filter_extremes:
        print(f"🔍 Filtering out extreme price movements "
              f"(>{extreme_threshold*100:.0f}% daily changes)")
    else:
        print("⚠️ Including all price movements (no extreme event filtering)")
    
    # Read candidate stocks
    if symbol_file:
        candidate_stocks = read_candidate_stocks_csv(symbol_file)
        print(f"📂 Using custom symbol file: {symbol_file}")
    elif use_cboe:
        candidate_stocks = read_cboe_symbols_csv()
        print("📈 Using CBOE weekly options symbols (filtered)")
    else:
        candidate_stocks = read_candidate_stocks_csv()
        print("📋 Using default candidate_stocks.csv file")
    
    if not candidate_stocks:
        print("❌ No candidate stocks to analyze. "
              "Please check your symbol file.")
        return
    
    # Limit symbols for testing if requested
    if max_symbols and len(candidate_stocks) > max_symbols:
        candidate_stocks = candidate_stocks[:max_symbols]
        print(f"🔬 Limited to first {max_symbols} symbols for testing")
    
    print(f"🔍 Analyzing {len(candidate_stocks)} candidate stocks...")
    print("⏱️ This may take a while due to rate limiting...")
    
    results = []
    
    for i, symbol in enumerate(candidate_stocks, 1):
        print(f"\n[{i}/{len(candidate_stocks)}] Analyzing {symbol}...", 
              end=" ")
        
        # Fetch historical data with custom lookback period
        historical_data = get_historical_stock_data(symbol, days=lookback_days)
        if historical_data is None:
            print("❌ Skipped")
            continue
        
        # Run backtest with extreme filtering
        result = simulate_trading_strategy(historical_data, symbol, 
                                           filter_extremes, extreme_threshold,
                                           lookback_days)
        results.append(result)
        
        print(f"✅ Return: {result.total_return:+.1%}, "
              f"Win Rate: {result.win_rate:.1%}, "
              f"Trades: {result.total_trades}")
        
        # Add delay between requests
        if i < len(candidate_stocks):
            add_request_delay(1.0)
    
    # Display results
    format_profitability_results(results)
    
    # Save results
    save_results_to_json(results)
    
    print(f"\n✅ Analysis complete! Results saved for {len(results)} stocks.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Stock Profitability Analysis - Find profitable stocks'
    )
    parser.add_argument(
        '--no-filter',
        action='store_true',
        help='Disable extreme event filtering (include all movements)'
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=0.25,
        help='Extreme movement threshold as decimal (default: 0.25 = 25%%)'
    )
    parser.add_argument(
        '--cboe',
        action='store_true',
        help='Use CBOE weekly options symbols instead of candidate_stocks.csv'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Custom symbol file path (CSV format)'
    )
    parser.add_argument(
        '--max-symbols',
        type=int,
        help='Maximum number of symbols to analyze (for testing)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=252,
        help='Number of trading days to analyze (default: 252 = 1 year)'
    )
    
    args = parser.parse_args()
    
    # Run analysis with specified parameters
    main(filter_extremes=not args.no_filter,
         extreme_threshold=args.threshold,
         use_cboe=args.cboe,
         symbol_file=args.file,
         max_symbols=args.max_symbols,
         lookback_days=args.days)