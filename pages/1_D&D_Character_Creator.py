import os
import json
import random
import openai
import streamlit as st
import pandas as pd
import requests
from uuid import uuid4
from fpdf import FPDF
from PIL import Image

# Set OpenAI API Key
#openai.api_key = os.environ.get('OPENAI_API_KEY')

# Set OpenAI API Key
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY")

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
        "appearance": "Liora is a tall and slender High Elf with long, flowing silver hair that cascades down her back. Her piercing blue eyes seem to hold the mysteries of the ages, often lost in deep thought. Her skin is a pale shade, almost luminescent under certain lights. She typically wears her enlightened robes, and a silver circlet can always be seen resting on her forehead. Around her neck, she wears a necklace with a crystal orb that is said to have been touched by the first wizards.",
        "age": 124,
        "pronouns": "She/Her",
        "orientation": "Bisexual",
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
        "languages": "Common, Elvish, Draconic, Sylvan",
        "skills": "Arcana, History",
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
        "portrait_prompt": "A tall and slender High Elf named Liora Moonshadow with long, flowing silver hair and piercing blue eyes. She wears enlightened robes and a silver circlet on her forehead. Around her neck, she has a crystal orb necklace. In her hand, she holds a Staff of the Arcane and carries a spellbook."
    }
    ]
    messages=[
        {"role": "system", "content": "You are a helpful dungeon master's assistant. You are helping a user fill in their D&D character sheet."},
        {"role": "system", "content": f"Here are some example character sheets:\n\n{json.dumps(examples)}"},
        {"role": "system", "content": "The user will provide an incomplete JSON character sheet. Your job will be to fill it out completely. Feel free to take artistic licence with all character details, but make sure the character sheet is logically consistent and the character is playable. Also include a portrait_prompt value we can pass to dalle to create a character portrait."},
        {"role": "user", "content": f"{json.dumps(character)}"},
        {"role": "system", "content": "Please completely fill in the JSON data for the character sheet based on the provided character sheet. Use proper JSON formatting for your response.  Don't leave any values blank. Make sure facts about the character are consistent across the generated character sheet JSON."},
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
    
    # Use character name in filename
    filename_base = character_name.replace(" ", "_") if character_name else "default_character"
    filename = f"{IMAGE_DIRECTORY}/{filename_base}"
    with open(filename, "wb") as file:
        file.write(response.content)
    return filename

def generate_portrait(prompt, character_name):
    """
    Generate a portrait based on the prompt using DALL-E and save it locally.
    
    Args:
    - prompt (str): The prompt for DALL-E to generate an image.
    - character_name (str): The name of the character for filename generation.

    Returns:
    - str: Filepath where the portrait is saved.
    """
    response = openai.Image.create(prompt=prompt, n=1, size="256x256")
    image_url = response.data[0]['url']
    
    # Create a proper filename using the character's name and a unique identifier
    safe_name = character_name.replace(" ", "_")
    filename = f"{safe_name}_{uuid4()}.png"
    
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

    # Title: Character Name
    pdf.set_font("Arial", 'B', 24)
    pdf.cell(0, 20, txt=character['name'], ln=True, align='C')

    # Function to create section header
    def add_section_header(title):
        pdf.set_font("Arial", 'B', 18)
        pdf.cell(0, 15, txt=title, ln=True, fill=True, align='L')

    # Function to add key-value pair
    def add_key_value(key, value):
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=f"{key.replace('_', ' ').capitalize()}: {value}", align='L')

    # Character Basic Info
    add_section_header("Character Details")
    basic_info_keys = ['pronouns', 'orientation', 'race', 'class', 'alignment', 'background', 'age']
    for key in basic_info_keys:
        add_key_value(key, character[key])

    # Character Traits
    add_section_header("Character Traits")
    trait_keys = ['personality_traits', 'ideals', 'bonds', 'flaws', 'character_backstory', 'allies_enemies']
    for key in trait_keys:
        add_key_value(key, character[key])

    # Skills and Languages
    add_section_header("Skills & Languages")
    add_key_value("Skills", ', '.join(character['skills']))
    add_key_value("Languages", ', '.join(character['languages']))

    # Equipment and Treasure
    add_section_header("Equipment & Treasure")
    add_key_value("Equipment", character['equipment'])
    add_key_value("Treasure", character['treasure'])

    # Portraits
    for filename in portrait_filenames:
        try:
            pdf.ln(10)
            pdf.image(filename, x=10, y=None, w=90)
            pdf.ln(5)
        except Exception as e:
            st.warning(f"Error adding image {filename} to PDF: {e}")

    # Footer with page number
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.alias_nb_pages()
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, 'Page ' + str(pdf.page_no()) + '/{nb}', 0, 0, 'C')

    pdf_file_path = os.path.join(CHARACTER_SHEET_DIRECTORY, f"{character['name'].replace(' ', '_')}_{uuid4()}.pdf")
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
        "appearance": "",
        "race": "",
        "class": "",
        "alignment": "",
        "background": "",
        "age": "",
        "personality_traits": "",
        "ideals": "",
        "bonds": "",
        "flaws": "",
        "character_backstory": "",
        "allies_enemies": "",
        "languages": "",
        "custom_language": "",
        "skills": "",
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

