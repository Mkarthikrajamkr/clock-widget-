# Trading Time Block Manager

A modern Windows desktop application for traders built with **Python + PyQt6**. The app helps plan custom trading sessions, track live progress, and receive alarms using the user's **system local time**. No timezone is hardcoded, so the same build works globally.

## Features

- Create multiple trading blocks with a name, start time, end time, notes/strategy, color, recurrence, and per-block alarm options.
- Dark trading-dashboard interface with rounded responsive cards.
- Live date and clock display.
- Session statuses: **Upcoming**, **Active**, and **Completed**.
- Real-time progress bars, completion percentage, and countdown text updated every second.
- Alarm triggers:
  - Before session starts
  - At session start
  - Before session ends
- Popup and sound alert support via Qt.
- Add, edit, delete, import, export, and load starter session templates.
- Auto-save and auto-load sessions from local JSON storage.
- Optional floating mini timer widget.
- Always-on-top mode and keyboard shortcuts.
- Supports overnight sessions that cross midnight.

## Project structure

```text
trading_time_block_manager/
├── __init__.py
├── alarm.py             # Alarm trigger evaluation and signals
├── __main__.py          # python -m package entry point
├── main.py              # Application entry point
├── resources.py         # Runtime-generated app icon
├── sample_data.py       # Starter session templates
├── models.py            # TradingBlock model and time/status calculations
├── storage.py           # Local JSON persistence and import/export
├── timer_manager.py     # One-second Qt timer service
└── ui/
    ├── __init__.py
    ├── main_window.py   # Main dashboard and actions
    ├── mini_timer.py    # Floating mini timer widget
    ├── session_card.py  # Modern visual session card
    └── session_dialog.py# Add/edit form
```

## Requirements

- Python 3.11 or newer recommended
- Windows 10/11 for target packaging
- Dependencies listed in `requirements.txt`

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the app

```powershell
python -m trading_time_block_manager
```

You can also use the console entry point after installing the package in editable mode:

```powershell
pip install -e .
trading-time-block-manager
```

## Keyboard shortcuts

- `Ctrl+N` — Add a new trading block
- `Ctrl+M` — Toggle the floating mini timer
- `Ctrl+E` — Export sessions

## Local data storage

Sessions are stored as JSON at:

- Windows: `%APPDATA%\TradingTimeBlockManager\sessions.json`
- Other systems: `~/.trading_time_block_manager/sessions.json`

Export/import can be used to move templates between machines.

## Build a Windows executable

Install dependencies first, then run PyInstaller from the project root:

```powershell
.\build_windows.ps1
```

The executable will be created under:

```text
dist/TradingTimeBlockManager/TradingTimeBlockManager.exe
```

For a single-file executable, use:

```powershell
python -m PyInstaller --noconfirm --onefile --windowed --name TradingTimeBlockManager --collect-all PyQt6 run_app.py
```

## Notes for future enhancements

- Add custom alert tone selection and persistence.
- Add SQLite as an optional backend if session metadata grows.
- Add market-calendar integrations for exchange holidays.
- Add theme presets and richer card animations.
