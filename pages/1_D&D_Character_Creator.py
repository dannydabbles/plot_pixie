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
        "name": "Hootclaw",
        "description": "An intelligent owlbear with a curious nature. Despite his fierce appearance, he's gentle at heart and possesses a unique magic affinity.",
        "appearance": "Hootclaw stands tall with a mix of owl and bear features. His feathered body is a mix of brown and white with sharp talons and a beak. His eyes are large and yellow, displaying a surprising depth of understanding.",
        "age": 15,
        "pronouns": "They/Them",
        "orientation": "Asexual",
        "race": "Owlbear",
        "class": "Druid",
        "alignment": "Neutral Good",
        "background": "Wilderness",
        "personality_traits": "I'm naturally curious and love to explore. I communicate more through actions than words.",
        "ideals": "Harmony. Nature is a balance of forces that should be respected.",
        "bonds": "The forest is my home, and I will defend it.",
        "flaws": "I'm easily distracted by shiny objects.",
        "character_backstory": "Hootclaw was found as a cub by a circle of druids who recognized his innate magical abilities. Raised among them, he learned the ways of nature and magic.",
        "allies_enemies": "Allied with the Druid Circle of the Whispering Pines. Watchful of hunters and trappers.",
        "languages": "Beast Speech, Druidic",
        "skills": "Nature, Perception",
        "custom_language": "Owlbear vocalizations",
        "custom_skill": "Mystical communion with forest spirits",
        "equipment": "Mystical totems, herbs, and a pouch of shiny trinkets",
        "treasure": "A feather imbued with protective magic",
        "custom_equipment": "Talismans made from forest materials",
        "custom_treasure": "A luminescent mushroom with healing properties",
        "spellcasting_class": "Druid",
        "spellcasting_ability": "Wisdom",
        "spell_save_dc": "14",
        "spell_attack_bonus": "+6",
        "portrait_prompt": "A large owlbear named Hootclaw with a mix of brown and white feathers, sharp talons, and deep yellow eyes."
    },
    {
        "name": "Ella Starshine",
        "description": "A young and enthusiastic adventurer with a bright spirit. She's always ready for a new quest and carries a small wooden sword.",
        "appearance": "Ella is a petite child with curly golden hair and freckles. She wears simple clothes and a cloak made from her grandmother's old quilt. Her eyes sparkle with mischief and curiosity.",
        "age": 8,
        "pronouns": "She/Her",
        "orientation": "Too young to determine",
        "race": "Halfling",
        "class": "Rogue",
        "alignment": "Chaotic Good",
        "background": "Urchin",
        "personality_traits": "I'm always curious and can't resist poking my nose into every mystery. I love to make new friends.",
        "ideals": "Adventure. Every day is a new story waiting to be written.",
        "bonds": "I cherish the quilt-cloak my grandmother gave me.",
        "flaws": "I sometimes act without thinking, driven by my curiosity.",
        "character_backstory": "Ella grew up listening to tales of adventure from her grandmother. Inspired, she decided to set out on her own little quests in and around her village.",
        "allies_enemies": "Friends with the local animals. Afraid of the grumpy old miller.",
        "languages": "Common, Halfling",
        "skills": "Acrobatics, Stealth",
        "custom_language": "Animal whispers",
        "custom_skill": "Finding hidden paths",
        "equipment": "Small wooden sword, quilt-cloak, and a pouch of marbles",
        "treasure": "A tiny gem she believes is magic",
        "custom_equipment": "A tiny compass that always points to her home",
        "custom_treasure": "A feather from a 'real' phoenix",
        "spellcasting_class": "None",
        "spellcasting_ability": "N/A",
        "spell_save_dc": "N/A",
        "spell_attack_bonus": "N/A",
        "portrait_prompt": "A petite halfling child named Ella Starshine with curly golden hair, freckles, and sparkling eyes. She wears a quilt-cloak and holds a small wooden sword."
    },
    {
        "name": "Nerida Lumina",
        "description": "An ancient merfolk who has seen the rise and fall of empires beneath the waves. Their beauty and wisdom are unmatched, and their heart embraces a myriad of loves.",
        "appearance": "Nerida has long, flowing hair that shifts colors like the northern lights. Their scales shimmer in shades of blue and green, and their eyes are deep pools of ancient knowledge. They wear ornaments made of coral and pearls.",
        "age": 453,
        "pronouns": "They/Them",
        "orientation": "Pansexual",
        "race": "Merfolk",
        "class": "Bard",
        "alignment": "Neutral",
        "background": "Noble",
        "personality_traits": "I am calm and reflective, often sharing tales of the past. I appreciate the beauty in all things.",
        "ideals": "Love. The heart's capacity for love is boundless.",
        "bonds": "I am bound to the great Coral Throne and its legacy.",
        "flaws": "I often get lost in memories, sometimes neglecting the present.",
        "character_backstory": "Nerida is a descendant of the ancient Lumina lineage, rulers of the underwater city of Luminara. They've witnessed centuries of history and are a keeper of ancient songs and tales.",
        "allies_enemies": "Allied with the Court of Luminara. Watchful of the Abyssal Marauders.",
        "languages": "Common, Aquan, Sylvan",
        "skills": "Performance, History",
        "custom_language": "Ancient Merfolk Song",
        "custom_skill": "Siren's call",
        "equipment": "Lute made of seashells, coral crown, and a pouch of sea gems",
        "treasure": "A pearl that holds the memories of their ancestors",
        "custom_equipment": "Coral harp that can calm turbulent waters",
        "custom_treasure": "A starfish that can guide one to hidden underwater realms",
        "spellcasting_class": "Bard",
        "spellcasting_ability": "Charisma",
        "spell_save_dc": "18",
        "spell_attack_bonus": "+10",
        "portrait_prompt": "An ancient merfolk named Nerida Lumina with hair that shifts colors like the northern lights and shimmering blue and green scales. They wear coral ornaments and hold a lute made of seashells."
    }
    ]
    messages=[
        {"role": "system", "content": "You are a helpful dungeon master's assistant. You are helping a user fill in their D&D character sheet."},
        {"role": "system", "content": f"Here are some example character sheets:\n\n{json.dumps(examples)}"},
        {"role": "system", "content": "The user will provide an incomplete JSON character sheet. Your job will be to fill it out completely. Feel free to take artistic licence with all character details, but make sure the character sheet is logically consistent and the character is playable. Also include a portrait_prompt value we can pass to dalle to create a character portrait."},
        {"role": "user", "content": f"{json.dumps(character)}"},
        {"role": "system", "content": "Please completely fill in the JSON data for the character sheet based on the provided character sheet. Use proper JSON formatting for your response.  Don't leave any values blank.  Make the generated character unique. Make sure facts about the character are consistent across the generated character sheet JSON."},
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
    form = st.form(key='character_form', clear_on_submit=True)
    with form:
        character['name'] = st.text_input("Character Name", character['name'])
        character['description'] = st.text_area("Description", character['description'])

        with st.expander("Basic Info"):
            character['pronouns'] = st.text_input("Pronouns", character.get('pronouns', ''))
            character['orientation'] = st.text_input("Orientation", character.get('orientation', ''))
            character['race'] = st.text_input("Race", character['race'])
            character['class'] = st.text_input("Class", character['class'])
            character['alignment'] = st.text_input("Alignment", character['alignment'])
            character['background'] = st.text_input("Background", character['background'])
            character['age'] = st.text_input("Age", character['age'] or get_character_age())

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
        # If there's a valid PDF path in the session state, display the download button
        if 'pdf_path' in st.session_state and st.session_state.pdf_path:
            st.markdown(f"[Download Character Sheet PDF]({st.session_state.pdf_path})")

    return form

def main():
    """
    Main function for the Streamlit app.
    """
    st.markdown("# D&D Character Creator")
    st.markdown("#### (Any empty fields will be filled in)")
  
    if 'character' not in st.session_state or not st.session_state.character:
        st.session_state.character = default_character()

    character = st.session_state.character

    form = build_form(character)

    if form.form_submit_button("Generate Character Sheet", use_container_width=True):
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

        st.session_state.character = character
        st.experimental_rerun()

if __name__ == "__main__":
    main()
