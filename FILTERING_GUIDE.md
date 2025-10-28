# Extreme Event Filtering in Stock Profitability Analysis

## Overview
The updated profitability analyzer now includes sophisticated filtering to exclude stocks with extreme price movements that are unlikely to repeat. This helps create more realistic backtesting results by removing outlier events.

## How Extreme Event Filtering Works

### Detection Criteria
- **Threshold**: Default 25% daily price movement (configurable)
- **Calculation**: Absolute percentage change from previous day's close
- **Buffer Zone**: Excludes 2 days before and after each extreme event

### Example Usage

```bash
# Run with default filtering (excludes 25%+ daily moves)
python profitability_analyzer.py

# Run with custom threshold (excludes 15%+ daily moves)
python profitability_analyzer.py --threshold 0.15

# Run without any filtering (include all movements)
python profitability_analyzer.py --no-filter

# Show help and options
python profitability_analyzer.py --help
```

### What Gets Filtered Out

The tool automatically identifies and excludes:
- **Earnings announcements** causing large price swings
- **Merger/acquisition news** creating abnormal volatility  
- **Major market events** (crashes, rallies)
- **Company-specific crises** (lawsuits, scandals)
- **Stock splits/dividends** causing price adjustments

### Benefits of Filtering

1. **More Realistic Results**: Removes one-time events unlikely to repeat
2. **Better Strategy Assessment**: Focuses on repeatable patterns
3. **Reduced Noise**: Eliminates outliers that skew performance metrics
4. **Improved Comparability**: Creates level playing field between stocks

### Output Changes

When filtering is active, you'll see additional information:
```
[1/30] Analyzing AAPL... 
   📊 Filtered out 8 days with extreme events (>25% moves)
   🔍 Analysis period reduced from 252 to 244 days after filtering
✅ Return: +12.5%, Win Rate: 65.2%, Trades: 23
```

### Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--threshold` | 0.25 | Daily movement threshold (25%) |
| `--no-filter` | False | Disable all filtering |
| Buffer days | 2 | Days excluded around extreme events |

This enhancement makes the profitability analysis more robust and practical for real-world trading strategy development.