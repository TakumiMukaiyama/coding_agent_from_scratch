"""
Terraformコードの生成から検証までを一気通貫で行うサンプルスクリプト

このスクリプトでは以下のプロセスを実行します：
1. ValidatorAgentによる必要情報の整備
2. ProgrammerAgentによるTerraformコードの生成
3. ReviewerAgentによるコードレビュー
4. フィードバックに基づく修正（必要な場合）
"""

import os
import re
import subprocess
import sys
import tempfile

# モジュールのパスを追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.agent.schema.reviewer_input import ReviewerInput
from src.usecase.programmer.agent import ProgrammerAgent
from src.usecase.reviewer.agent import ReviewerAgent
from src.usecase.validator.agent import ValidatorAgent


def main():
    print("===== Terraformコード生成プロセスを開始します =====")

    # 出力ディレクトリの作成
    output_dir = os.path.join(os.path.dirname(__file__), "terraform_output")
    os.makedirs(output_dir, exist_ok=True)

    # 各エージェントの初期化
    validator_agent = ValidatorAgent()
    programmer_agent = ProgrammerAgent()
    reviewer_agent = ReviewerAgent()

    # ステップ1: Validatorによる必要情報の整備
    print("\n== ステップ1: 要件を分析し、必要な情報を整理します ==")
    instruction_validator = """
    AWSにて以下の要件を満たすTerraformコードを作成する必要があります：
    - VPCを1つ作成（CIDR: 10.0.0.0/16）
    - 2つのパブリックサブネット（異なるAZ、CIDR: 10.0.1.0/24, 10.0.2.0/24）
    - 2つのプライベートサブネット（異なるAZ、CIDR: 10.0.3.0/24, 10.0.4.0/24）
    - インターネットゲートウェイとNAT Gateway
    - 各サブネットに対応するルートテーブル
    - セキュリティグループ（HTTP/HTTPS/SSH）
    """

    validation_result = validator_agent.run(instruction_validator)
    print(f"バリデーション結果: {validation_result['output']}")

    # 必要な情報が足りない場合の処理
    if not validation_result["is_valid"]:
        print(f"不足している情報があります: {validation_result['missing_fields']}")
        # 実際のアプリケーションではここでユーザーに追加情報を求める処理を入れる

    # ステップ2: ProgrammerAgentによるTerraformコードの生成
    print("\n== ステップ2: Terraformコードを生成します ==")
    instruction_programmer = """
    AWSで以下のインフラを構築するTerraformコードを作成してください:
    
    1. VPC (CIDR: 10.0.0.0/16)
    2. 2つのパブリックサブネット (ap-northeast-1a, ap-northeast-1c, CIDR: 10.0.1.0/24, 10.0.2.0/24)
    3. 2つのプライベートサブネット (ap-northeast-1a, ap-northeast-1c, CIDR: 10.0.3.0/24, 10.0.4.0/24)
    4. インターネットゲートウェイとNAT Gateway
    5. 適切なルートテーブル設定
    6. HTTP/HTTPS/SSHを許可するセキュリティグループ
    
    コードは以下の条件を満たすこと:
    - module化して再利用可能にする
    - 適切な変数とoutputを定義する
    - リソース名は適切に命名する
    - 必要に応じてタグを付ける
    
    出力形式：
    ```ファイル名
    ファイルの内容
    ```
    
    すべての必要なファイルを出力してください。
    """

    programmer_output = programmer_agent.run(instruction_programmer)
    print("プログラマーの出力を取得しました")

    # 生成されたコードをファイルに保存
    terraform_files = extract_terraform_code(programmer_output)
    save_terraform_files(terraform_files, output_dir)

    # コードの差分を生成
    code_diff = generate_code_diff(terraform_files, output_dir)

    # ステップ3: ReviewerAgentによるコードレビュー
    print("\n== ステップ3: 生成されたコードをレビューします ==")
    reviewer_input = ReviewerInput(
        diff=code_diff,
        programmer_comment="VPCとサブネットを含むAWSインフラのTerraformコードを作成しました。module化して再利用可能にしています。",
    )

    review_result = reviewer_agent.run(reviewer_input)
    print(
        f"レビュー結果: {review_result.summary[:300]}..."
    )  # 出力が長いので一部だけ表示

    # ステップ4: レビュアーのフィードバックに基づく修正（LGTMでなければ）
    if not review_result.lgtm:
        print(
            "\n== ステップ4: レビュアーのフィードバックに基づいてコードを修正します =="
        )
        instruction_update = f"""
        先ほど作成したTerraformコードを以下のレビューコメントに基づいて修正してください:
        
        {review_result.summary}
        
        出力形式：
        ```ファイル名
        ファイルの内容
        ```
        
        すべての必要なファイルを出力してください。
        """

        updated_output = programmer_agent.run(
            instruction_update, reviewer_comment=review_result.summary
        )
        print("修正結果を取得しました")

        # 修正されたコードを保存
        updated_output_dir = os.path.join(
            os.path.dirname(__file__), "terraform_output_updated"
        )
        os.makedirs(updated_output_dir, exist_ok=True)

        updated_terraform_code = extract_terraform_code(updated_output)
        save_terraform_files(updated_terraform_code, updated_output_dir)

        # 最終的なコードに対して再度レビューを行う
        updated_diff = generate_code_diff(
            updated_terraform_code,
            updated_output_dir,
            is_update=True,
            original_dir=output_dir,
        )
        final_reviewer_input = ReviewerInput(
            diff=updated_diff,
            programmer_comment="フィードバックに基づいてTerraformコードを修正しました。",
        )

        final_review = reviewer_agent.run(final_reviewer_input)
        print(f"最終レビュー結果: {final_review.summary[:300]}...")

        if final_review.lgtm:
            print("\n✅ コードがLGTMを受け取りました！")
        else:
            print("\n⚠️ 追加の修正が必要かもしれません。")
    else:
        print("\n✅ 初回でLGTMを受け取りました！")

    print("\n===== Terraformコード生成プロセスが完了しました =====")
    print(f"生成されたTerraformファイルは {output_dir} に保存されています")
    if not review_result.lgtm:
        print(f"修正されたTerraformファイルは {updated_output_dir} に保存されています")


