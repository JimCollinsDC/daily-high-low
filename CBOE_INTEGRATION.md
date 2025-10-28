# CBOE Symbols Integration Guide

## Overview
The profitability analyzer now supports the CBOE (Chicago Board Options Exchange) weekly options symbols directory, providing access to 600+ actively traded stocks for comprehensive analysis.

## Features

### Automatic Symbol Filtering
The system intelligently filters the CBOE symbol list to include only regular stocks suitable for the local high/low strategy:

**Filtered OUT** (examples):
- ❌ ETFs (SVIX, BITX, ETHU)
- ❌ VIX-related products (UVIX, SVIX)
- ❌ Cryptocurrency funds (BITX, ETHU)
- ❌ Complex derivatives and futures
- ❌ Symbols longer than 5 characters

**Included FOR ANALYSIS** (examples):
- ✅ Large caps (MMM, ABT, ABBV, ACN, ADBE)
- ✅ Mid caps (ANF, ASO, AAP)
- ✅ Tech stocks (AMD, ADBE)
- ✅ All sectors represented

### Usage Options

```bash
# Use CBOE symbols (607 filtered stocks)
python profitability_analyzer.py --cboe

# Test with first 10 CBOE symbols
python profitability_analyzer.py --cboe --max-symbols 10

# Use CBOE with custom filtering threshold
python profitability_analyzer.py --cboe --threshold 0.15

# Use CBOE without extreme event filtering
python profitability_analyzer.py --cboe --no-filter

# Use custom symbol file
python profitability_analyzer.py --file your_symbols.csv

# Show all options
python profitability_analyzer.py --help
```

### File Format Support

The analyzer now supports multiple CSV formats:

1. **CBOE Format**: `Stock Symbol,Company Name`
2. **Standard Format**: `symbol,name` 
3. **Custom Format**: Auto-detects first column as symbols

### Performance Expectations

**Full CBOE Analysis** (607 stocks):
- Estimated time: 10-12 hours (1-second delays)
- Output: Comprehensive ranking of all major stocks
- Best for: Complete market analysis

**Sample Analysis** (10-50 stocks):
- Estimated time: 10-50 minutes
- Output: Quick insights into top performers
- Best for: Testing and strategy validation

## Results Quality

The CBOE symbol list provides:
- **Comprehensive Coverage**: Major stocks across all sectors
- **High Liquidity**: Only actively traded securities
- **Weekly Options**: Stocks with weekly option expiration
- **Quality Filter**: Excludes complex instruments
- **Professional Grade**: Exchange-maintained accuracy

## Example Output

```
📊 Loaded 607 filtered stock symbols from CBOE file
📈 Using CBOE weekly options symbols (filtered)
🔍 Analyzing 607 candidate stocks...

[1/607] Analyzing MMM... ✅ Return: +5.2%, Win Rate: 36.7%, Trades: 49
[2/607] Analyzing ABT... ✅ Return: -8.1%, Win Rate: 41.7%, Trades: 48
[3/607] Analyzing ABBV... ✅ Return: +35.6%, Win Rate: 54.8%, Trades: 42
...

📈 Best performer: ABBV (+35.6% return)
💾 Results saved to: profitability_results_20251010_210342.json
```

This integration transforms the tool from analyzing small symbol lists to comprehensive market-wide profitability analysis using professionally curated stock symbols.