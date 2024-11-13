import streamlit as st
import requests
import os
import tempfile
import fitz  # PyMuPDF

def extract_text_from_pdf(uploaded_file):
    # Ensure the save directory exists
    os.makedirs("pdf_files", exist_ok=True)

    # Generate a unique file name for the uploaded PDF (you can modify this if you need a specific naming pattern)
    temp_file_path = os.path.join("pdf_files", "uploaded_pdf.pdf")

    try:
        # Save the uploaded file in the specified directory
        with open(temp_file_path, "wb") as file:
            file.write(uploaded_file.getvalue())

        # Open the PDF with PyMuPDF
        doc = fitz.open(temp_file_path)

        # Extract text from each page
        extracted_text = ""
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)  # Get the page
            extracted_text += page.get_text()  # Extract text from the page

        return extracted_text
    except Exception as e:
        print("Exception Found: ", e)
    finally:
        # Make sure to close the PDF file and then remove it
        if 'doc' in locals():
            doc.close()  # Explicitly close the document to release the file
        # Clean up the saved file after processing
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

 
# Function to get API response (code2)
def get_api_response(content, summ_prompt):
    url = "http://10.75.26.253:11434/api/generate"
    context = []

    # summ_prompt = "You are a global trade expert. Summarize the content by extracting the main insights and takeaways. Emphasize core topics, new information, and any actionable points. Include the primary objectives and the overall conclusion in layman terms."
 
    payload = {
        "model": "llama3",
        "prompt": f"{summ_prompt} {content}",
        "stream": False,
        "context": context
    }
   
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
   
    if response.status_code == 200:
        response_data = response.json().get('response', '')
        return response_data
    else:
        return "Request failed with status code: " + str(response.status_code)
 
# Streamlit UI
def main():
    st.title("PDF Summarization App")
 
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
 
    if uploaded_file is not None:
        # st.write("Processing your file...")
 
        # Step 1: Extract text from the uploaded PDF
        with st.spinner("📂 Uploading the file..."):
            extracted_text = extract_text_from_pdf(uploaded_file)
       
        # Check if text extraction was successful
        if not extracted_text.strip():
            st.write("No extractable text found in the PDF.")
            return
    
        st.write("Please choose the relevant answers from the below dropdowns.")
        
        # dropdown_inputLanguage = ["French", "Spanish", "English", "Unknown"]
        # dropdown_contentType = ["Import/Export Controls", "Landed Cost", "ECCN", "Unknown"]
        # dropdown_outputLanguage = ["Native Language", "English"]

        # inputLanguage = st.selectbox("Langauge:", dropdown_inputLanguage)
        # contentType = st.selectbox("Content Type:", dropdown_contentType)
        # outputLanguage= st.selectbox("Output Required in:", dropdown_outputLanguage)

        if st.button("Summarize"):

            summ_prompt = f"Summarize the given regulation. Also, provide your output in bullet points and ensure your output is based on the content of this document."
            # summ_prompt = f"Summarize the content by extracting the main insights and takeaways. Emphasize core topics, new information, and any actionable points. Include the primary objectives and the overall conclusion. Restrict your knowledge to the given content only. Do not write anything other than the summary."
            # summ_prompt = f"You are a global trade expert in {contentType} and you are experienced in {inputLanguage}. Summarize the content by extracting the main insights and takeaways. Emphasize core topics, new information, and any actionable points. Include the primary objectives and the overall conclusion. Provide the summary in {inputLanguage}. Restrict your knowledge to the given content only."

            st.write(summ_prompt)
        
            # Step 2: Pass the extracted text to the API for summarization
            with st.spinner("📝 Summarizing... Please wait."):
                response = get_api_response(extracted_text, summ_prompt)
        
            # Display the response in the UI
            st.subheader("AI Summarization:")
            st.markdown("""
                ---
                **⚠️ Important Note:**  
                AI-generated content can sometimes contain errors or inaccuracies. **Always manually verify any critical information** before acting on it.
                """)
            st.write(response)



if __name__ == "__main__":
    main()
 