#!/bin/bash

# エラーが発生した場合にスクリプトを終了
set -e

# スクリプトのディレクトリに移動
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ログディレクトリを作成
mkdir -p logs

# 現在の日時でログファイル名を生成
LOG_FILE="logs/agent_$(date +%Y%m%d_%H%M%S).log"

# デフォルトの指示内容
DEFAULT_INSTRUCTION="Generate a code which calculate fibonacci number. Language is Python."

# 引数の確認
if [ $# -eq 0 ]; then
    echo "指示内容を入力してください（デフォルト: $DEFAULT_INSTRUCTION）:"
    read -r INSTRUCTION
    if [ -z "$INSTRUCTION" ]; then
        INSTRUCTION="$DEFAULT_INSTRUCTION"
    fi
else
    INSTRUCTION="$*"
fi

echo "実行中の指示: $INSTRUCTION" | tee "$LOG_FILE"
echo "ログファイル: $LOG_FILE" | tee -a "$LOG_FILE"
echo "実行開始時刻: $(date)" | tee -a "$LOG_FILE"
echo "================================" | tee -a "$LOG_FILE"

# Typerアプリケーションの実行（coordinatorサブコマンドを削除）
uv run python -m src.main "$INSTRUCTION" 2>&1 | tee -a "$LOG_FILE"

echo "================================" | tee -a "$LOG_FILE"
echo "実行終了時刻: $(date)" | tee -a "$LOG_FILE"
echo "実行完了" | tee -a "$LOG_FILE"
echo "ログが保存されました: $LOG_FILE" 