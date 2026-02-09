import streamlit as st
import os
import re
import base64

def process_markdown(md_content, image_uris):
    """
    Process markdown content and replace image paths with base64 data URIs.
    """
    markdown_with_embedded_images = md_content
    image_tags = re.findall(r'!\[(.*?)\]\((.*?)\)', md_content)

    for alt_text, img_path in image_tags:
        img_filename = os.path.basename(img_path)

        if img_filename in image_uris:
            original_tag = f"![{alt_text}]({img_path})"
            new_tag = f"![{alt_text}]({image_uris[img_filename]})"
            markdown_with_embedded_images = markdown_with_embedded_images.replace(original_tag, new_tag)

    return markdown_with_embedded_images

def get_mime_type(filename):
    """Get MIME type based on file extension."""
    ext = os.path.splitext(filename)[1][1:].lower()
    mime_types = {
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif': 'image/gif',
        'webp': 'image/webp'
    }
    return mime_types.get(ext, 'image/png')

def encode_image_to_uri(img_bytes, filename):
    """Encode image bytes to base64 data URI."""
    base64_img = base64.b64encode(img_bytes).decode("utf-8")
    mime_type = get_mime_type(filename)
    return f"data:{mime_type};base64,{base64_img}"

def main():
    """
    Streamlit application that reads markdown files and images from:
    1. Direct markdown file upload + image file uploads
    2. ZIP archives (backward compatible)
    """
    st.set_page_config(page_title="Markdown File Renderer", layout="wide")

    st.title("Streamlit Markdown Renderer")

    # Tabs for different input methods
    tab1, tab2 = st.tabs(["Direct Files (Markdown + Images)", "Local Directory"])

    with tab1:
        st.write("Upload a markdown file and its related images from different folders.")

        # Markdown file uploader
        uploaded_md = st.file_uploader("Choose a markdown file", type=["md"])

        # Image files uploader (accept multiple files)
        uploaded_images = st.file_uploader(
            "Choose image files (you can select multiple)",
            type=["png", "jpg", "jpeg", "gif", "webp"],
            accept_multiple_files=True
        )

        if uploaded_md is not None:
            try:
                # Read markdown content
                md_content = uploaded_md.read().decode("utf-8")

                # Process uploaded images
                image_uris = {}
                for img_file in uploaded_images:
                    img_bytes = img_file.read()
                    data_uri = encode_image_to_uri(img_bytes, img_file.name)
                    image_uris[img_file.name] = data_uri

                # Process markdown with embedded images
                markdown_with_embedded_images = process_markdown(md_content, image_uris)

                st.markdown(markdown_with_embedded_images, unsafe_allow_html=True)
                st.success("Markdown and embedded images rendered successfully!")

            except Exception as e:
                st.error(f"An error occurred while processing the files: {e}")
        else:
            st.info("Please upload a markdown file to get started.")

    with tab2:
        st.write("Specify a local directory containing your `.md` file and related images.")
        
        dir_path = st.text_input("Enter directory path:", value=os.getcwd())
        
        if dir_path and os.path.isdir(dir_path):
            try:
                files = os.listdir(dir_path)
                md_files = [f for f in files if f.endswith(".md")]
                
                if md_files:
                    selected_md = st.selectbox("Select a markdown file:", md_files)
                    
                    if selected_md:
                        md_full_path = os.path.join(dir_path, selected_md)
                        with open(md_full_path, "r", encoding="utf-8") as f:
                            md_content = f.read()
                        
                        image_uris = {}
                        for filename in files:
                            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                                img_full_path = os.path.join(dir_path, filename)
                                with open(img_full_path, "rb") as f:
                                    img_bytes = f.read()
                                data_uri = encode_image_to_uri(img_bytes, filename)
                                image_uris[filename] = data_uri
                        
                        markdown_with_embedded_images = process_markdown(md_content, image_uris)
                        st.markdown(markdown_with_embedded_images, unsafe_allow_html=True)
                        st.success(f"Rendered: {selected_md}")
                else:
                    st.warning("No `.md` files found in the specified directory.")
            except Exception as e:
                st.error(f"Error reading directory: {e}")
        elif dir_path:
            st.error("Invalid directory path.")

if __name__ == "__main__":
    main()

