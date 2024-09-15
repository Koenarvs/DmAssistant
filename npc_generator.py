import random
import json
import os
from openai import OpenAI
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load data from JSON file
with open('npc_generation_ellium.json', 'r') as file:
    data = json.load(file)

classes_subclasses = data["classes_subclasses"]
backgrounds_traits = data["backgrounds_traits"]
background_info_default = data["background_info_default"]
appearance_traits = data["appearance_traits"]
languages = data["languages"]
backstories = data["backstories"]
roles_in_world = data["roles_in_world"]
deities_data = data["deities"]
factions = data["factions"]
alignments = data["alignments"]

def sample(lst, k=1):
    """Emulates _.sample from Underscore.js."""
    if k > 1:
        return random.sample(lst, k)
    return random.choice(lst)

def generate_personality(background):
    background_info = backgrounds_traits.get(background, background_info_default)
    
    personality_traits = sample(background_info["personality_traits"], k=2)
    ideals = background_info["ideals"]
    bonds = background_info["bonds"]
    flaws = background_info["flaws"]
    
    return personality_traits, ideals, bonds, flaws

def select_class_and_subclass(race):
    """Selects a class and an appropriate subclass based on race restrictions."""
    available_classes = list(classes_subclasses.keys())
    random.shuffle(available_classes)  # Shuffle to ensure randomness

    for cls in available_classes:
        subclasses = classes_subclasses[cls]
        # Filter subclasses that allow the given race
        valid_subclasses = [sub for sub, races in subclasses.items() if race in races]
        if valid_subclasses:
            selected_subclass = sample(valid_subclasses)
            return cls, selected_subclass
    return None, None  # No valid class found for the race

def generate_faction():
    """Randomly assigns a faction to the NPC with a 50% chance."""
    if random.random() < 0.5:
        return sample(factions)["name"]
    return "None"

def generate_deity_aspect():
    """Selects a deity aspect from the JSON data."""
    deity_choice = sample(list(deities_data.keys()))
    
    if deity_choice == "Other Deities":
        other_deities = deities_data["Other Deities"]
        deity_sub_choice = sample(list(other_deities.keys()))
        if deity_sub_choice == "None":
            return "None"
        deity_info = other_deities[deity_sub_choice]
        aspect = sample(deity_info.get("aspects", []))
        return aspect
    elif deity_choice == "None":
        return "None"
    else:
        deity_info = deities_data[deity_choice]
        aspect = sample(deity_info.get("aspects", []))
        return aspect

def generate_npc():
    randrace = ["human", "dwarf", "elf", "tabaxi", "halfelf"]
    randgender = ["male", "female"]
    
    race = sample(randrace)
    gender = sample(randgender)
    
    # Determine if NPC has a class or 'N/A' (80%-90% 'N/A')
    if random.random() < 0.85:  # 85% chance to have class 'N/A'
        npc_class = "N/A"
    else:
        # Select a class and subclass based on racial restrictions
        cls, subclass = select_class_and_subclass(race)
        if cls and subclass:
            npc_class = f"{cls} - {subclass}"
        else:
            npc_class = "N/A"  # Fallback if no subclass is available for the race
    
    age = str(random.randint(18, 100))
    
    # Generate name based on race using ChatGPT
    try:
        name = generate_name(race, gender)
    except Exception as e:
        logger.error(f"Error generating name via ChatGPT: {e}")
        name = "Unnamed NPC"
    
    # Generate background
    background = generate_background(race)
    
    # Generate appearance
    appearance = generate_appearance(race)
    
    # Generate languages
    npc_languages = ", ".join(sample(languages, k=random.randint(1,3)))
    
    # Generate personality traits, ideals, bonds, flaws
    personality_traits, ideals, bonds, flaws = generate_personality(background)
    
    # Generate backstory
    backstory = backstories.get(background, "I have a mysterious past that I rarely speak of.")
    
    # Generate role in world
    role_in_world = sample(roles_in_world)
    
    # Alignment is always 'N/A' initially, can be updated in future improvements
    alignment = "N/A"
    
    # Generate deity aspect
    deity_aspect = generate_deity_aspect()
    
    # Generate faction
    faction = generate_faction()
    
    # Image Path (placeholder, as automated image selection is complex)
    image_path = ""
    
    npc = {
        "name": name,
        "race": race.capitalize(),
        "class": npc_class,
        "gender": gender.capitalize(),
        "age": age,
        "appearance": appearance,
        "background": background,
        "languages": npc_languages,
        "personality_traits": "\n".join(personality_traits),
        "ideals": ideals,
        "bonds": bonds,
        "flaws": flaws,
        "backstory": backstory,
        "role_in_world": role_in_world,
        "alignment": alignment,
        "deity_aspect": deity_aspect,
        "faction": faction,
        "image_path": image_path
    }
    
    return npc

def generate_name(race, gender):
    """
    Generates a name based on race and gender using OpenAI's API (v1.0.0+).
    """
    if not client.api_key:
        raise ValueError("OpenAI API key is not set in environment variables.")

    # Define prompts based on race
    if race == "human":
        prompt = (f"Generate a {gender} human name that is culturally appropriate and sounds similar to names from "
                  f"Lord of the Rings, The Wheel of Time, or A Song of Fire and Ice with a clear Nordic/Viking influence.")
    elif race == "dwarf":
        prompt = (f"Generate a {gender} dwarf name in Tolkonian style.")
    elif race == "elf":
        prompt = (f"Generate a {gender} elf name in Tolkonian style based on the Quenya elven language.")
    elif race == "halfelf":
        prompt = (f"Generate a {gender} half-elf name that is either human or elven, or a creative mix of both.")
    elif race == "tabaxi":
        prompt = (f"Generate a {gender} Tabaxi name following the pattern 'Noun of the Adjective Noun', "
                  f"for example, 'Riddle of the Rising Peak'.")
    else:
        prompt = (f"Generate a {gender} name suitable for a {race} character in a high-fantasy setting.")

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in generating culturally and contextually appropriate fantasy names."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            n=1,
            temperature=0.7,
        )
        name = response.choices[0].message.content.strip()
        
        # Clean up the name if it includes quotes or other artifacts
        name = name.strip('"').strip("'")
        
        # For Tabaxi, ensure the name follows the specified pattern
        if race == "tabaxi":
            # Optionally, validate the format or regenerate if it doesn't match
            if " of the " not in name:
                logger.warning(f"Generated Tabaxi name does not match the required pattern: {name}. Regenerating.")
                return generate_name(race, gender)  # Recursive call to regenerate the name

        return name
    except Exception as e:
        logger.error(f"Error during OpenAI API call: {e}")
        raise

def generate_background(race):
    backgrounds = list(backgrounds_traits.keys())
    return sample(backgrounds)

def generate_appearance(race):
    selected_traits = sample(appearance_traits, k=3)
    return ", ".join(selected_traits)

# Example usage
if __name__ == "__main__":
    npc = generate_npc()
    print(json.dumps(npc, indent=2))