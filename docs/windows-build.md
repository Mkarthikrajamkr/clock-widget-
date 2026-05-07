# Windows `.exe` build guide

From a Windows PowerShell terminal in the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m PyInstaller --noconfirm --windowed --name TradingTimeBlockManager --collect-all PyQt6 run_app.py
```

Output:

```text
dist/TradingTimeBlockManager/TradingTimeBlockManager.exe
```

Use `--onefile` if you prefer a single executable:

```powershell
python -m PyInstaller --noconfirm --onefile --windowed --name TradingTimeBlockManager --collect-all PyQt6 run_app.py
```

If Windows SmartScreen warns on an unsigned build, sign the executable with your organization's code-signing certificate before distribution.

Alternatively, run the included helper script:

```powershell
.\build_windows.ps1
```
