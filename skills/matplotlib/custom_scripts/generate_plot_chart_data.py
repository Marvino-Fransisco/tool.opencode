#!/usr/bin/env python3
"""
Generate chart JSON data for plot_chart.py

Reads XRP_USDT_{timeframe}m.json from /market-analyzer/ and adds:
  - price_tick: 0.0005
  - vah, val, tp, entry, sl (optional CLI args)
  - title: auto-generated

Output: /market-analyzer/chart_{timeframe}m.json

Usage:
    python generate_plot_chart_data.py -t 1
    python generate_plot_chart_data.py -t 1 --vah 2.50 --val 2.40 --tp 2.55 --entry 2.45 --sl 2.35
    python generate_plot_chart_data.py -t 1 --vah 2.50,2.60 --val 2.40,2.45 --tp 2.55,2.65 --entry 2.45 --sl 2.35
    python generate_plot_chart_data.py -t 1 -o /custom/path/mychart.json
"""

import argparse
import json
import os
from pathlib import Path
from typing import Optional


INPUT_DIR = Path("/market-analyzer")
OUTPUT_DIR = Path("/market-analyzer")
PRICE_TICK = 0.0005


def parse_float_list(value: str) -> list[float]:
    return [float(x.strip()) for x in value.split(",")]


def load_input_data(timeframe: int) -> dict:
    input_file = INPUT_DIR / f"XRP_USDT_{timeframe}m.json"
    
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    with open(input_file, 'r') as f:
        return json.load(f)


def generate_output_data(
    input_data: dict,
    timeframe: int,
    vah: list[float],
    val: list[float],
    tp: list[float],
    entry: float,
    sl: float
) -> dict:
    output_data = input_data.copy()
    
    output_data["price_tick"] = PRICE_TICK
    if vah is not None:
        output_data["vah"] = vah
    if val is not None:
        output_data["val"] = val
    if tp is not None:
        output_data["tp"] = tp
    if entry is not None:
        output_data["entry"] = entry
    if sl is not None:
        output_data["sl"] = sl
    output_data["title"] = f"XRP/USDT ({timeframe}m)"
    
    return output_data


def save_output_data(data: dict, timeframe: int, output_path: Optional[str] = None) -> Path:
    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
    else:
        output_file = OUTPUT_DIR / f"chart_{timeframe}m.json"
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    return output_file


def main():
    parser = argparse.ArgumentParser(
        description="Generate chart JSON data for plot_chart.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python generate_plot_chart_data.py -t 1
    python generate_plot_chart_data.py -t 1 --vah 2.50 --val 2.40 --tp 2.55 --entry 2.45 --sl 2.35
    python generate_plot_chart_data.py -t 1 --vah 2.50,2.60 --val 2.40,2.45 --tp 2.55,2.65 --entry 2.45 --sl 2.35
    python generate_plot_chart_data.py -t 1 -o /custom/path/mychart.json
        """
    )
    
    parser.add_argument(
        "-t", "--timeframe",
        type=int,
        required=True,
        choices=[1, 4, 5],
        help="Timeframe in minutes (1, 4, or 5)"
    )
    parser.add_argument("--vah", type=parse_float_list, default=None, help="Value Area High (comma-separated for multiple)")
    parser.add_argument("--val", type=parse_float_list, default=None, help="Value Area Low (comma-separated for multiple)")
    parser.add_argument("--tp", type=parse_float_list, default=None, help="Take Profit level (comma-separated for multiple)")
    parser.add_argument("--entry", type=float, default=None, help="Entry price")
    parser.add_argument("--sl", type=float, default=None, help="Stop Loss level")
    parser.add_argument("-o", "--output", type=str, default=None, help="Full output file path (default: /market-analyzer/chart_{timeframe}m.json)")
    
    args = parser.parse_args()
    
    try:
        input_data = load_input_data(args.timeframe)
        print(f"Loaded input data from: XRP_USDT_{args.timeframe}m.json")
        
        output_data = generate_output_data(
            input_data,
            args.timeframe,
            args.vah,
            args.val,
            args.tp,
            args.entry,
            args.sl
        )
        
        output_file = save_output_data(output_data, args.timeframe, args.output)
        print(f"Output saved to: {output_file}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
