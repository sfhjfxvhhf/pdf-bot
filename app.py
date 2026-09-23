import os
import time
import streamlit as st
from google import genai
from pypdf import PdfReader

# পেজের কনফিগারেশন
st.set_page_config(
    page_title="Smart AI Question Maker", 
    page_icon="🎓", 
    layout="centered"
)

# --- কাস্টম সিএসএস অ্যানিমেশন ও ডিজাইন ---
st.markdown("""
<style>
    /* টাইটেল গ্রেডিয়েন্ট অ্যানিমেশন */
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .animated-title {
        background: linear-gradient(270deg, #ff4b4b, #8a2be2, #00d2ff);
        background-size: 600% 600%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 6s ease infinite;
        font-weight: 800;
        text-align: center;
        font-size: 2.3rem;
        margin-bottom: 5px;
    }
    
    /* সাব-টাইটেল */
    .animated-subtitle {
        text-align: center;
        color: #7d8590;
        font-size: 0.95rem;
        margin-bottom: 25px;
    }

    /* বাটন অ্যানিমেশন ও হোভার ইফেক্ট */
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease-in-out;
        border: 1px solid rgba(255, 75, 75, 0.3);
    }
    div.stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0px 8px 20px rgba(255, 75, 75, 0.25);
    }

    /* বক্স কার্ড ডিজাইন */
    .status-card {
        padding: 12px 18px;
        border-radius: 10px;
        background: rgba(0, 210, 255, 0.05);
        border-left: 4px solid #00d2ff;
        margin: 10px 0;
        animation: fadeIn 0.5s ease-in;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(5px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# হেডার সেকশন
st.markdown('<div class="animated-title">🎓 AI প্রশ্ন প্রস্তুতকারক বট</div>', unsafe_allow_html=True)
st.markdown('<div class="animated-subtitle">Gemini 2.5 Flash চালিত — লাইভ অ্যানিমেশন ও ওয়ান-ক্লিক কপি সুবিধা</div>', unsafe_allow_html=True)

MODEL_NAME = "gemini-2.5-flash"

# API Key ম্যানেজমেন্ট
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    api_key = st.text_input("🔑 আপনার Google Gemini API Key দিন:", type="password")

uploaded_file = st.file_uploader("📂 আপনার PDF ফাইলটি আপলোড করুন", type=["pdf"])

# ১. অ্যানিমেটেড প্রোগ্রেস বার সহ PDF পড়ার ফাংশন
def extract_pdf_with_animation(file):
    reader = PdfReader(file)
    total_pages = len(reader.pages)
    extracted_text = ""
    
    prog_placeholder = st.empty()
    bar = prog_placeholder.progress(0, text="📄 PDF পাতা প্রসেস শুরু হচ্ছে... 0%")
    
    for idx, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            extracted_text += text + "\n"
        
        # শতকরা (%) হিসেব
        percent = int(((idx + 1) / total_pages) * 100)
        bar.progress(percent, text=f"📄 PDF প্রসেস হচ্ছে: {percent}% ({idx+1}/{total_pages} পাতা)")
        time.sleep(0.02)  # অ্যানিমেশন সুন্দর দেখাতে সামান্য ডিলে
        
    bar.progress(100, text="✨ PDF সফলভাবে সম্পন্ন: 100%")
    time.sleep(0.5)
    prog_placeholder.empty() # কাজ শেষে প্রোগ্রেস বার হাইড করে দেওয়া
    return extracted_text

# ২. লাইভ % সহ AI লেখার স্ট্রিমিং ও অ্যানিমেশন
def stream_ai_with_percentage(client, prompt, est_chars=1800):
    status_bar = st.progress(0, text="⚡ AI ভাবছে... 0%")
    output_box = st.empty()
    full_text = ""

    try:
        response_stream = client.models.generate_content_stream(
            model=MODEL_NAME, 
            contents=prompt
        )

        for chunk in response_stream:
            if chunk.text:
                full_text += chunk.text
                # লাইভ পার্সেন্টেজ হিসাব
                current_percent = min(int((len(full_text) / est_chars) * 95), 95)
                status_bar.progress(current_percent, text=f"✍️ AI লিখছে: {current_percent}%")
                output_box.markdown(full_text)

        # ১০০% সম্পন্ন
        status_bar.progress(100, text="🎉 লেখা সম্পন্ন: 100%")
        st.toast("✅ সম্পূর্ণ সফলভাবে তৈরি হয়েছে!", icon="🎉")
        st.balloons() # স্ক্রিনে সুন্দর বেলুন ওড়ার অ্যানিমেশন
        time.sleep(1)
        status_bar.empty()
        return full_text
    except Exception as err:
        status_bar.empty()
        st.error(f"❌ সমস্যা হয়েছে: {err}")
        return None

# মূল ইন্টারঅ্যাকশন
if uploaded_file and api_key:
    client = genai.Client(api_key=api_key.strip())

    text = extract_pdf_with_animation(uploaded_file)
    content = text[:15000]

    st.markdown('<div class="status-card">✅ <b>PDF লোড সম্পন্ন!</b> নিচের যেকোনো অপশনে চাপ দিন:</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    # ১. ব্যাখ্যাসহ MCQ
    with col1:
        if st.button("📝 ব্যাখ্যাসহ MCQ"):
            prompt = f"তুমি একজন অভিজ্ঞ শিক্ষক। নিচের তথ্যের ভিত্তিতে গুরুত্বপূর্ণ ৫টি MCQ প্রশ্ন তৈরি করো। প্রতিটি প্রশ্নের ৪টি অপশন দেবে, সঠিক উত্তর স্পষ্ট করবে এবং সহজ বাংলায় বিস্তারিত ব্যাখ্যা দেবে।\n\nতথ্য:\n{content}"
            result = stream_ai_with_percentage(client, prompt, est_chars=2000)
            if result:
                st.markdown("#### 📋 এক ক্লিকে সম্পূর্ণ MCQ কপি করতে নিচের বক্সের ডানপাশের আইকনে চাপ দিন:")
                st.code(result, language="markdown")

    # ২. অনুধাবনমূলক প্রশ্ন
    with col2:
        if st.button("😍 অনুধাবনমূলক প্রশ্ন"):
            prompt = f"তুমি একজন অভিজ্ঞ শিক্ষক। নিচের তথ্যের ওপর ভিত্তি করে গুরুত্বপূর্ণ ৫টি 'অনুধাবনমূলক প্রশ্ন' এবং তার আদর্শ বিশ্লেষণধর্মী উত্তর তৈরি করো।\n\nতথ্য:\n{content}"
            result = stream_ai_with_percentage(client, prompt, est_chars=1600)
            if result:
                st.markdown("#### 📋 সম্পূর্ণ অনুধাবন প্রশ্ন কপি করুন:")
                st.code(result, language="markdown")

    # ৩. সংক্ষিপ্ত প্রশ্ন
    with col3:
        if st.button("📌 সংক্ষিপ্ত প্রশ্ন"):
            prompt = f"তুমি একজন অভিজ্ঞ শিক্ষক। নিচের তথ্যের ওপর ভিত্তি করে গুরুত্বপূর্ণ ৫টি 'সংক্ষিপ্ত প্রশ্ন' এবং টু-দ্য-পয়েন্ট উত্তর তৈরি করো।\n\nতথ্য:\n{content}"
            result = stream_ai_with_percentage(client, prompt, est_chars=1200)
            if result:
                st.markdown("#### 📋 সম্পূর্ণ সংক্ষিপ্ত প্রশ্ন কপি করুন:")
                st.code(result, language="markdown")

    # কাস্টম চ্যাট
    st.divider()
    user_query = st.text_input("💬 PDF থেকে যেকোনো প্রশ্ন এখানে লিখুন:")
    if st.button("উত্তর দিন 🚀") and user_query:
        prompt = f"তথ্য: {content}\n\nপ্রশ্ন: {user_query}\nসহজ বাংলায় মানসম্মত উত্তর দাও।"
        res = stream_ai_with_percentage(client, prompt, est_chars=1000)
        if res:
            st.code(res, language="markdown")
