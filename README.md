# valorant-team-randomizer
A smart, map-aware team composition generator for Valorant with built-in role history tracking.
# 🎯 Valorant Team Randomiser

A sleek, map-aware web application built with Python and Streamlit, designed to generate strategically viable team compositions for your daily Valorant games. 

It balances completely randomized fun with logical layout guardrails to ensure your friend group gets an exciting, unrepeated gaming experience every single match.

---

## ✨ Key Features

* **🗺️ Map-Aware Comp Logic:** Automatically limits the available Controller pools depending on the selected map (e.g., handling open fields on Breeze vs tight sites on Ascent).
* **🔄 Anti-Repeat Role Tracking:** Remembers what role category each player locked in during their last match to actively prevent someone from getting stuck on smoke duty back-to-back.
* **🃏 Advanced Tactical Triggers:** 
  * If the primary Initiator rolls **Breach**, the app forces a secondary info/scanning initiator.
  * If the primary Duelist rolls **Yoru**, the app automatically forces a secondary duelist buddy for site execution support.
* **🛡️ Smart Sentinel Divisions:** Separates Sentinels into **Hold** and **Backstab** sub-pools to guarantee at least one flank anchor on every layout.
* **🎰 Single-Agent Individual Re-rolls:** If a friend doesn't own or want a specific character, roll them a replacement within that exact same category without shifting anyone else's picks.
* **🔒 Strict History Locking:** A dedicated confirmation pipeline ensures only finalized, accepted team compositions get recorded into the tracking database.

---

## 📂 Project Structure

```text
Valorant_Randomizer/
├── data.json         # Stores all character sub-pools, competitive match pools, and map criteria
├── main.py          # The primary Streamlit visual engine and calculation script
├── requirements.txt # Deployment installation instruction log for cloud servers
└── README.md        # This instruction guide page
```

---

## 🛠️ Local Installation & Development

If you want to run this application locally on your laptop:

1. Make sure you have **Python** installed.
2. Open your terminal or command prompt and install the dependencies:
   ```bash
   pip install streamlit
   ```
3. Navigate to the project directory and launch the Streamlit engine:
   ```bash
   python -m streamlit run main.py
   ```

---

## 🚀 Web Deployment

This project is optimised to run as a free live web app using the **Streamlit Community Cloud** pipeline linked directly to this repository. You can share the resulting URL with your Discord server so friends can review or cycle their agents on their phones or browsers.

*GLHF in your matches!* 🎮
