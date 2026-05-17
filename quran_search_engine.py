"""
🌟 محرك البحث القرآني المتقدم
البحث عن الآيات بالسياق والألفاظ
"""

import pandas as pd
import re
from pathlib import Path
from typing import List, Tuple, Dict
import os

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1️⃣ دالة التنميط (Normalization)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def normalize_arabic(text):
    """توحيد النصوص العربية للبحث الدقيق"""
    if not isinstance(text, str):
        return ""
    
    # إزالة التشكيل (الفتحات والضمات والسكون)
    text = re.sub(r"[\u064B-\u0652]", "", text)
    
    # توحيد الألفات
    text = re.sub(r"[إأآٱا]", "ا", text)
    
    # توحيد الياء والألف المقصورة
    text = re.sub(r"[ىي]", "ي", text)
    
    # توحيد التاء والهاء
    text = re.sub(r"[ةه]", "ه", text)
    
    return text.strip()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2️⃣ تحميل البيانات
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class QuranDataLoader:
    """تحميل بيانات القرآن والألفاظ"""
    
    def __init__(self):
        self.df_quran = None
        self.df_words = None
        self.load_data()
    
    def load_data(self):
        """تحميل الملفات"""
        quran_paths = [
            "data/data_quran.xlsx",
            "data_quran.xlsx",
            "./data/data_quran.xlsx",
        ]
        
        words_paths = [
            "data/data_words.xlsx",
            "data_words.xlsx",
            "./data/data_words.xlsx",
        ]
        
        # تحميل بيانات القرآن
        for path in quran_paths:
            if os.path.exists(path):
                self.df_quran = pd.read_excel(path)
                print(f"✅ تم تحميل بيانات القرآن من: {path}")
                print(f"   الأعمدة المتوفرة: {list(self.df_quran.columns)}\n")
                break
        
        # تحميل بيانات الألفاظ
        for path in words_paths:
            if os.path.exists(path):
                self.df_words = pd.read_excel(path)
                print(f"✅ تم تحميل بيانات الألفاظ من: {path}")
                print(f"   الأعمدة المتوفرة: {list(self.df_words.columns)}\n")
                break
        
        if self.df_quran is None:
            print("⚠️ لم يتم العثور على ملف بيانات القرآن")
        if self.df_words is None:
            print("⚠️ لم يتم العثور على ملف بيانات الألفاظ")
    
    def get_quran_df(self):
        return self.df_quran
    
    def get_words_df(self):
        return self.df_words

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3️⃣ محرك البحث عن السياق
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class ContextSearchEngine:
    """البحث عن الآيات بالسياق"""
    
    def __init__(self, df_quran):
        self.df = df_quran
        if self.df is None:
            raise ValueError("لا توجد بيانات القرآن")
        
        # تحديد أسماء الأعمدة
        self._identify_columns()
    
    def _identify_columns(self):
        """تحديد أسماء الأعمدة تلقائياً"""
        cols = self.df.columns
        
        # البحث عن عمود السورة
        self.surah_col = None
        for col in ['السورة', 'surah', 'Surah', 'سورة']:
            if col in cols:
                self.surah_col = col
                break
        
        # البحث عن عمود رقم الآية
        self.verse_col = None
        for col in ['رقم الآية', 'verse_number', 'Verse', 'آية', 'v رقم الآية']:
            if col in cols:
                self.verse_col = col
                break
        
        # البحث عن عمود نص الآية
        self.text_col = None
        for col in ['نص الآية', 'text', 'Text', 'الآية']:
            if col in cols:
                self.text_col = col
                break
        
        if not all([self.surah_col, self.verse_col, self.text_col]):
            raise ValueError(
                f"❌ لم نتمكن من تحديد جميع الأعمدة المطلوبة\n"
                f"الأعمدة المتوفرة: {list(cols)}"
            )
    
    def search_context(self, query: str) -> List[Dict]:
        """البحث عن آية بالسياق"""
        
        query_normalized = normalize_arabic(query)
        if not query_normalized:
            return []
        
        results = []
        
        # البحث عن الآيات التي تطابق البحث
        for idx, row in self.df.iterrows():
            text = str(row[self.text_col])
            text_normalized = normalize_arabic(text)
            
            if query_normalized in text_normalized:
                surah = row[self.surah_col]
                verse_num = int(row[self.verse_col])
                
                # الحصول على السياق (6 قبل و 6 بعد)
                context_verses = self._get_context_verses(surah, verse_num)
                
                results.append({
                    'surah': surah,
                    'verse': verse_num,
                    'text': text,
                    'context': context_verses
                })
        
        return results
    
    def _get_context_verses(self, surah: str, verse_num: int) -> List[Dict]:
        """الحصول على 6 آيات قبل و 6 بعد"""
        
        start = max(1, verse_num - 6)
        end = verse_num + 6
        
        # تصفية الآيات من نفس السورة
        mask = (
            (self.df[self.surah_col] == surah) &
            (self.df[self.verse_col].astype(int).between(start, end))
        )
        
        verses = self.df[mask].sort_values(self.verse_col)
        
        context = []
        for _, row in verses.iterrows():
            v_num = int(row[self.verse_col])
            is_center = (v_num == verse_num)
            
            context.append({
                'verse_num': v_num,
                'text': row[self.text_col],
                'is_center': is_center
            })
        
        return context

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4️⃣ محرك البحث عن الألفاظ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class WordSearchEngine:
    """البحث عن الألفاظ والكلمات"""
    
    def __init__(self, df_words, df_quran):
        self.df_words = df_words
        self.df_quran = df_quran
        
        if self.df_words is None:
            raise ValueError("لا توجد بيانات الألفاظ")
        if self.df_quran is None:
            raise ValueError("لا توجد بيانات القرآن")
        
        # تحديد أسماء الأعمدة
        self._identify_columns()
    
    def _identify_columns(self):
        """تحديد أسماء الأعمدة تلقائياً"""
        
        # أعمدة ملف الألفاظ
        cols_words = self.df_words.columns
        
        self.word_col = None
        for col in ['اللفظ', 'word', 'Word', 'الكلمة']:
            if col in cols_words:
                self.word_col = col
                break
        
        self.count_col = None
        for col in ['عدد الورود', 'count', 'Count', 'العدد']:
            if col in cols_words:
                self.count_col = col
                break
        
        self.surah_col_words = None
        for col in ['السورة', 'surah', 'Surah']:
            if col in cols_words:
                self.surah_col_words = col
                break
        
        self.verse_col_words = None
        for col in ['رقم الآية', 'verse_number', 'Verse', 'آية', 'r رقم الآية']:
            if col in cols_words:
                self.verse_col_words = col
                break
        
        self.text_col_words = None
        for col in ['نص الآية الكاملة', 'نص الآية', 'text', 'Text']:
            if col in cols_words:
                self.text_col_words = col
                break
        
        # أعمدة ملف القرآن
        cols_quran = self.df_quran.columns
        
        self.surah_col_quran = None
        for col in ['السورة', 'surah', 'Surah']:
            if col in cols_quran:
                self.surah_col_quran = col
                break
        
        self.verse_col_quran = None
        for col in ['رقم الآية', 'verse_number', 'Verse', 'آية', 'v رقم الآية']:
            if col in cols_quran:
                self.verse_col_quran = col
                break
        
        self.text_col_quran = None
        for col in ['نص الآية', 'text', 'Text', 'الآية']:
            if col in cols_quran:
                self.text_col_quran = col
                break
    
    def search_word(self, query: str) -> Dict:
        """البحث عن لفظ في جميع المواضع"""
        
        query_normalized = normalize_arabic(query)
        if not query_normalized:
            return {'success': False, 'message': 'الكلمة فارغة'}
        
        # البحث في ملف الألفاظ
        mask = self.df_words[self.word_col].apply(
            lambda x: query_normalized in normalize_arabic(str(x))
        )
        
        results = self.df_words[mask]
        
        if results.empty:
            return {
                'success': False,
                'message': f'لم يتم العثور على اللفظ: "{query}"'
            }
        
        # تجميع النتائج
        occurrences = []
        total_count = 0
        
        for _, row in results.iterrows():
            count = int(row[self.count_col]) if self.count_col else 1
            total_count += count
            
            surah = row[self.surah_col_words] if self.surah_col_words else "؟"
            verse = row[self.verse_col_words] if self.verse_col_words else "؟"
            text = row[self.text_col_words] if self.text_col_words else "نص غير متوفر"
            
            occurrences.append({
                'surah': surah,
                'verse': verse,
                'text': text,
                'count': count
            })
        
        return {
            'success': True,
            'query': query,
            'total_count': total_count,
            'occurrences': occurrences
        }
    
    def get_context_for_verse(self, surah: str, verse_num: int) -> List[Dict]:
        """الحصول على السياق لآية معينة"""
        
        if self.df_quran is None:
            return []
        
        start = max(1, verse_num - 6)
        end = verse_num + 6
        
        mask = (
            (self.df_quran[self.surah_col_quran] == surah) &
            (self.df_quran[self.verse_col_quran].astype(int).between(start, end))
        )
        
        verses = self.df_quran[mask].sort_values(self.verse_col_quran)
        
        context = []
        for _, row in verses.iterrows():
            v_num = int(row[self.verse_col_quran])
            is_center = (v_num == verse_num)
            
            context.append({
                'verse_num': v_num,
                'text': row[self.text_col_quran],
                'is_center': is_center
            })
        
        return context

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5️⃣ دوال العرض
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def print_context_results(results: List[Dict]):
    """طباعة نتائج البحث بالسياق"""
    
    if not results:
        print("❌ لم يتم العثور على نتائج\n")
        return
    
    print(f"\n{'='*80}")
    print(f"📖 نتائج البحث - عدد الآيات المطابقة: {len(results)}")
    print(f"{'='*80}\n")
    
    for idx, result in enumerate(results, 1):
        print(f"\n{'━'*80}")
        print(f"📌 النتيجة #{idx}")
        print(f"السورة: {result['surah']} | الآية: {result['verse']}")
        print(f"{'━'*80}\n")
        
        print("📍 السياق (6 آيات قبل + الآية + 6 آيات بعد):\n")
        
        for ctx_verse in result['context']:
            marker = "⭐ " if ctx_verse['is_center'] else "  "
            print(f"{marker}[{ctx_verse['verse_num']}] ﴿{ctx_verse['text']}﴾\n")
        
        print(f"\n{'─'*80}\n")

