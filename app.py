import os
import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# পেজের কনফিগারেশন
st.set_page_config(page_title="PDF Question Generator", page_icon="📚", layout="centered")

st.title("📚 PDF ভিত্তিক প্রশ্ন প্রস্তুতকারক বট")
st.caption("PDF ফাইল আপলোড করে এক ক্লিকে ব্যাখ্যাসহ MCQ, অনুধাবন ও সংক্ষিপ্ত প্রশ্ন তৈরি করুন।")

# Render-এর Environment Variable থেকে অথবা ম্যানুয়ালি API Key নেওয়া
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    api_key = st.text_input("AQ.Ab8RN6Lf1hYw7FvX_NWoUW-dg6HbsZQalt6Tuvad-UIVsLiQeg", type="password")

uploaded_file = st.file_uploader("আপনার PDF ফাইলটি আপলোড করুন", type=["pdf"])

def extract_pdf_text(file):
    reader = PdfReader(file)
    extracted_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            extracted_text += text + "\n"
    return extracted_text

if uploaded_file and api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    with st.spinner("PDF ফাইলটি প্রসেস করা হচ্ছে..."):
        text = extract_pdf_text(uploaded_file)
        content = text[:15000]

    st.success("✅ PDF পড়া সম্পন্ন হয়েছে! নিচের অপশনগুলো থেকে বেছে নিন:")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📝 ব্যাখ্যাসহ MCQ"):
            prompt = f"তুমি একজন অভিজ্ঞ শিক্ষক। নিচের তথ্যের ভিত্তিতে গুরুত্বপূর্ণ ৫টি MCQ (বহুনির্বাচনী প্রশ্ন) তৈরি করো। প্রতিটি প্রশ্নের ৪টি অপশন দেবে, সঠিক উত্তর চিহ্নিত করবে এবং কেন উত্তরটি সঠিক তার সহজ বাংলায় বিস্তারিত ব্যাখ্যা দেবে।\n\nতথ্য:\n{content}"
            with st.spinner("MCQ তৈরি হচ্ছে..."):
                res = model.generate_content(prompt)
                st.markdown(res.text)

    with col2:
        if st.button("😍 অনুধাবনমূলক প্রশ্ন"):
            prompt = f"তুমি একজন অভিজ্ঞ শিক্ষক। নিচের তথ্যের ওপর ভিত্তি করে গুরুত্বপূর্ণ ৫টি 'অনুধাবনমূলক প্রশ্ন' এবং তার মানসম্মত আদর্শ উত্তর তৈরি করো।\n\nতথ্য:\n{content}"
            with st.spinner("অনুধাবন প্রশ্ন তৈরি হচ্ছে..."):
                res = model.generate_content(prompt)
                st.markdown(res.text)

    with col3:
        if st.button("📌 সংক্ষিপ্ত প্রশ্ন"):
            prompt = f"তুমি একজন অভিজ্ঞ শিক্ষক। নিচের তথ্যের ওপর ভিত্তি করে গুরুত্বপূর্ণ ৫টি 'সংক্ষিপ্ত প্রশ্ন' এবং টু-দ্য-পয়েন্ট উত্তর তৈরি করো।\n\nতথ্য:\n{content}"
            with st.spinner("সংক্ষিপ্ত প্রশ্ন তৈরি হচ্ছে..."):
                res = model.generate_content(prompt)
                st.markdown(res.text)

    st.divider()
    user_query = st.text_input("💬 PDF থেকে যেকোনো প্রশ্ন থাকলে এখানে লিখুন:")
    if st.button("উত্তর দাও") and user_query:
        with st.spinner("উত্তর ভাবছে..."):
            res = model.generate_content(f"তথ্য: {content}\n\nপ্রশ্ন: {user_query}\nসহজ বাংলায় উত্তর দাও।")
            st.markdown(res.text)
