import os
import openai
import streamlit as st
import pandas as pd
from uuid import uuid4

# Set OpenAI API Key
openai.api_key = os.environ.get('OpenAI_API_Key')

def get_character_data(character):
    """
    Query the ChatGPT API to fill out missing character data based on provided data.
    """
    prompt = f"Describe a D&D character with the following attributes: {character}"
    response = openai.Completion.create(model="text-davinci-003", prompt=prompt, max_tokens=150)
    return response.choices[0].text.strip()

def generate_portrait(prompt):
    """
    Generate a portrait based on the prompt using DALL-E and save it locally.
    """
    response = openai.Image.create(prompt=prompt, n=1, size="256x256")
    image_url = response.data[0]['url']
    filename = f"portraits/{uuid4()}.png"
    st.image(image_url).save(filename)
    return filename

def generate_html_character_sheet(character, portrait_filenames):
    """
    Generate an HTML character sheet based on character data and save it locally.
    """
    html_content = f"""
    <h1>{character['name']}</h1>
    <p><strong>Race:</strong> {character['race']}</p>
    <p><strong>Class:</strong> {character['class']}</p>
    <p><strong>Alignment:</strong> {character['alignment']}</p>
    <p><strong>Background:</strong> {character['background']}</p>
    <p><strong>Description:</strong> {character['description']}</p>
    <p><strong>Personality Traits:</strong> {character['personality_traits']}</p>
    <p><strong>Ideals:</strong> {character['ideals']}</p>
    <p><strong>Bonds:</strong> {character['bonds']}</p>
    <p><strong>Flaws:</strong> {character['flaws']}</p>
    """
    for filename in portrait_filenames:
        html_content += f'<img src="{filename}" alt="Portrait of {character["name"]}">'
    filename = f"character_sheets/{uuid4()}.html"
    with open(filename, 'w') as file:
        file.write(html_content)
    return filename

def main():
    """
    Main function for the Streamlit app.
    """
    st.title("D&D Character Generator with Portraits")

    character = {
        "name": st.text_input("Character Name", "Aelar"),
        "age": st.number_input("Age", min_value=1, max_value=500, value=25),
        "race": st.selectbox("Race", ["Human", "Elf", "Dwarf", "Orc", "Tiefling", "Custom"]),
        "class": st.selectbox("Class", ["Warrior", "Mage", "Rogue", "Cleric", "Ranger", "Custom"]),
        "alignment": st.selectbox("Alignment", ["Lawful Good", "Neutral Good", "Chaotic Good", "Lawful Neutral", "True Neutral", "Chaotic Neutral", "Lawful Evil", "Neutral Evil", "Chaotic Evil"]),
        "background": st.selectbox("Background", ["Acolyte", "Criminal", "Folk Hero", "Noble", "Sage", "Soldier", "Custom"]),
        "personality_traits": st.text_area("Personality Traits"),
        "ideals": st.text_area("Ideals"),
        "bonds": st.text_area("Bonds"),
        "flaws": st.text_area("Flaws"),
        "description": st.text_area("Description")
    }

    # Custom fields input
    if character["race"] == "Custom":
        character["race"] = st.text_input("Specify Your Custom Race")
    if character["class"] == "Custom":
        character["class"] = st.text_input("Specify Your Custom Class")
    if character["background"] == "Custom":
        character["background"] = st.text_input("Specify Your Custom Background")

    # Number of portraits
    num_portraits = st.slider("Number of Portraits", 1, 5)

    if st.button("Generate Character Sheet"):
        # Fetch filled out character data from the API
        character["description"] = get_character_data(character)

        # Generate portrait prompts and portraits
        portrait_filenames = []
        for _ in range(num_portraits):
            portrait_prompt = get_character_data({key: character[key] for key in ["name", "race", "class", "background"]})
            portrait_filenames.append(generate_portrait(portrait_prompt))

        # Generate HTML character sheet and save
        html_filename = generate_html_character_sheet(character, portrait_filenames)

        # Save character data as parquet
        df = pd.DataFrame([character])
        parquet_filename = f"data/{uuid4()}.parquet"
        df.to_parquet(parquet_filename)

        # Redirect to the HTML character sheet
        st.write(f"Character sheet saved at {html_filename} and data saved at {parquet_filename}")
        st.markdown(f"[Click here to view the character sheet]({html_filename})")

if __name__ == "__main__":
    main()
