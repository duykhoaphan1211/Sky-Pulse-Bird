# Sky Pulse Bird

A game created **100% by AI** is an upgraded version of Flappy Bird featuring new mechanics, modes, bosses, and even a hidden **EASTER EGG** that appears when you press the **3 and 6** keys while not in a level!

Chatbots like Gemini or ChatGPT can be used to analyze the game to understand shortcuts, mechanics,...

Need 2 dependence libraries: [**Pygame-ce**](https://pypi.org/project/pygame-ce/) & [**Numpy**](https://pypi.org/project/numpy/)

# Minimum Requirements

- OS: **Windows 10 & newer**, MacOS and Linux: I don't know about them.
- Computer Architecture: **64-bit (x64).**

# Set Up (FOR WINDOWS USERS, STILL work on OTHER OS, but I only use Windows):
- Install Python: [3.14.4](https://www.python.org/ftp/python/3.14.4/python-3.14.4-amd64.exe)
- (Search) and Go to **"Command Prompt"** software and type: **pip install pygame-ce** and press Enter, then **pip install numpy** and press Enter.
- Download the .py file: [Sky Pulse Bird](https://github.com/duykhoaphan1211/Sky-Pulse-Bird/blob/main/sky_pulse_bird_fix_legendary.py)
- Open it by double left-click or right-click, then go to "Open with" and select **"Python"** software.
- Play the game!

# Sky Pulse Bird

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.14.4-blue">
  <img alt="pygame-ce" src="https://img.shields.io/badge/pygame--ce-compatible-2ea44f">
  <img alt="numpy" src="https://img.shields.io/badge/numpy-used-4d77cf">
  <img alt="Mode" src="https://img.shields.io/badge/Arcade%20%2B%20Boss%20%2B%20HELL-3%20modes-ff8c42">
  <img alt="Resolution" src="https://img.shields.io/badge/960×540-60%20FPS-8a63d2">
</p>

<p align="center">
  <b>Sky Pulse Bird</b> is a fast-paced 2D flight game with dodge-based gameplay, skins, items, quests, achievements, boss fights, and persistent progression.
</p>

---

## Table of Contents

- [Overview](#overview)
- [Controls](#controls)
- [Game Modes](#game-modes)
- [Difficulty](#difficulty)
- [Items & Power-Ups](#items--power-ups)
- [Skins](#skins)
- [Bosses](#bosses)
- [Quests & Achievements](#quests--achievements)
- [Progression & Save Data](#progression--save-data)
- [Tips for New Players](#tips-for-new-players)
---

## Overview

Sky Pulse Bird is a compact but content-rich arcade flight game focused on timing, reflexes, and progression. You control a bird, avoid pipes, collect items, survive as long as possible, and challenge bosses in a separate battle mode. The game includes multiple visual themes, unlockable skins, daily and weekly quests, achievements, and automatic save support.

### Key Features

| Feature | Description |
|---|---|
| Core gameplay | Fly, dodge pipes, collect coins and items, and keep your rhythm stable |
| Game modes | Arcade and Boss |
| Difficulty levels | Easy, Normal, Hard, Insane |
| Progression | Coins, skin unlocks, quests, achievements, best scores |
| Boss fights | Multi-phase bosses with unique projectile patterns and effects |
| Visuals | Animated backgrounds, theme variation, polished FX |
| Save system | Automatic saving for progress, skins, quests, achievements, and scores |

---

## Controls

| Action | Key / Input |
|---|---|
| Flap / fly upward | `Space` / `Up Arrow` / Mouse Click |
| Confirm / select | `Enter` |
| Back / cancel | `Esc` |
| Navigate menus | `Arrow Keys` / `A-D` / `W-S` |
| Switch profile tabs | `1` `2` `3` |
| Open / close selection screens | Click the corresponding buttons |

---

## Game Modes

| Mode | Description | Best For |
|---|---|---|
| **Arcade** | Standard mode where you dodge pipes, score points, and collect items while surviving as long as possible | Practice, coin farming, quest completion |
| **Boss** | A dedicated boss battle mode with HP, phases, and unique attacks | Challenge runs, boss wins, higher rewards |
| **HELL** | A special high-intensity boss experience with the harshest pressure | Experienced players only |

### Reward Structure
- Arcade rewards depend on the run result and difficulty.
- Boss mode grants rewards based on difficulty and boss selection.
- HELL offers the highest pressure and the biggest rewards.

---

## Difficulty

| Difficulty | Gravity | Flap Strength | Pipe Speed | Gap Size | Pipe Frequency | Power-Up Rate | Boss HP | Wind | Background Speed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Easy | 1350 | -430 | 220 | 190 | 1.62 | 0.26 | 6 | 10 | 26 |
| Normal | 1500 | -440 | 250 | 165 | 1.40 | 0.20 | 8 | 16 | 33 |
| Hard | 1650 | -452 | 285 | 142 | 1.20 | 0.15 | 10 | 24 | 40 |
| Insane | 1860 | -454 | 336 | 118 | 0.95 | 0.08 | 13 | 36 | 49 |

### What These Mean
- Higher gravity makes the bird fall faster.
- Stronger flap values give more lift, but require tighter timing.
- Faster pipes demand quicker reactions.
- Smaller gaps and denser pipe spawns make survival harder.
- Power-ups appear less often at higher difficulty levels.

---

## Items & Power-Ups

| Item | Effect | Duration / Behavior |
|---|---|---|
| **Coin** | Adds currency immediately when collected | Usually +10 coins per coin, can be multiplied |
| **Shield** | Gives temporary protection | Easy 7.0s, Normal 6.5s, Hard/Insane 6.0s |
| **Magnet** | Pulls nearby items toward the bird | Easy 5.8s, Normal 5.4s, Hard/Insane 5.0s |
| **Multiplier** | Multiplies coin and score rewards | Easy 6.5s, Normal 6.0s, Hard/Insane 5.5s |
| **Core** | Appears in boss fights only | Deals 1 damage to the boss |

### Spawn Rates by Difficulty

| Difficulty | Coin | Magnet | Shield | Multiplier |
|---|---:|---:|---:|---:|
| Easy | 0.32 | 0.26 | 0.18 | 0.24 |
| Normal | 0.33 | 0.25 | 0.16 | 0.26 |
| Hard | 0.34 | 0.24 | 0.15 | 0.27 |
| Insane | 0.35 | 0.23 | 0.14 | 0.28 |

### Notes
- Shield and Invulnerability are shown on the HUD when active.
- Core is a combat item used to damage bosses, not a farming item.
- Every power-up has its own visual effect for clarity and feedback.

---

## Skins

Skins are cosmetic only. They change the bird’s appearance and visual style, and they are unlocked with coins.

| # | Skin | Price | FX Style |
|---:|---|---:|---|
| 1 | CLASSIC | 0 | CLASSIC |
| 2 | NEON | 80 | NEON |
| 3 | AQUA | 90 | AQUA |
| 4 | MINT | 100 | MINT |
| 5 | CHERRY | 110 | CHERRY |
| 6 | LAGOON | 120 | LAGOON |
| 7 | EMBER | 130 | EMBER |
| 8 | SHADOW | 140 | SHADOW |
| 9 | VIOLET | 150 | VIOLET |
| 10 | ROSE | 160 | ROSE |
| 11 | CRYSTAL | 180 | CRYSTAL |
| 12 | SOLAR | 200 | SOLAR |
| 13 | LAVA | 220 | LAVA |
| 14 | AURORA | 240 | AURORA |
| 15 | PIXEL | 260 | PIXEL |
| 16 | FROST | 280 | FROST |
| 17 | STEEL | 300 | STEEL |
| 18 | GHOST | 320 | GHOST |
| 19 | PRISM | 340 | PRISM |
| 20 | CYBER | 360 | CYBER |
| 21 | GALAXY | 380 | GALAXY |
| 22 | VOID | 400 | VOID |
| 23 | ROYAL | 420 | ROYAL |
| 24 | SAND | 440 | SAND |
| 25 | CORAL | 460 | CORAL |

### Skin Recommendations
- For clean readability: CLASSIC, NEON, AQUA, FROST.
- For flashy effects: EMBER, VOID, PRISM, CYBER, GALAXY.
- For premium vibes: ROYAL, AURORA, CORAL.

---

## Bosses

Bosses have HP, multiple phases, and attack families with their own shapes and effects. The game includes 16 major bosses plus a special HELL boss variant.

| Boss | Short Name | Attack / Art Style | Overview |
|---|---|---|---|
| Aegis Core | Aegis | shield / aegis | Defensive opening boss with stable pressure |
| Tempest | Tempest | wind / tempest | Wind-like patterns and lane pressure |
| Void Regent | Void | void / void | Dark, tricky, and unpredictable |
| Chrono Bastion | Chrono | time / chrono | Time-based movement and rotating hazards |
| Prism Nexus | Prism | prism / prism | Refraction-style visual attacks |
| Verdant Bloom | Bloom | bloom / bloom | Organic pressure and growth-themed patterns |
| Ember Warden | Ember | fire / ember | Heat-based hazard boss |
| Tide Oracle | Tide | wave / tide | Water-like wave arcs and flow pressure |
| Frost Citadel | Frost | ice / frost | Cold, sharp, and timing-heavy |
| Stellar Forge | Stellar | star / stellar | Cosmic bursts and star-shaped attacks |
| Obsidian Seraph | Obsidian | dark / obsidian | Heavy dark geometry and dense pressure |
| Aurora Heart | Aurora | light / aurora | Smooth glowing patterns and elegant movement |
| Nova Crown | Nova | burst / nova | Fast explosive star pressure |
| Rift Monarch | Rift | rift / rift | Space-tearing attack patterns |
| Thorn Sovereign | Thorn | thorn / thorn | Sharp, branching hazard lines |
| Sentinel Prism | Sentinel | sentinel / sentinel | Defensive ring-based boss with clean geometry |
| HELL | HELL | ember / ember | Special extreme boss variant |

### Boss Behavior
- Bosses progress through 3 phases:
  - Phase 2 below 66% HP
  - Phase 3 below 33% HP
- Each phase increases pressure, speed, or attack density.
- Boss projectiles are designed to avoid completely blocking the play lane.
- The HELL encounter is the hardest version, with the most intense pacing and effects.

### Boss Rewards
- Boss clears grant coin rewards based on difficulty.
- Standard bosses reward more as their index and difficulty rise.
- HELL grants the largest special reward.

---

## Quests & Achievements

### Quests

The game includes both **daily** and **weekly** quests. They are generated from a fixed pool and tracked by date and week.

| Type | Quest Name | Objective | Reward |
|---|---|---|---:|
| Daily | Pipe Sweep | Score a target number of pipes | 45–70 |
| Daily | Coin Pulse | Collect coins | 45–80 |
| Daily | Sky Rhythm | Flap a target number of times | 40–75 |
| Daily | Supply Run | Collect items | 50–85 |
| Daily | Long Glide | Play for a set amount of time | 45–80 |
| Daily | Shield Drill | Block hits with a shield | 55–90 |
| Weekly | Boss Breaker | Defeat bosses | 140–220 |
| Weekly | Core Pressure | Deal boss damage | 130–210 |
| Weekly | Road Worker | Finish runs | 120–190 |
| Weekly | Clean Flight | Win runs | 150–230 |
| Weekly | Legend Lane | Score a total number of pipes | 150–240 |
| Weekly | Rare Supply | Collect rare items | 140–220 |
| Weekly | Endurance Run | Play for a long time | 150–240 |

### Achievements

| Achievement | Requirement |
|---|---|
| First Flight | Flap once |
| Airborne | Play for 90 seconds |
| Pipe Ace | Score 25 pipes |
| Coin Hoard | Collect 250 coins |
| Item Lover | Collect 40 items |
| Shield Guard | Block 4 hits with shields |
| Boss Breaker | Defeat 1 boss |
| Boss Master | Defeat 4 bosses |
| Hard Fighter | Defeat a boss on Hard |
| Daily Runner | Complete 3 daily quests |
| Weekly Champ | Complete 3 weekly quests |
| Veteran | Finish 20 runs |
| Sky Runner | Finish 5 runs |
| Pipe Veteran | Score 100 pipes |
| Coin Collector | Collect 1000 coins |
| Combo Spark | Reach a combo of 10 |
| Marathon | Play for 600 seconds |
| Boss Hunter | Defeat 10 bosses |
| Hard Conqueror | Defeat 3 bosses on Hard |
| Quest Legend | Complete 10 daily quests |

---

## Progression & Save Data

| Saved Data | What It Stores |
|---|---|
| Skins | Current skin and unlocked skins |
| Difficulty | Last selected difficulty |
| Coins | Current coin total |
| Best scores | Best score per mode / difficulty |
| Sound | Audio on/off state |
| Boss | Last selected boss |
| Profile totals | Total runs, wins, deaths, combos, quests, boss damage, and more |
| Achievements | Unlocked achievement list |
| Quest state | Daily / weekly quest progress |
| Last run summary | Summary of the most recent run |
| UI state | Profile tab, achievement view, hitbox visibility |

### Main Profile Stats
- Runs
- Wins
- Boss wins
- Boss wins on Hard
- Deaths
- Flaps
- Pipes scored
- Coins collected
- Items collected
- Shield breaks
- Boss damage dealt
- Play time
- Daily quests completed
- Weekly quests completed
- Max score
- Best combo

---

## Tips for New Players

1. Do not hold the flap button too long. Short, controlled taps are more stable.
2. In Arcade mode, survival matters more than raw speed at first.
3. Shield is extremely useful while you are learning pipe timing.
4. Magnet helps collect items more safely, especially in coin-heavy runs.
5. Multiplier is one of the best tools for farming coins efficiently.
6. In boss fights, learn the phase change before pushing damage aggressively.
7. If a lane feels too tight, reset your rhythm instead of spamming flaps.
8. Unlock cheaper skins first so you can have more visual variety without long grinding.