def extract_terraform_code(output: str) -> dict[str, str]:
    """
    エージェント出力からTerraformコードを抽出する関数
    出力形式：
    ```ファイル名
    ファイルの内容
    ```
    """
    terraform_files = {}

    # コードブロックのパターン
    pattern = r"```([^\n]+)\n(.*?)```"

    # 正規表現でコードブロックを検索（re.DOTALLは複数行マッチのため）
    matches = re.finditer(pattern, output, re.DOTALL)

    for match in matches:
        file_name = match.group(1).strip()
        file_content = match.group(2).strip()

        # ファイル名が有効で、コンテンツがある場合のみ追加
        if file_name and file_content:
            # "tf" または "terraform" がファイル名の一部またはファイル拡張子の場合のみ追加
            # これにより、コメントやサンプルコードなど、Terraformファイルではないものを除外
            if (
                file_name.endswith(".tf")
                or "terraform" in file_name.lower()
                or "/" in file_name
            ):
                terraform_files[file_name] = file_content

    # 抽出できたファイル数を表示
    print(f"{len(terraform_files)}個のTerraformファイルを抽出しました。")
    for file_name in terraform_files.keys():
        print(f"- {file_name}")

    return terraform_files


def save_terraform_files(terraform_files: dict[str, str], output_dir: str):
    """
    Terraformコードをファイルに保存する関数

    Args:
        terraform_files: ファイル名とコンテンツのディクショナリ
        output_dir: 出力ディレクトリのパス
    """
    os.makedirs(output_dir, exist_ok=True)

    for file_path, content in terraform_files.items():
        full_path = os.path.join(output_dir, file_path)

        # ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, "w") as f:
            f.write(content)

    print(f"{len(terraform_files)}個のファイルを {output_dir} に保存しました")


