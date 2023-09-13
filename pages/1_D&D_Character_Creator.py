import os
import json
import random
import openai
import streamlit as st
import pandas as pd
import requests
from uuid import uuid4
from fpdf import FPDF

# Set OpenAI API Key
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Constants
CURRENT_DIRECTORY = os.getcwd()
IMAGE_DIRECTORY = os.path.join(CURRENT_DIRECTORY, "images")
CHARACTER_SHEET_DIRECTORY = os.path.join(CURRENT_DIRECTORY, "character_sheets")
DATA_DIRECTORY = os.path.join(CURRENT_DIRECTORY, "data")
MAX_TOKENS = 1500

# Ensure directories exist
os.makedirs(IMAGE_DIRECTORY, exist_ok=True)
os.makedirs(CHARACTER_SHEET_DIRECTORY, exist_ok=True)
os.makedirs(DATA_DIRECTORY, exist_ok=True)

# List options
race_options = [
    "", "Human", "Elf", "Dwarf", "Orc", "Tiefling", "Gnome", "Halfling", 
    "Dragonborn", "Aarakocra", "Genasi", "Goliath", "Tabaxi", "Triton", "Custom"
]
class_options = [
    "", "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk", "Paladin", 
    "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard", "Custom"
]
alignment_options = [
    "", "Lawful Good", "Neutral Good", "Chaotic Good", "Lawful Neutral", 
    "True Neutral", "Chaotic Neutral", "Lawful Evil", "Neutral Evil", "Chaotic Evil"
]
background_options = [
    "", "Acolyte", "Charlatan", "Criminal", "Entertainer", "Folk Hero", 
    "Guild Artisan", "Hermit", "Noble", "Outlander", "Sage", "Sailor", 
    "Soldier", "Urchin", "Custom"
]
spellcasting_class_options = [
    "", "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk", "Paladin", 
    "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard", "Custom"
]
languages_options = [
    "", "Common", "Dwarvish", "Elvish", "Giant", "Gnomish", "Goblin", "Halfling",
    "Orc", "Abyssal", "Celestial", "Draconic", "Deep Speech", "Infernal",
    "Primordial", "Sylvan", "Undercommon", "Custom"
]
skills_options = [
    "Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception", "History", 
    "Insight", "Intimidation", "Investigation", "Medicine", "Nature", "Perception", 
    "Performance", "Persuasion", "Religion", "Sleight of Hand", "Stealth", "Survival", "Custom"
]
spellcasting_class_options = [
    "", "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk", "Paladin", 
    "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard", "Custom"
]

# Initialize the session state for the character if not present
if "character" not in st.session_state:
    st.session_state.character = {}

def unique_key(base_key_name):
    """Generate a unique key for Streamlit widgets."""
    return f"{base_key_name}_uuid{uuid4()}"

def get_character_age():
    """
    Generate a weighted random age for a character between 0 and 500 years old.

    Returns:
        int: The age of the character.
    """
    age_weights = [0.05, 0.1, 0.45, 0.2, 0.1, 0.05, 0.05]
    age_choices = [
        random.randint(1, 13), random.randint(13, 17), random.randint(18, 35),
        random.randint(36, 50), random.randint(50, 100), random.randint(101, 200),
        random.randint(201, 500)
    ]
    age = random.choices(age_choices, weights=age_weights)[0]
    return age

