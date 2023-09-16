import os
import sys
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
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY")

# Constants
CURRENT_DIRECTORY = os.getcwd()
IMAGE_DIRECTORY = os.path.join(CURRENT_DIRECTORY, "images")
CHARACTER_SHEET_DIRECTORY = os.path.join(CURRENT_DIRECTORY, "character_sheets")
DATA_DIRECTORY = os.path.join(CURRENT_DIRECTORY, "data")
PAGES_DIRECTORY = os.path.join(CURRENT_DIRECTORY, "pages")
MAX_TOKENS = 1500

# Ensure directories exist
os.makedirs(IMAGE_DIRECTORY, exist_ok=True)
os.makedirs(CHARACTER_SHEET_DIRECTORY, exist_ok=True)
os.makedirs(DATA_DIRECTORY, exist_ok=True)

# List options
CLASS_LIST = [
    "Barbarian",
    "Bard",
    "Cleric",
    "Druid",
    "Fighter",
    "Monk",
    "Paladin",
    "Ranger",
    "Rogue",
    "Sorcerer",
    "Warlock",
    "Wizard"
]
RACE_LIST = [
    "Dragonborn",
    "Dwarf",
    "Elf",
    "Gnome",
    "Half-Elf",
    "Half-Orc",
    "Halfling",
    "Human",
    "Tiefling",
    "Aarakocra",
    "Aasimar",
    "Bugbear",
    "Firbolg",
    "Goblin",
    "Goliath",
    "Hobgoblin",
    "Kenku",
    "Kobold",
    "Lizardfolk",
    "Orc",
    "Tabaxi",
    "Triton",
    "Yuan-ti Pureblood",
    "Genasi",
    "Changeling",
    "Kalashtar",
    "Shifter",
    "Warforged",
    "Centaur",
    "Loxodon",
    "Minotaur",
    "Simic Hybrid",
    "Vedalken",
    "Verdan",
    "Leonin",
    "Satyr"
]

def get_character_age():
    """
    Generate a weighted random age for a character between 0 and 500 years old.

    Returns:
        int: The age of the character.
    """
    age_weights = [0.07, 0.1, 0.43, 0.2, 0.1, 0.05, 0.05]
    age_choices = [
        random.randint(1, 13), random.randint(13, 17), random.randint(18, 35),
        random.randint(36, 50), random.randint(50, 120), random.randint(121, 1000),
        random.randint(1001, sys.maxsize)
    ]
    age = random.choices(age_choices, weights=age_weights)[0]
    return age

def get_character_examples():
    """
    Load character_examples.json file in current directory.

    Returns:
        list: List of character examples.
    """
    character_examples = []
    with open(os.path.join(PAGES_DIRECTORY, "character_examples.json")) as f:
        character_examples = json.loads(f.read())
    return character_examples

def get_character_data(character):
    """
    Query the ChatGPT API to fill out missing character data based on provided data.
    
    Args:
        character (dict): Dictionary containing character attributes.

    Returns:
        str: Generated character description.
    """
    examples = get_character_examples()

    print(f"Examples: {json.dumps(examples)}")

    messages=[
    {"role": "system", "content": "You are a dedicated assistant for dungeon masters. Your current task is to assist with filling out D&D character sheets."},
    {"role": "system", "content": "The user may give you an incomplete character sheet in JSON format. You must complete it, ensuring there are no empty values. Infuse the character with unique details, but make sure it remains playable within D&D 5e rules. Additionally, provide a 'portrait_prompt' for creating a character portrait using DALLE."},
    {"role": "system", "content": f"Here is an example character sheet for reference:\n\n{json.dumps(examples[0])}"},
    {"role": "user", "content": "Help me generate or fill out D&D 5e character sheets. Retain any existing values unless they're obviously placeholders. Ensure the character's details are consistent, follow D&D 5e rules, and are formatted as text strings. Impress me."},
    {"role": "assistant", "content": f"{json.dumps(examples[1])}"},
    {"role": "user", "content": "That's an excellent start. Now, generate a new character sheet for me."},
    {"role": "assistant", "content": f"{json.dumps(examples[2])}"}
    ]

    # Loop through each character example as a user/asistant message pair
    for example in examples[3:]:
        messages.append({"role": "user", "content": "Now, generate a new character sheet for me."})
        messages.append({"role": "assistant", "content": f"{json.dumps(example)}"})

    messages.append({"role": "user", "content": f"Now, complete this random unrelated character sheet for me.  Only return valid JSON.\n\n{json.dumps(character)}"})

    print(f"Messages: {json.dumps(messages)}")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k", messages=messages, max_tokens=MAX_TOKENS
    )
    print(f"Response: {json.dumps(response)}")
    result = json.loads(response.choices[0].message.content)
    print(f"Result: {json.dumps(result)}")
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

