#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stock Portfolio Tracker Bot
Tracks stock prices and portfolio value, sends updates to Slack
"""

import yfinance as yf
import requests
from datetime import datetime
import os
import sys

# Get Slack webhook from environment variable
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')

# YOUR PORTFOLIO - Edit this with your actual stocks
PORTFOLIO = {
    'AAPL': 1,    # Apple - 10 shares
    'MSFT': 1,     # Microsoft - 5 shares
    'VOO': 4.202,     # Vanguard S&P 500 ETF - 20 shares
    'QTUM': 4.681
    'QQQ': .187
    'SPY': 4.612
    'XLU': .578
    'JAAA': 2.067
    'SCHD': 5.564
    # Add your stocks here: 'SYMBOL': quantity
}

def get_stock_data(symbol):
    """Fetch current price and daily change for a stock"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period='2d')  # Get last 2 days for comparison
        
        if len(hist) < 1:
            print(f"No data available for {symbol}")
            return None
        
        current_price = hist['Close'].iloc[-1]
        
        # Calculate daily change if we have previous day data
        if len(hist) >= 2:
            prev_price = hist['Close'].iloc[-2]
            change = current_price - prev_price
            change_pct = (change / prev_price) * 100
        else:
            change = 0
            change_pct = 0
        
        return {
            'symbol': symbol,
            'price': current_price,
            'change': change,
            'change_pct': change_pct
        }
        
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def calculate_portfolio():
    """Calculate total portfolio value and format data"""
    print("Fetching stock prices...\n")
    
    portfolio_data = []
    total_value = 0
    total_daily_change = 0
    
    for symbol, shares in PORTFOLIO.items():
        print(f"Fetching {symbol}...")
        data = get_stock_data(symbol)
        
        if data:
            value = data['price'] * shares
            daily_change = data['change'] * shares
            
            portfolio_data.append({
                'symbol': symbol,
                'shares': shares,
                'price': data['price'],
                'value': value,
                'change': data['change'],
                'change_pct': data['change_pct'],
                'daily_change': daily_change
            })
            
            total_value += value
            total_daily_change += daily_change
            
            print(f"  {symbol}: ${data['price']:.2f} ({data['change_pct']:+.2f}%)")
    
    total_change_pct = (total_daily_change / (total_value - total_daily_change)) * 100 if total_value > 0 else 0
    
    print(f"\nTotal Portfolio Value: ${total_value:,.2f}")
    print(f"Daily Change: ${total_daily_change:+,.2f} ({total_change_pct:+.2f}%)")
    
    return portfolio_data, total_value, total_daily_change, total_change_pct

def format_message(portfolio_data, total_value, total_daily_change, total_change_pct):
    """Format portfolio data into Slack message"""
    
    # Determine emoji based on performance
    if total_daily_change > 0:
        emoji = "📈"
        trend = "up"
    elif total_daily_change < 0:
        emoji = "📉"
        trend = "down"
    else:
        emoji = "➡️"
        trend = "flat"
    
    message = f"{emoji} *Portfolio Update - {datetime.now().strftime('%B %d, %Y at %I:%M %p EST')}*\n\n"
    
    # Individual holdings
    for stock in portfolio_data:
        change_emoji = "🟢" if stock['change'] >= 0 else "🔴"
        message += f"{change_emoji} *{stock['symbol']}*\n"
        message += f"  {stock['shares']} shares @ ${stock['price']:.2f} = ${stock['value']:,.2f}\n"
        message += f"  Today: ${stock['change']:+.2f} ({stock['change_pct']:+.2f}%)\n\n"
    
    # Summary
    message += "─────────────────────\n"
    message += f"*Total Portfolio Value:* ${total_value:,.2f}\n"
    message += f"*Today's Change:* ${total_daily_change:+,.2f} ({total_change_pct:+.2f}%)\n"
    message += f"*Trend:* {trend.capitalize()}"
    
    return message

def send_to_slack(message):
    """Send formatted message to Slack"""
    
    if not SLACK_WEBHOOK_URL:
        print("\nError: SLACK_WEBHOOK_URL environment variable not set!")
        sys.exit(1)
    
    slack_data = {
        'text': message,
        'username': 'Stock Tracker Bot',
        'icon_emoji': ':chart_with_upwards_trend:'
    }
    
    try:
        print("\nSending to Slack...")
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json=slack_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print("Successfully sent to Slack!")
            return True
        else:
            print(f"Slack Error: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error sending to Slack: {e}")
        return False

def main():
    """Main function"""
    print("=" * 50)
    print("STOCK TRACKER BOT STARTING")
    print("=" * 50)
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Calculate portfolio
    portfolio_data, total_value, total_daily_change, total_change_pct = calculate_portfolio()
    
    # Format message
    message = format_message(portfolio_data, total_value, total_daily_change, total_change_pct)
    
    # Send to Slack
    success = send_to_slack(message)
    
    print("\n" + "=" * 50)
    if success:
        print("BOT COMPLETED SUCCESSFULLY")
    else:
        print("BOT COMPLETED WITH ERRORS")
    print("=" * 50)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

4. Click **"Commit new file"**

---

### **Step 3: Create requirements.txt**

1. Click **"Add file"** → **"Create new file"**
2. Name: `requirements.txt`
3. Paste:
```
yfinance==0.2.32
requests==2.31.0