def get_character_data(character):
    """
    Query the ChatGPT API to fill out missing character data based on provided data.
    
    Args:
        character (dict): Dictionary containing character attributes.

    Returns:
        str: Generated character description.
    """
    examples = [
       {
  "name": "Liora Moonshadow",
  "description": "A graceful elf with silver hair and piercing blue eyes, adept in the arcane arts and carrying the wisdom of the ages.",
  "age": 124,
  "race": "High Elf",
  "class": "Wizard",
  "alignment": "Neutral",
  "background": "Sage",
  "personality_traits": "I am lost in thought, often oblivious to my surroundings. I'm fascinated by ancient artifacts and the secrets they hold.",
  "ideals": "Knowledge. The pursuit of knowledge is the greatest endeavor.",
  "bonds": "I am on a quest to find an ancient spellbook said to contain the secrets of the universe.",
  "flaws": "I often overlook immediate dangers, being too engrossed in my studies or thoughts.",
  "character_backstory": "Liora hails from the ancient city of Ellyndor. Trained in the Grand Library, she became obsessed with a lost spellbook of immense power. Now she travels the land in search of this artifact, using her magic to uncover hidden truths.",
  "allies_enemies": "Allied with the Keepers of the Grand Library. Beware of the Dark Enchantress, who also seeks the spellbook.",
  "languages": ["Common", "Elvish", "Draconic", "Sylvan"],
  "skills": ["Arcana", "History"],
  "custom_language": "Ancient High Elvish",
  "custom_skill": "Magical artifact identification",
  "equipment": "Staff of the Arcane, robes of the enlightened, spellbook, and a pouch of spell components",
  "treasure": "A crystal orb said to have been touched by the first wizards",
  "custom_equipment": "Silver circlet that enhances focus",
  "custom_treasure": "A shard from the Mirror of Fates",
  "spellcasting_class": "Wizard",
  "spellcasting_ability": "Intelligence",
  "spell_save_dc": "16",
  "spell_attack_bonus": "+8",
  "portrait_prompt": "High Elf Wizard with silver hair and blue eyes. Wears enlightened robes and a silver circlet. Holds a Staff of the Arcane and a spellbook. Crystal orb necklace. Background shard from the Mirror of Fates.",
} 
    ]
    messages=[
        {"role": "system", "content": "You are a helpful dungeon master's assistant. You are helping a user fill in their D&D character sheet."},
        {"role": "system", "content": f"Here are some example character sheets:\n\n{json.dumps(examples)}"},
        {"role": "system", "content": "The user will provide an incomplete JSON character sheet. Your job will be to fill it out completely. Feel free to take artistic licence with all character details, but make sure the character sheet is logically consistent and the character is playable. Also include a portrait_prompt value we can pass to dalle to create a character portrait."},
        {"role": "user", "content": f"{json.dumps(character)}"},
        {"role": "system", "content": "Please completely fill in the JSON data for the character sheet based on the provided character sheet. Use proper JSON formatting for your response.  Don't leave any values blank."},
    ]
    print(f"Messages: {messages}")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages, max_tokens=MAX_TOKENS
    ) 
    result = json.loads(response.choices[0].message.content)
    print(f"Result: {result}")
    return result

def save_dalle_image_to_disk(image_url, character_name, portrait_num):
    """
    Saves the DALL·E generated image to the local disk.

    Args:
    - image_url (str): URL of the image generated by DALL·E.
    - character_name (str): Name of the character to be used in filename.
    - portrait_num (int): The number of the portrait for this character.

    Returns:
    - str: The path to the saved file.
    """
    response = requests.get(image_url)
    response.raise_for_status()  # Raise an error for failed requests
    
    filename = f"{IMAGE_DIRECTORY}{character_name}_portrait_{portrait_num}.png"
    with open(filename, "wb") as file:
        file.write(response.content)
    return filename

def generate_portrait(prompt):
    """
    Generate a portrait based on the prompt using DALL-E and save it locally.
    
    Args:
    - prompt (str): The prompt for DALL-E to generate an image.

    Returns:
    - str: Filepath where the portrait is saved.
    """
    response = openai.Image.create(prompt=prompt, n=1, size="256x256")
    image_url = response.data[0]['url']
    filename = f".png"
    return save_dalle_image_to_disk(image_url, filename, 1)

