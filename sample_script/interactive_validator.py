"""
ValidatorAgent のインタラクティブテスト用スクリプト:
標準入力から指示を受け取り、ValidatorAgentで処理します。
必須情報が不足している場合は、フィードバックを返します。
"""

import json
import sys
from typing import Any, Dict

from src.infrastructure.utils.logger import get_logger
from src.usecase.validator.agent import REQUIRED_FIELDS, ValidatorAgent

logger = get_logger(__name__)


def serialize_for_json(obj):
    """JSONシリアライズのためにオブジェクトを変換"""
    if isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_for_json(item) for item in obj]
    elif hasattr(obj, "__dict__"):
        return {
            k: serialize_for_json(v)
            for k, v in obj.__dict__.items()
            if not k.startswith("_")
        }
    elif hasattr(obj, "model_dump"):
        # Pydanticモデルの処理
        return serialize_for_json(obj.model_dump())
    else:
        # その他の型はそのまま
        return obj


def format_result(result: Dict[str, Any]) -> str:
    """結果を読みやすい形式にフォーマットする"""
    output = f"### 出力結果:\n{result['output']}\n\n"

    if not result["is_valid"]:
        output += "### 不足している情報:\n"
        for resource_type, fields in result["missing_fields"].items():
            output += f"リソースタイプ '{resource_type}' の不足フィールド: {', '.join(fields)}\n"

    if result["resources"]:
        output += "\n### 検出されたリソース:\n"
        for resource in result["resources"]:
            output += f"- タイプ: {resource.get('resource_type', 'unknown')}\n"
            for key, value in resource.items():
                if key != "resource_type":
                    output += f"  {key}: {value}\n"

    return output


def print_resource_fields():
    """利用可能なリソースタイプとそれらの必須フィールドを表示"""
    print("\n=== 利用可能なリソースタイプと必須フィールド ===")
    for resource_type, fields in REQUIRED_FIELDS.items():
        print(f"\nリソースタイプ: {resource_type}")
        print(f"必須フィールド: {', '.join(fields)}")
    print("\n")


def interactive_session():
    """インタラクティブなValidatorAgentセッションを実行"""
    agent = ValidatorAgent()
    history = []  # 会話履歴

    print(
        "ValidatorAgentインタラクティブテスト (終了するには 'exit' または 'quit' と入力)"
    )
    print("特殊コマンド:")
    print("  help     - ヘルプを表示")
    print("  fields   - 利用可能なリソースタイプと必須フィールドを表示")
    print("  exit/quit - 終了")
    print("\n指示を入力してください:")

    while True:
        # ユーザー入力を取得
        user_input = input("> ")

        # 特殊コマンドの処理
        if user_input.lower() in ["exit", "quit"]:
            print("テストを終了します")
            break
        elif user_input.lower() == "help":
            print("\n=== ヘルプ ===")
            print(
                "このツールはValidatorAgentのテスト用インタラクティブインターフェースです。"
            )
            print("指示を入力すると、それに対応するリソースがバリデートされます。")
            print("必須フィールドが不足している場合は、それらを補うよう指示されます。")
            print("\n特殊コマンド:")
            print("  help     - このヘルプを表示")
            print("  fields   - 利用可能なリソースタイプと必須フィールドを表示")
            print("  exit/quit - 終了")
            continue
        elif user_input.lower() == "fields":
            print_resource_fields()
            continue

        # レビューアコメントの取得（オプション）
        reviewer_comment = None
        reviewer_input = input(
            "レビューアコメント（省略可能、スキップするには Enter）: "
        )
        if reviewer_input.strip():
            reviewer_comment = reviewer_input

        try:
            # エージェントを実行
            result = agent.run(
                instruction=user_input, reviewer_comment=reviewer_comment
            )

            # 結果を表示
            formatted_result = format_result(result)
            print("\n" + formatted_result)

            # 会話履歴に追加
            history.append(
                {
                    "instruction": user_input,
                    "reviewer_comment": reviewer_comment,
                    "result": result,
                }
            )

            # 不足フィールドがある場合はフィードバック
            if not result["is_valid"]:
                print("\n情報が不足しています。追加情報を入力してください。")

        except Exception as e:
            print(f"エラーが発生しました: {str(e)}")
            logger.error(f"エラー詳細: {e}", exc_info=True)

    # 終了時に会話履歴をファイルに保存（オプション）
    save_history = input("会話履歴をファイルに保存しますか？ (y/n): ")
    if save_history.lower() == "y":
        filename = (
            input("保存するファイル名（デフォルト: history.json）: ") or "history.json"
        )
        try:
            # シリアライズ可能な形式に変換
            serializable_history = serialize_for_json(history)
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(serializable_history, f, ensure_ascii=False, indent=2)
            print(f"会話履歴を {filename} に保存しました")
        except Exception as e:
            print(f"ファイル保存中にエラーが発生しました: {str(e)}")


def batch_process(instruction_file: str):
    """ファイルから指示を読み込んでバッチ処理"""
    agent = ValidatorAgent()
    results = []

    try:
        with open(instruction_file, "r", encoding="utf-8") as f:
            instructions = [line.strip() for line in f if line.strip()]

        for instruction in instructions:
            print(f"処理中: {instruction}")
            result = agent.run(instruction=instruction)
            formatted_result = format_result(result)
            print(formatted_result)
            print("-" * 50)
            results.append({"instruction": instruction, "result": result})

        # 結果をJSONファイルに保存
        output_file = instruction_file + ".results.json"
        serializable_results = serialize_for_json(results)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(serializable_results, f, ensure_ascii=False, indent=2)
        print(f"結果を {output_file} に保存しました")

    except Exception as e:
        print(f"バッチ処理中にエラーが発生しました: {str(e)}")
        logger.error(f"エラー詳細: {e}", exc_info=True)


def main():
    """メイン関数"""
    # コマンドライン引数をチェック
    if len(sys.argv) > 1:
        # ファイルから指示を読み込んでバッチ処理
        instruction_file = sys.argv[1]
        print(f"ファイル '{instruction_file}' からの指示をバッチ処理します")
        batch_process(instruction_file)
    else:
        # インタラクティブモード
        interactive_session()


if __name__ == "__main__":
    main()
