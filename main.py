import streamlit as st
import json
import os
import random

# Ensure styling looks clean and modern
st.set_page_config(page_title="Valorant Team Randomizer", layout="wide")

# 1. LOAD THE JSON DATABASE FILE
DATA_FILE = "data.json"

@st.cache_data
def load_game_data():
    """Loads and caches the map data so it doesn't read the disk on every click."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        st.error(f"Could not find '{DATA_FILE}'! Please make sure it is in your project folder.")
        return None

VALORANT_DATA = load_game_data()

# ----------------------------------------------------
# 4. ALGORITHMIC FUNCTIONS (The 9 Composition Rules)
# ----------------------------------------------------
def generate_team_composition(map_name):
    """Generates a valid 5-agent composition following all 9 rules."""
    if not VALORANT_DATA:
        return None
        
    # We attempt up to 100 times to guarantee a valid combination without duplicates
    for _ in range(100):
        team = []
        picked_agents = set()
        
        # Rule 1: Slot 1 - Controller (Map Specific)
        map_rules = VALORANT_DATA.get("map_rules", {})
        ctrl_pool = map_rules.get(map_name, {}).get("Controller", [])
        if not ctrl_pool:
            continue
        controller = random.choice(ctrl_pool)
        team.append({"agent": controller, "role": "Controller"})
        picked_agents.add(controller)
        
        # Rule 1 & 2: Slot 2 - Sentinel Backstab
        sb_pool = [a for a in VALORANT_DATA["characters"]["Sentinel (Backstab)"] if a not in picked_agents]
        if not sb_pool: 
            continue
        sentinel_b = random.choice(sb_pool)
        team.append({"agent": sentinel_b, "role": "Sentinel"})
        picked_agents.add(sentinel_b)
        
        # Rule 1: Slot 3 - Primary Initiator
        # Pulls from either standard Initiator or the specialized Breach pool
        full_init_pool = VALORANT_DATA["characters"]["Initiator"] + VALORANT_DATA["characters"]["Initiator (Stun)"]
        i_pool = [a for a in full_init_pool if a not in picked_agents]
        if not i_pool: 
            continue
        initiator = random.choice(i_pool)
        team.append({"agent": initiator, "role": "Initiator"})
        picked_agents.add(initiator)
        
        # Rule 1: Slot 4 - Primary Duelist
        d_pool = [a for a in VALORANT_DATA["characters"]["Duelist"] if a not in picked_agents]
        if not d_pool: 
            continue
        duelist = random.choice(d_pool)
        team.append({"agent": duelist, "role": "Duelist"})
        picked_agents.add(duelist)
        
        # Rule 3: Slot 5 (The Flex Slot Resolution)
        flex_pool = []
        flex_role = ""
        
        # Rule 6: If primary initiator was Breach (Stun), flex must be a Scan/Info Initiator
        if initiator == "Breach":
            flex_pool = [a for a in VALORANT_DATA["characters"]["Initiator"] if a not in picked_agents]
            flex_role = "Initiator"
            
        # Rule 7: If duelist is Yoru, flex must be another Duelist
        elif duelist == "Yoru":
            flex_pool = [a for a in VALORANT_DATA["characters"]["Duelist"] if a not in picked_agents]
            flex_role = "Duelist"
            
        # Rule 8: Double smoke on specific maps if controller is Viper or Harbor
        elif map_name in ["Breeze", "Icebox", "Pearl"] and controller in ["Viper", "Harbor"]:
            # Pull a traditional dome controller
            dome_pool = ["Astra", "Clove", "Miks", "Omen"]
            flex_pool = [a for a in dome_pool if a not in picked_agents]
            flex_role = "Controller"
            
        # Rule 3 Default: Flex rolls either a 2nd Duelist or a Sentinel (Hold)
        else:
            chosen_type = random.choice(["Duelist", "Sentinel (Hold)"])
            flex_pool = [a for a in VALORANT_DATA["characters"][chosen_type] if a not in picked_agents]
            flex_role = "Duelist" if chosen_type == "Duelist" else "Sentinel"
            
        if not flex_pool: 
            continue
            
        flex_agent = random.choice(flex_pool)
        # Rule 9: No duplicate agents
        team.append({"agent": flex_agent, "role": flex_role})
        return team
        
    return None

def assign_team_to_players(team, players):
    """Distributes the 5 rolled agents to friends respecting anti-repeat role history."""
    history = st.session_state.role_history
    
    # Try up to 100 random shuffles to satisfy the anti-repeat constraint
    for _ in range(100):
        random.shuffle(players)
        valid_assignment = True
        assignment = {}
        
        for i, player in enumerate(players):
            agent_info = team[i]
            # Verify if this player played this exact role category last game
            if history.get(player) == agent_info["role"]:
                valid_assignment = False
                break
            assignment[player] = {
                "agent": agent_info["agent"],
                "role": agent_info["role"]
            }
            
        if valid_assignment:
            return assignment
            
    # Safety Net: If history rules make assignment mathematically impossible,
    # we bypass the history logic for this match so the page doesn't freeze.
    assignment = {}
    for i, player in enumerate(players):
        agent_info = team[i]
        assignment[player] = {
            "agent": agent_info["agent"],
            "role": agent_info["role"]
        }
    return assignment

# 2. INITIALIZE SESSION STATE MEMORY BLOCKS
if "current_team" not in st.session_state:
    st.session_state.current_team = None  # Holds the currently rolled 5-agent team

if "role_history" not in st.session_state:
    st.session_state.role_history = {}  # Tracks what role category each player rolled last match

# 3. BUILD THE SIDEBAR FOR PLAYER NAMES
st.sidebar.header("👤 Friend Group Setup")
st.sidebar.write("Enter the names of the 5 players:")

player_names = []
for i in range(5):
    name = st.sidebar.text_input(f"Player {i+1}", value=f"Player {i+1}", key=f"player_in_{i}")
    player_names.append(name.strip())

# Add space between inputs and buttons
st.sidebar.write("")

# The existing Reset Button
if st.sidebar.button("🔄 Reset Role History", use_container_width=True):
    st.session_state.role_history = {}
    st.sidebar.success("Role history cleared!")

# --- NEW POP-UP LOGIC STARTS HERE ---

# 1. Define the Pop-up Window content
@st.dialog("📋 Current Role History")
def show_history_popup():
    history = st.session_state.role_history
    if not history:
        st.write("🕊️ No matches recorded yet! Everyone's history is fresh.")
    else:
        st.write("Here is the role category each player locked in during their last match:")
        
        # Define matching emojis for the pop-up list
        emoji_map = {
            "Controller": "☁️ Controller",
            "Duelist": "⚔️ Duelist",
            "Sentinel": "🛡️ Sentinel",
            "Initiator": "👁️ Initiator"
        }
        
        # Display each player and their last played role
        for p_name, role in history.items():
            display_role = emoji_map.get(role, role)
            st.markdown(f"👤 **{p_name}** last played:  {display_role}")
            
    st.write("---")
    if st.button("Close"):
        st.rerun()

# 2. Draw the View History Button on the Sidebar
if st.sidebar.button("📊 View Last Roles", use_container_width=True):
    show_history_popup()

# --- NEW POP-UP LOGIC ENDS HERE ---

# 4. BUILD THE MAIN PANEL HEADER
st.title("🎯 VALORANT TEAM RANDOMIZER")
st.write("A map-aware, smart team picker that makes sure you never repeat roles back-to-back.")

# Display the map selector using the matchpool inside data.json
if VALORANT_DATA:
    matchpool = VALORANT_DATA.get("current_matchpool", [])
    
    st.subheader("🗺️ Select Upcoming Map")
    chosen_map = st.selectbox("Which map are you playing next?", options=matchpool)
    
    st.write(f"You have selected: **{chosen_map}**")

# ----------------------------------------------------
# 5. SINGLE-AGENT INDIVIDUAL RE-ROLL ENGINE
# ----------------------------------------------------
    def reroll_single_agent(player_name, role_category, current_team_dict):
        """Finds a replacement agent of the exact same role category who isn't already taken."""
        if not VALORANT_DATA:
            return
            
        # Figure out the correct character pool to draw from based on the role category
        if role_category == "Controller":
            # Must respect map rules for controllers
            map_rules = VALORANT_DATA.get("map_rules", {})
            pool = map_rules.get(chosen_map, {}).get("Controller", [])
        elif role_category == "Duelist":
            pool = VALORANT_DATA["characters"]["Duelist"]
        elif role_category == "Sentinel":
            # Draw from both Sentinel sub-pools
            pool = VALORANT_DATA["characters"]["Sentinel (Hold)"] + VALORANT_DATA["characters"]["Sentinel (Backstab)"]
        elif role_category == "Initiator":
            # Draw from both Initiator sub-pools
            pool = VALORANT_DATA["characters"]["Initiator"] + VALORANT_DATA["characters"]["Initiator (Stun)"]
        else:
            pool = []

        # Find out which agents are currently sitting on the team so we avoid duplicates
        taken_agents = {info["agent"] for p_name, info in current_team_dict.items() if p_name != player_name}
        
        # Filter the pool for valid options
        available_options = [agent for agent in pool if agent not in taken_agents]
        
        if available_options:
            new_agent = random.choice(available_options)
            # Update the agent in place inside our permanent session state memory
            st.session_state.current_team[player_name]["agent"] = new_agent
            st.success(f"Swapped agent for {player_name}!")
        else:
            st.warning(f"No other non-duplicate {role_category}s available!")

    # ----------------------------------------------------
    # 6. MAIN PANEL UI & ROLL INTERACTION
    # ----------------------------------------------------
    
    # Track if a brand new roll just occurred to clear locking states
    if st.button("🎲 ROLL TEAM COMPOSITION", type="primary", use_container_width=True):
        base_comp = generate_team_composition(chosen_map)
        
        if base_comp:
            assigned_team = assign_team_to_players(base_comp, player_names.copy())
            st.session_state.current_team = assigned_team
            st.session_state.team_locked = False  # Reset lock state for the new roll
        else:
            st.error("Could not generate a valid composition matching constraints. Check your JSON format.")

    # ----------------------------------------------------
    # 7. THE VISUAL RESULTS DASHBOARD & LOCK ENGINE
    # ----------------------------------------------------
    if st.session_state.current_team:
        st.subheader(f"🎯 Assigned Team for {chosen_map.upper()}")
        
        # Create a header row using columns for a clean table look
        h_col1, h_col2, h_col3, h_col4 = st.columns(4)
        h_col1.markdown("**👤 Player**")
        h_col2.markdown("**🎭 Agent**")
        h_col3.markdown("**🛡️ Category**")
        h_col4.markdown("**🔄 Action**")
        st.write("---")
        
        emoji_map = {
            "Controller": "☁️ Controller",
            "Duelist": "⚔️ Duelist",
            "Sentinel": "🛡️ Sentinel",
            "Initiator": "👁️ Initiator"
        }
        
        # Loop through our stored team data and print out one visual row per friend
        for p_name, info in st.session_state.current_team.items():
            col1, col2, col3, col4 = st.columns(4)
            
            display_role = emoji_map.get(info['role'], info['role'])
            
            col1.write(p_name)
            col2.markdown(f"**{info['agent']}**")
            col3.write(display_role)
            
            # Disable individual re-rolls once the team is locked in place
            is_disabled = st.session_state.get("team_locked", False)
            
            if col4.button("Re-roll", key=f"btn_{p_name}", disabled=is_disabled):
                reroll_single_agent(p_name, info["role"], st.session_state.current_team)
                st.rerun()
                
        st.write("---")
        
        # The new Lock Button that officially commits the roles to history
        if not st.session_state.get("team_locked", False):
            if st.button("🔒 LOCK FINAL TEAM COMPOSITION", use_container_width=True):
                # Save only the absolute final roles on screen to history
                for p_name, info in st.session_state.current_team.items():
                    st.session_state.role_history[p_name] = info["role"]
                
                st.session_state.team_locked = True
                st.success("✅ Match lineup locked! Roles saved to history for the next round.")
                st.rerun()
        else:
            st.info("🔒 This team is locked and recorded. Good luck with your match! Click 'Roll Team Composition' above when you are ready for the next game.")
