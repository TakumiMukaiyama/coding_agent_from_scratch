#!/usr/bin/env python
"""プログラマーエージェントとレビュアーエージェントの開発サイクルの例を示します。"""

import os
import sys
import time

from openai import RateLimitError

from src.usecase.agent_coordinator import AgentCoordinator

# 親ディレクトリをPYTHONPATHに追加（インポートの前に実行）
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)


def main():
    # コーディネーターを初期化
    coordinator = AgentCoordinator()

    # 開発サイクルを実行
    instruction = """
    以下のタスクを実装してください：
        
    1. examples/fibonacci.pyという新しいファイルを作成する
    2. フィボナッチ数列を計算する関数を実装する
    3. 関数はn番目のフィボナッチ数を返すようにする
    4. 再帰と反復の両方の実装を提供する
    5. コマンドラインから実行できるメイン関数も実装する
    """

    max_retries = 3
    retry_delay = 60  # 秒単位

    for attempt in range(max_retries):
        try:
            # 自動でブランチ名を生成して作業用ブランチを作成
            final_programmer_output, final_reviewer_output = (
                coordinator.development_cycle(
                    instruction,
                    max_iterations=2,
                    auto_create_branch=True,
                )
            )

            print("\n=== 最終結果 ===")
            print(f"プログラマー最終出力: {final_programmer_output[:200]}...")
            print(f"レビュアー最終出力: {final_reviewer_output[:200]}...")
            break

        except RateLimitError as e:
            if attempt < max_retries - 1:
                print(
                    f"レート制限エラーが発生しました。{retry_delay}秒後に再試行します。(試行 {attempt + 1}/{max_retries})",
                )
                time.sleep(retry_delay)
                # 次の試行では待機時間を2倍にする
                retry_delay *= 2
            else:
                print(f"最大試行回数に達しました。エラー: {e}")
                raise


if __name__ == "__main__":
    main()
