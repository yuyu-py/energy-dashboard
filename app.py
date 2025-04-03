# app.py
import pandas as pd
from dash import Dash, dcc, html, Input, Output

# データの読み込みと前処理（フィルタリングなし）
energy_data = (
    pd.read_csv("energy_data.csv")
    .assign(date=lambda data: pd.to_datetime(data["date"], format="%Y-%m-%d"))
    .sort_values(by="date")
)

# 地域の一覧を取得
regions = energy_data["region"].sort_values().unique()

# 外部スタイルシートの設定
external_stylesheets = [
    {
        "href": (
            "https://fonts.googleapis.com/css2?"
            "family=Noto+Sans+JP:wght@400;700&display=swap"
        ),
        "rel": "stylesheet",
    },
]

# Dashアプリケーションのインスタンス化（外部スタイルシートを指定）
app = Dash(__name__, external_stylesheets=external_stylesheets)

# ブラウザのタブに表示されるタイトルを設定
app.title = "日本の電力消費ダッシュボード | データで見る電力事情"

# アプリのレイアウトを定義
app.layout = html.Div(
    children=[
        # ヘッダーセクション
        html.Div(
            children=[
                html.P(children="💡", className="header-emoji"),
                html.H1(
                    children="日本の電力消費ダッシュボード", 
                    className="header-title"
                ),
                html.P(
                    children=(
                        "2025年1月の電力消費データと再生可能エネルギー比率を"
                        "地域別に分析・可視化"
                    ),
                    className="header-description",
                ),
            ],
            className="header",
        ),
        
        # コンテンツエリア
        html.Div(
            children=[
                # フィルターメニュー
                html.Div(
                    children=[
                        # 地域フィルター
                        html.Div(
                            children=[
                                html.Div(children="地域", className="menu-title"),
                                dcc.Dropdown(
                                    id="region-filter",
                                    options=[
                                        {"label": region, "value": region}
                                        for region in regions
                                    ],
                                    value="関東",  # デフォルト値
                                    clearable=False,
                                    className="dropdown",
                                ),
                            ],
                        ),
                        # 日付範囲フィルター
                        html.Div(
                            children=[
                                html.Div(children="期間", className="menu-title"),
                                dcc.DatePickerRange(
                                    id="date-range",
                                    min_date_allowed=energy_data["date"].min().date(),
                                    max_date_allowed=energy_data["date"].max().date(),
                                    start_date=energy_data["date"].min().date(),
                                    end_date=energy_data["date"].max().date(),
                                    display_format="YYYY/MM/DD",
                                ),
                            ],
                        ),
                    ],
                    className="menu",
                ),
                
                # グラフセクション
                html.Div(
                    children=[
                        # 電力消費量グラフ
                        html.Div(
                            children=dcc.Graph(
                                id="consumption-chart",
                                config={"displayModeBar": False},
                                style={"height": "450px"},  # グラフの高さを指定
                                responsive=True,  # レスポンシブ対応を有効化
                            ),
                            className="card",
                        ),
                        
                        # 再生可能エネルギー比率グラフ
                        html.Div(
                            children=dcc.Graph(
                                id="renewable-chart",
                                config={"displayModeBar": False},
                                style={"height": "450px"},  # グラフの高さを指定
                                responsive=True,  # レスポンシブ対応を有効化
                            ),
                            className="card",
                        ),
                    ],
                    className="wrapper",
                ),
            ],
        ),
    ]
)

# コールバック関数の定義
@app.callback(
    # 出力の定義
    Output("consumption-chart", "figure"),
    Output("renewable-chart", "figure"),
    # 入力の定義
    Input("region-filter", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
)
def update_charts(region, start_date, end_date):
    """フィルタ条件に基づいてグラフを更新する関数"""
    # データのフィルタリング
    filtered_data = energy_data.query(
        "region == @region"
        " and date >= @start_date and date <= @end_date"
    )
    
    # 消費量グラフの生成
    consumption_chart = {
        "data": [
            {
                "x": filtered_data["date"],
                "y": filtered_data["consumption"],
                "type": "lines",
                "hovertemplate": "%{y:,.1f}万kWh<extra></extra>",
                "line": {"width": 3},  # 線の太さを増やす
            },
        ],
        "layout": {
            "title": {
                "text": f"{region}地方の電力消費量",
                "x": 0.05,
                "xanchor": "left",
                "font": {"size": 20},  # タイトルのフォントサイズを大きく
            },
            "xaxis": {
                "fixedrange": True,
                "title": "日付",  # 軸ラベルを追加
                "gridcolor": "#EEEEEE",  # グリッド線の色を指定
            },
            "yaxis": {
                "fixedrange": True,
                "title": "消費量（万kWh）",  # 軸ラベルを追加
                "gridcolor": "#EEEEEE",  # グリッド線の色を指定
            },
            "colorway": ["#1565C0"],
            "margin": {"t": 50, "l": 50, "r": 25, "b": 50},  # マージン調整
            "hovermode": "closest",  # ホバー表示を最適化
            "plot_bgcolor": "white",  # グラフ背景色を白に
            "autosize": True,  # 自動サイズ調整を有効化
        },
    }
    
    # 再生可能エネルギー比率グラフの生成
    renewable_chart = {
        "data": [
            {
                "x": filtered_data["date"],
                "y": filtered_data["renewable_percent"],
                "type": "lines",
                "line": {"width": 3},  # 線の太さを増やす
                "hovertemplate": "%{y:.1f}%<extra></extra>",  # ホバー表示を改善
            },
        ],
        "layout": {
            "title": {
                "text": f"{region}地方の再生可能エネルギー比率",
                "x": 0.05,
                "xanchor": "left",
                "font": {"size": 20},  # タイトルのフォントサイズを大きく
            },
            "xaxis": {
                "fixedrange": True,
                "title": "日付",  # 軸ラベルを追加
                "gridcolor": "#EEEEEE",  # グリッド線の色を指定
            },
            "yaxis": {
                "ticksuffix": "%",
                "fixedrange": True,
                "title": "再生可能エネルギー比率",  # 軸ラベルを追加
                "gridcolor": "#EEEEEE",  # グリッド線の色を指定
            },
            "colorway": ["#00897B"],
            "margin": {"t": 50, "l": 50, "r": 25, "b": 50},  # マージン調整
            "hovermode": "closest",  # ホバー表示を最適化
            "plot_bgcolor": "white",  # グラフ背景色を白に
            "autosize": True,  # 自動サイズ調整を有効化
        },
    }
    
    # 両方のグラフを返す
    return consumption_chart, renewable_chart

# サーバー起動設定
if __name__ == "__main__":
    app.run(debug=True)