def create_pdf_character_sheet(character, portrait_filenames=[]):
    pdf = FPDF()
    pdf.add_page()
    
    # Set colors for headers and fills
    header_color = (60, 60, 60)  # Dark gray
    fill_color = (220, 220, 220)  # Light gray
    
    # Define fonts
    header_font = ("Arial", 'B', 18)
    sub_header_font = ("Arial", 'B', 14)
    label_font = ("Arial", 'B', 12)
    value_font = ("Arial", '', 12)
    
    # Function to add a section header
    def add_section_header(title, y_offset=None):
        if y_offset:
            pdf.ln(y_offset)
        pdf.set_fill_color(*header_color)
        pdf.set_font(*header_font)
        pdf.cell(0, 10, txt=title, ln=True, fill=True, align='L')
    
    # Function to add a sub-section header
    def add_sub_section_header(title):
        pdf.set_fill_color(*fill_color)
        pdf.set_font(*sub_header_font)
        pdf.cell(0, 10, txt=title, ln=True, fill=True, align='L')
    
    # Function to add key-value pairs with multi_cell for text wrapping
    def add_key_value(key, value, w1=45, w2=45, ln=False):
        pdf.set_font(*label_font)
        pdf.cell(w1, 8, txt=f"{key.replace('_', ' ').capitalize()}:", align='R')
        pdf.set_font(*value_font)
        current_y = pdf.get_y()
        current_x = pdf.get_x()
        pdf.multi_cell(w2, 8, txt=f"{value}")
        if not ln:
            pdf.set_xy(current_x + w2, current_y)
    
    # Character Name as Header
    pdf.set_font("Arial", 'B', 24)
    pdf.cell(0, 20, txt=character['name'], ln=True, align='C')

    # Character level as sub-header
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 10, txt=character['name'], ln=True, align='C')

    # Separate description to handle spacing and wrapping properly
    description = character["description"]
    description_height = len(description) / 72 + 1
    add_key_value("description", character["description"], w1=50, w2=140, ln=True) 
    
    # Basic Info
    add_section_header("Basic Info")
    basic_info_keys = ['level', 'pronouns', 'orientation', 'race', 'class', 'alignment', 'background', 'age', 'height', 'weight', 'eyes', 'skin', 'hair', 'experience_points']
    for idx, key in enumerate(basic_info_keys):
        add_key_value(key, character[key], ln=(idx % 2 != 0))
    
    # Character Stats
    add_section_header("Character Stats", y_offset=10)
    stats_keys = ['armor_class', 'hit_points', 'speed', 'strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma', 'passive_wisdom_perception', 'inspiration', 'proficiency_bonus']
    for idx, key in enumerate(stats_keys):
        add_key_value(key, character[key], ln=(idx % 2 != 0))
    
    # Saving Throws & Skills
    add_section_header("Saving Throws & Skills", y_offset=10)
    throws_keys = ['strength_save', 'dexterity_save', 'constitution_save', 'intelligence_save', 'wisdom_save', 'charisma_save']
    for idx, key in enumerate(throws_keys):
        add_key_value(key, character[key], ln=(idx % 2 != 0))
    
    # Skills
    add_sub_section_header("Skills")
    skills_list = ["Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception", "History", "Insight", "Intimidation", "Investigation", "Medicine", "Nature", "Perception", "Performance", "Persuasion", "Religion", "Sleight of Hand", "Stealth", "Survival"]
    for idx, skill in enumerate(skills_list):
        skill_key = f"skills_{skill.lower().replace(' ', '_')}"
        add_key_value(skill, character[skill_key], ln=(idx % 2 != 0))
    
    # Proficiencies & Languages
    add_section_header("Proficiencies & Languages", y_offset=10)
    add_key_value("Languages", character['languages'], w1=50, w2=140, ln=True)
    add_key_value("Proficiencies", character['proficiencies'], w1=50, w2=140)
    
    # Character Traits
    add_section_header("Character Traits", y_offset=10)
    trait_keys = ['personality_traits', 'ideals', 'bonds', 'flaws', 'character_appearance', 'character_backstory']
    for key in trait_keys:
        add_key_value(key, character[key], w1=80, w2=110, ln=True)
    
    # Additional Features & Traits
    add_section_header("Additional Features & Traits", y_offset=10)
    add_key_value("Features", character['features_traits'], w1=80, w2=110, ln=True)
    add_key_value("Additional Features", character['additional_features_traits'], w1=80, w2=110)
    
    # Equipment & Treasure
    add_section_header("Equipment & Treasure", y_offset=10)
    add_key_value("Equipment", character['equipment'], w1=80, w2=110, ln=True)
    add_key_value("Treasure", character['treasure'], w1=80, w2=110)
    
    # Attacks & Spellcasting
    add_section_header("Attacks & Spellcasting", y_offset=10)
    add_key_value("Details", character['attacks_spellcasting'], w1=80, w2=110, ln=True)
    add_key_value("Spellcasting Class", character['spellcasting_class'], w1=80, w2=110)
    add_key_value("Spellcasting Ability", character['spellcasting_ability'], w1=80, w2=110, ln=True)
    add_key_value("Spell Save DC", character['spell_save_dc'], w1=80, w2=110, ln=True)
    add_key_value("Spell Attack Bonus", character['spell_attack_bonus'], w1=80, w2=110, ln=True)
    
    # Portraits
    for filename in portrait_filenames:
        try:
            pdf.ln(10)
            pdf.image(filename, x=10, y=None, w=90)
            pdf.ln(5)
        except Exception as e:
            print(f"Error adding image {filename} to PDF: {e}")
    
    # Footer with page number
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.alias_nb_pages()
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, 'Page ' + str(pdf.page_no()) + '/{nb}', 0, 0, 'C')
    
    pdf_file_path = os.path.join(CHARACTER_SHEET_DIRECTORY, f"{character['name'].replace(' ', '_')}_{uuid4()}.pdf")
    pdf.output(pdf_file_path)

    return pdf_file_path

