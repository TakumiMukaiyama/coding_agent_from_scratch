#!/bin/bash

# エラーが発生した場合にスクリプトを終了
set -e

# スクリプトのディレクトリに移動
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

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

echo "実行中の指示: $INSTRUCTION"
echo "================================"

# Typerアプリケーションの実行（coordinatorサブコマンドを削除）
uv run python -m src.main "$INSTRUCTION"

echo "================================"
echo "実行完了" 