def create_pdf_character_sheet(character, portrait_filenames):
    """
    Generate a PDF character sheet based on character data and save it locally.

    Args:
        character (dict): Dictionary containing character attributes.
        portrait_filenames (list): List of portrait filenames for the character.

    Returns:
        str: The path to the saved PDF file.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=character['name'], ln=True)
    for key, value in character.items():
        if key != "name":
            pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
    for filename in portrait_filenames:
        pdf.image(filename, x=10, y=None, w=90)
    pdf_file_path = os.path.join(CHARACTER_SHEET_DIRECTORY, f".pdf")
    pdf.output(pdf_file_path)
    return pdf_file_path

def transform_to_dict(data_str):
    """
    Transform the provided data string into a dictionary.

    Args:
    - data_str (str): The string containing "key: value" pairs separated by newlines.

    Returns:
    - dict: The transformed dictionary.
    """
    print(f"Data string: {data_str}")
    #import ipdb; ipdb.set_trace()
    data_dict = json.loads(data_str)  # Convert the string to a dictionary
    return data_dict

def default_character():
    default_character = {
        "name": "",
        "description": "",
        "race": "",
        "class": "",
        "alignment": "",
        "background": "",
        "age": get_character_age(),
        "personality_traits": "",
        "ideals": "",
        "bonds": "",
        "flaws": "",
        "character_backstory": "",
        "allies_enemies": "",
        "languages": [],
        "custom_language": "",
        "skills": [],
        "custom_skill": "",
        "equipment": "",
        "treasure": "",
        "custom_equipment": "",
        "custom_treasure": "",
        "spellcasting_class": "",
        "custom_spellcasting_class": "",
        "spellcasting_ability": "",
        "spell_save_dc": "",
        "spell_attack_bonus": "",
        "portrait_prompt": ""  # This key can be used to store a prompt for generating a character portrait
    }
    return default_character

# Set the page configuration at the very top of the script
st.set_page_config(page_title="D&D Character Creator", page_icon="📈")

portrait_placeholder = None
save_button_placeholder = None

def build_form(character):
    character['name'] = st.text_input("Character Name", character['name'])
    character['description'] = st.text_area("Description", character['description'])

    with st.expander("Basic Info"):
        character['race'] = st.text_input("Race", character['race'])
        character['class'] = st.text_input("Class", character['class'])
        character['alignment'] = st.text_input("Alignment", character['alignment'])
        character['background'] = st.text_input("Background", character['background'])
        character['age'] = st.number_input("Age", min_value=1, max_value=500, value=character['age'])

    with st.expander("Character Traits"):
        character['personality_traits'] = st.text_area("Personality Traits", character['personality_traits'])
        character['ideals'] = st.text_area("Ideals", character['ideals'])
        character['bonds'] = st.text_area("Bonds", character['bonds'])
        character['flaws'] = st.text_area("Flaws", character['flaws'])
        character['character_backstory'] = st.text_area("Backstory", character['character_backstory'])
        character['allies_enemies'] = st.text_area("Allies & Enemies", character['allies_enemies'])

    with st.expander("Skills and Languages"):
        character['skills'] = st.multiselect("Skills", ['Skill 1', 'Skill 2', 'Skill 3'], character['skills'])  # Placeholder skills
        character['custom_skill'] = st.text_input("Custom Skill", character['custom_skill'])
        character['languages'] = st.multiselect("Languages", ['Common', 'Elvish', 'Dwarvish'], character['languages'])  # Placeholder languages
        character['custom_language'] = st.text_input("Custom Language", character['custom_language'])

    with st.expander("Equipment and Treasure"):
        character['equipment'] = st.text_area("Equipment", character['equipment'])
        character['treasure'] = st.text_area("Treasure", character['treasure'])
        character['custom_equipment'] = st.text_input("Custom Equipment", character['custom_equipment'])
        character['custom_treasure'] = st.text_input("Custom Treasure", character['custom_treasure'])

    with st.expander("Spellcasting"):
        character['spellcasting_class'] = st.text_input("Spellcasting Class", character['spellcasting_class'])
        character['custom_spellcasting_class'] = st.text_input("Custom Spellcasting Class", character['custom_spellcasting_class'])
        character['spellcasting_ability'] = st.text_input("Spellcasting Ability", character['spellcasting_ability'])
        character['spell_save_dc'] = st.text_input("Spell Save DC", character['spell_save_dc'])
        character['spell_attack_bonus'] = st.text_input("Spell Attack Bonus", character['spell_attack_bonus'])

def main():
    """
    Main function for the Streamlit app.
    """
    st.markdown("# D&D Character Creator")
  
    if 'character' not in st.session_state or not st.session_state.character:
        st.session_state.character = default_character()

    character = st.session_state.character

    build_form(character)

    if st.button("Generate Character Sheet"):
        #import ipdb; ipdb.set_trace()
        generated_data = get_character_data(character)
        #import ipdb; ipdb.set_trace()
        for key, value in generated_data.items():
            character[key] = value

        st.session_state.character = character
        # Generate portrait prompts and portrait
        num_portraits = st.slider("Number of Portraits", 1, 5)
        portrait_filenames = []
        for _ in range(num_portraits):
            portrait_prompt = character.get("portrait_prompt", "")
            
            # Check if portrait_prompt is empty
            if not portrait_prompt:
                st.write("No portrait prompt provided. Skipping portrait generation.")
                continue
            
            portrait_filenames.append(generate_portrait(portrait_prompt))

        portrait_placeholder = st.empty()
        save_button_placeholder = st.empty()

        for filename in portrait_filenames:
            portrait_placeholder.image(filename, caption=f"Portrait of {character['name']}", use_column_width=True)

        # Create PDF character sheet and save
        pdf_filename = create_pdf_character_sheet(character, portrait_filenames)

        # Display the saved locations to the user
        st.write(f"Character sheet saved as {pdf_filename}")
        st.markdown(f"[Click here to download the character sheet]({pdf_filename})")

        st.experimental_rerun()

if __name__ == "__main__":
    main()
