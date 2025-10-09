import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import pandas as pd

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import app functions after path modification  # noqa: E402
from app import (analyze_local_extreme_highs, analyze_local_close_highs,
                 analyze_local_extreme_lows, analyze_local_close_lows,
                 get_stock_data)


class TestStockAnalysis(unittest.TestCase):

    def setUp(self):
        """Set up test data."""
        # Create sample stock data for 3-day analysis
        dates = pd.date_range(start='2025-10-06', end='2025-10-08', freq='D')
        self.sample_data = pd.DataFrame({
            # Yesterday (155) > max(today 152, 2-days-ago 150)
            'High': [150.0, 155.0, 152.0],
            # Yesterday (140) < min(today 149, 2-days-ago 145)
            'Low': [145.0, 140.0, 149.0],
            'Close': [148.0, 153.0, 151.0],
            'Open': [147.0, 151.0, 150.0],
            'Volume': [1000000, 1200000, 1100000]
        }, index=dates)

    def test_analyze_local_extreme_highs_detected(self):
        """Test local extreme high detection when condition is met."""
        result = analyze_local_extreme_highs(self.sample_data)

        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'local_extreme_high')
        self.assertEqual(result['high_price'], 155.0)
        self.assertEqual(result['close_price'], 153.0)

    def test_analyze_local_extreme_highs_not_detected(self):
        """Test local extreme high detection when condition is not met."""
        # Modify data so no local extreme high exists
        modified_data = self.sample_data.copy()
        # Yesterday high too low
        modified_data.iloc[-2, modified_data.columns.get_loc('High')] = 145.0

        result = analyze_local_extreme_highs(modified_data)
        self.assertIsNone(result)

    def test_analyze_local_close_highs_detected(self):
        """Test local close high detection when condition is met."""
        result = analyze_local_close_highs(self.sample_data)

        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'local_close_high')
        self.assertEqual(result['close_price'], 153.0)

    def test_analyze_local_extreme_lows_detected(self):
        """Test local extreme low detection when condition is met."""
        result = analyze_local_extreme_lows(self.sample_data)

        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'local_extreme_low')
        self.assertEqual(result['low_price'], 140.0)
        self.assertEqual(result['close_price'], 153.0)

    def test_analyze_local_close_lows_not_detected(self):
        """Test local close low detection when condition is not met."""
        # Modify data so no local close low exists
        modified_data = self.sample_data.copy()
        # Yesterday close too high
        modified_data.iloc[-2, modified_data.columns.get_loc('Close')] = 160.0

        result = analyze_local_close_lows(modified_data)
        self.assertIsNone(result)

    def test_insufficient_data(self):
        """Test behavior with insufficient data."""
        insufficient_data = self.sample_data.head(2)  # Only 2 days

        extreme_high_result = analyze_local_extreme_highs(insufficient_data)
        close_high_result = analyze_local_close_highs(insufficient_data)
        extreme_low_result = analyze_local_extreme_lows(insufficient_data)
        close_low_result = analyze_local_close_lows(insufficient_data)

        self.assertIsNone(extreme_high_result)
        self.assertIsNone(close_high_result)
        self.assertIsNone(extreme_low_result)
        self.assertIsNone(close_low_result)

    @patch('app.yf.Ticker')
    @patch('app.requests.Session')
    def test_get_stock_data_success(self, mock_session, mock_ticker):
        """Test successful stock data retrieval."""
        # Mock the yfinance response
        mock_ticker_instance = MagicMock()
        mock_ticker.return_value = mock_ticker_instance
        mock_ticker_instance.history.return_value = self.sample_data

        result = get_stock_data('AAPL')

        self.assertIsNotNone(result)
        self.assertIsInstance(result, pd.DataFrame)
        mock_ticker.assert_called_once_with('AAPL')

    @patch('app.yf.Ticker')
    @patch('app.requests.Session')
    def test_get_stock_data_empty_response(self, mock_session, mock_ticker):
        """Test handling of empty yfinance response."""
        # Mock empty response
        mock_ticker_instance = MagicMock()
        mock_ticker.return_value = mock_ticker_instance
        mock_ticker_instance.history.return_value = pd.DataFrame()

        result = get_stock_data('INVALID')

        self.assertIsNone(result)

    @patch('app.yf.Ticker')
    @patch('app.requests.Session')
    def test_get_stock_data_exception(self, mock_session, mock_ticker):
        """Test handling of exceptions during data retrieval."""
        # Mock exception
        mock_ticker.side_effect = Exception("Network error")

        result = get_stock_data('AAPL')

        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
