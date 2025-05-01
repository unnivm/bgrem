import streamlit as st
from PIL import Image, UnidentifiedImageError
from rembg import remove
import io



# Page configuration
st.set_page_config(page_title="Background Remover & Editor", layout="centered")

st.title("🖼️ Background Remover + Editor")
st.markdown("Upload a `.png` image, remove the background, resize it, set background color, and download it in your preferred format!")

# Example images section
col1, col2 = st.columns(2)

with col1:
    st.image("sample_images/original.png", caption="🎯 Original Image", use_container_width=True)

with col2:
    st.image("sample_images/processed.png", caption="✅ Background Removed", use_container_width=True)


# File uploader
uploaded_file = st.file_uploader("Choose a PNG file", type=["png"])

# Output format
output_format = st.selectbox("Select output format", ["PNG", "JPG", "WEBP"])

# Resize options
st.markdown("### Resize Output Image (optional)")
resize_enabled = st.checkbox("Resize image?")
if resize_enabled:
    new_width = st.number_input("Width (px)", min_value=1, value=300)
    new_height = st.number_input("Height (px)", min_value=1, value=300)

# Background color
st.markdown("### Background Color (optional)")
apply_background_color = st.checkbox("Apply a solid background color to processed image?")
bg_color = st.color_picker("Pick a background color", "#ffffff")

if uploaded_file:
    try:
        uploaded_file.seek(0)
        original_image = Image.open(uploaded_file).convert("RGBA")

        # Show original
        st.subheader("Original Image Preview")
        st.image(original_image, width=300)

        if st.button("✨ Remove Background"):
            with st.spinner("Processing..."):
                uploaded_file.seek(0)
                input_bytes = uploaded_file.read()
                output_bytes = remove(input_bytes)
                processed_image = Image.open(io.BytesIO(output_bytes)).convert("RGBA")

                # Resize
                if resize_enabled:
                    processed_image = processed_image.resize((new_width, new_height))

                # Apply background color if chosen
                if apply_background_color:
                    background = Image.new("RGBA", processed_image.size, bg_color)
                    background.paste(processed_image, mask=processed_image.split()[3])  # use alpha as mask
                    processed_image = background.convert("RGB")
                elif output_format == "JPG":
                    # JPG doesn't support transparency, convert with white background
                    background = Image.new("RGB", processed_image.size, (255, 255, 255))
                    background.paste(processed_image, mask=processed_image.split()[3])
                    processed_image = background

                # Show comparison
                st.subheader("Comparison")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Original Image**")
                    st.image(original_image, width=300)
                with col2:
                    st.markdown("**Processed Image**")
                    st.image(processed_image, width=300)

                # Prepare download
                download_buffer = io.BytesIO()
                file_ext = output_format.lower()

                processed_image.save(download_buffer, format=output_format)
                download_buffer.seek(0)

                st.download_button(
                    label=f"⬇️ Download as {output_format}",
                    data=download_buffer,
                    file_name=f"processed_image.{file_ext}",
                    mime=f"image/{'jpeg' if file_ext == 'jpg' else file_ext}",
                )

    except UnidentifiedImageError:
        st.error("❌ Could not identify the image file. Please upload a valid PNG.")
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
