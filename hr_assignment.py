import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
import warnings
warnings.filterwarnings(action='ignore')
import os


st.set_page_config(page_title="퇴직율 대시보드", layout="wide")
sns.set(style="whitegrid")

# 폰트 경로를 직접 지정
font_dir = "./fonts"
font_path = os.path.join(font_dir, "NotoSansKR-Regular.ttf")

fontprop = fm.FontProperties(fname=font_path)

plt.rcParams["font.family"] = fontprop.get_name()
plt.rcParams["axes.unicode_minus"] = False

# 1) 데이터 로드
@st.cache_data
def load_df(path:str ="HR Data.csv") -> pd.DataFrame:
    try:
        df = pd.read_csv(path, encoding="utf-8")
    except: 
        return pd.DataFrame()
    df["퇴직"] = df["퇴직여부"].map({"Yes":1, "No":0}).astype("int8")
    df.drop(['직원수', '18세이상'], axis=1, inplace=True)
    return df

df = load_df()
if df.empty:
    st.error("데이터가 없습니다. 'HR Data.csv' 파일을 확인하세요.")
    st.stop()

# ===== KPI  =====
# 1) 헤더 & KPI
st.title("다양성 HR 대시보드")

n = len(df); quit_n = int(df["퇴직"].sum())

female_ratio = (df["성별"].value_counts(normalize=True).get("Female", 0)) * 100
mean_age = df["나이"].mean()

k1, k2, k3 = st.columns(3)
k1.metric("전체 직원 수", f"{n:,}명")
k2.metric("여성 비율", f"{female_ratio:.1f}%")
k3.metric("평균 연령", f"{mean_age:.1f}세")

# ==== 그래프 1행 2열 ====
c1, c2 = st.columns(2)

# (좌) 성별 구성 파이차트
with c1:
    st.subheader("⚧ 성별 구성 비율")
    gender_count = df["성별"].value_counts()
    fig1, ax1 = plt.subplots(figsize=(5,5))
    ax1.pie(
        gender_count,
        labels=gender_count.index,
        autopct="%.1f%%",
        startangle=90,
        textprops={'fontproperties': fontprop}
    )
    st.pyplot(fig1)

# (우) 연령대 분포 바차트
with c2:
    st.subheader("👥 연령대 분포")
    bins = [18,29,39,49,59,70]
    labels = ["20대 이하","30대","40대","50대","60대 이상"]
    df["연령대"] = pd.cut(df["나이"], bins=bins, labels=labels, right=True)
    age_dist = df["연령대"].value_counts().sort_index()
    
    fig2, ax2 = plt.subplots(figsize=(6,4))
    sns.barplot(x=age_dist.index, y=age_dist.values, ax=ax2)
    ax2.set_ylabel("직원 수", fontproperties=fontprop)
    ax2.set_xlabel("연령대", fontproperties=fontprop)
    ax2.set_xticklabels(age_dist.index, fontproperties=fontprop)
    ax2.bar_label(ax2.containers[0], fontproperties=fontprop)
    st.pyplot(fig2)

# ===== 그래프 1행 1열 =====
st.subheader("💍 결혼 여부별 야근 정도 (성별 구분)")
if "결혼여부" in df.columns and "야근정도" in df.columns and "성별" in df.columns:
    cross = pd.crosstab([df["결혼여부"], df["성별"]], df["야근정도"], normalize="index")*100
    cross = cross.reset_index()

    fig3, ax3 = plt.subplots(figsize=(8,4))
    sns.barplot(x="결혼여부", y=cross.columns[2], hue="성별", data=cross, ax=ax3)
    ax3.set_ylabel("비율(%)", fontproperties=fontprop)
    ax3.set_xlabel("결혼여부", fontproperties=fontprop)
    ax3.set_xticklabels(ax3.get_xticklabels(), fontproperties=fontprop)
    ax3.legend(title="성별", title_fontproperties=fontprop, prop=fontprop)
    st.pyplot(fig3)
else:
    st.info("⚠️ 데이터에 [결혼여부], [야근정도], [성별] 컬럼이 필요합니다.")
    