def generate_code_diff(
    terraform_files: dict[str, str],
    output_dir: str,
    is_update: bool = False,
    original_dir: str = None,
) -> str:
    """
    コードの差分を生成する関数

    Args:
        terraform_files: 生成されたTerraformファイル
        output_dir: 出力ディレクトリのパス
        is_update: 更新かどうかのフラグ
        original_dir: 比較元ディレクトリ（更新時のみ使用）

    Returns:
        差分の文字列
    """
    # 一時ディレクトリを作成して空のgitリポジトリを初期化
    with tempfile.TemporaryDirectory() as temp_dir:
        # gitリポジトリを初期化
        subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)

        if is_update and original_dir:
            # 更新前のファイルをコピー
            for root, _, files in os.walk(original_dir):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), original_dir)
                    src_path = os.path.join(root, file)
                    dst_path = os.path.join(temp_dir, rel_path)

                    # ディレクトリが存在しない場合は作成
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)

                    # ファイルをコピー
                    with open(src_path) as src, open(dst_path, "w") as dst:
                        dst.write(src.read())

            # ファイルをgitに追加してコミット
            subprocess.run(["git", "add", "."], cwd=temp_dir, capture_output=True)
            subprocess.run(
                ["git", "config", "user.email", "terraform-agent@example.com"],
                cwd=temp_dir,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Terraform Agent"],
                cwd=temp_dir,
                capture_output=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "Initial version"],
                cwd=temp_dir,
                capture_output=True,
            )

            # 現在のファイルをコピー
            for file_path, content in terraform_files.items():
                full_path = os.path.join(temp_dir, file_path)

                # ディレクトリが存在しない場合は作成
                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                with open(full_path, "w") as f:
                    f.write(content)
        else:
            # 新規の場合は単純にファイルを作成
            for file_path, content in terraform_files.items():
                full_path = os.path.join(temp_dir, file_path)

                # ディレクトリが存在しない場合は作成
                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                with open(full_path, "w") as f:
                    f.write(content)

            # ファイルをgitに追加してコミット
            subprocess.run(["git", "add", "."], cwd=temp_dir, capture_output=True)
            subprocess.run(
                ["git", "config", "user.email", "terraform-agent@example.com"],
                cwd=temp_dir,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Terraform Agent"],
                cwd=temp_dir,
                capture_output=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "Initial version"],
                cwd=temp_dir,
                capture_output=True,
            )

            # 一旦全てのファイルを削除して、代わりに空ファイルを作成
            for file_path in terraform_files.keys():
                os.remove(os.path.join(temp_dir, file_path))

        # Gitリポジトリの状態を確認
        if is_update:
            # 既存のファイルと現在のファイルの差分を取得
            diff_result = subprocess.run(
                ["git", "diff", "HEAD"], cwd=temp_dir, capture_output=True, text=True
            )
        else:
            # 新規ファイルの差分を取得（新規ファイル vs 空）
            # ファイルをgitに追加してコミット
            subprocess.run(["git", "add", "."], cwd=temp_dir, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "Empty state"],
                cwd=temp_dir,
                capture_output=True,
            )

            # 現在のファイルをコピー
            for file_path, content in terraform_files.items():
                full_path = os.path.join(temp_dir, file_path)

                # ディレクトリが存在しない場合は作成
                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                with open(full_path, "w") as f:
                    f.write(content)

            # ステージングに追加（コミットはしない）
            subprocess.run(["git", "add", "."], cwd=temp_dir, capture_output=True)

            # 差分を取得
            diff_result = subprocess.run(
                ["git", "diff", "--staged"],
                cwd=temp_dir,
                capture_output=True,
                text=True,
            )

        # 差分を返す
        return diff_result.stdout


if __name__ == "__main__":
    main()
