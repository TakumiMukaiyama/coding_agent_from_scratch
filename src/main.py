import json
import os
import sys

import typer
from src.application.client.aws.dynamodb_client import DynamodbClient
from src.application.client.slack_client import SlackClient
from src.infrastructure.config.aws_setting import aws_settings
from src.infrastructure.config.slack_setting import slack_settings
from src.infrastructure.utils.logger import get_logger
from src.usecase.agent_coordinator import AgentCoordinator
from src.usecase.reporter.agent import ReporterAgent
from src.usecase.validator.agent import ValidatorAgent
from dotenv import load_dotenv

load_dotenv()

logger = get_logger(__name__)

app = typer.Typer(help="エージェント実行CLI")


@app.command()
def validator(
    instruction: str = typer.Argument(..., help="バリデーションしたい構成に関する指示内容"),
    reviewer_comment: str | None = typer.Option(
        None,
        "--reviewer-comment",
        "-r",
        help="レビュアーからのフィードバック",
    ),
):
    """Validatorエージェントを実行します."""
    try:
        agent = ValidatorAgent()
        result = agent.run(instruction, reviewer_comment)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}", file=sys.stderr)
        sys.exit(1)


@app.command()
def coordinator(
    instruction: str = typer.Argument(..., help="プログラマーエージェントへの指示内容"),
):
    """Programmerエージェントを実行します."""
    dynamodb_client = DynamodbClient(aws_settings.DYNAMODB_TABLE_NAME)
    slack_client = SlackClient(
        signing_secret=slack_settings.SLACK_SIGNING_SECRET,
        bot_token=slack_settings.SLACK_BOT_USER_OAUTH_TOKEN,
    )
    session_id = os.environ.get("SESSION_ID")

    # SESSION_IDが設定されていない場合は空文字列で処理
    if session_id is None:
        logger.warning("SESSION_IDが設定されていません。デフォルト値を使用します。")
        session_id = ""
        thread_ts = ""
        channel_id = ""
    else:
        session_item = dynamodb_client.get_item({"session_id": session_id})
        thread_ts = session_item.get("thread_ts", "")
        channel_id = session_item.get("channel_id", "")

    try:
        # terraform code生成
        agent = AgentCoordinator()
        max_iterations = 3
        auto_create_branch = True
        prompt = """
        snowflakeのterraformコードを生成し、terraform/snowflake/environments/配下のファイルを編集し、適用してください。
        terraformコードの生成ルールはagents/src/agent/rules/terraform_coding.mdを参照し、厳守してください。
        ※ GoogleSearchClient.searchは使わないでください
        ※ 実行確認は不要です。ファイルの編集を行なってください
        """
        instruction = f"{prompt}\n{instruction}"
        slack_client.send_thread_message(channel_id, thread_ts, "コードの生成を開始します :loading:")
        result = agent.development_cycle(instruction, max_iterations, auto_create_branch)
        slack_client.send_thread_message(channel_id, thread_ts, "コードの生成が完了したよ〜〜👏")

    except Exception:
        logger.exception()
        slack_client.send_thread_message(channel_id, thread_ts, "エラーが発生したブラ〜〜😭")
        sys.exit(1)

    # ブランチの変更を確認
    branch_name = result.get("branch_name", "")
    if not branch_name:
        slack_client.send_thread_message(channel_id, thread_ts, "作業ブランチ名が設定されていません。プルリクエストを作成できません。")
        sys.exit(1)

    # PR情報の取得
    pr_number = result.get("pr_number")
    pr_url = result.get("pr_url")

    if not pr_number:
        slack_client.send_thread_message(channel_id, thread_ts, "プルリクエストの作成に失敗したブラ〜〜😭")
        sys.exit(1)

    # プルリクエスト情報をDynamoDBに保存
    try:
        if session_id:
            try:
                # セッションIDを使用してアイテムを取得
                session_item = dynamodb_client.get_item({"session_id": session_id})

                if session_item:
                    dynamodb_client.update_item(
                        key={"session_id": session_id},
                        update_expression="SET pr_id = :pr_id",
                        expression_attribute_values={":pr_id": str(pr_number)},
                    )
                    # statusは予約語なので、#statusを使用
                    dynamodb_client.update_item(
                        key={"session_id": session_id},
                        update_expression="SET #status = :status",
                        expression_attribute_names={"#status": "status"},
                        expression_attribute_values={":status": "IN_REVIEW"},
                    )
                else:
                    # 新規アイテムの作成
                    dynamodb_client.put_item(
                        {
                            "session_id": session_id,
                            "pr_id": str(pr_number),
                        },
                    )

                logger.info(f"DynamoDBにPR ID {pr_number} を保存しました")
            except Exception:
                logger.exception()
                slack_client.send_thread_message(channel_id, thread_ts, "DynamoDBの更新に失敗したブラ〜〜😭")
        else:
            print("SESSION_IDが設定されていないため、DynamoDBの更新をスキップします")
        slack_client.send_thread_message(channel_id, thread_ts, "PRの作成が完了したよ〜〜👏")
    except Exception:
        if session_id and channel_id and thread_ts:
            slack_client.send_thread_message(channel_id, thread_ts, "エラーが発生したブラ〜〜😭")
        sys.exit(1)


@app.command()
def reporter():
    """Reporterエージェントを実行します。"""
    try:
        agent = ReporterAgent()
        result = agent.run()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    app()
