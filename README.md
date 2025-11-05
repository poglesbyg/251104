# Appalachian Trail Analysis & Visualization

An interactive analysis and visualization project exploring the Appalachian Trail - one of the longest hiking-only footpaths in the world, stretching approximately 2,190 miles from Georgia to Maine.

## Features

- **Trail Statistics**: Distance, elevation gain/loss, state-by-state breakdown
- **Elevation Profile**: Detailed visualization of the trail's elevation changes
- **Interactive Maps**: Explore the trail route with interactive maps
- **Data Analysis**: Insights into trail characteristics, difficulty sections, and more
- **FKT Analysis**: In-depth analysis of the fastest known time (40d 18h 6m) including pace requirements, daily breakdown, and comparison with typical thru-hikes
- **Daylight Analysis**: Calculates available daylight hours based on location and season, showing how it affects hiking strategy and duration
- **Daylight Constraints**: NEW! Realistic hiking scenarios considering only daylight hours - shows that FKT requires significant night hiking and provides optimal pacing for daylight-only thru-hikes

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for fast Python package management.

```bash
# Install dependencies
uv sync

# Install with dev dependencies (includes Jupyter)
uv sync --extra dev
```

## Usage

### Complete Trail Analysis

Run the main analysis:

```bash
uv run python main_analysis.py
```

### FKT (Fastest Known Time) Analysis

Analyze the record-breaking 40 days, 18 hours, 6 minutes achievement:

```bash
uv run python fkt_analysis_report.py
```

### Daylight-Only Hiking Analysis

Compare 24/7 hiking (FKT) vs practical daylight-only hiking:

```bash
uv run python daylight_fkt_comparison.py
```

### Daylight-Constrained Analysis

Analyze realistic hiking scenarios with daylight-only constraints:

```bash
uv run python daylight_analysis_report.py
```

This reveals that the FKT requires extensive night hiking and provides optimal pacing recommendations for daylight-only thru-hikes.

### Interactive Exploration

Explore interactively with the Jupyter notebook:

```bash
uv run jupyter notebook appalachian_trail_analysis.ipynb
```

## Project Structure

- `data/` - Trail data and GPX files
- `src/` - Analysis and visualization modules
  - `data_loader.py` - Trail data generation
  - `analysis.py` - Statistical analysis tools
  - `visualization.py` - Trail visualizations
  - `fkt_analysis.py` - FKT performance analysis
  - `fkt_visualization.py` - FKT-specific visualizations
  - `daylight_analysis.py` - Daylight hours calculations
  - `daylight_visualization.py` - Daylight-specific visualizations
  - `daylight_analysis.py` - Daylight constraint calculations
  - `daylight_visualization.py` - Daylight analysis visualizations
- `outputs/` - Generated visualizations and reports
- `main_analysis.py` - Main analysis script
- `fkt_analysis_report.py` - FKT-specific analysis script
- `daylight_analysis_report.py` - Daylight-constrained analysis script
- `appalachian_trail_analysis.ipynb` - Interactive analysis notebook

## Data Sources

The project uses publicly available Appalachian Trail data including GPS coordinates, elevation data, and trail information.

## About the Appalachian Trail

The Appalachian Trail (AT) is a marked hiking trail extending between Springer Mountain in Georgia and Mount Katahdin in Maine. It passes through 14 states and is maintained by the Appalachian Trail Conservancy and various local trail clubs.

### Fastest Known Time (FKT)

The current self-supported FKT for the Appalachian Trail is **40 days, 18 hours, and 6 minutes** - an extraordinary achievement representing:

- **48 miles per day** sustained pace
- **20+ hours of daily movement** (minimal rest)
- **5,400+ feet elevation gain** every single day
- **3.7x faster** than typical thru-hike (150 days)

This project includes comprehensive analysis of what this incredible pace entails, including daily breakdowns, terrain challenges, and comparison with various hiking strategies.

### Daylight-Only Hiking

Most thru-hikers only hike during daylight hours for safety and practical reasons. The analysis shows:

- **March/April starts** provide optimal daylight (14-15 hours/day average)
- **Daylight-only at FKT pace** would require 4.4 mph (ultramarathon pace!)
- **Realistic daylight hiking**: 2-3 mph pace = 60-90 days total
- **Traditional thru-hike**: 150 days with comfortable 8-10 hours hiking/day

Starting in mid-March (NOBO) or mid-June (SOBO) maximizes available daylight hours.

