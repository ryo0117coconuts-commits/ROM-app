# ✋ 手指屈曲可動域（ROM）WEB自動解析システム

理学療法における「手指の関節可動域（ROM）測定」をデジタル化（DX）し、リハビリの経過を定量的に可動化するためのWebアプリケーションです。

動画をアップロードするだけで、AIがリアルタイムに手指の骨格線を検出し、最大屈曲・最大伸展角度の推移を自動でグラフ化します。

---

## 🚀 主な機能

- **リアルタイム骨格検知**: Webカメラ等で撮影した動画から、手指の関節位置を自動検出。
- **角度自動計算**: 選択した関節（PIP関節など）の屈曲・伸展角度をフレーム単位でリアルタイム計測。
- **経過推移の可動化**: 過去の測定データと今回の結果を組み合わせ、リハビリの回復経過を折れ線グラフで表示。
- **エラー回避設計**: クラウドサーバー上での動作を想定し、日本語フォントエラー等を完全に排除した安定動作設計。

## 🛠️ 使用技術（テックスタック）

- **Language**: Python 3.x
- **AI / Computer Vision**: MediaPipe, OpenCV
- **Web Framework**: Streamlit
- **Data Science**: Pandas, NumPy
- **Data Visualization**: Matplotlib

## 📦 起動方法（ローカル環境）

リポジトリをクローンし、必要なライブラリをインストールしたあと、Streamlitで起動します。

```bash
git clone [https://github.com/](https://github.com/)ryo0117coconuts-commits/Rom-app.git
cd ROM-app
pip install -r requirements.txt
streamlit run app.py
