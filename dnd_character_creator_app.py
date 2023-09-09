import os
import openai
import streamlit as st
import boto3
import asyncio
from PIL import Image

# Configuration from environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")

openai.api_key = OPENAI_API_KEY
s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

st.set_page_config(
    page_title="D&D Character Generator with Portraits",
    layout="centered"
)

def openai_completion(prompt):
    """Send a text prompt to ChatGPT and return its generated completion."""
    response = openai.Completion.create(prompt=prompt, max_tokens=150, temperature=0.5)
    return response['choices'][0]['text']

async def generate_character_details(character):
    """Use ChatGPT to fill in missing character details."""
    if not character.get("description"):
        prompt = f"Describe a character named {character['name']} who is a {character['race']}."
        character['description'] = openai_completion(prompt)
    return character

async def generate_portrait(prompt):
    """Send a prompt to DALL-E and return the generated image URL."""
    response = openai.Image.create(prompt=prompt, n=1, size="256x256")
    return response['data'][0]['url']

def upload_to_s3(image_url):
    """Upload a generated portrait to S3 and return its public URL."""
    s3.upload_file(image_url, S3_BUCKET_NAME, 'path_in_bucket')
    s3_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/path_in_bucket"
    return s3_url

def generate_character_sheet(character):
    """Generate a HTML character sheet."""
    return f"""
    <div style="border:2px solid black;padding:20px;">
        <h2>{character['name']}</h2>
        <p><strong>Description:</strong> {character['description']}</p>
        <p><strong>Race:</strong> {character['race']}</p>
        <p><strong>Backstory:</strong> {character['backstory']}</p>
        <p><strong>Alignment:</strong> {character['alignment']}</p>
        <p><strong>Traits:</strong> {character['traits']}</p>
        <p><strong>Ideals:</strong> {character['ideals']}</p>
        <p><strong>Bonds:</strong> {character['bonds']}</p>
        <p><strong>Flaws:</strong> {character['flaws']}</p>
        <img src="{character['portrait_url']}" alt="Character Portrait" style="width:200px;height:200px;">
    </div>
    """

def main():
    """Main function for the Streamlit app."""
    st.title("D&D Character Generator with Portraits")

    # Form Fields
    character = {
        "name": st.text_input("Name"),
        "description": st.text_area("Description"),
        "race": st.selectbox("Race", ["Elf", "Dwarf", "Human"]),
        "backstory": st.text_area("Backstory"),
        "alignment": st.radio("Alignment", ["Lawful Good", "Chaotic Neutral"]),
        "traits": st.text_area("Personality Traits"),
        "ideals": st.text_area("Ideals"),
        "bonds": st.text_area("Bonds"),
        "flaws": st.text_area("Flaws")
    }

    portrait_prompt = st.text_area("Portrait Prompt (Optional. If empty, we'll generate one based on the description.)")

    # Generate and Display Character Sheet
    if st.button("Generate Character Sheet"):
        try:
            # Fill in missing details
            character = asyncio.run(generate_character_details(character))
            
            # Get portrait
            if not portrait_prompt:
                portrait_prompt = f"A portrait of {character['name']}, a {character['description']}"
            image_url = asyncio.run(generate_portrait(portrait_prompt))
            s3_url = upload_to_s3(image_url)
            character["portrait_url"] = s3_url
            
            # Display character sheet
            html_sheet = generate_character_sheet(character)
            st.markdown(html_sheet, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()
