# Appalachian Trail Analysis & Visualization

An interactive analysis and visualization project exploring the Appalachian Trail - one of the longest hiking-only footpaths in the world, stretching approximately 2,190 miles from Georgia to Maine.

## Features

- **Trail Statistics**: Distance, elevation gain/loss, state-by-state breakdown
- **Elevation Profile**: Detailed visualization of the trail's elevation changes
- **Interactive Maps**: Explore the trail route with interactive maps
- **Data Analysis**: Insights into trail characteristics, difficulty sections, and more

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for fast Python package management.

```bash
# Install dependencies
uv sync

# Install with dev dependencies (includes Jupyter)
uv sync --extra dev
```

## Usage

Run the main analysis:

```bash
uv run python main_analysis.py
```

Or explore interactively with the Jupyter notebook:

```bash
uv run jupyter notebook appalachian_trail_analysis.ipynb
```

## Project Structure

- `data/` - Trail data and GPX files
- `src/` - Analysis and visualization modules
- `outputs/` - Generated visualizations and reports
- `main_analysis.py` - Main analysis script
- `appalachian_trail_analysis.ipynb` - Interactive analysis notebook

## Data Sources

The project uses publicly available Appalachian Trail data including GPS coordinates, elevation data, and trail information.

## About the Appalachian Trail

The Appalachian Trail (AT) is a marked hiking trail extending between Springer Mountain in Georgia and Mount Katahdin in Maine. It passes through 14 states and is maintained by the Appalachian Trail Conservancy and various local trail clubs.

