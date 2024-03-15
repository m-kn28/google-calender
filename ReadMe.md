# Google Calendar Event Checker

このスクリプトは、指定されたGoogleカレンダーのイベントを定期的にチェックし、特定の条件に基づいてアクションを実行します。特に、サロンの予約システムへの自動登録を行う機能が追加されています。

## 機能

- Googleカレンダーのイベントを定期的にチェック
- 指定された時間内のイベントを取得
- イベントに基づいてサロンの予約システムに自動で予約を登録
- スクリプトの自動再起動によるメモリリークの防止

## 事前準備

1. Google Cloud Platformでサービスアカウントを作成し、カレンダーAPIを有効にします。
2. サービスアカウントのキーファイル（JSON）をダウンロードし、プロジェクトの適切な場所に配置します。
3. Google ChromeおよびGoogle Chrome Driverのインストール
4. `config.py` ファイルに `SERVICE_ACCOUNT_FILE_PATH`、`CALENDAR_ID`、`GOOGLE_CHROME_DRIVER_PATH`、`SALON_BOARD_USER_ID`、`SALON_BOARD_PASSWORD` を設定します。

```
[sample] config.py
# Set the service account file and calendar id
SERVICE_ACCOUNT_FILE_PATH = './service-account.json'
CALENDAR_ID = ''
GOOGLE_CHROME_DRIVER_PATH = './driver/chromedriver'
SALON_BOARD_USER_ID = ''
SALON_BOARD_PASSWORD = ''

# Set the logging interval and backup count
LOGGING_FILE_PATH = './application.log'
LOGGING_INTERVAL = 1
LOGGING_BACKUP_COUNT = 30
```

```
[sample] ubuntu install path
(google-calender) ubuntu@f7d66587b22c:~/google-calender/scripts$ tree
.
├── application.log
├── command.py
├── config
│   └── config.py
├── driver
│   └── chromedriver-linux64
│       ├── LICENSE.chromedriver
│       └── chromedriver
├── entity
│   └── calendar.py
├── lib
│   └── custom_logger.py
├── service-account.json
└── services
    ├── google_calender.py
    └── salon_board.py
```

## 使い方

1. 必要なライブラリをインストールします。


```
bash
pip install > requirements.txt
```

2. スクリプトを実行します。

```
bash
python app/command.py --check_hours=1 --max_results=10 --confirm_interval=60 --is_restart=False --restart_interval=3600
```

### コマンドラインオプション

- `--check_hours`: チェックする時間範囲（デフォルトは1時間）
- `--max_results`: 取得するイベントの最大数（デフォルトは10）
- `--confirm_interval`: イベントチェックの間隔（秒単位、デフォルトは60秒）
- `--is_restart`: スクリプトを自動的に再起動するかどうか（デフォルトはFalse）
- `--restart_interval`: スクリプトを再起動する間隔（秒単位、デフォルトは3600秒）

## 注意事項

- このスクリプトは、メモリリークを防ぐために定期的に再起動する機能を含んでいます。必要な場合は、`--is_restart` オプションを `True` に設定して使用してください。
- サービスアカウントのキーファイルとカレンダーIDの設定は、セキュリティを考慮して適切に管理してください。
- サロンの予約システムへの自動登録機能を使用するには、`GOOGLE_CHROME_DRIVER_PATH`、`SALON_BOARD_USER_ID`、`SALON_BOARD_PASSWORD` の設定が必要です。これらは、サロンの予約システムにアクセスし、予約を登録するために使用されます。