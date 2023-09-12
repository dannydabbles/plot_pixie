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

# Initialize the session state for the character if not present
if "character" not in st.session_state:
    st.session_state.character = {}

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
    result = response.choices[0].message.content
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

def input_basic_information(placeholder, character_data):
    """
    Gather basic information about the character from the user.
    
    Args:
        placeholder (streamlit.delta_generator.DeltaGenerator): Streamlit container for the section.
        character_data (dict): Dictionary containing current character information.

    Returns:
        dict: Dictionary containing basic character information.
    """
    with placeholder.expander("Basic Information", expanded=True):
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
        
        race = st.selectbox("Race", race_options, key=f"race_select_{uuid4()}")
        if race == "Custom":
            race = st.text_input("Custom Race", character_data.get("race", ""), key=f"custom_race_input_{uuid4()}")
        
        char_class = st.selectbox("Class", class_options, key=f"class_select_{uuid4()}")
        if char_class == "Custom":
            char_class = st.text_input("Custom Class", character_data.get("class", ""), key=f"custom_class_input_{uuid4()}")
        
        alignment = st.selectbox("Alignment", alignment_options, key=f"alignment_select_{uuid4()}")
        background = st.selectbox("Background", background_options, key=f"background_select_{uuid4()}")
        if background == "Custom":
            background = st.text_input("Custom Background", character_data.get("background", ""), key=f"custom_background_input_{uuid4()}")

        age_num = character_data.get("age")
        if not age_num:
            age_num = get_character_age()
        age_num = int(age_num)
        age = st.number_input("Age", min_value=1, max_value=500, step=1, value=age_num, key=f"age_input_{uuid4()}")

        return {
            "age": age,
            "race": race,
            "class": char_class,
            "alignment": alignment,
            "background": background
        }

def input_personality_and_backstory(placeholder, character_data):
    """
    Gather information about the character's personality and backstory.
    
    Args:
    - placeholder (streamlit.delta_generator.DeltaGenerator): Streamlit container for the section.
    - character_data (dict): Dictionary containing current character information.

    Returns:
    - dict: Dictionary containing character's personality and backstory.
    """
    with placeholder.expander("Personality & Backstory", expanded=True):
        
        personality_traits = st.text_area(
            "Personality Traits", 
            character_data.get("personality_traits", ""), 
            key=f"personality_traits_textarea_{uuid4()}"
        )
        
        ideals = st.text_area(
            "Ideals", 
            character_data.get("ideals", ""), 
            key=f"ideals_textarea_{uuid4()}"
        )
        
        bonds = st.text_area(
            "Bonds", 
            character_data.get("bonds", ""), 
            key=f"bonds_textarea_{uuid4()}"
        )
        
        flaws = st.text_area(
            "Flaws", 
            character_data.get("flaws", ""), 
            key=f"flaws_textarea_{uuid4()}"
        )
        
        character_backstory = st.text_area(
            "Character Backstory", 
            character_data.get("character_backstory", ""), 
            key=f"character_backstory_textarea_{uuid4()}"
        )
        
        allies_enemies = st.text_area(
            "Allies & Enemies", 
            character_data.get("allies_enemies", ""), 
            key=f"allies_enemies_textarea_{uuid4()}"
        )

        return {
            "personality_traits": personality_traits,
            "ideals": ideals,
            "bonds": bonds,
            "flaws": flaws,
            "character_backstory": character_backstory,
            "allies_enemies": allies_enemies
        }

