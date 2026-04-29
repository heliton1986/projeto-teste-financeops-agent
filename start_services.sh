#!/bin/bash
# Inicia API (porta 8000) e UI (porta 8501) em background

PROJ_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJ_DIR"

source .env 2>/dev/null || true

echo "[FinanceOps] Iniciando servicos..."

python execution/run_api.py &> /tmp/financeops_api.log &
API_PID=$!
echo "API    PID $API_PID — http://localhost:8000/docs"

streamlit run src/ui/app.py --server.headless true &> /tmp/financeops_ui.log &
UI_PID=$!
echo "UI     PID $UI_PID  — http://localhost:8501"

echo ""
echo "Logs: /tmp/financeops_api.log | /tmp/financeops_ui.log"
echo "Parar: kill $API_PID $UI_PID"
