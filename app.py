import os
import time
import streamlit as st
from google import genai
from pypdf import PdfReader

# পেজের কনফিগারেশন
st.set_page_config(page_title="PDF Question Generator", page_icon="📚", layout="centered")

st.title("📚 PDF ভিত্তিক প্রশ্ন প্রস্তুতকারক বট")
st.caption("Gemini 2.5 Flash চালিত — লাইভ প্রোগ্রেস ট্র্যাকিং ও ওয়ান-ক্লিক কপি সুবিধা")

MODEL_NAME = "gemini-2.5-flash"

# API Key হ্যান্ডলিং
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    api_key = st.text_input("আপনার Google Gemini API Key দিন:", type="password")

uploaded_file = st.file_uploader("আপনার PDF ফাইলটি আপলোড করুন", type=["pdf"])

# ১. কত % PDF প্রসেস হচ্ছে তা দেখানোর ফাংশন
def extract_pdf_text_with_progress(file):
    reader = PdfReader(file)
    total_pages = len(reader.pages)
    extracted_text = ""
    
    progress_bar = st.progress(0, text="PDF পড়া শুরু হচ্ছে... 0%")
    
    for idx, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            extracted_text += text + "\n"
        
        # শতকরা (%) হিসেব
        percent = int(((idx + 1) / total_pages) * 100)
        progress_bar.progress(percent, text=f"PDF পড়া হচ্ছে: {percent}% ({idx+1}/{total_pages} পাতা সম্পন্ন)")
        time.sleep(0.01) # স্মুথ অ্যানিমেশনের জন্য
        
    progress_bar.progress(100, text="✅ PDF প্রসেসিং সম্পন্ন: 100%")
    return extracted_text

# ২. কত % AI লিখছে তা লাইভ দেখানোর ফাংশন (Streaming)
def stream_ai_response(client, prompt, est_chars=1800):
    progress_bar = st.progress(0, text="AI লেখা শুরু করছে... 0%")
    output_area = st.empty()
    full_text = ""

    try:
        # জেমিনির স্ট্রিমিং রেসপন্স
        response_stream = client.models.generate_content_stream(
            model=MODEL_NAME, 
            contents=prompt
        )

        for chunk in response_stream:
            if chunk.text:
                full_text += chunk.text
                # লেখার পরিমাণের ওপর ভিত্তি করে লাইভ % হিসেব (সর্বোচ্চ ৯৫% পর্যন্ত স্ট্রিমিং চলাকালীন)
                percent = min(int((len(full_text) / est_chars) * 95), 95)
                progress_bar.progress(percent, text=f"AI লিখছে... {percent}%")
                output_area.markdown(full_text)

        # লেখা শেষ হলে ১০০%
        progress_bar.progress(100, text="🎉 AI লেখা সম্পন্ন: 100%")
        return full_text
    except Exception as err:
        progress_bar.empty()
        st.error(f"এরর হয়েছে: {err}")
        return None

# মূল ইন্টারঅ্যাকশন
if uploaded_file and api_key:
    client = genai.Client(api_key=api_key.strip())

    text = extract_pdf_text_with_progress(uploaded_file)
    content = text[:15000]

    st.divider()
    st.subheader("নিচের অপশনগুলো থেকে বেছে নিন:")

    col1, col2, col3 = st.columns(3)

    # ১. ব্যাখ্যাসহ MCQ
    with col1:
        if st.button("📝 ব্যাখ্যাসহ MCQ"):
            prompt = f"তুমি একজন অভিজ্ঞ শিক্ষক। নিচের তথ্যের ভিত্তিতে গুরুত্বপূর্ণ ৫টি MCQ তৈরি করো। প্রতিটির ৪টি অপশন দেবে, সঠিক উত্তর চিহ্নিত করবে এবং কেন উত্তরটি সঠিক তার সহজ বাংলায় বিস্তারিত ব্যাখ্যা দেবে।\n\nতথ্য:\n{content}"
            result = stream_ai_response(client, prompt, est_chars=2000)
            
            # ৩. এক ক্লিকে সম্পূর্ণ MCQ কপি করার বক্স
            if result:
                st.markdown("---")
                st.markdown("#### 📋 এক ক্লিকে সম্পূর্ণ MCQ কপি করতে নিচের বক্সের ডানপাশের আইকনে চাপ দিন:")
                st.code(result, language="markdown")

    # ২. অনুধাবনমূলক প্রশ্ন
    with col2:
        if st.button("😍 অনুধাবনমূলক প্রশ্ন"):
            prompt = f"তুমি একজন অভিজ্ঞ শিক্ষক। নিচের তথ্যের ওপর ভিত্তি করে গুরুত্বপূর্ণ ৫টি 'অনুধাবনমূলক প্রশ্ন' এবং তার মানসম্মত আদর্শ উত্তর তৈরি করো।\n\nতথ্য:\n{content}"
            result = stream_ai_response(client, prompt, est_chars=1600)
            if result:
                st.markdown("---")
                st.markdown("#### 📋 কপি করুন:")
                st.code(result, language="markdown")

    # ৩. সংক্ষিপ্ত প্রশ্ন
    with col3:
        if st.button("📌 সংক্ষিপ্ত প্রশ্ন"):
            prompt = f"তুমি একজন অভিজ্ঞ শিক্ষক। নিচের তথ্যের ওপর ভিত্তি করে গুরুত্বপূর্ণ ৫টি 'সংক্ষিপ্ত প্রশ্ন' এবং টু-দ্য-পয়েন্ট উত্তর তৈরি করো।\n\nতথ্য:\n{content}"
            result = stream_ai_response(client, prompt, est_chars=1200)
            if result:
                st.markdown("---")
                st.markdown("#### 📋 কপি করুন:")
                st.code(result, language="markdown")

    # ফ্রি চ্যাট অপশন
    st.divider()
    user_query = st.text_input("💬 PDF থেকে যেকোনো প্রশ্ন থাকলে এখানে লিখুন:")
    if st.button("উত্তর দাও") and user_query:
        prompt = f"তথ্য: {content}\n\nপ্রশ্ন: {user_query}\nসহজ বাংলায় উত্তর দাও।"
        res = stream_ai_response(client, prompt, est_chars=1000)
        if res:
            st.code(res, language="markdown")