def input_abilities_and_skills(placeholder, character_data):
    """
    Gather information about the character's abilities and skills.
    
    Args:
    - placeholder (streamlit.delta_generator.DeltaGenerator): Streamlit container for the section.
    - character_data (dict): Dictionary containing current character information.

    Returns:
    - dict: Dictionary containing character's abilities and skills.
    """
    with placeholder.expander("Abilities & Skills", expanded=True):
        
        languages_options = [
            "", "Common", "Dwarvish", "Elvish", "Giant", "Gnomish", "Goblin", "Halfling",
            "Orc", "Abyssal", "Celestial", "Draconic", "Deep Speech", "Infernal",
            "Primordial", "Sylvan", "Undercommon", "Custom"
        ]

        # Ensure that default languages are in the available options
        default_languages = [lang for lang in character_data.get("languages", []) if lang in languages_options]
        languages = st.multiselect(
            "Languages", 
            languages_options, 
            default=default_languages, 
            key=f"languages_multiselect_{uuid4()}"
        )
        
        custom_language = ""
        if "Custom" in languages:
            custom_language = st.text_input(
                "Specify the custom language", 
                character_data.get("custom_language", ""), 
                key=f"custom_language_input_{uuid4()}"
            )
            languages.append(custom_language)
            languages.remove("Custom")

        skills_options = [
            "Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception", "History", 
            "Insight", "Intimidation", "Investigation", "Medicine", "Nature", "Perception", 
            "Performance", "Persuasion", "Religion", "Sleight of Hand", "Stealth", "Survival", "Custom"
        ]
        
        # Ensure that default skills are in the available options
        default_skills = [skill for skill in character_data.get("skills", []) if skill in skills_options]
        skills = st.multiselect(
            "Skills", 
            skills_options, 
            default=default_skills, 
            key=f"skills_multiselect_{uuid4()}"
        ) 

        custom_skill = ""
        if "Custom" in skills:
            custom_skill = st.text_input(
                "Specify the custom skill", 
                character_data.get("custom_skill", ""), 
                key=f"custom_skill_input_{uuid4()}"
            )
            skills.append(custom_skill)
            skills.remove("Custom")
        
        return {
            "languages": languages,
            "skills": skills,
            "custom_language": custom_language if "Custom" in character_data.get("languages", []) else "",
            "custom_skill": custom_skill if "Custom" in character_data.get("skills", []) else ""
        }

def input_equipment_and_treasures(placeholder, character_data):
    """
    Gather information about the character's equipment and treasures.
    
    Args:
    - placeholder (streamlit.delta_generator.DeltaGenerator): Streamlit container for the section.
    - character_data (dict): Dictionary containing current character information.

    Returns:
    - dict: Dictionary containing character's equipment and treasures.
    """
    with placeholder.expander("Equipment & Treasures", expanded=True):
        
        equipment = st.text_area(
            "Starting Equipment", 
            character_data.get("equipment", ""), 
            key=f"equipment_textarea_{uuid4()}"
        )
        
        treasure = st.text_area(
            "Treasure", 
            character_data.get("treasure", ""), 
            key=f"treasure_textarea_{uuid4()}"
        )
        
        custom_equipment = st.text_input(
            "Custom Equipment (if any)", 
            character_data.get("custom_equipment", ""), 
            key=f"custom_equipment_input_{uuid4()}"
        )
        
        custom_treasure = st.text_input(
            "Custom Treasure (if any)", 
            character_data.get("custom_treasure", ""), 
            key=f"custom_treasure_input_{uuid4()}"
        )

        return {
            "equipment": equipment,
            "treasure": treasure,
            "custom_equipment": custom_equipment,
            "custom_treasure": custom_treasure
        }

def input_spellcasting(placeholder, character_data):
    """
    Gather information about the character's spellcasting abilities.
    
    Args:
    - placeholder (streamlit.delta_generator.DeltaGenerator): Streamlit container for the section.
    - character_data (dict): Dictionary containing current character information.

    Returns:
    - dict: Dictionary containing character's spellcasting information.
    """
    with placeholder.expander("Spellcasting", expanded=True):
        
        spellcasting_class_options = [
            "", "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk", "Paladin", 
            "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard", "Custom"
        ]
        
        spellcasting_class = st.selectbox(
            "Spellcasting Class", 
            spellcasting_class_options, 
            key=f"spellcasting_class_select_{uuid4()}"
        )
        
        custom_spellcasting_class = ""
        if spellcasting_class == "Custom":
            custom_spellcasting_class = st.text_input(
                "Specify the custom spellcasting class", 
                character_data.get("custom_spellcasting_class", ""), 
                key=f"custom_spellcasting_class_input_{uuid4()}"
            )
            spellcasting_class = custom_spellcasting_class
        
        spellcasting_ability = st.text_input(
            "Spellcasting Ability", 
            character_data.get("spellcasting_ability", ""), 
            key=f"spellcasting_ability_input_{uuid4()}"
        )
        
        spell_save_dc = st.text_input(
            "Spell Save DC", 
            character_data.get("spell_save_dc", ""), 
            key=f"spell_save_dc_input_{uuid4()}"
        )
        
        spell_attack_bonus = st.text_input(
            "Spell Attack Bonus", 
            character_data.get("spell_attack_bonus", ""), 
            key=f"spell_attack_bonus_input_{uuid4()}"
        )

        return {
            "spellcasting_class": spellcasting_class,
            "spellcasting_ability": spellcasting_ability,
            "spell_save_dc": spell_save_dc,
            "spell_attack_bonus": spell_attack_bonus
        }

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

