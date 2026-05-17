"""
🌟 مجلس البينة - محرك البحث القرآني المتقدم V2
نظام التبادل الديناميكي الهيكلي مع التحكم المادي
"""

import streamlit as st
import pandas as pd
import re
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚙️ إعدادات Streamlit
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.set_page_config(
    page_title="مجلس البينة - البحث القرآني V2",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎨 التصميم والأنماط CSS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
    <style>
    * { direction: rtl; text-align: right; }
    
    .main {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
        color: #ffffff;
    }
    
    .control-panel {
        background: rgba(0, 204, 255, 0.08);
        border: 2px solid #00ccff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 25px;
        box-shadow: 0 0 20px rgba(0, 204, 255, 0.1);
    }
    
    .table-container {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 10px;
        padding: 15px;
        margin: 20px 0;
        border: 1px solid #1a1a3a;
    }
    
    .preview-container {
        background: rgba(255, 51, 102, 0.05);
        border: 2px solid #ff3366;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: inset 0 0 15px rgba(255, 51, 102, 0.1);
    }
    
    .verse-text {
        background: rgba(0, 204, 255, 0.08);
        border-right: 4px solid #00ccff;
        padding: 18px;
        border-radius: 8px;
        font-size: 18px;
        line-height: 2;
        color: #ffffff;
        word-wrap: break-word;
        font-family: 'Arial', sans-serif;
    }
    
    .action-buttons {
        display: flex;
        gap: 10px;
        margin-top: 15px;
        flex-wrap: wrap;
    }
    
    .stButton>button {
        background-color: #ff3366 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        background-color: #ff1744 !important;
        box-shadow: 0 0 15px rgba(255, 51, 102, 0.5) !important;
    }
    
    .context-verses {
        background: rgba(0, 204, 255, 0.03);
        border-left: 3px solid #00ccff;
        padding: 15px;
        margin: 10px 0;
        border-radius: 6px;
    }
    
    .context-center {
        background: rgba(255, 51, 102, 0.1);
        border-left: 4px solid #ff3366;
        font-weight: bold;
    }
    
    h1, h2, h3 { 
        color: #00ccff !important; 
        text-shadow: 0 0 10px rgba(0, 204, 255, 0.3);
    }
    
    .info-text {
        color: #888888;
        font-size: 13px;
        margin-top: 5px;
    }
    
    .stat-box {
        background: rgba(76, 175, 80, 0.1);
        border-left: 4px solid #4CAF50;
        padding: 12px;
        border-radius: 6px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔧 دوال مساعدة
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def normalize_arabic(text):
    """توحيد النصوص العربية للبحث"""
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

def search_context(df, surah_col, verse_col, text_col, query, before, after):
    """البحث عن السياق"""
    query_norm = normalize_arabic(query)
    if not query_norm:
        return []
    
    results = []
    for idx, row in df.iterrows():
        text_norm = normalize_arabic(str(row[text_col]))
        if query_norm in text_norm:
            surah = row[surah_col]
            verse = int(row[verse_col])
            
            # الحصول على السياق
            start = max(1, verse - before)
            end = verse + after
            
            mask = (
                (df[surah_col] == surah) &
                (df[verse_col].astype(int).between(start, end))
            )
            
            context_df = df[mask].sort_values(verse_col)
            context_verses = []
            
            for _, ctx_row in context_df.iterrows():
                v_num = int(ctx_row[verse_col])
                context_verses.append({
                    'verse': v_num,
                    'text': ctx_row[text_col],
                    'is_center': (v_num == verse)
                })
            
            results.append({
                'surah': surah,
                'verse': verse,
                'text': row[text_col],
                'context_verses': context_verses,
                'index': idx
            })
    
    return results

def search_words(df, word_col, query):
    """البحث عن الألفاظ"""
    query_norm = normalize_arabic(query)
    if not query_norm:
        return pd.DataFrame()
    
    mask = df[word_col].apply(lambda x: query_norm in normalize_arabic(str(x)))
    return df[mask]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📱 تهيئة الجلسة (Session State)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if 'selected_verse' not in st.session_state:
    st.session_state.selected_verse = None

if 'selected_words' not in st.session_state:
    st.session_state.selected_words = None

if 'context_query' not in st.session_state:
    st.session_state.context_query = ""

if 'words_query' not in st.session_state:
    st.session_state.words_query = ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎯 العنوان الرئيسي
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<h1 style='text-align: center;'>📖 مجلس البينة</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #00ccff;'>محرك البحث القرآني المتقدم V2</h4>", unsafe_allow_html=True)

st.divider()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1️⃣ لوحة التحكم (Control Panel)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
    <div class='control-panel'>
        <h3 style='color: #00ccff;'>⚙️ لوحة التحكم - معايير السياق الديناميكية</h3>
    </div>
""", unsafe_allow_html=True)

col_before, col_after = st.columns(2)

with col_before:
    verses_before = st.number_input(
        "📍 عدد الآيات قبل الآية المستهدفة:",
        min_value=1,
        max_value=20,
        value=2,
        step=1,
        key="verses_before"
    )

with col_after:
    verses_after = st.number_input(
        "📍 عدد الآيات بعد الآية المستهدفة:",
        min_value=1,
        max_value=20,
        value=2,
        step=1,
        key="verses_after"
    )

st.markdown(f"""
    <div class='stat-box'>
        📊 <strong>إجمالي الآيات في السياق:</strong> {verses_before + verses_after + 1} آية 
        ({verses_before} قبل + 1 مركزية + {verses_after} بعد)
    </div>
""", unsafe_allow_html=True)

st.divider()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# تحميل البيانات
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
df_quran = load_quran_data()
df_words = load_words_data()

if df_quran is None:
    st.error("❌ لم يتم العثور على ملف بيانات القرآن")
    st.stop()

surah_col, verse_col, text_col = identify_quran_columns(df_quran)

if not all([surah_col, verse_col, text_col]):
    st.error("❌ لم نتمكن من تحديد أعمدة بيانات القرآن")
    st.stop()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2️⃣ البحث عن الألفاظ (Left Column)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("<h3 style='color: #00ccff;'>🔤 البحث عن اللفظ/الكلمة</h3>", unsafe_allow_html=True)

col_search, col_btn = st.columns([4, 1])

with col_search:
    words_query = st.text_input(
        "ابحث عن لفظ أو كلمة:",
        value=st.session_state.words_query,
        placeholder="مثال: الحمد, كتاب, ملك",
        key="words_input"
    )
    st.session_state.words_query = words_query

with col_btn:
    search_words_btn = st.button("🔍 بحث", key="btn_search_words")

# نتائج البحث عن الألفاظ
if search_words_btn and words_query:
    if df_words is None:
        st.warning("⚠️ بيانات الألفاظ غير متوفرة")
    else:
        word_col_w, count_col_w, surah_col_w, verse_col_w, text_col_w = identify_words_columns(df_words)
        
        if word_col_w is None:
            st.error("❌ لم نتمكن من تحديد أعمدة ملف الألفاظ")
        else:
            results_words = search_words(df_words, word_col_w, words_query)
            
            if results_words.empty:
                st.warning(f"❌ لم يتم العثور على اللفظ: '{words_query}'")
            else:
                st.markdown(f"""
                    <div class='stat-box'>
                        📊 <strong>البحث عن:</strong> {words_query} | 
                        <strong>المواضع:</strong> {len(results_words)}
                    </div>
                """, unsafe_allow_html=True)
                
                # ━━━ المستوى الأول: جدول النتائج ━━━
                st.markdown("<h4 style='color: #ff3366;'>📊 جدول النتائج الشامل</h4>", unsafe_allow_html=True)
                
                # تحضير البيانات للجدول
                table_data = []
                for idx, (_, row) in enumerate(results_words.iterrows(), 1):
                    table_data.append({
                        'الرقم': idx,
                        'الآية': row[text_col_w] if text_col_w else "نص غير متوفر",
                        'السورة': row[surah_col_w] if surah_col_w else "؟",
                        'رقم': int(row[verse_col_w]) if verse_col_w else "؟",
                        'الفهرس': idx - 1  # للاستخدام الداخلي
                    })
                
                df_table = pd.DataFrame(table_data)
                
                # عرض الجدول
                st.markdown('<div class="table-container">', unsafe_allow_html=True)
                
                # اختيار الصف
                selected_idx = st.selectbox(
                    "اختر صفاً من الجدول:",
                    range(len(table_data)),
                    format_func=lambda x: f"#{x+1} - {table_data[x]['السورة']}:{table_data[x]['رقم']}",
                    key="select_word_row"
                )
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # ━━━ المستوى الثاني: معاينة الآية ━━━
                if selected_idx is not None:
                    selected_row = table_data[selected_idx]
                    st.session_state.selected_words = {
                        'surah': selected_row['السورة'],
                        'verse': selected_row['رقم'],
                        'text': selected_row['الآية'],
                        'idx': selected_row['الفهرس']
                    }
                    
                    st.markdown('<div class="preview-container">', unsafe_allow_html=True)
                    st.markdown(f"<h4 style='color: #ff3366;'>📄 معاينة الآية</h4>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>السورة:</strong> {selected_row['السورة']} | <strong>الآية:</strong> {selected_row['رقم']}</p>", unsafe_allow_html=True)
                    
                    st.code(selected_row['الآية'], language=None)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # ━━━ المستوى الثالث: أزرار التحويل ━━━
                    st.markdown("<h4 style='color: #00ccff;'>⚡ الخيارات السريعة</h4>", unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("🔄 تحويل لبحث السياق", key="btn_to_context_words"):
                            st.session_state.context_query = selected_row['الآية']
                            st.info(f"✅ تم نقل الآية إلى بحث السياق! سيتم البحث برقم السياق: {verses_before} قبل و {verses_after} بعد")
                    
                    with col2:
                        if st.button("🔍 تتبع لفظ من الآية", key="btn_track_word"):
                            st.session_state.show_word_selector = True
                    
                    # عرض أداة اختيار اللفظ
                    if st.session_state.get('show_word_selector', False):
                        st.markdown("<h4 style='color: #00ccff;'>اختر كلمة لتتبعها</h4>", unsafe_allow_html=True)
                        
                        # تقسيم الآية إلى كلمات
                        words_list = selected_row['الآية'].split()
                        
                        selected_word = st.selectbox(
                            "اختر كلمة:",
                            words_list,
                            key="select_word_from_verse"
                        )
                        
                        if st.button("✅ ابدأ البحث عن هذه الكلمة", key="btn_search_selected_word"):
                            st.session_state.words_query = selected_word
                            st.session_state.show_word_selector = False
                            st.rerun()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3️⃣ البحث بالسياق (Right Column)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.divider()
st.markdown("<h3 style='color: #00ccff;'>📍 البحث عن الآية بالسياق</h3>", unsafe_allow_html=True)

col_search_c, col_btn_c = st.columns([4, 1])

with col_search_c:
    context_query = st.text_input(
        "ابحث عن آية أو كلمة أو جملة:",
        value=st.session_state.context_query,
        placeholder="مثال: الحمد لله, اني جاعل في الارض",
        key="context_input"
    )
    st.session_state.context_query = context_query

with col_btn_c:
    search_context_btn = st.button("🔍 بحث", key="btn_search_context")

# نتائج البحث بالسياق
if search_context_btn and context_query:
    results_context = search_context(
        df_quran, 
        surah_col, 
        verse_col, 
        text_col, 
        context_query,
        verses_before,
        verses_after
    )
    
    if not results_context:
        st.warning(f"❌ لم يتم العثور على نتائج لـ: '{context_query}'")
    else:
        st.markdown(f"""
            <div class='stat-box'>
                📊 <strong>البحث عن:</strong> {context_query} | 
                <strong>النتائج:</strong> {len(results_context)}
            </div>
        """, unsafe_allow_html=True)
        
        # ━━━ المستوى الأول: جدول النتائج ━━━
        st.markdown("<h4 style='color: #ff3366;'>📊 جدول النتائج الشامل</h4>", unsafe_allow_html=True)
        
        # تحضير البيانات للجدول
        table_data_context = []
        for idx, result in enumerate(results_context, 1):
            table_data_context.append({
                'الرقم': idx,
                'الآية': result['text'],
                'السورة': result['surah'],
                'رقم': result['verse'],
                'الفهرس': idx - 1
            })
        
        df_table_context = pd.DataFrame(table_data_context)
        
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        
        # اختيار الصف
        selected_context_idx = st.selectbox(
            "اختر صفاً من الجدول:",
            range(len(table_data_context)),
            format_func=lambda x: f"#{x+1} - {table_data_context[x]['السورة']}:{table_data_context[x]['رقم']}",
            key="select_context_row"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ━━━ المستوى الثاني: معاينة الآية + السياق ━━━
        if selected_context_idx is not None:
            selected_result = results_context[selected_context_idx]
            
            st.markdown('<div class="preview-container">', unsafe_allow_html=True)
            st.markdown(f"<h4 style='color: #ff3366;'>📄 معاينة الآية</h4>", unsafe_allow_html=True)
            st.markdown(f"<p><strong>السورة:</strong> {selected_result['surah']} | <strong>الآية:</strong> {selected_result['verse']}</p>", unsafe_allow_html=True)
            
            st.code(selected_result['text'], language=None)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # ━━━ عرض السياق الموسع ━━━
            st.markdown(f"<h4 style='color: #00ccff;'>📖 السياق الموسع ({verses_before} قبل + 1 مركزية + {verses_after} بعد)</h4>", unsafe_allow_html=True)
            
            for ctx_verse in selected_result['context_verses']:
                if ctx_verse['is_center']:
                    st.markdown(f"""
                        <div class='context-verses context-center'>
                            <strong>⭐ [{ctx_verse['verse']}]</strong> ﴿{ctx_verse['text']}﴾
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class='context-verses'>
                            <strong>[{ctx_verse['verse']}]</strong> ﴿{ctx_verse['text']}﴾
                        </div>
                    """, unsafe_allow_html=True)
            
            # ━━━ المستوى الثالث: أزرار التحويل ━━━
            st.markdown("<h4 style='color: #00ccff;'>⚡ الخيارات السريعة</h4>", unsafe_allow_html=True)
            
            if st.button("🔍 تتبع لفظ من الآية", key="btn_track_word_context"):
                st.session_state.show_word_selector_context = True
            
            # عرض أداة اختيار اللفظ للسياق
            if st.session_state.get('show_word_selector_context', False):
                st.markdown("<h4 style='color: #00ccff;'>اختر كلمة لتتبعها</h4>", unsafe_allow_html=True)
                
                # تقسيم الآية إلى كلمات
                words_list_context = selected_result['text'].split()
                
                selected_word_context = st.selectbox(
                    "اختر كلمة:",
                    words_list_context,
                    key="select_word_from_verse_context"
                )
                
                if st.button("✅ ابدأ البحث عن هذه الكلمة", key="btn_search_selected_word_context"):
                    st.session_state.words_query = selected_word_context
                    st.session_state.show_word_selector_context = False
                    st.rerun()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📋 الشريط الجانبي
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with st.sidebar:
    st.markdown("<h2 style='color: #00ccff;'>ℹ️ معلومات</h2>", unsafe_allow_html=True)
    st.divider()
    
    with st.expander("📖 شرح الاستخدام"):
        st.write("""
        **البحث عن اللفظ:**
        - أدخل كلمة أو لفظ
        - اضغط بحث
        - اختر صفاً من الجدول
        - انسخ الآية أو تحويل للسياق
        
        **البحث بالسياق:**
        - أدخل جملة أو كلمة من الآية
        - اضغط بحث
        - اختر الآية من الجدول
        - شاهد الآية مع سياقها الموسع
        """)
    
    with st.expander("⚙️ المعايير المستخدمة"):
        st.write(f"""
        - **آيات قبل:** {verses_before}
        - **آيات بعد:** {verses_after}
        - **الإجمالي:** {verses_before + verses_after + 1}
        """)
    
    with st.expander("📊 إحصائيات البيانات"):
        st.write(f"**عدد الآيات:** {len(df_quran)}")
        if df_words is not None:
            st.write(f"**عدد الألفاظ:** {len(df_words)}")

st.divider()
st.markdown("<p style='text-align: center; color: #00ccff; font-size: 12px;'>© 2024 - مجلس البينة | V2.0</p>", unsafe_allow_html=True)
