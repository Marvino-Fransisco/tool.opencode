---
name: matplotlib
description: Low-level plotting library for full customization. Use when you need fine-grained control over every plot element, creating novel plot types, or integrating with specific scientific workflows. Export to PNG/PDF/SVG for publication. For quick statistical plots use seaborn; for interactive plots use plotly; for publication-ready multi-panel figures with journal styling, use scientific-visualization.
license: PSF
metadata:
  skill-author: K-Dense Inc.
---

# Matplotlib

## What I Do

- Create any type of plot or chart (line, scatter, bar, histogram, heatmap, contour, etc.)
- Generate scientific or statistical visualizations
- Customize plot appearance (colors, styles, labels, legends)
- Create multi-panel figures with subplots
- Export visualizations to various formats (PNG, PDF, SVG)
- Build interactive plots or animations
- Work with 3D visualizations
- Integrate plots into Jupyter notebooks or GUI applications

## When to Use Me

Use this skill when:
- You need fine-grained control over every plot element
- Creating novel plot types not covered by higher-level libraries
- Integrating with specific scientific workflows
- Exporting publication-quality figures (PNG/PDF/SVG)

For quick statistical plots, use seaborn. For interactive plots, use plotly. For publication-ready multi-panel figures with journal styling, use scientific-visualization.

## Core Concepts

### The Matplotlib Hierarchy

Matplotlib uses a hierarchical structure of objects:

1. **Figure** - The top-level container for all plot elements
2. **Axes** - The actual plotting area where data is displayed (one Figure can contain multiple Axes)
3. **Artist** - Everything visible on the figure (lines, text, ticks, etc.)
4. **Axis** - The number line objects (x-axis, y-axis) that handle ticks and labels

### Two Interfaces

**1. pyplot Interface (Implicit, MATLAB-style)**
```python
import matplotlib.pyplot as plt

plt.plot([1, 2, 3, 4])
plt.ylabel('some numbers')
plt.show()
```
- Convenient for quick, simple plots
- Maintains state automatically
- Good for interactive work and simple scripts

**2. Object-Oriented Interface (Explicit)**
```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot([1, 2, 3, 4])
ax.set_ylabel('some numbers')
plt.show()
```
- **Recommended for most use cases**
- More explicit control over figure and axes
- Better for complex figures with multiple subplots
- Easier to maintain and debug

## Common Workflows

### Basic Plot Creation

```python
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(10, 6))

x = np.linspace(0, 2*np.pi, 100)
ax.plot(x, np.sin(x), label='sin(x)')
ax.plot(x, np.cos(x), label='cos(x)')

ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_title('Trigonometric Functions')
ax.legend()
ax.grid(True, alpha=0.3)

plt.savefig('plot.png', dpi=300, bbox_inches='tight')
plt.show()
```

### Multiple Subplots

```python
# Regular grid
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
axes[0, 0].plot(x, y1)
axes[0, 1].scatter(x, y2)
axes[1, 0].bar(categories, values)
axes[1, 1].hist(data, bins=30)

# Mosaic layout (more flexible)
fig, axes = plt.subplot_mosaic([['left', 'right_top'],
                                 ['left', 'right_bottom']],
                                figsize=(10, 8))
axes['left'].plot(x, y)
```

### Plot Types Quick Reference

| Type | Use Case | Example |
|------|----------|---------|
| Line | Time series, trends | `ax.plot(x, y, linewidth=2, linestyle='--')` |
| Scatter | Relationships, correlations | `ax.scatter(x, y, s=sizes, c=colors, cmap='viridis')` |
| Bar | Categorical comparisons | `ax.bar(categories, values)` |
| Histogram | Distributions | `ax.hist(data, bins=30, edgecolor='black')` |
| Heatmap | Matrix data | `ax.imshow(matrix, cmap='coolwarm')` |
| Box | Statistical distributions | `ax.boxplot([data1, data2], labels=['A', 'B'])` |

See `references/plot_types.md` for comprehensive examples.

### Styling

```python
# Color specification
color = 'steelblue'       # Named
color = '#FF5733'         # Hex
color = (0.1, 0.2, 0.3)   # RGB tuple

# Style sheets
plt.style.use('seaborn-v0_8-darkgrid')

# rcParams for global settings
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
```

See `references/styling_guide.md` for detailed styling options.

### Saving Figures

```python
# High-resolution for publications
plt.savefig('figure.png', dpi=300, bbox_inches='tight', facecolor='white')

# Vector formats (scalable)
plt.savefig('figure.pdf', bbox_inches='tight')
plt.savefig('figure.svg', bbox_inches='tight')
```

### 3D Plots

```python
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X, Y, Z, cmap='viridis')
ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
```

## Best Practices

1. **Use OO interface** - `fig, ax = plt.subplots()` for production code
2. **Set figsize at creation** - `figsize=(10, 6)` appropriate for output medium
3. **Use layout management** - `constrained_layout=True` prevents overlapping
4. **Choose colormaps wisely**:
   - Sequential (viridis, plasma): Ordered data
   - Diverging (coolwarm, RdBu): Data with meaningful center
   - Qualitative (tab10, Set3): Categorical data
   - Avoid rainbow colormaps (jet) - not perceptually uniform
5. **Accessibility** - Use colorblind-friendly colormaps (viridis, cividis)
6. **Performance** - Use `rasterized=True` for large datasets

## Code Organization Pattern

```python
def create_analysis_plot(data, title):
    """Create standardized analysis plot."""
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)

    ax.plot(data['x'], data['y'], linewidth=2)

    ax.set_xlabel('X Axis Label', fontsize=12)
    ax.set_ylabel('Y Axis Label', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    return fig, ax

fig, ax = create_analysis_plot(my_data, 'My Analysis')
plt.savefig('analysis.png', dpi=300, bbox_inches='tight')
```

## Helper Scripts

- `scripts/plot_template.py` - Template demonstrating various plot types
- `scripts/style_configurator.py` - Interactive style configuration utility

## Reference Documents

- `references/plot_types.md` - Complete catalog of plot types
- `references/styling_guide.md` - Detailed styling and colormaps
- `references/api_reference.md` - Core classes and methods
- `references/common_issues.md` - Troubleshooting guide

## Common Gotchas

| Issue | Solution |
|-------|----------|
| Overlapping elements | Use `constrained_layout=True` or `tight_layout()` |
| State confusion | Use OO interface to avoid pyplot state machine |
| Memory issues | Close figures explicitly: `plt.close(fig)` |
| Font warnings | Set `plt.rcParams['font.sans-serif']` |
| DPI confusion | Remember: `pixels = dpi * inches` |

## Resources

- Documentation: https://matplotlib.org/
- Gallery: https://matplotlib.org/stable/gallery/
- Cheatsheets: https://matplotlib.org/cheatsheets/
- Tutorials: https://matplotlib.org/stable/tutorials/
