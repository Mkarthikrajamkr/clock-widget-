# Windows `.exe` build guide

From a Windows PowerShell terminal in the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pyinstaller --noconfirm --windowed --name TradingTimeBlockManager --collect-all PyQt6 -m trading_time_block_manager.main
```

Output:

```text
dist/TradingTimeBlockManager/TradingTimeBlockManager.exe
```

Use `--onefile` if you prefer a single executable:

```powershell
pyinstaller --noconfirm --onefile --windowed --name TradingTimeBlockManager --collect-all PyQt6 -m trading_time_block_manager.main
```

If Windows SmartScreen warns on an unsigned build, sign the executable with your organization's code-signing certificate before distribution.