def build_form(character):
    """
    Constructs the interactive form in the Streamlit application to gather and display 
    character details for a D&D character.

    The form consists of multiple sections, including:
    - Basic Information: Character's name, description, race, class, alignment, background, age, pronouns, and orientation.
    - Character Traits: Appearance, personality traits, ideals, bonds, flaws, backstory, allies, and enemies.
    - Skills and Languages: Character's skills and languages, both standard and custom.
    - Equipment and Treasure: Items and treasures the character possesses.
    - Spellcasting: Information about the character's spellcasting class, ability, save DC, and attack bonus.
    - Portraits: Displays generated character portraits if available.

    Args:
        character (dict): A dictionary containing the character's details. The dictionary keys 
                          correspond to various character attributes, and this function updates
                          the dictionary in-place based on user input.

    Returns:
        None. The function updates the `character` dictionary in-place and displays the form 
        fields on the Streamlit app.
    """
    character['name'] = st.text_input("Character Name", character['name'])
    character['description'] = st.text_area("Description", character['description'])

    with st.expander("Basic Info"):
        character['pronouns'] = st.text_input("Pronouns", character.get('pronouns', ''))
        character['orientation'] = st.text_input("Orientation", character.get('orientation', ''))
        character['race'] = st.text_input("Race", character['race'])
        character['class'] = st.text_input("Class", character['class'])
        character['alignment'] = st.text_input("Alignment", character['alignment'])
        character['background'] = st.text_input("Background", character['background'])
        character['age'] = st.text_input("Age", value=character['age'])

    with st.expander("Character Traits"):
        character['appearance'] = st.text_area("Appearance", character['appearance'])
        character['personality_traits'] = st.text_area("Personality Traits", character['personality_traits'])
        character['ideals'] = st.text_area("Ideals", character['ideals'])
        character['bonds'] = st.text_area("Bonds", character['bonds'])
        character['flaws'] = st.text_area("Flaws", character['flaws'])
        character['character_backstory'] = st.text_area("Backstory", character['character_backstory'])
        character['allies_enemies'] = st.text_area("Allies & Enemies", character['allies_enemies'])

    with st.expander("Skills and Languages"):
        character['skills'] = st.text_input("Skills", character['skills'])
        character['languages'] = st.text_input("Languages", character['languages'])

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
    
    if 'portrait_filenames' in st.session_state and st.session_state.portrait_filenames:
        for filename in st.session_state.portrait_filenames:
            st.image(filename, caption=f"Portrait of {character['name']}", use_column_width=True)

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
        portrait_placeholder = st.empty()
        save_button_placeholder = st.empty()

        with st.spinner('Generating character data...'):
            try:
                # Get character data from API
                generated_data = get_character_data(character)
                for key, value in generated_data.items():
                    character[key] = value
            except Exception as e:
                st.error(f"Error generating character data: {str(e)}")
                return

        with st.spinner('Generating PDF character sheet...'):
            try:
                st.session_state.portrait_filenames = []

                # Generate portrait prompts and portrait
                #num_portraits = st.slider("Number of Portraits", 1, 5)
                num_portraits = 1
                for _ in range(num_portraits):
                    portrait_prompt = character.get("portrait_prompt", "")

                    # Check if portrait_prompt is empty
                    if not portrait_prompt:
                        #st.write("No portrait prompt provided. Skipping portrait generation.")
                        continue

                    with st.spinner('Generating character portrait...'):
                        st.session_state.portrait_filenames.append(generate_portrait(portrait_prompt, character['name']))

                # Create PDF character sheet and save
                pdf_filename = create_pdf_character_sheet(character, st.session_state.portrait_filenames)

                # Save the path to the PDF in the session state
                st.session_state.pdf_path = pdf_filename

            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
                return

        st.experimental_rerun()

    # If there's a valid PDF path in the session state, display the download button
    if 'pdf_path' in st.session_state and st.session_state.pdf_path:
        st.markdown(f"[Download Character Sheet PDF]({st.session_state.pdf_path})")

if __name__ == "__main__":
    main()
