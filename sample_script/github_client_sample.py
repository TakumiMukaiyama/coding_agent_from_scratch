import os
import sys
from pprint import pprint

from dotenv import load_dotenv

# 親ディレクトリをパスに追加してagentsパッケージをインポートできるようにする
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from src.application.client.github_client import GitHubClient

# デバッグログを有効化 - コメントを外すとHTTPリクエストの詳細が表示されます
# logging.basicConfig(level=logging.DEBUG)

load_dotenv()

# 使用するリポジトリ名（自分のリポジトリに変更してください）
REPO_NAME = "Finatext/ai-contest-hanare-banare"


def main():
    """GitHubClientの基本的な機能を示すサンプル関数.

    GitHubClientの基本的な機能を示すサンプル関数.
    """
    # GitHubクライアントの初期化（環境変数GITHUB_TOKENから取得）
    client = GitHubClient(os.environ["GITHUB_TOKEN"])

    # 認証ユーザー情報の表示
    try:
        user = client.github.get_user()
        print(f"認証ユーザー: {user.login}")
        print(f"フルアクセス可能なリポジトリ数: {len(list(user.get_repos()))}")

        # アクセス可能なリポジトリ一覧を表示
        print("\nアクセス可能なリポジトリ一覧:")
        for repo in user.get_repos():
            print(
                f"- {repo.full_name} (デフォルトブランチ: {repo.default_branch}, 権限: {repo.permissions.admin and '管理者' or repo.permissions.push and '書き込み' or '読み取り'})",
            )

        # リポジトリの選択（アクセス可能なリポジトリのいずれかを使用）
        available_repos = [
            repo.full_name for repo in user.get_repos() if repo.permissions.push
        ]
        if available_repos:
            print(f"\n書き込み権限のあるリポジトリを使用します: {available_repos[0]}")
            REPO_NAME = available_repos[0]

        print("")
    except Exception as e:
        print(f"認証ユーザー情報の取得に失敗: {e}")

    print("\n1. リポジトリ情報の取得:")
    try:
        repo = client.get_repository(REPO_NAME)
        print(f"リポジトリ名: {repo.name}")
        print(f"オーナー: {repo.owner.login}")
        print(f"説明: {repo.description}")
        print(f"デフォルトブランチ: {repo.default_branch}")
        print(f"スター数: {repo.stargazers_count}")
    except Exception as e:
        print(f"エラー: {e}")

    print("\n2. ブランチ一覧の取得:")
    try:
        branches = client.list_branches(REPO_NAME)
        print(f"ブランチ一覧: {', '.join(branches)}")
    except Exception as e:
        print(f"エラー: {e}")

    print("\n3. ファイル内容の取得:")
    try:
        # ファイルパスは適宜変更してください
        file_path = "README.md"
        content = client.get_file_content(REPO_NAME, file_path)
        print(f"{file_path}の内容（先頭100文字）:")
        print(content[:100] + "..." if len(content) > 100 else content)
    except Exception as e:
        print(f"エラー: {e}")

    print("\n4. リポジトリ内のファイル一覧の取得:")
    try:
        # 任意のディレクトリを指定できます（空文字列はルートディレクトリ）
        contents = client.get_repo_contents(REPO_NAME, "")
        print("ルートディレクトリの内容:")
        for item in contents:
            print(f"  - {item.path} ({item.type})")
    except Exception as e:
        print(f"エラー: {e}")

    print("\n5. イシュー一覧の取得:")
    try:
        issues = client.list_issues(REPO_NAME, state="open")
        print(f"オープンなイシュー数: {len(issues)}")
        if issues:
            print("最新のイシュー:")
            for issue in issues[:3]:  # 最新の3件まで表示
                print(f"  - #{issue.number}: {issue.title}")
    except Exception as e:
        print(f"エラー: {e}")

    print("\n6. PRの詳細情報を取得:")
    try:
        # 存在するPR番号に変更してください
        pr_number = "1"
        pr_info = client.get_pr_info(REPO_NAME, pr_number)
        print(f"PR #{pr_number} の情報:")
        pprint(pr_info)
    except Exception as e:
        print(f"エラー: {e}")

    print("\n7. 新しいブランチの作成:")
    try:
        # 新しいブランチを作成
        branch_name = "test-github-client-sample"
        new_branch = client.create_branch(REPO_NAME, branch_name)
        print(f"新しいブランチが作成されました: {new_branch.name}")
    except Exception as e:
        print(f"エラー: {e}")

    print("\n8. 未コミットファイルのコミット:")
    try:
        # ローカルにあるファイルをコミットする例
        file_path = "agents/sample_script/github_client_sample.py"
        abs_file_path = os.path.abspath(file_path)

        # ファイルの存在確認
        if os.path.exists(file_path):
            print(f"相対パスでファイルが存在します: {file_path}")
        else:
            print(f"相対パスでファイルが見つかりません: {file_path}")

        if os.path.exists(abs_file_path):
            print(f"絶対パスでファイルが存在します: {abs_file_path}")
        else:
            print(f"絶対パスでファイルが見つかりません: {abs_file_path}")

        # ファイル内容の先頭を表示
        try:
            with open(file_path) as f:
                content = f.read(100)
                print(f"ファイル内容（先頭100文字）: {content}...")
        except Exception as e:
            print(f"ファイル読み込みエラー: {e}")

        file_paths = [abs_file_path]  # 絶対パスを使用

        # 作成したブランチにコミット
        result = client.commit_untracked_files(
            REPO_NAME,
            branch_name,
            file_paths,
            commit_message="サンプルスクリプトのコミット",
        )
        print("未コミットファイルをコミットしました")
        print(f"コミットSHA: {result['commit']['sha']}")
        print("コミットされたファイル:")
        for file_path in result["files"]:
            print(f"  - {file_path}")
    except Exception as e:
        print(f"エラー: {e}")


if __name__ == "__main__":
    main()

# 注意：
# このサンプルスクリプトで「未コミットファイルのコミット」機能がエラーになる場合は、以下を確認してください：
# 1. 使用しているGitHubトークンが対象リポジトリに対する書き込み権限を持っているか
# 2. 認証ユーザー（表示されるユーザー名）が対象リポジトリに対するコラボレーター権限を持っているか
# 3. リポジトリ名（REPO_NAME変数）が正しく設定されているか
#
# GitHubトークンのスコープを確認し、必要に応じて `repo` スコープを含むトークンを生成してください。
# 参考：https://docs.github.com/ja/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
