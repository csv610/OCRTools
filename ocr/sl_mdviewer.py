import streamlit as st
import os
import re
import base64
import zipfile
import io

def main():
    """
    This Streamlit application reads a .zip file containing a markdown file
    and images, then renders the markdown with embedded images.
    """
    st.set_page_config(page_title="Markdown File Renderer", layout="wide")

    st.title("Streamlit Markdown Renderer")
    st.write("Please upload a `.zip` file containing your `.md` file and any related images.")

    # Use a single file uploader for the .zip archive
    uploaded_zip = st.file_uploader("Choose a .zip file", type=["zip"])
    
    if uploaded_zip is not None:
        try:
            # Read the uploaded .zip file
            with zipfile.ZipFile(io.BytesIO(uploaded_zip.getvalue()), 'r') as zip_ref:
                # Find the markdown file and images inside the archive
                md_content = None
                image_uris = {}

                for filename in zip_ref.namelist():
                    # Check for the markdown file
                    if filename.endswith(".md"):
                        md_content = zip_ref.read(filename).decode("utf-8")
                    
                    # Check for image files
                    elif filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        img_bytes = zip_ref.read(filename)
                        base64_img = base64.b64encode(img_bytes).decode("utf-8")
                        mime_type = f"image/{os.path.splitext(filename)[1][1:]}"
                        data_uri = f"data:{mime_type};base64,{base64_img}"
                        image_uris[os.path.basename(filename)] = data_uri

                if md_content is not None:
                    # Find all image tags in the markdown content using regex
                    markdown_with_embedded_images = md_content
                    image_tags = re.findall(r'!\[(.*?)\]\((.*?)\)', md_content)

                    for alt_text, img_path in image_tags:
                        img_filename = os.path.basename(img_path)
                        
                        if img_filename in image_uris:
                            original_tag = f"![{alt_text}]({img_path})"
                            new_tag = f"![{alt_text}]({image_uris[img_filename]})"
                            markdown_with_embedded_images = markdown_with_embedded_images.replace(original_tag, new_tag)

                    st.markdown(markdown_with_embedded_images, unsafe_allow_html=True)
                    st.success("Markdown and embedded images rendered successfully!")
                else:
                    st.error("No `.md` file found in the uploaded `.zip` archive.")

        except zipfile.BadZipFile:
            st.error("The uploaded file is not a valid `.zip` file.")
        except Exception as e:
            st.error(f"An error occurred while processing the file: {e}")
            
    else:
        st.info("Please upload a `.zip` file containing your markdown file and images.")

if __name__ == "__main__":
    main()

