#!/usr/bin/env python3
"""
Candlestick Chart with TradingView Dark Theme

Creates interactive candlestick charts with volume panel, key levels,
and crosshair annotation on hover.

Usage:
    python plot_chart.py --data /path/to/data.json --output /path/to/chart.png

Or use as module:
    from plot_chart import plot_candlestick_chart
    plot_candlestick_chart(data, figsize=(14, 10))

JSON data structure should include:
    - symbol, timeframe, timestamps, open, high, low, close, volume
    - Optional: price_tick (for decimal precision), vah (list or float), val (list or float), tp, entry, sl, title
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Rectangle
import argparse
import json
import math
from datetime import datetime

try:
    import mplcursors
except ImportError:
    mplcursors = None


TRADINGVIEW_STYLE = {
    'background': '#131722',
    'panel_bg': '#1e222d',
    'up_candle': '#26a69a',
    'down_candle': '#ef5350',
    'up_volume': '#26a69a',
    'down_volume': '#ef5350',
    'text': '#d1d4dc',
    'axis': '#363a45',
    'vah': '#FF9800',
    'val': '#00BCD4',
    'vah_val_pairs': [
        '#00BCD4',  # cyan
        '#E91E63',  # pink
        '#FFEB3B',  # yellow
        '#9C27B0',  # purple
        '#4CAF50',  # green
        '#FF5722',  # deep orange
        '#3F51B5',  # indigo
        '#009688',  # teal
        '#FFC107',  # amber
        '#8BC34A',  # light green
    ],
    'tp': '#4CAF50',
    'entry': '#2196F3',
    'sl': '#F44336',
}


def set_tradingview_style():
    plt.rcParams.update({
        'figure.facecolor': TRADINGVIEW_STYLE['background'],
        'figure.edgecolor': TRADINGVIEW_STYLE['background'],
        'axes.facecolor': TRADINGVIEW_STYLE['panel_bg'],
        'axes.edgecolor': TRADINGVIEW_STYLE['axis'],
        'axes.labelcolor': TRADINGVIEW_STYLE['text'],
        'axes.titlecolor': TRADINGVIEW_STYLE['text'],
        'text.color': TRADINGVIEW_STYLE['text'],
        'xtick.color': TRADINGVIEW_STYLE['text'],
        'ytick.color': TRADINGVIEW_STYLE['text'],
        'xtick.labelcolor': TRADINGVIEW_STYLE['text'],
        'ytick.labelcolor': TRADINGVIEW_STYLE['text'],
        'grid.color': TRADINGVIEW_STYLE['axis'],
        'axes.grid': False,
        'axes.spines.top': True,
        'axes.spines.right': True,
        'axes.spines.bottom': True,
        'axes.spines.left': True,
        'axes.edgecolor': TRADINGVIEW_STYLE['axis'],
        'legend.facecolor': TRADINGVIEW_STYLE['panel_bg'],
        'legend.edgecolor': TRADINGVIEW_STYLE['axis'],
        'legend.labelcolor': TRADINGVIEW_STYLE['text'],
        'savefig.facecolor': TRADINGVIEW_STYLE['background'],
    })


def get_decimal_places(price_tick):
    if price_tick is None or price_tick >= 1:
        return 4
    return max(4, abs(int(round(math.log10(price_tick)))))


def parse_timestamps(timestamps):
    parsed = []
    for ts in timestamps:
        if isinstance(ts, str):
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                parsed.append(dt)
            except ValueError:
                parsed.append(datetime.strptime(ts, '%Y-%m-%dT%H:%M:%SZ'))
        else:
            parsed.append(ts)
    return parsed


def draw_candlestick(ax, data, width=0.6, right_padding_pct=0.10):
    opens = np.array(data['open'])
    highs = np.array(data['high'])
    lows = np.array(data['low'])
    closes = np.array(data['close'])
    n = len(opens)
    
    up_color = TRADINGVIEW_STYLE['up_candle']
    down_color = TRADINGVIEW_STYLE['down_candle']
    
    candles = []
    for i in range(n):
        is_bullish = closes[i] >= opens[i]
        color = up_color if is_bullish else down_color
        
        ax.plot([i, i], [lows[i], highs[i]], color=color, linewidth=1, solid_capstyle='round')
        
        body_bottom = min(opens[i], closes[i])
        body_height = abs(closes[i] - opens[i])
        body_height = max(body_height, opens[i] * 0.0001)
        
        rect = Rectangle(
            (i - width / 2, body_bottom),
            width,
            body_height,
            facecolor=color,
            edgecolor=color,
            linewidth=0.5
        )
        ax.add_patch(rect)
        candles.append(rect)
    
    padding = n * right_padding_pct
    ax.set_xlim(-0.5, n - 0.5 + padding)
    return candles


def draw_volume_bars(ax, data, width=0.8, right_padding_pct=0.10):
    opens = np.array(data['open'])
    closes = np.array(data['close'])
    volumes = np.array(data['volume'])
    n = len(volumes)
    
    up_color = TRADINGVIEW_STYLE['up_volume']
    down_color = TRADINGVIEW_STYLE['down_volume']
    
    for i in range(n):
        is_bullish = closes[i] >= opens[i]
        color = up_color if is_bullish else down_color
        
        ax.bar(i, volumes[i], width=width, color=color, alpha=0.5, edgecolor='none')
    
    padding = n * right_padding_pct
    ax.set_xlim(-0.5, n - 0.5 + padding)


def draw_levels(ax, vah=None, val=None, tp=None, entry=None, sl=None, x_max=None, decimal_places=4):
    levels = []
    pair_colors = TRADINGVIEW_STYLE['vah_val_pairs']
    
    if vah is not None or val is not None:
        vah_list = vah if isinstance(vah, list) else [vah] if vah is not None else []
        val_list = val if isinstance(val, list) else [val] if val is not None else []
        max_pairs = max(len(vah_list), len(val_list))
        
        for i in range(max_pairs):
            color = pair_colors[i % len(pair_colors)]
            if i < len(vah_list) and vah_list[i] is not None:
                line = ax.axhline(y=vah_list[i], color=color, linestyle='--', linewidth=1, alpha=0.8)
                levels.append(line)
            if i < len(val_list) and val_list[i] is not None:
                line = ax.axhline(y=val_list[i], color=color, linestyle='--', linewidth=1, alpha=0.8)
                levels.append(line)
    
    if tp is not None:
        tp_list = tp if isinstance(tp, list) else [tp]
        for t in tp_list:
            line = ax.axhline(y=t, color=TRADINGVIEW_STYLE['tp'], linestyle='-', linewidth=1.5, alpha=0.9)
            levels.append(line)
    
    if entry is not None:
        line = ax.axhline(y=entry, color=TRADINGVIEW_STYLE['entry'], linestyle='-', linewidth=1.5, alpha=0.9)
        levels.append(line)
    
    if sl is not None:
        line = ax.axhline(y=sl, color=TRADINGVIEW_STYLE['sl'], linestyle='-', linewidth=1.5, alpha=0.9)
        levels.append(line)
    
    return levels


def setup_crosshair(fig, price_ax, volume_ax, data, decimal_places=4):
    if mplcursors is None:
        print("Warning: mplcursors not installed. Install with: pip install mplcursors")
        return None
    
    timestamps = parse_timestamps(data.get('timestamps', []))
    opens = data['open']
    highs = data['high']
    lows = data['low']
    closes = data['close']
    volumes = data['volume']
    
    cursor = mplcursors.cursor(price_ax, hover=True)
    fmt = f'.{decimal_places}f'
    
    @cursor.connect("add")
    def on_add(sel):
        idx = int(round(sel.target[0]))
        if idx < 0 or idx >= len(opens):
            return
        
        ts_str = timestamps[idx].strftime('%Y-%m-%d %H:%M') if idx < len(timestamps) else f"Bar {idx}"
        
        text = (
            f"Time: {ts_str}\n"
            f"O: {opens[idx]:{fmt}}\n"
            f"H: {highs[idx]:{fmt}}\n"
            f"L: {lows[idx]:{fmt}}\n"
            f"C: {closes[idx]:{fmt}}\n"
            f"V: {volumes[idx]:{fmt}}"
        )
        
        sel.annotation.set_text(text)
        sel.annotation.get_bbox_patch().set(
            facecolor=TRADINGVIEW_STYLE['panel_bg'],
            edgecolor=TRADINGVIEW_STYLE['axis'],
            alpha=0.95
        )
        sel.annotation.set_color(TRADINGVIEW_STYLE['text'])
        sel.annotation.set_fontsize(9)
    
    return cursor


def plot_candlestick_chart(data, vah=None, val=None, tp=None, entry=None, sl=None, title=None, figsize=(14, 10), price_tick=None):
    """
    Plot a candlestick chart with volume and key levels.
    
    Parameters
    ----------
    data : dict
        Dictionary containing OHLCV data:
        - symbol: str (e.g., 'BTC/USDT')
        - timeframe: str (e.g., '1m')
        - timestamps: list of str or datetime
        - open: list of float
        - high: list of float
        - low: list of float
        - close: list of float
        - volume: list of float
    vah : float or list of float, optional
        Value Area High level(s)
    val : float or list of float, optional
        Value Area Low level(s)
    tp : float or list of float, optional
        Take Profit level(s)
    entry : float, optional
        Entry price level
    sl : float, optional
        Stop Loss level
    title : str, optional
        Custom chart title
    figsize : tuple
        Figure size (width, height)
    price_tick : float, optional
        Price tick for decimal precision (e.g., 0.0005 or 0.001)
    
    Returns
    -------
    fig : matplotlib.figure.Figure
    axes : dict with 'price' and 'volume' keys
    """
    set_tradingview_style()
    
    decimal_places = get_decimal_places(price_tick)
    
    fig = plt.figure(figsize=figsize, facecolor=TRADINGVIEW_STYLE['background'])
    gs = GridSpec(2, 1, height_ratios=[4, 1], hspace=0.05, figure=fig)
    
    price_ax = fig.add_subplot(gs[0])
    volume_ax = fig.add_subplot(gs[1], sharex=price_ax)
    
    draw_candlestick(price_ax, data)
    
    draw_volume_bars(volume_ax, data)
    
    n = len(data['open'])
    draw_levels(price_ax, vah=vah, val=val, tp=tp, entry=entry, sl=sl, x_max=n - 1, decimal_places=decimal_places)
    
    all_prices = list(data['open']) + list(data['high']) + list(data['low']) + list(data['close'])
    
    for level in [sl, entry]:
        if level is not None:
            all_prices.append(level)
    
    for levels in [vah, val, tp]:
        if levels is not None:
            level_list = levels if isinstance(levels, list) else [levels]
            all_prices.extend(level_list)
    
    price_min = min(all_prices)
    price_max = max(all_prices)
    price_padding = (price_max - price_min) * 0.1
    price_ax.set_ylim(price_min - price_padding, price_max + price_padding)
    
    volume_max = max(data['volume'])
    volume_ax.set_ylim(0, volume_max * 1.2)
    
    timestamps = parse_timestamps(data.get('timestamps', []))
    if timestamps:
        n_ticks = min(10, n)
        tick_indices = np.linspace(0, n - 1, n_ticks, dtype=int)
        tick_labels = [timestamps[i].strftime('%m/%d %H:%M') for i in tick_indices]
        volume_ax.set_xticks(tick_indices)
        volume_ax.set_xticklabels(tick_labels, rotation=45, ha='right', fontsize=8)
    
    symbol = data.get('symbol', 'Unknown')
    timeframe = data.get('timeframe', '')
    if title is None:
        title = f"{symbol}"
        if timeframe:
            title += f" ({timeframe})"
    
    price_ax.set_title(title, color=TRADINGVIEW_STYLE['text'], fontsize=14, fontweight='bold', pad=10)
    price_ax.set_ylabel('Price', color=TRADINGVIEW_STYLE['text'], fontsize=10)
    volume_ax.set_ylabel('Volume', color=TRADINGVIEW_STYLE['text'], fontsize=10)
    volume_ax.set_xlabel('Time', color=TRADINGVIEW_STYLE['text'], fontsize=10)
    
    price_ax.tick_params(axis='x', labelbottom=False)
    price_ax.grid(False)
    volume_ax.grid(False)
    
    legend_elements = []
    fmt = f'.{decimal_places}f'
    pair_colors = TRADINGVIEW_STYLE['vah_val_pairs']
    
    if vah is not None or val is not None:
        vah_list = vah if isinstance(vah, list) else [vah] if vah is not None else []
        val_list = val if isinstance(val, list) else [val] if val is not None else []
        max_pairs = max(len(vah_list), len(val_list))
        
        for i in range(max_pairs):
            color = pair_colors[i % len(pair_colors)]
            vah_val = vah_list[i] if i < len(vah_list) else None
            val_val = val_list[i] if i < len(val_list) else None
            
            if vah_val is not None and val_val is not None:
                label = f'Pair {i+1}: VAH {vah_val:{fmt}} / VAL {val_val:{fmt}}'
            elif vah_val is not None:
                label = f'Pair {i+1}: VAH {vah_val:{fmt}}'
            else:
                label = f'Pair {i+1}: VAL {val_val:{fmt}}'
            
            legend_elements.append(plt.Line2D([0], [0], color=color, linestyle='--', label=label))
    if tp is not None:
        tp_list = tp if isinstance(tp, list) else [tp]
        for t in tp_list:
            legend_elements.append(plt.Line2D([0], [0], color=TRADINGVIEW_STYLE['tp'], linestyle='-', label=f'TP: {t:{fmt}}'))
    if entry is not None:
        legend_elements.append(plt.Line2D([0], [0], color=TRADINGVIEW_STYLE['entry'], linestyle='-', label=f'Entry: {entry:{fmt}}'))
    if sl is not None:
        legend_elements.append(plt.Line2D([0], [0], color=TRADINGVIEW_STYLE['sl'], linestyle='-', label=f'SL: {sl:{fmt}}'))
    
    if legend_elements:
        price_ax.legend(
            handles=legend_elements,
            loc='upper left',
            fontsize=9,
            framealpha=0.9,
            facecolor=TRADINGVIEW_STYLE['panel_bg'],
            edgecolor=TRADINGVIEW_STYLE['axis']
        )
    
    setup_crosshair(fig, price_ax, volume_ax, data, decimal_places=decimal_places)
    
    plt.tight_layout()
    
    return fig, {'price': price_ax, 'volume': volume_ax}


def load_json_data(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description='Candlestick Chart with TradingView Dark Theme',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with JSON data file (default output: /market-analyzer/candlestick_chart.png)
  python plot_chart.py --data /market-analyzer/chart_1m.json

  # With custom output path
  python plot_chart.py --data /market-analyzer/chart_1m.json --output /custom/path/chart.png

  # With custom figure size
  python plot_chart.py --data /market-analyzer/chart_1m.json --figsize 20,12

  # Show without saving
  python plot_chart.py --data /market-analyzer/chart_1m.json --no-save
        """
    )
    
    parser.add_argument('--data', type=str, required=True,
                        help='Path to JSON data file containing OHLCV data and levels')
    parser.add_argument('--output', '-o', type=str, default='/market-analyzer/candlestick_chart.png',
                        help='Full output file path (default: /market-analyzer/candlestick_chart.png)')
    parser.add_argument('--no-save', action='store_true',
                        help='Do not save to file, only display')
    parser.add_argument('--figsize', type=str, default='16,10',
                        help='Figure size as width,height (default: 16,10)')
    
    args = parser.parse_args()
    
    figsize = tuple(map(int, args.figsize.split(',')))
    
    try:
        data = load_json_data(args.data)
    except FileNotFoundError:
        print(f"Error: Data file not found: {args.data}")
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in data file: {e}")
        return 1
    
    fig, axes = plot_candlestick_chart(
        data,
        vah=data.get('vah'),
        val=data.get('val'),
        tp=data.get('tp'),
        entry=data.get('entry'),
        sl=data.get('sl'),
        title=data.get('title'),
        figsize=figsize,
        price_tick=data.get('price_tick')
    )
    
    if not args.no_save:
        output_path = args.output
        fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
        print(f"Chart saved to {output_path}")
    
    plt.show()
    return 0


if __name__ == "__main__":
    exit(main())
