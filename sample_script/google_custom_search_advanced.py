"""
Google Custom Search APIの高度な使用方法を示すサンプルスクリプト

このスクリプトでは以下の機能を実装しています：
1. コマンドライン引数による検索クエリと件数の指定
2. 検索結果のJSONファイルへの保存
3. 検索結果のページネーション処理
4. エラーハンドリングとリトライ処理

使用方法:
    python google_custom_search_advanced.py [検索クエリ] [取得件数]

    例：
    python google_custom_search_advanced.py "機械学習 フレームワーク" 20
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime

from dotenv import load_dotenv

from src.application.client.google_search_client import GoogleSearchClient

# .envファイルを読み込む
load_dotenv()

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("google_search.log")],
)
logger = logging.getLogger("google_search")


def parse_arguments():
    """コマンドライン引数をパースする関数"""
    parser = argparse.ArgumentParser(
        description="Google Custom Search APIを使用して検索を実行します"
    )
    parser.add_argument("query", nargs="?", default="人工知能 応用", help="検索クエリ")
    parser.add_argument(
        "--count",
        "-c",
        type=int,
        default=10,
        help="取得する検索結果の件数 (デフォルト: 10)",
    )
    parser.add_argument("--output", "-o", help="結果を保存するJSONファイルのパス")
    parser.add_argument(
        "--start",
        "-s",
        type=int,
        default=1,
        help="検索結果の開始インデックス (デフォルト: 1)",
    )
    return parser.parse_args()


def save_results_to_file(results, filepath=None):
    """検索結果をJSONファイルに保存する関数"""
    if filepath is None:
        # ファイル名が指定されていない場合は、現在時刻を含むファイル名を生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"search_results_{timestamp}.json"

    # 結果を整形してJSONファイルに保存
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    logger.info(f"検索結果を {filepath} に保存しました")
    return filepath


def is_ip_restriction_error(error):
    """IPアドレス制限エラーかどうかを判定する関数"""
    error_str = str(error)
    return (
        "IP address restriction" in error_str
        or "violates this restriction" in error_str
    )


def fetch_all_results(client, query, total_count, max_retries=3, retry_delay=2):
    """
    指定した件数の検索結果を取得する関数

    Args:
        client: GoogleSearchClientのインスタンス
        query: 検索クエリ
        total_count: 取得する検索結果の合計件数
        max_retries: リトライ回数
        retry_delay: リトライ間の待機時間（秒）

    Returns:
        dict: 全検索結果を含む辞書
    """
    all_items = []
    batch_size = min(
        10, total_count
    )  # Google APIの制限により、1回のリクエストで最大10件まで

    # 必要なページ数を計算
    pages_needed = (total_count + batch_size - 1) // batch_size

    search_info = None

    for page in range(pages_needed):
        start_index = page * batch_size + 1  # Google APIは1から始まるインデックスを使用

        # リトライロジック
        retry_count = 0
        while retry_count <= max_retries:
            try:
                logger.info(
                    f"ページ {page + 1}/{pages_needed} を取得中 (開始位置: {start_index})"
                )

                # 最後のページでは残りの件数だけ取得
                remaining = total_count - len(all_items)
                current_batch_size = min(batch_size, remaining)

                results = client.search(
                    query=query, num=current_batch_size, start=start_index
                )

                # 検索情報を保存（最初のページから）
                if page == 0 and "searchInformation" in results:
                    search_info = results["searchInformation"]

                # 結果がない場合は終了
                if "items" not in results:
                    logger.warning("これ以上の検索結果はありません")
                    break

                # 検索結果をリストに追加
                all_items.extend(results["items"])
                logger.info(f"現在 {len(all_items)}/{total_count} 件の結果を取得済み")

                # 指定件数に達したら終了
                if len(all_items) >= total_count:
                    break

                # APIの制限を考慮して少し待機
                time.sleep(0.5)
                break  # 成功したのでループを抜ける

            except Exception as e:
                # IPアドレス制限エラーの場合は特別なメッセージを表示して終了
                if is_ip_restriction_error(e):
                    logger.error(
                        "Google API Keyに設定されているIPアドレス制限に違反しています。"
                    )
                    logger.error(
                        "Google Cloud Consoleで、このIPアドレスからのアクセスを許可するよう設定を変更してください。"
                    )
                    logger.error(f"エラー詳細: {e}")
                    raise RuntimeError(
                        "IPアドレス制限エラー: Google Cloud Consoleで許可設定が必要です"
                    ) from e

                retry_count += 1
                if retry_count > max_retries:
                    logger.error(f"最大リトライ回数に達しました: {e}")
                    raise

                logger.warning(
                    f"エラーが発生しました（リトライ {retry_count}/{max_retries}）: {e}"
                )
                time.sleep(retry_delay)

    # 最終的な結果を構築
    final_results = {
        "items": all_items[:total_count],  # 指定件数に制限
        "searchInformation": search_info or {},
        "totalRetrieved": len(all_items),
        "requestedCount": total_count,
    }

    return final_results


def display_results(results, query):
    """検索結果を表示する関数"""
    items = results.get("items", [])
    search_info = results.get("searchInformation", {})

    print("\n=== 検索結果 ===")
    print(f"クエリ: {query}")
    print(f"取得件数: {len(items)}")
    print(f"検索時間: {search_info.get('searchTime', '不明')}秒")
    print(f"合計結果数（推定）: {search_info.get('totalResults', '不明')}件")
    print("=" * 50)

    for i, item in enumerate(items, 1):
        print(f"\n{i}. {item['title']}")
        print(f"   URL: {item['link']}")

        if "snippet" in item:
            print(f"   概要: {item['snippet']}")

        if "pagemap" in item and "cse_thumbnail" in item["pagemap"]:
            thumbnail = item["pagemap"]["cse_thumbnail"][0]
            print(f"   サムネイル: {thumbnail.get('src', '不明')}")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    try:
        # コマンドライン引数の処理
        args = parse_arguments()

        logger.info(f"検索クエリ: {args.query}")
        logger.info(f"取得件数: {args.count}")

        # GoogleSearchClientのインスタンスを作成
        client = GoogleSearchClient()

        # 検索実行（全件取得）
        try:
            results = fetch_all_results(client, args.query, args.count)

            # 結果表示
            display_results(results, args.query)

            # 結果をファイルに保存
            if args.output:
                save_results_to_file(results, args.output)
            else:
                # ユーザーに保存するか尋ねる
                save_option = input("\n検索結果をJSONファイルに保存しますか？ (y/n): ")
                if save_option.lower() in ["y", "yes"]:
                    save_results_to_file(results)

        except RuntimeError as e:
            if "IPアドレス制限エラー" in str(e):
                logger.error(
                    "実行を中止します: API Keyの制限により検索を実行できません"
                )
                print("\n=== エラー: Google API Keyの設定に問題があります ===")
                print("現在のIPアドレスからのアクセスが許可されていません。")
                print(
                    "Google Cloud Consoleで、API Keyの設定を確認し、IP制限を解除するか、"
                )
                print("現在使用しているIPアドレスを許可リストに追加してください。")
                print("=" * 50)
            else:
                raise

    except KeyboardInterrupt:
        logger.info("ユーザーによって処理が中断されました")
        sys.exit(1)

    except Exception as e:
        logger.error(f"エラーが発生しました: {e}", exc_info=True)
        sys.exit(1)

    logger.info("処理が正常に完了しました")
