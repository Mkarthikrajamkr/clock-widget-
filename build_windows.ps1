$ErrorActionPreference = "Stop"

python -m pip install --upgrade pip
pip install -r requirements.txt
python -m PyInstaller --noconfirm --windowed --name TradingTimeBlockManager --collect-all PyQt6 run_app.py

Write-Host "Built dist\TradingTimeBlockManager\TradingTimeBlockManager.exe"
