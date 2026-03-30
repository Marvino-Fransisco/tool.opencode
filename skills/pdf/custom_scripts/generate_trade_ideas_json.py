#!/usr/bin/env python3
"""
Generate JSON data file for trade ideas PDF generator.
Usage: python generate_trade_ideas_json.py --symbol "BTC/USD" --direction LONG --entry 50000 --sl 49000 --tp1 52000
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_RISK_WARNING = (
    "This report is for informational purposes only and does not constitute financial advice. "
    "Trading involves substantial risk of loss and is not suitable for all investors. "
    "Past performance is not indicative of future results. Always do your own research."
)


def calculate_risk_reward(entry, sl, tp):
    if not entry or not sl or not tp:
        return None
    
    try:
        entry = float(entry)
        sl = float(sl)
        tp = float(tp)
        
        risk = abs(entry - sl)
        reward = abs(tp - entry)
        
        if risk == 0:
            return None
        
        ratio = reward / risk
        return f"1:{ratio:.1f}"
    except (ValueError, ZeroDivisionError):
        return None


def detect_chart_images(charts_dir, symbol):
    charts = {}
    
    if not charts_dir or not os.path.isdir(charts_dir):
        return charts
    
    symbol_clean = symbol.replace('/', '_').replace('\\', '_').upper()
    
    patterns = {
        'chart_5m_vaval': [f'*{symbol_clean}*vaval*.png', f'*vaval*{symbol_clean}*.png', '*vaval*.png', '*vaval*.jpg', '*vaval*.jpeg'],
        'chart_5m_tpsl': [f'*{symbol_clean}*tpsl*.png', f'*tpsl*{symbol_clean}*.png', '*tpsl*.png', '*tpsl*.jpg', '*tpsl*.jpeg'],
    }
    
    for chart_key, pattern_list in patterns.items():
        for pattern in pattern_list:
            matches = list(Path(charts_dir).glob(pattern))
            if matches:
                charts[chart_key] = str(matches[0])
                break
    
    return charts


def generate_trade_name(direction, symbol, index):
    direction_prefix = "Long" if direction.upper() == "LONG" else "Short"
    return f"{direction_prefix} Setup #{index}"


def create_trade(args, index, charts_dir):
    symbol = args.symbol
    direction = args.direction.upper()
    entry = float(args.entry)
    sl = float(args.sl)
    tp1 = float(args.tp1)
    tp2 = float(args.tp2) if args.tp2 else None
    
    risk_reward = calculate_risk_reward(entry, sl, tp1)
    
    trade = {
        "trade_id": str(index),
        "name": generate_trade_name(direction, symbol, index),
        "direction": direction,
        "risk_reward_ratio": risk_reward,
        "entry_price": entry,
        "stop_loss": sl,
        "target_1": {"price": tp1},
        "notes": args.notes or ""
    }
    
    if tp2:
        trade["target_2"] = {"price": tp2}
    
    if charts_dir:
        charts = detect_chart_images(charts_dir, symbol)
        if charts:
            trade["charts"] = charts
    
    return trade


def load_existing_json(output_path):
    if os.path.exists(output_path):
        try:
            with open(output_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return None


def main():
    parser = argparse.ArgumentParser(
        description='Generate JSON data for trade ideas PDF',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python generate_trade_ideas_json.py \\
    --symbol "BTC/USD" \\
    --direction LONG \\
    --entry 50000 \\
    --sl 49000 \\
    --tp1 52000 \\
    --tp2 54000 \\
    --notes "Breakout above resistance" \\
    --charts-dir ./charts \\
    --output ./trade_ideas.json
"""
    )
    
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., "BTC/USD")')
    parser.add_argument('--direction', required=True, choices=['LONG', 'SHORT', 'long', 'short'], 
                        help='Trade direction')
    parser.add_argument('--entry', required=True, type=float, help='Entry price')
    parser.add_argument('--sl', required=True, type=float, help='Stop loss price')
    parser.add_argument('--tp1', required=True, type=float, help='Take profit 1 price')
    parser.add_argument('--tp2', type=float, help='Take profit 2 price (optional)')
    parser.add_argument('--notes', default='', help='Trade notes/reasoning')
    parser.add_argument('--charts-dir', help='Directory to auto-detect chart images')
    parser.add_argument('--output', '-o', default='trade_ideas.json', 
                        help='Output JSON file path (default: trade_ideas.json)')
    parser.add_argument('--append', action='store_true', 
                        help='Append to existing JSON file if it exists')
    parser.add_argument('--risk-warning', default=DEFAULT_RISK_WARNING,
                        help='Custom risk warning text')
    
    args = parser.parse_args()
    
    output_path = os.path.abspath(args.output)
    output_dir = os.path.dirname(output_path)
    
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    charts_dir = args.charts_dir
    if charts_dir:
        charts_dir = os.path.abspath(charts_dir)
    
    existing_data = None
    if args.append:
        existing_data = load_existing_json(output_path)
    
    if existing_data:
        data = existing_data
        existing_trades = data.get('trade_ideas', [])
        next_id = len(existing_trades) + 1
        
        metadata = data.get('report_metadata', {})
        metadata['generated_at'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        if args.symbol:
            metadata['symbol'] = args.symbol
        data['report_metadata'] = metadata
    else:
        next_id = 1
        data = {
            "report_metadata": {
                "symbol": args.symbol,
                "generated_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "analysis_type": "Trade Ideas"
            },
            "trade_ideas": [],
            "risk_warning": args.risk_warning
        }
    
    trade = create_trade(args, next_id, charts_dir)
    data['trade_ideas'].append(trade)
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"JSON generated: {output_path}")
    print(f"Trade #{next_id}: {trade['name']} @ {trade['entry_price']} ({trade['direction']})")
    
    return output_path


if __name__ == "__main__":
    main()
