import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json
import os

# ---------------------------------------------------------
# 1. إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(
    page_title="SANAD AI - Smart Crisis Management",
    page_icon="🚨",
    layout="wide"
)

# أسماء ملفات الحفظ الدائم
STUDENTS_FILE = "students_data.csv"
CONFIG_FILE = "school_config.json"

# ---------------------------------------------------------
# 2. دوال الحفظ والتحميل الدائم
# ---------------------------------------------------------
def load_school_info():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "name": "ملاذ المعرفة الأهلية (Maladh School)",
        "location": "الرياض - حي الياسمين (Building A & B)"
    }

def save_school_info(name, location):
    config = {"name": name, "location": location}
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def load_students_data():
    if os.path.exists(STUDENTS_FILE):
        try:
            df = pd.read_csv(STUDENTS_FILE, dtype={"id": str})
            return df
        except Exception:
            pass
    initial_data = [
        {"id": "STU-101", "name": "أحمد المنصور", "status": "Safe", "lat": 24.7136, "lon": 46.6753, "zone": "مبنى أ - الدور الأول"},
        {"id": "STU-102", "name": "سارة علي", "status": "Safe", "lat": 24.7138, "lon": 46.6755, "zone": "مبنى أ - الدور الثاني"},
        {"id": "STU-103", "name": "فهد خالد", "status": "Needs Assistance", "lat": 24.7132, "lon": 46.6750, "zone": "المكتبة - المبنى ب"},
        {"id": "STU-104", "name": "نورة ناصر", "status": "Unknown", "lat": 24.7135, "lon": 46.6758, "zone": "المقصف المدرسي"},
    ]
    df = pd.DataFrame(initial_data)
    df.to_csv(STUDENTS_FILE, index=False, encoding="utf-8-sig")
    return df

def save_students_data(df):
    df.to_csv(STUDENTS_FILE, index=False, encoding="utf-8-sig")

# ---------------------------------------------------------
# 3. تهيئة البيانات والجلسة
# ---------------------------------------------------------
school_info = load_school_info()
if "school_name" not in st.session_state:
    st.session_state.school_name = school_info["name"]
if "school_location" not in st.session_state:
    st.session_state.school_location = school_info["location"]

if "users_data" not in st.session_state:
    st.session_state.users_data = load_students_data()

# متغيرة حالة الإنذار الجماعي
if "evacuation_alarm" not in st.session_state:
    st.session_state.evacuation_alarm = False

# ---------------------------------------------------------
# 4. الشريط الجانبي
# ---------------------------------------------------------
st.sidebar.image("https://img.icons8.com/color/96/000000/siren.png", width=80)
st.sidebar.title("نظام سند | SANAD AI")
st.sidebar.markdown(f"🏫 **{st.session_state.school_name}**")
st.sidebar.caption(f"📍 {st.session_state.school_location}")
st.sidebar.markdown("---")

user_role = st.sidebar.radio(
    "🔑 اختر نوع المستخدم (Role):", 
    ["📱 واجهة الطالب / الزائر", "🖥️ لوحة تحكم الطوارئ (خاص بالمشرفين)"]
)