# Set the page configuration at the very top of the script
st.set_page_config(page_title="D&D Character Creator", page_icon="📈")

# Placeholders for all user inputs
placeholders = {
    "name": st.empty(),
    "description": st.empty(),
    "basic_information": st.empty(),
    "personality_and_backstory": st.empty(),
    "abilities_and_skills": st.empty(),
    "equipment_and_treasures": st.empty(),
    "spellcasting": st.empty()
}

# Placeholders for the generated sections
character_placeholder = st.empty()
portrait_placeholder = st.empty()
save_button_placeholder = st.empty()

def main():
    """
    Main function for the Streamlit app.
    """
    st.markdown("# D&D Character Creator")
   
    character = st.session_state.character 

    # Initial user input using placeholders
    character["name"] = placeholders["name"].text_input("Character Name", character.get("name", ""))
    character["description"] = placeholders["description"].text_area("Description", character.get("description", ""))

    # Collect user's input for the other sections
    character.update(input_basic_information(placeholders["basic_information"], character))
    character.update(input_personality_and_backstory(placeholders["personality_and_backstory"], character))
    character.update(input_abilities_and_skills(placeholders["abilities_and_skills"], character))
    character.update(input_equipment_and_treasures(placeholders["equipment_and_treasures"], character))
    character.update(input_spellcasting(placeholders["spellcasting"], character))    

    # Check if user wants to generate a character sheet
    if st.button("Generate Character Sheet"):
        # Fetch filled out character data from the API
        generated_data = get_character_data(character)
        character_data = transform_to_dict(generated_data)
        character.update(character_data)

        # Update placeholders with generated data
        character["name"] = placeholders["name"].text_input("Character Name", character['name'], key=f"character_name_input_{uuid4()}")
        character["description"] = placeholders["description"].text_area("Description", character['description'], key=f"character_description_input_{uuid4()}")
        character.update(input_basic_information(placeholders["basic_information"], character))
        character.update(input_personality_and_backstory(placeholders["personality_and_backstory"], character))
        character.update(input_abilities_and_skills(placeholders["abilities_and_skills"], character))
        character.update(input_equipment_and_treasures(placeholders["equipment_and_treasures"], character))
        character.update(input_spellcasting(placeholders["spellcasting"], character))
        
        # Generate portrait prompts and portraits
        num_portraits = st.slider("Number of Portraits", 1, 5)
        portrait_filenames = []
        for _ in range(num_portraits):
            portrait_prompt = character.get("portrait_prompt", "")
            
            # Check if portrait_prompt is empty
            if not portrait_prompt:
                st.write("No portrait prompt provided. Skipping portrait generation.")
                continue
            
            portrait_filenames.append(generate_portrait(portrait_prompt))
        for filename in portrait_filenames:
            portrait_placeholder.image(filename, caption=f"Portrait of {character['name']}", use_column_width=True)

        # Create PDF character sheet and save
        pdf_filename = create_pdf_character_sheet(character, portrait_filenames)

        # Display the saved locations to the user
        st.write(f"Character sheet saved as {pdf_filename}")
        st.markdown(f"[Click here to download the character sheet]({pdf_filename})") 

if __name__ == "__main__":
    main()
