"""
JSON操作に関するユーティリティ関数・クラス

JSONデータの変換や処理に関する汎用的な機能を提供します。
"""

import json
from datetime import datetime


class DateTimeEncoder(json.JSONEncoder):
    """
    datetimeオブジェクトをISOフォーマット文字列に変換するJSONエンコーダー

    標準のJSONエンコーダーを拡張し、datetimeオブジェクトをシリアライズできるようにします。
    """

    def default(self, obj):
        """
        オブジェクトのシリアライズ方法を定義

        Args:
            obj: シリアライズ対象のオブジェクト

        Returns:
            シリアライズされた値
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)