# ---------------------------------------------------------
# 📱 5. واجهة الطالب
# ---------------------------------------------------------
if user_role == "📱 واجهة الطالب / الزائر":
    st.title("🚨 تطبيق سند للسلامة والاستجابة اللحظية")
    st.markdown(f"**المبنى:** {st.session_state.school_name} | **الموقع:** {st.session_state.school_location}")
    
    # 🔔 فحص حالة الإنذار الجماعي
    if st.session_state.evacuation_alarm:
        st.error("""
            # 🚨 ⚠️ إنذار إخلاء عاجل وصارم ⚠️ 🚨
            ### تم تفعيل إنذار الطوارئ من غرفة العمليات الآن!
            **يرجى التوجه فوراً وبشكل منتظم نحو أقرب مخرج طوارئ وتجنب استخدام المصاعد.**
        """)
        
        # رابط صوت إنذار طوارئ مباشر وواضح
        sound_url = "https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"
        
        # مشغل الصوت التلقائي وتجاوز قيود المتصفح مع إتاحة مشغل مدمج
        st.audio(sound_url, format="audio/mp3", autoplay=True)
        st.caption("🔊 في حال لم يعمل الصوت تلقائياً بسبب إعدادات المتصفح لديك، اضغط زر التشغيل أعلى لسمع صافرة الإنذار.")

    st.markdown("---")

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📱 تحديث حالة السلامة اللحظية")
        st.info("💡 عند وقوع أزمة، حدد اسمك واضغط الزر المناسب لإبلاغ غرفة العمليات فوراً.")
        
        df_students = st.session_state.users_data
        
        if not df_students.empty:
            student_list = df_students["id"] + " - " + df_students["name"]
            selected_student = st.selectbox("اختر اسمك من القائمة:", student_list)
            selected_id = selected_student.split(" - ")[0]
            
            st.write("### 🟢 حدّث حالتك الآن:")
            btn_safe = st.button("✅ أنا في مكان آمن (I am Safe)", use_container_width=True, type="primary")
            btn_help = st.button("🚨 أحتاج مساعدة عاجلة (Need Immediate Help)", use_container_width=True)
            
            if btn_safe:
                st.session_state.users_data.loc[st.session_state.users_data["id"] == selected_id, "status"] = "Safe"
                save_students_data(st.session_state.users_data)
                st.success("تم تسجيل حالتك كـ (آمن). تم إبلاغ إدارة السلامة المدرسية.")
                
            if btn_help:
                st.session_state.users_data.loc[st.session_state.users_data["id"] == selected_id, "status"] = "Needs Assistance"
                save_students_data(st.session_state.users_data)
                st.error("تم إرسال إشارة استغاثة عاجلة! فريق الدفاع المدني والسلامة المدرسية في طريقهم إليك.")
        else:
            st.warning("لا يوجد طلاب مسجلين حالياً في النظام.")

    with col2:
        st.subheader("🗺️ مسار الإخلاء الموصى به بالذكاء الاصطناعي")
        st.success("🤖 **AI Evacuation Guide:** أقرب مخرج آمن لك حالياً: **المخرج الشرقي (Exit East 2)** - نسبة الازدحام 10%.")
        
        m_student = folium.Map(location=[24.7136, 46.6753], zoom_start=18)
        folium.Marker([24.7136, 46.6753], popup="موقعك الحالي", icon=folium.Icon(color="blue", icon="user")).add_to(m_student)
        folium.Marker([24.7140, 46.6758], popup="مخرج الطوارئ الآمن", icon=folium.Icon(color="green", icon="running")).add_to(m_student)
        folium.PolyLine([[24.7136, 46.6753], [24.7140, 46.6758]], color="green", weight=4, opacity=0.8).add_to(m_student)
        st_folium(m_student, width=500, height=300)

