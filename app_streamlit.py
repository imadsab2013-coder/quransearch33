"""
🌟 تطبيق Streamlit للبحث القرآني المتقدم
مع السياق والألفاظ والتفاعل الكامل
"""

import streamlit as st
import pandas as pd
import re
import os
from typing import List, Dict, Tuple

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚙️ إعدادات Streamlit
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.set_page_config(
    page_title="مجلس البينة - البحث القرآني",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎨 التصميم والأنماط
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
    <style>
    * { direction: rtl; text-align: right; }
    
    .main {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
        color: #ffffff;
    }
    
    .search-box {
        background: rgba(0, 204, 255, 0.1);
        border: 2px solid #00ccff;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 0 20px rgba(0, 204, 255, 0.2);
    }
    
    .result-card {
        background: rgba(0, 0, 0, 0.4);
        border-right: 4px solid #ff3366;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: inset 0 0 20px rgba(0, 204, 255, 0.05);
    }
    
    .verse-text {
        background: rgba(0, 204, 255, 0.05);
        border-right: 3px solid #00ccff;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        font-size: 18px;
        line-height: 2;
        color: #ffffff;
    }
    
    .center-verse {
        background: rgba(255, 51, 102, 0.1);
        border-right: 4px solid #ff3366;
        font-weight: bold;
    }
    
    .word-result {
        background: rgba(76, 175, 80, 0.05);
        border: 1px solid #4CAF50;
        border-radius: 8px;
        padding: 12px;
        margin: 10px 0;
    }
    
    h1, h2, h3 { color: #00ccff !important; }
    
    .stButton>button {
        background-color: #ff3366 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
    }
    
    .stButton>button:hover {
        background-color: #ff1744 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔧 دوال مساعدة
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def normalize_arabic(text):
    """توحيد النصوص العربية"""
    if not isinstance(text, str):
        return ""
    text = re.sub(r"[\u064B-\u0652]", "", text)
    text = re.sub(r"[إأآٱا]", "ا", text)
    text = re.sub(r"[ىي]", "ي", text)
    text = re.sub(r"[ةه]", "ه", text)
    return text.strip()

@st.cache_data
def load_quran_data():
    """تحميل بيانات القرآن"""
    for path in ["data/data_quran.xlsx", "data_quran.xlsx", "./data/data_quran.xlsx"]:
        if os.path.exists(path):
            return pd.read_excel(path)
    return None

@st.cache_data
def load_words_data():
    """تحميل بيانات الألفاظ"""
    for path in ["data/data_words.xlsx", "data_words.xlsx", "./data/data_words.xlsx"]:
        if os.path.exists(path):
            return pd.read_excel(path)
    return None

def identify_quran_columns(df):
    """تحديد أسماء الأعمدة في ملف القرآن"""
    cols = df.columns
    surah_col = next((c for c in cols if c in ['السورة', 'surah', 'Surah']), None)
    verse_col = next((c for c in cols if c in ['رقم الآية', 'verse_number', 'Verse', 'آية', 'v رقم الآية']), None)
    text_col = next((c for c in cols if c in ['نص الآية', 'text', 'Text', 'الآية']), None)
    return surah_col, verse_col, text_col

def identify_words_columns(df):
    """تحديد أسماء الأعمدة في ملف الألفاظ"""
    cols = df.columns
    word_col = next((c for c in cols if c in ['اللفظ', 'word', 'Word', 'الكلمة']), None)
    count_col = next((c for c in cols if c in ['عدد الورود', 'count', 'Count', 'العدد']), None)
    surah_col = next((c for c in cols if c in ['السورة', 'surah', 'Surah']), None)
    verse_col = next((c for c in cols if c in ['رقم الآية', 'verse_number', 'Verse', 'آية', 'r رقم الآية']), None)
    text_col = next((c for c in cols if c in ['نص الآية الكاملة', 'نص الآية', 'text', 'Text']), None)
    return word_col, count_col, surah_col, verse_col, text_col

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📱 الواجهة الرئيسية
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# العنوان الرئيسي
col1, col2 = st.columns([1, 3])
with col2:
    st.markdown("<h1 style='color: #00ccff; text-align: center;'>📖 مجلس البينة</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #00ccff; text-align: center;'>محرك البحث القرآني المتقدم</h3>", unsafe_allow_html=True)

st.divider()

# تحميل البيانات
df_quran = load_quran_data()
df_words = load_words_data()

if df_quran is None:
    st.error("❌ لم يتم العثور على ملف بيانات القرآن (data_quran.xlsx)")
    st.stop()

# تحديد الأعمدة
surah_col, verse_col, text_col = identify_quran_columns(df_quran)

if not all([surah_col, verse_col, text_col]):
    st.error("❌ لم نتمكن من تحديد أعمدة بيانات القرآن")
    st.info(f"الأعمدة المتوفرة: {list(df_quran.columns)}")
    st.stop()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔍 تنسيق البحث
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

left_col, right_col = st.columns(2)

# ━━━━━━ البحث عن السياق (اليسار) ━━━━━━
with left_col:
    st.markdown("""
        <div class='search-box'>
            <h3 style='color: #00ccff;'>📍 البحث عن الآية بالسياق</h3>
        </div>
    """, unsafe_allow_html=True)
    
    context_query = st.text_input(
        "ابحث عن آية أو كلمة أو جملة:",
        placeholder="مثال: الحمد لله, اني جاعل في الارض",
        key="context_search"
    )
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        search_context = st.button("🔍 بحث بالسياق", key="btn_context")
    with col_btn2:
        st.write("")  # فسحة
    
    if search_context and context_query:
        query_norm = normalize_arabic(context_query)
        
        # البحث
        matching_verses = []
        for idx, row in df_quran.iterrows():
            text_norm = normalize_arabic(str(row[text_col]))
            if query_norm in text_norm:
                matching_verses.append({
                    'surah': row[surah_col],
                    'verse': int(row[verse_col]),
                    'idx': idx
                })
        
        if matching_verses:
            st.success(f"✅ وجدت {len(matching_verses)} نتيجة")
            
            # عرض كل نتيجة
            for result_idx, match in enumerate(matching_verses):
                with st.container():
                    st.markdown(f"""
                        <div class='result-card'>
                            <h4>📌 النتيجة #{result_idx + 1}</h4>
                            <p><strong>السورة:</strong> {match['surah']} | <strong>الآية:</strong> {match['verse']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # الحصول على السياق
                    start_verse = max(1, match['verse'] - 6)
                    end_verse = match['verse'] + 6
                    
                    mask = (
                        (df_quran[surah_col] == match['surah']) &
                        (df_quran[verse_col].astype(int).between(start_verse, end_verse))
                    )
                    
                    context_df = df_quran[mask].sort_values(verse_col)
                    
                    # عرض السياق
                    st.markdown("<h4 style='color: #ff3366;'>📖 السياق (6 آيات قبل + الآية + 6 آيات بعد):</h4>", unsafe_allow_html=True)
                    
                    for _, verse_row in context_df.iterrows():
                        v_num = int(verse_row[verse_col])
                        v_text = verse_row[text_col]
                        
                        if v_num == match['verse']:
                            st.markdown(f"""
                                <div class='verse-text center-verse'>
                                    <strong>⭐ [{v_num}]</strong> ﴿{v_text}﴾
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                                <div class='verse-text'>
                                    <strong>[{v_num}]</strong> ﴿{v_text}﴾
                                </div>
                            """, unsafe_allow_html=True)
                    
                    st.divider()
        else:
            st.warning("❌ لم يتم العثور على نتائج")

# ━━━━━━ البحث عن الألفاظ (اليمين) ━━━━━━
with right_col:
    st.markdown("""
        <div class='search-box'>
            <h3 style='color: #00ccff;'>🔤 البحث عن اللفظ/الكلمة</h3>
        </div>
    """, unsafe_allow_html=True)
    
    if df_words is None:
        st.warning("⚠️ بيانات الألفاظ غير متوفرة")
        word_query = st.text_input(
            "البحث محدود بدون بيانات الألفاظ",
            disabled=True,
            key="word_search"
        )
    else:
        word_col_w, count_col_w, surah_col_w, verse_col_w, text_col_w = identify_words_columns(df_words)
        
        word_query = st.text_input(
            "ابحث عن لفظ أو كلمة:",
            placeholder="مثال: الحمد, كتاب, ملك",
            key="word_search"
        )
        
        col_btn3, col_btn4 = st.columns(2)
        with col_btn3:
            search_word = st.button("🔍 بحث عن اللفظ", key="btn_word")
        with col_btn4:
            st.write("")  # فسحة
        
        if search_word and word_query:
            query_norm = normalize_arabic(word_query)
            
            # البحث في ملف الألفاظ
            if word_col_w:
                mask = df_words[word_col_w].apply(
                    lambda x: query_norm in normalize_arabic(str(x))
                )
                results = df_words[mask]
            else:
                results = pd.DataFrame()
            
            if not results.empty:
                total_count = results[count_col_w].sum() if count_col_w else len(results)
                st.success(f"✅ المواضع: {total_count}")
                
                st.markdown(f"""
                    <div class='search-box'>
                        <h4>📊 البحث عن: {word_query}</h4>
                        <p>🔢 عدد المواضع: {total_count}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # عرض النتائج
                for result_idx, (_, row) in enumerate(results.iterrows(), 1):
                    surah = row[surah_col_w] if surah_col_w else "؟"
                    verse = int(row[verse_col_w]) if verse_col_w else "؟"
                    text = row[text_col_w] if text_col_w else "نص غير متوفر"
                    count = int(row[count_col_w]) if count_col_w else 1
                    
                    with st.container():
                        # زر لعرض السياق
                        col_verse, col_context = st.columns([3, 1])
                        
                        with col_verse:
                            st.markdown(f"""
                                <div class='word-result'>
                                    <strong>{result_idx}. {surah} : {verse}</strong><br>
                                    ﴿{text}﴾
                                </div>
                            """, unsafe_allow_html=True)
                        
                        with col_context:
                            if st.button("📖 السياق", key=f"context_{result_idx}"):
                                st.session_state[f"show_context_{result_idx}"] = True
                        
                        # عرض السياق إذا تم الضغط
                        if st.session_state.get(f"show_context_{result_idx}", False):
                            st.markdown(f"""
                                <h4 style='color: #ff3366;'>📖 السياق - {surah} : {verse}</h4>
                            """, unsafe_allow_html=True)
                            
                            # الحصول على السياق من ملف القرآن
                            start_verse = max(1, verse - 6)
                            end_verse = verse + 6
                            
                            mask_context = (
                                (df_quran[surah_col] == surah) &
                                (df_quran[verse_col].astype(int).between(start_verse, end_verse))
                            )
                            
                            context_df = df_quran[mask_context].sort_values(verse_col)
                            
                            for _, ctx_verse in context_df.iterrows():
                                v_num = int(ctx_verse[verse_col])
                                v_text = ctx_verse[text_col]
                                
                                if v_num == verse:
                                    st.markdown(f"""
                                        <div class='verse-text center-verse'>
                                            <strong>⭐ [{v_num}]</strong> ﴿{v_text}﴾
                                        </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.markdown(f"""
                                        <div class='verse-text'>
                                            <strong>[{v_num}]</strong> ﴿{v_text}﴾
                                        </div>
                                    """, unsafe_allow_html=True)
                            
                            st.divider()
            else:
                st.warning(f"❌ لم يتم العثور على اللفظ: '{word_query}'")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📋 الشريط الجانبي
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with st.sidebar:
    st.markdown("<h2 style='color: #00ccff;'>⚙️ الإعدادات</h2>", unsafe_allow_html=True)
    st.divider()
    
    with st.expander("📊 معلومات البيانات"):
        st.write("**بيانات القرآن:**")
        st.info(f"عدد الآيات: {len(df_quran)}")
        st.write(f"الأعمدة: {', '.join(df_quran.columns)}")
        
        if df_words is not None:
            st.write("\n**بيانات الألفاظ:**")
            st.info(f"عدد الصفوف: {len(df_words)}")
            st.write(f"الأعمدة: {', '.join(df_words.columns)}")
    
    with st.expander("💡 نصائح البحث"):
        st.write("""
        - **البحث بالسياق:** أدخل كلمة أو جملة من الآية
        - **البحث عن اللفظ:** أدخل الكلمة بأي شكل من أشكالها
        - اللفظ يبحث تلقائياً عن جميع الحروف (بدون تشكيل)
        - اضغط على "السياق" لرؤية 13 آية حول الآية
        """)
    
    with st.expander("🌐 معلومات التطبيق"):
        st.write("""
        **مجلس البينة - محرك البحث القرآني المتقدم**
        
        تطبيق متخصص للبحث والدراسة المتقدمة للقرآن الكريم
        
        - 🔍 بحث متقدم بالسياق
        - 🔤 بحث عن الألفاظ والكلمات
        - 📖 عرض السياق الموسع
        - ✨ معالجة التشكيل التلقائية
        """)

st.divider()
st.markdown("<p style='text-align: center; color: #00ccff;'>© 2024 - مجلس البينة</p>", unsafe_allow_html=True)