def default_character():
    # Grab an example character and clear out the values
    character_examples = get_character_examples()

    default_character = character_examples[0]
    for key in default_character:
        if isinstance(default_character[key], list):
            default_character[key] = []
        else:
            default_character[key] = ""

    return default_character

# Set the page configuration at the very top of the script
st.set_page_config(page_title="D&D Character Creator", page_icon="📈")

def build_form(character):
    """
    Constructs the interactive form in the Streamlit application to gather and display 
    character details for a D&D character.

    The form consists of multiple sections, including:
    - Level, Character Name, and Description
    - Basic Information: Character's pronouns, orientation, race, class, alignment, background, age, and other physical traits.
    - Stats: Various statistics related to the character's abilities and combat readiness.
    - Saving Throws: Character's saving throw proficiencies.
    - Skills: Various skills the character is proficient in.
    - Character Traits: Appearance, personality traits, ideals, bonds, flaws, and backstory.
    - Attacks and Spellcasting: Information related to the character's combat and magic abilities.
    - Other Proficiencies and Languages: Other skills and languages the character knows.
    - Equipment: Gear and items the character possesses.
    - Features and Traits: Special abilities and features the character has.
    - Allies and Organizations: Allies and enemies of the character.
    - Spellcasting: Information about the character's spellcasting abilities and known spells.

    Args:
        character (dict): A dictionary containing the character's details. The dictionary keys 
                          correspond to various character attributes, and this function updates
                          the dictionary in-place based on user input.

    Returns:
        form: The Streamlit form object containing all the character input fields.
    """
    # If there's a valid PDF path in the session state, display the download button
    if 'pdf_path' in st.session_state and st.session_state.pdf_path:
        with open(st.session_state.pdf_path, 'rb') as file:
            btn = st.download_button(
                label="Download Character Sheet PDF",
                data=file,
                file_name=f"{character['name'].replace(' ', '_')}.pdf",
                mime="application/pdf"
            )

    form = st.form(key='character_form', clear_on_submit=True)

    with form:
        if 'portrait_filenames' in st.session_state and st.session_state.portrait_filenames:
            for filename in st.session_state.portrait_filenames:
                st.image(filename, caption=f"Portrait of {character['name']}", use_column_width=True)

        # Level, Name, Description
        character['level'] = st.text_input("Level", character.get('level', ''))
        character['name'] = st.text_input("Character Name", character['name'])
        character['description'] = st.text_area("Description", character['description'])

        # Basic Info
        with st.expander("Basic Info"):
            cols = st.columns(2)
            character['pronouns'] = cols[0].text_input("Pronouns", character.get('pronouns', ''), key='basic_pronouns_input')
            character['orientation'] = cols[0].text_input("Orientation", character.get('orientation', ''), key='basic_orientation_input')
            character['race'] = cols[0].text_input("Race", character['race'], key='basic_race_input')
            character['class'] = cols[0].text_input("Class", character['class'], key='basic_class_input')
            character['alignment'] = cols[0].text_input("Alignment", character['alignment'], key='basic_alignment_input')
            character['background'] = cols[0].text_input("Background", character['background'], key='basic_background_input')
            character['age'] = cols[1].text_input("Age", character['age'], key='basic_age_input')
            character['height'] = cols[1].text_input("Height", character.get('height', ''), key='basic_height_input')
            character['weight'] = cols[1].text_input("Weight", character.get('weight', ''), key='basic_weight_input')
            character['eyes'] = cols[1].text_input("Eyes", character.get('eyes', ''), key='basic_eyes_input')
            character['skin'] = cols[1].text_input("Skin", character.get('skin', ''), key='basic_skin_input')
            character['hair'] = cols[1].text_input("Hair", character.get('hair', ''), key='basic_hair_input')
            character['experience_points'] = st.text_input("Experience Points", character.get('experience_points', ''), key='basic_experience_points_input')

        # Stats
        with st.expander("Stats"):
            cols = st.columns(6)
            character['armor_class'] = cols[0].text_input("Armor Class", character.get('armor_class', ''), key='stats_armor_class_input')
            character['hit_points'] = cols[1].text_input("Hit Points", character.get('hit_points', ''), key='stats_hit_points_input')
            character['speed'] = cols[2].text_input("Speed", character.get('speed', ''), key='stats_speed_input')
            character['strength'] = cols[3].text_input("Strength", character.get('strength', ''), key='stats_strength_input')
            character['dexterity'] = cols[4].text_input("Dexterity", character.get('dexterity', ''), key='stats_dexterity_input')
            character['constitution'] = cols[5].text_input("Constitution", character.get('constitution', ''), key='stats_constitution_input')
            character['intelligence'] = cols[0].text_input("Intelligence", character.get('intelligence', ''), key='stats_intelligence_input')
            character['wisdom'] = cols[1].text_input("Wisdom", character.get('wisdom', ''), key='stats_wisdom_input')
            character['charisma'] = cols[2].text_input("Charisma", character.get('charisma', ''), key='stats_charisma_input')
            character['passive_wisdom'] = cols[3].text_input("Passive Wisdom (Perception)", character.get('passive_wisdom_perception', ''), key='stats_passive_wisdom_input')
            character['inspiration'] = cols[4].text_input("Inspiration", character.get('inspiration', ''), key='stats_inspiration_input')
            character['proficiency_bonus'] = cols[5].text_input("Proficiency Bonus", character.get('proficiency_bonus', ''), key='stats_proficiency_bonus_input')

        # Saving Throws
        with st.expander("Saving Throws"):
            cols = st.columns(6)
            character['strength_save'] = cols[0].text_input("Strength", character.get('strength_save', ''), key='saves_strength_input')
            character['dexterity_save'] = cols[1].text_input("Dexterity", character.get('dexterity_save', ''), key='saves_dexterity_input')
            character['constitution_save'] = cols[2].text_input("Constitution", character.get('constitution_save', ''), key='saves_constitution_input')
            character['intelligence_save'] = cols[3].text_input("Intelligence", character.get('intelligence_save', ''), key='saves_intelligence_input')
            character['wisdom_save'] = cols[4].text_input("Wisdom", character.get('wisdom_save', ''), key='saves_wisdom_input')
            character['charisma_save'] = cols[5].text_input("Charisma", character.get('charisma_save', ''), key='saves_charisma_input')

        # Skills
        with st.expander("Skills"):
            cols = st.columns(4)
            skills_list = ["Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception", "History", "Insight", "Intimidation", "Investigation", "Medicine", "Nature", "Perception", "Performance", "Persuasion", "Religion", "Sleight of Hand", "Stealth", "Survival"]
            for idx, skill in enumerate(skills_list):
                character[f"skills_{skill.lower().replace(' ', '_')}"] = cols[idx % 4].text_input(skill, character.get(f"skills_{skill.lower().replace(' ', '_')}", ''), key=f"skills_{skill.replace(' ', '_').lower()}_input")

        # Character Traits
        with st.expander("Character Traits"):
            character['personality_traits'] = st.text_area("Personality Traits", character.get('personality_traits', ''), key='traits_personality_input')
            character['ideals'] = st.text_area("Ideals", character.get('ideals', ''), key='traits_ideals_input')
            character['bonds'] = st.text_area("Bonds", character.get('bonds', ''), key='traits_bonds_input')
            character['flaws'] = st.text_area("Flaws", character.get('flaws', ''), key='traits_flaws_input')

        # Attacks and Spellcasting
        with st.expander("Attacks and Spellcasting"):
            character['attacks_spellcasting'] = st.text_area("Details", character.get('attacks_spellcasting', ''), key='attacks_details_input')

        # Other Proficiencies and Languages
        with st.expander("Proficiencies and Languages"):
            character['languages'] = st.text_input("Languages", character.get('languages', ''))
            character['proficiencies'] = st.text_input("Proficiencies", character.get('proficiencies', ''))

        # Equipment
        with st.expander("Equipment"):
            character['equipment'] = st.text_area("Details", character.get('equipment', ''), key='equipment_details_input')

        # Features and Traits
        with st.expander("Features and Traits"):
            character['features_traits'] = st.text_area("Details", character.get('features_traits', ''), key='features_details_input')

        # Allies and Organizations
        with st.expander("Allies and Organizations"):
            character['allies_organizations'] = st.text_area("Details", character.get('allies_organizations', ''), key='allies_organizations_details_input')

        # Spellcasting
        with st.expander("Spellcasting"):
            cols = st.columns(4)
            character['spellcasting_class'] = cols[0].text_input("Spellcasting Class", character.get('spellcasting_class', ''), key='spells_class_input')
            character['spellcasting_ability'] = cols[1].text_input("Spellcasting Ability", character.get('spellcasting_ability', ''), key='spells_ability_input')
            character['spell_save_dc'] = cols[2].text_input("Spell Save DC", character.get('spell_save_dc', ''), key='spells_save_dc_input')
            character['spell_attack_bonus'] = cols[3].text_input("Spell Attack Bonus", character.get('spell_attack_bonus', ''), key='spells_attack_bonus_input')

        # Spells Known
        with st.expander("Spells Known"):
            for level in range(1, 10):
                character[f'{level}_level_spells'] = st.text_area(f"Level {level} Spells", character.get(f'{level}_level_spells', ''), key=f'{level}_level_spells_input')

        # Character Appearance
        with st.expander("Character Appearance"):
            character['character_appearance'] = st.text_area("Details", character.get('character_appearance', ''), key='character_appearance_details_input')

        # Character Backstory
        with st.expander("Character Backstory"):
            character['character_backstory'] = st.text_area("Details", character.get('character_backstory', ''), key='backstory_details_input')

        # Additional Features and Traits
        with st.expander("Additional Features and Traits"):
            character['additional_features_traits'] = st.text_area("Details", character.get('additional_features_traits', ''), key='additional_features_details_input')

        # Treasure
        with st.expander("Treasure"):
            character['treasure'] = st.text_area("Details", character.get('treasure', ''), key='treasure_details_input')

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
            # If all values are empty, set some random defaults
            if all(value == "" for value in character.values()):
                character['age'] = get_character_age()
                character['level'] = random.randint(1, 20)
                character['class'] = random.choice(CLASS_LIST)
                character['race'] = random.choice(RACE_LIST)

            # Check if all values are filled in
            if not all(value != "" for value in character.values()):
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
                num_portraits = 1
                #num_portraits = st.slider("Number of Portraits", 1, 5)
                for _ in range(num_portraits):
                    portrait_prompt = character.get("portrait_prompt", "")

                    # Check if portrait_prompt is empty
                    if not portrait_prompt:
                        st.write("No portrait prompt provided. Skipping portrait generation.")
                        continue

                    try:
                        with st.spinner('Generating character portrait...'):
                            st.session_state.portrait_filenames.append(generate_portrait(portrait_prompt, character['name']))
                    except Exception as e:
                        st.error(f"Error generating portrait: {str(e)}")

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
