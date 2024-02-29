import streamlit as st
import os
from PIL import Image
import torch

from src.networks.image_transformer_net import ImageTransformNet
from src.models.style_transfer import style_transfer


def display_styles(styles_path='static/styles'):

    # Create a dictionnary with the different styles names and the paths to the corresponding images
    styles = {}
    for style in os.listdir(styles_path):
        styles[style.split('.')[0]] = f'{styles_path}/{style}'

    # Display the box to choose a style
    selected_style = st.selectbox('Choose one of the following styles:', list(styles.keys()))

    # Display the selected image
    st.image(styles[selected_style], caption=selected_style, width=256)

    return selected_style


def upload_image():

    # File uploader widget for image upload
    uploaded_image = st.file_uploader('Upload an image:', type=['jpg', 'jpeg', 'png'])

    if uploaded_image is None:
        st.info('Please upload an image.')

    return uploaded_image


@st.cache_data
def torch_device():
    """Set torch device for style transfer models"""
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


@st.cache_data
def load_model(model_path, device):
    """Load the specified style transfer model"""
    style_model = ImageTransformNet().to(device) # loads the image transformation network and sends it to the device.
    style_model.load_state_dict(torch.load(model_path, map_location=device)) # loads the weights of the desired model.

    return style_model


def transform_image(image, device, model):
    """Apply style transfer to the image"""
    image = Image.open(image)
    size = image.size
    image = style_transfer(image, device, model, img_size=max(size))
    image = image.resize(size)
    return image


def display_transformed_image(original_image, transformed_image):
    """Display the original and the transformed images"""

    col1, col2 = st.columns(2)  # Create two columns

    with col1:
        st.image(original_image, caption='Original image', use_column_width=True)

    with col2:
        st.image(transformed_image, caption='Transformed image', use_column_width=True)


def main():
    st.title('Add a new style to your images!')
    device = torch_device()
    style = display_styles()
    model = load_model(f'models/{style}.model', device)
    image = upload_image()
    if image is not None:
        transformed_image = transform_image(image, device, model)
        display_transformed_image(image, transformed_image)


if __name__ == "__main__":
    main()
