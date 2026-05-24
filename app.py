import streamlit as st
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tempfile
import os

# MediaPipeの読み込み
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

st.set_page_config(page_title="手指ROM自動解析システム", page_icon="✋", layout="wide")
plt.rcParams['font.family'] = 'MS Gothic'

st.title("✋ 手指屈曲可動域（ROM）WEB自動解析アプリ")
st.markdown("動画から手指の骨格線をリアルタイムに描画し、**「最大屈曲・最大伸展」の推移グラフ**を作成します。")

# 過去の測定履歴を保存する仕組み
if "history_data" not in st.session_state:
    st.session_state.history_data = [
        {"測定回数": "1回目 (初期)", "最大伸展角度(°)": 15.0, "最大屈曲角度(°)": 65.0},
        {"測定回数": "2回目 (2週後)", "最大伸展角度(°)": 8.0, "最大屈曲角度(°)": 78.0},
    ]

st.sidebar.header("📁 アプリについて")
st.sidebar.write("臨床や研究の現場で、手指の関節角度を簡易的に定量化するためのDXツールです。")
st.sidebar.markdown("---")
st.sidebar.info("開発者：理学療法士")

uploaded_file = st.file_uploader("動画ファイル（MP4形式など）を選択してください", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    st.success("🎉 動画の読み込みに成功しました！解析を開始します。")
    
    preview_col, report_col = st.columns([1, 1])
    
    with preview_col:
        st.subheader("🎬 骨格視覚化プレビュー")
        video_placeholder = st.empty()
    
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    cap = cv2.VideoCapture(tfile.name)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    raw_data = []
    frame_count = 0
    
    with mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5) as hands_model:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_count += 1
            time_sec = frame_count / fps
            
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands_model.process(image_rgb)
            
            def calculate_angle(p1, p2, p3):
                v1 = np.array([p1.x - p2.x, p1.y - p2.y, p1.z - p2.z])
                v2 = np.array([p3.x - p2.x, p3.y - p2.y, p3.z - p2.z])
                cos_th = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                return np.degrees(np.arccos(np.clip(cos_th, -1.0, 1.0)))
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image_rgb, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                        mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
                    )
                    
                    mcp = hand_landmarks.landmark[5]
                    pip = hand_landmarks.landmark[6]
                    dip = hand_landmarks.landmark[7]
                    
                    raw_angle = calculate_angle(mcp, pip, dip)
                    index_pip_angle = 180.0 - raw_angle
                    raw_data.append({"Time_sec": time_sec, "Index_PIP_Angle": index_pip_angle})
            else:
                if len(raw_data) > 0:
                    raw_data.append({"Time_sec": time_sec, "Index_PIP_Angle": raw_data[-1]["Index_PIP_Angle"]})
            
            resized_image = cv2.resize(image_rgb, (400, 300))
            video_placeholder.image(resized_image, channels="RGB")
            
        cap.release()
        os.unlink(tfile.name)

    with report_col:
        df_raw = pd.DataFrame(raw_data)
        
        if not df_raw.empty:
            max_flexion = df_raw["Index_PIP_Angle"].max()
            max_extension = df_raw["Index_PIP_Angle"].min()
            
            st.subheader("📊 今回の測定結果（ピーク値）")
            
            meta_col1, meta_col2 = st.columns(2)
            meta_col1.metric(label="👍 最大屈曲角度 (PIP)", value=f"{max_flexion:.1f} °")
            meta_col2.metric(label="🤚 最大伸展角度 (PIP)", value=f"{max_extension:.1f} °")
            
            st.markdown("---")
            if st.button("💾 この測定結果を経過履歴に追加する"):
                next_count = len(st.session_state.history_data) + 1
                st.session_state.history_data.append({
                    "測定回数": f"{next_count}回目 (今回)",
                    "最大伸展角度(°)": round(max_extension, 1),
                    "最大屈曲角度(°)": round(max_flexion, 1)
                })
                st.success("履歴に追加しました！下の「経過推移グラフ」が更新されます。")

            st.balloons()
        else:
            st.error("データが正常に集計できませんでした。")

st.markdown("---")
st.header("📉 複数回のリハビリ経過・可動域推移グラフ")

df_history = pd.DataFrame(st.session_state.history_data)
col_graph, col_table = st.columns([2, 1])

with col_graph:
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df_history["測定回数"], df_history["最大屈曲角度(°)"], marker='o', linewidth=3, color="#1f77b4", label="最大屈曲")
    ax.plot(df_history["測定回数"], df_history["最大伸展角度(°)"], marker='s', linewidth=3, color="#ff7f0e", label="最大伸展")
    ax.set_title("手指可動域（ROM）リハビリ経過の推移", fontsize=12, fontweight='bold')
    ax.set_ylabel("角度 (度)", fontsize=10)
    ax.set_ylim(-5, 110)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(loc="center right")
    st.pyplot(fig)

with col_table:
    st.write("📋 経過データ一覧")
    st.dataframe(df_history, hide_index=True)
