import streamlit as st

# Set page config
st.set_page_config(
    page_title="PlotPixie 🧙‍♂️✨",
    page_icon="🧙‍♂️✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
st.sidebar.title("PlotPixie 🧙‍♂️✨")
st.sidebar.write("Your AI D&D assistant.")
st.sidebar.success("Select a dungeon master's assistant above.")

st.write("# Welcome to PlotPixie! 🧙‍♂️✨")

# D&D Character Creator App
st.subheader("D&D Character Creator App")
st.write("""
- 🧝‍♀️ **Choose Your Race:** From Elves to Dwarves, select from a plethora of races to  kickstart your journey.
- ⚔️ **Select Your Class:** Be it a valiant Paladin or a cunning Rogue, choose a class that resonates with your inner hero.
- 🎭 **Craft Your Backstory:** Every hero has a tale. Forge your character's backstory, traits, etc. with our intuitive tool.
- 📜 **Character Sheet (PDF):** Once your choices are made, get a complete character sheet PDF for your newly minted character.
""")


# Hackathon Mention
st.subheader("PlotPixie at Streamlit Hackathon 2023")
st.write("""
We're thrilled to unveil PlotPixie as our contender for the Streamlit Hackathon 2023. Our aim is to harness the potential of Streamlit to deliver intuitive and engaging tools tailored for the D&D community. By blending cutting-edge technology with the timeless allure of dungeons and dragons, we aspire to make a useful contribution to the world of tabletop gaming.
""")

# Upcoming Features
st.subheader("Coming Soon to PlotPixie 📅")
st.write("""
    - **D&D Encounter Creator:** Design intricate encounters, fine-tune your challenges, and guarantee every session is unforgettable.
    - **Talk with a D&D Character:** Fancy some role-playing practice or just a friendly chat? Soon, you'll have the chance to interact with AI-driven D&D personas.
    - **Upgrade to GPT-4 API:** For enthusiasts seeking a deeper dive, we're introducing a premium option to harness the capabilities of GPT-4.
    - **Fine tune ChatGPT to further improve character sheet generation**
    - **... and more!** We're ceaselessly concocting novel features to enchant both dungeon masters and adventurers. Stay with us for more!
    """
)