def print_word_results(results: Dict, word_search_engine: WordSearchEngine):
    """طباعة نتائج البحث عن الألفاظ"""
    
    if not results['success']:
        print(f"\n❌ {results['message']}\n")
        return
    
    print(f"\n{'='*80}")
    print(f"📊 البحث عن: {results['query']}")
    print(f"🔢 المواضع: {results['total_count']}")
    print(f"{'='*80}\n")
    
    for idx, occurrence in enumerate(results['occurrences'], 1):
        print(f"{idx}. {occurrence['surah']} : {occurrence['verse']}")
        print(f"   ﴿{occurrence['text']}﴾\n")
    
    print(f"{'─'*80}\n")
    
    # خيار عرض السياق
    while True:
        print("\n💡 اختر آية لعرض سياقها (أدخل الرقم) أو اضغط 'خروج' للخروج:")
        choice = input(">>> ").strip()
        
        if choice.lower() in ['خروج', 'exit', 'q']:
            break
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(results['occurrences']):
                occurrence = results['occurrences'][idx]
                print(f"\n{'='*80}")
                print(f"📖 السياق - {occurrence['surah']} : {occurrence['verse']}")
                print(f"{'='*80}\n")
                
                context = word_search_engine.get_context_for_verse(
                    occurrence['surah'],
                    occurrence['verse']
                )
                
                for ctx_verse in context:
                    marker = "⭐ " if ctx_verse['is_center'] else "  "
                    print(f"{marker}[{ctx_verse['verse_num']}] ﴿{ctx_verse['text']}﴾\n")
                
                print(f"\n{'─'*80}\n")
            else:
                print("❌ رقم غير صحيح\n")
        except ValueError:
            print("❌ الرجاء إدخال رقم صحيح\n")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6️⃣ البرنامج الرئيسي
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main():
    """البرنامج الرئيسي"""
    
    print("\n" + "="*80)
    print("🌟 مرحباً بك في محرك البحث القرآني المتقدم 🌟")
    print("="*80 + "\n")
    
    # تحميل البيانات
    print("📂 جاري تحميل البيانات...\n")
    loader = QuranDataLoader()
    
    df_quran = loader.get_quran_df()
    df_words = loader.get_words_df()
    
    if df_quran is None:
        print("❌ فشل تحميل بيانات القرآن")
        return
    
    # إنشاء محركات البحث
    context_engine = ContextSearchEngine(df_quran)
    
    if df_words is not None:
        word_engine = WordSearchEngine(df_words, df_quran)
    else:
        word_engine = None
    
    print("\n✅ تم تحميل البيانات بنجاح!\n")
    
    # القائمة الرئيسية
    while True:
        print("\n" + "="*80)
        print("🔍 اختر نوع البحث:")
        print("="*80)
        print("1️⃣  - البحث عن آية بالسياق")
        print("2️⃣  - البحث عن لفظ/كلمة")
        print("3️⃣  - الخروج")
        print("="*80 + "\n")
        
        choice = input("اختيارك (1 أو 2 أو 3): ").strip()
        
        if choice == "1":
            print("\n📖 البحث عن آية بالسياق")
            print("(أدخل كلمة أو جملة من الآية)\n")
            query = input("ابحث عن: ").strip()
            
            if query:
                results = context_engine.search_context(query)
                print_context_results(results)
        
        elif choice == "2":
            if word_engine is None:
                print("\n❌ بيانات الألفاظ غير متوفرة\n")
                continue
            
            print("\n🔤 البحث عن لفظ/كلمة")
            print("(أدخل الكلمة أو اللفظ)\n")
            query = input("ابحث عن: ").strip()
            
            if query:
                results = word_engine.search_word(query)
                print_word_results(results, word_engine)
        
        elif choice == "3":
            print("\n👋 شكراً لاستخدامك محرك البحث القرآني!")
            break
        
        else:
            print("\n❌ اختيار غير صحيح\n")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == "__main__":
    main()