# ---------------------------------------------------------
# 🖥️ 6. لوحة تحكم الطوارئ
# ---------------------------------------------------------
else:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔒 حماية اللوحة")
    password = st.sidebar.text_input("أدخل كلمة مرور المسؤول:", type="password")
    
    if password != "1234":
        st.title("🖥️ غرفة عمليات وإدارة الطوارئ")
        st.warning("🔒 هذه اللوحة محمية وخاصة فقط بإدارة المدرسة وفريق السلامة المصرح لهم. يرجى إدخال رمز المرور عبر الشريط الجانبي للدخول.")
    else:
        st.title("🖥️ غرفة عمليات وإدارة الطوارئ المدرسية")
        st.markdown(f"**المؤسسة:** {st.session_state.school_name} | **الموقع الجغرافي:** {st.session_state.school_location}")
        st.markdown("---")

        # ⚙️ قسم إدارة النظام
        with st.expander("⚙️ إعدادات النظام: إدارة الطلاب وتعديل بيانات المدرسة"):
            col_sch, col_add, col_del = st.columns(3)
            
            with col_sch:
                st.markdown("#### 🏫 تعديل المدرسة")
                new_sch_name = st.text_input("اسم المدرسة / المرفق:", st.session_state.school_name)
                new_sch_loc = st.text_input("الموقع الجغرافي:", st.session_state.school_location)
                if st.button("تحديث البيانات"):
                    st.session_state.school_name = new_sch_name
                    st.session_state.school_location = new_sch_loc
                    save_school_info(new_sch_name, new_sch_loc)
                    st.success("تم تحديث وحفظ بيانات المدرسة دائمًا!")
                    st.rerun()

            with col_add:
                st.markdown("#### ➕ إضافة طالب")
                new_id = st.text_input("رقم الطالب (ID):", f"STU-{len(st.session_state.users_data)+101}")
                new_name = st.text_input("اسم الطالب الثلاثي:")
                new_zone = st.text_input("المنطقة / الفصل:", "الفصل 2/3")
                
                if st.button("إضافة الطالب"):
                    if new_name:
                        new_row = pd.DataFrame([{
                            "id": new_id, 
                            "name": new_name, 
                            "status": "Unknown", 
                            "lat": 24.7136 + (len(st.session_state.users_data) * 0.0001), 
                            "lon": 46.6753 + (len(st.session_state.users_data) * 0.0001), 
                            "zone": new_zone
                        }])
                        st.session_state.users_data = pd.concat([st.session_state.users_data, new_row], ignore_index=True)
                        save_students_data(st.session_state.users_data)
                        st.success(f"تمت إضافة ({new_name}) بنجاح!")
                        st.rerun()
                    else:
                        st.error("أدخل الاسم أولاً.")

            with col_del:
                st.markdown("#### 🗑️ حذف طالب من النظام")
                df_curr = st.session_state.users_data
                if not df_curr.empty:
                    student_options = df_curr["id"] + " - " + df_curr["name"]
                    selected_del = st.selectbox("اختر الطالب المراد حذفه:", student_options, key="del_select")
                    target_id = selected_del.split(" - ")[0]
                    
                    if st.button("❌ تأكيد الحذف النهائي", type="primary", key="del_btn"):
                        st.session_state.users_data = st.session_state.users_data[
                            st.session_state.users_data["id"] != target_id
                        ].copy().reset_index(drop=True)
                        save_students_data(st.session_state.users_data)
                        st.success("تم الحذف بنجاح!")
                        st.rerun()
                else:
                    st.info("لا يوجد طلاب حالياً للحذف.")

        st.markdown("---")

        # حساب الإحصائيات
        df = st.session_state.users_data
        total_users = len(df)
        safe_count = len(df[df["status"] == "Safe"])
        help_count = len(df[df["status"] == "Needs Assistance"])
        unknown_count = len(df[df["status"] == "Unknown"])
        safety_rate = int((safe_count / total_users) * 100) if total_users > 0 else 0
        
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("إجمالي الطلاب المسجلين", total_users)
        kpi2.metric("الآمنين (Safe)", safe_count, f"{safety_rate}%")
        kpi3.metric("طلبات مساعدة (Critical)", help_count, delta_color="inverse")
        kpi4.metric("غير محدد (Unknown)", unknown_count)
        
        st.progress(safety_rate / 100 if total_users > 0 else 0)
        
        col_map, col_table = st.columns([3, 2])
        
        with col_map:
            st.markdown("### 🗺️ الخريطة الحرارية والمواقع اللحظية")
            m_admin = folium.Map(location=[24.7136, 46.6753], zoom_start=18)
            
            for _, row in df.iterrows():
                if row["status"] == "Safe":
                    color = "green"
                    icon_type = "ok-sign"
                elif row["status"] == "Needs Assistance":
                    color = "red"
                    icon_type = "warning-sign"
                else:
                    color = "gray"
                    icon_type = "question-sign"
                    
                folium.Marker(
                    [row["lat"], row["lon"]],
                    popup=f"{row['name']} ({row['zone']}) - Status: {row['status']}",
                    icon=folium.Icon(color=color, icon=icon_type)
                ).add_to(m_admin)
                
            st_folium(m_admin, width=650, height=400)
            
        with col_table:
            st.markdown("### 📋 سجل الحالات والطلاب المباشر")
            st.dataframe(df[["id", "name", "status", "zone"]], use_container_width=True)
            
            st.markdown("---")
            st.markdown("### 📢 إرسال إنذار إخلاء جماعي")
            
            if not st.session_state.evacuation_alarm:
                if st.button("🚨 إطلاق إنذار الإخلاء الفوري", type="primary", use_container_width=True):
                    st.session_state.evacuation_alarm = True
                    st.error("⚠️ تم إطلاق الإنذار العاجل لجميع الطلاب الآن!")
                    st.rerun()
            else:
                st.error("🚨 الإنذار مفعّل حالياً في أجهزة الطلاب!")
                if st.button("✅ إيقاف الإنذار وإنهاء الحالة", type="secondary", use_container_width=True):
                    st.session_state.evacuation_alarm = False
                    st.success("تم إيقاف الإنذار وإعادة الواجهة للحالة الطبيعية.")
                    st.rerun()