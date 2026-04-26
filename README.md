# Sky Pulse Bird
A game created 100% by AI is an upgraded version of Flappy Bird featuring new mechanics, modes, bosses, and even a hidden **EASTER EGG** that appears when you press the **3 and 6** keys while not in a level!

Chatbots like Gemini or ChatGPT can be used to analyze the game to understand shortcuts, mechanics,...

Need 2 dependence libraries: **Pygame-ce** & **Numpy!**

## SET UP:
- Install Python: [3.14.4](https://www.python.org/ftp/python/3.14.4/python-3.14.4-amd64.exe)
- Windows: Go to "Command Prompt" software and type: pip install pygame-ce and press Enter, then pip install numpy and press Enter.
- Download the .py file.
- Open it by double left-click or right-click, then go to "Open with" and select "Python" software.
- Play the game!

# Sky Pulse Bird — Beginner Guide (by ChatGPT)

**Sky Pulse Bird** is a flappy-style action game with a modern menu system, multiple difficulties, Arcade and Boss modes, a special HELL fight, skins, quests, achievements, and persistent save data. The game runs at **960×540** and targets **60 FPS**. It saves progress to a local JSON file next to the game script.  

---

## 1) What the game is

Your goal is simple at first, but it gets deeper fast:

- Stay in the air.
- Pass through pipe gaps.
- Collect items.
- Earn coins.
- Unlock skins, quests, and achievements.
- Beat bosses in Boss Mode.
- Survive the special HELL encounter.

The game is not just about score. It also has long-term progress, daily quests, weekly quests, achievements, and saved records.

---

## 2) Core idea in one sentence

You control a bird, keep it flying, avoid obstacles, collect helpful items, and try to survive as long as possible.

---

## 3) Controls

### Main gameplay
| Action | Keyboard | Mouse |
|---|---|---|
| Flap / jump | `Space`, `Up Arrow`, `W` | Left click |
| Pause | `P` or `Esc` | — |
| Restart after death / clear | `R` | Click Replay |
| Return to menu from Game Over / Clear | `Esc` | Click Menu |

### Global shortcuts
| Action | Key |
|---|---|
| Toggle sound | `M` |
| Toggle hitbox overlay | `H` |

### Menus
| Screen | Controls |
|---|---|
| Main menu | `Up/Down`, `W/S`, `Enter`, `Esc` |
| Play mode selection | `Left/Right`, `A/D`, `Up/Down`, `W/S`, `Enter`, `Esc` |
| Difficulty selection | `Left/Right`, `A/D`, `Up/Down`, `W/S`, `Enter`, `Esc` |
| Boss selection | `Left/Right`, `A/D`, `Up/Down`, `Enter`, `Esc` |
| Skins | `Left/Right`, `A/D`, `Enter`, `Esc` |
| Profile | `Left/Right`, `A/D`, `1`, `2`, `3`, `Space`, `Esc`, `Enter` |
| Options | `Up/Down`, `W/S`, `Enter`, `Esc` |

---

## 4) Main menu

The main menu has these items:

- **PLAY**
- **SKINS**
- **Profile**
- **OPTIONS**
- **QUIT**

### What each item does
| Menu item | Meaning |
|---|---|
| PLAY | Opens the mode selection screen |
| SKINS | Opens the skin browser |
| Profile | Opens stats, quests, and achievements |
| OPTIONS | Opens game settings |
| QUIT | Exits the game |

The menu is fully navigable with keyboard or mouse.

---

## 5) Play menu: choosing your game type

When you press **PLAY**, the game shows three mode cards:

| Mode | What it means |
|---|---|
| ARCADE | Standard endless-style flight with pipes, items, and scoring |
| BOSS | A boss fight version with selected difficulty and boss |
| HELL | A special extreme boss fight with the final boss preset |

### Important note
HELL is treated as a special fight. It is not part of the normal visible boss selection grid.

---

## 6) Difficulty levels

The game has four difficulty levels:

| Difficulty | Feel |
|---|---|
| EASY | Most forgiving |
| NORMAL | Balanced default |
| HARD | Much tighter and faster |
| INSANE | Very fast and very demanding |

### Difficulty changes in practice
As difficulty goes up:

- gravity becomes harsher,
- flap strength changes,
- pipes move faster,
- gaps become smaller,
- pipe spacing becomes shorter,
- helpful item spawn rate goes down,
- boss HP becomes higher,
- fights become more intense.

---

## 7) How to actually play

### Basic flow
1. Choose a mode.
2. Choose a difficulty.
3. If needed, choose a boss.
4. Start flying.
5. Pass through pipe gaps.
6. Collect items.
7. Avoid collisions.
8. Use power-ups wisely.
9. Survive as long as possible.

### What happens when you pass a pipe
Passing a pipe gives you:

- **+1 score**
- **+2 coins**
- **+1 pipe scored**
- **+1 combo**

Your best score is saved automatically.

---

## 8) Bird movement and survival basics

Your bird is always falling unless you keep flapping.

### What affects the bird
| System | Effect |
|---|---|
| Gravity | Pulls you downward |
| Flap | Launches the bird upward |
| Shield | Protects from one hit |
| Revive | Saves you from a fatal hit if you still have one |
| Invulnerability | Temporary safety after a hit |
| Boost | Short movement effect that helps during flight |

### Beginner rule
Do not spam flap randomly. Try to make small, steady corrections instead of big panic clicks.

---

## 9) Items and power-ups

Items are one of the most important systems in the game. They can appear in Arcade and in Boss battles.

| Item | What it does |
|---|---|
| Coin | Gives coins instantly |
| Shield | Gives a temporary shield |
| Revive | Adds one revive |
| Magnet | Pulls nearby items toward you |
| Boost | Gives a short boost effect |
| Multiplier | Activates a temporary bonus multiplier |
| Core | Boss-only damage item that removes 1 boss HP |

### Item details
| Item | Practical use |
|---|---|
| Coin | Good for buying skins and building progress |
| Shield | Best for recovery after risky movement |
| Revive | A second chance when a run goes bad |
| Magnet | Makes item collection easier without perfect positioning |
| Boost | Helps you survive tighter gaps or reposition quickly |
| Multiplier | Strong for coin farming and progress |
| Core | Essential in Boss Mode and HELL |

### Important boss-only item
In Boss Mode, **Core** items directly damage the boss. When the boss HP reaches zero, the boss phase ends and the fight can be cleared.

---

## 10) Arcade Mode

Arcade Mode is the standard mode.

### What to expect
- Pipes scroll from right to left.
- Gap positions are designed to stay playable.
- Some pipes may move slightly for variety.
- Items can spawn beside or near pipes.
- The background theme changes as your score increases.

### Arcade strategy for new players
- Keep your bird near the middle of the screen.
- Do not hug the bottom.
- Try to look ahead, not at the bird only.
- Learn the pipe rhythm first.
- Collect items only when the movement is safe.

---

## 11) Boss Mode

Boss Mode is the more tactical mode.

### What changes
- A boss appears.
- Boss HP must be reduced.
- Pipes are still present.
- Boss attacks create pressure through projectiles and tighter spacing.
- Boss phases become more demanding as the battle continues.

### Boss battle loop
1. Survive the pipes.
2. Collect Core items when they appear.
3. Damage the boss.
4. Watch the boss’s HP and phase.
5. Clear the fight once HP reaches zero.

### Boss selection
Boss Mode lets you choose from many named bosses such as:

- Aegis Core
- Tempest
- Void Regent
- Chrono Bastion
- Prism Nexus
- Verdant Bloom
- Ember Warden
- Tide Oracle
- Frost Citadel
- Stellar Forge
- Obsidian Seraph
- Aurora Heart
- Nova Crown
- Rift Monarch
- Thorn Sovereign
- Sentinel Prism

HELL is a special separate fight.

---

## 12) HELL Mode

HELL is the hardest special boss fight.

### What makes it special
- It is a boss fight built around extreme pressure.
- It uses the final boss preset.
- It is stronger and more punishing than normal bosses.
- It is meant as a high-skill challenge, not a casual run.

### Best mindset for HELL
- Focus on survival first.
- Do not chase every item if the movement becomes unsafe.
- Take the safest line through gaps.
- Learn the timing before trying aggressive plays.

---

## 13) Scoring, coins, and combo

### Score
Your score increases every time you pass a pipe.

### Coins
Coins are earned from:

- passing pipes,
- collecting coin items,
- rewards from some run outcomes,
- quests and other progression systems.

### Combo
Combo increases when you keep passing pipes successfully in a row.

### Why combo matters
A high combo is a sign of consistency. It is also tied to at least one achievement in the game.

---

## 14) Health, shield, and revives

| System | What it means |
|---|---|
| Shield | Blocks one hit and then disappears |
| Revive | Gives you another chance after a fatal hit |
| Invulnerability | Brief safety window after damage |

### What happens on a hit
- If you have a shield, the shield breaks instead of ending the run.
- If you have a revive, the revive is consumed.
- If neither is available, the run ends.

### Beginner advice
Try to think of shields as “insurance” and revives as “emergency backup.”

---

## 15) Quests

The game has **daily quests** and **weekly quests**.

### Daily quests
Daily quests are smaller objectives, such as:

- score pipes,
- collect coins,
- flap a number of times,
- collect items,
- play for a set amount of time,
- collect boosts,
- block hits with a shield.

### Weekly quests
Weekly quests are bigger goals, such as:

- defeat bosses,
- deal boss damage,
- finish runs,
- win runs,
- score pipes total,
- collect rare items,
- play for a long time.

### How quest progress works
Quest progress is based on your saved profile totals. When you complete a quest, you can claim the reward, and the reward coins are added to your account.

### Why quests are useful
Quests are one of the fastest ways to earn coins and build long-term progress.

---

## 16) Achievements

Achievements are permanent milestone goals.

### Examples of achievements
- First Flight
- Airborne
- Pipe Ace
- Coin Hoard
- Item Lover
- Shield Guard
- Boss Breaker
- Boss Master
- Hard Fighter
- Daily Runner
- Weekly Champ
- Veteran
- Sky Runner
- Pipe Veteran
- Coin Collector
- Combo Spark
- Marathon
- Boss Hunter
- Hard Conqueror
- Quest Legend

### How they unlock
Achievements unlock automatically when your profile totals reach the target.

### Why they matter
They give you a clear sense of progress and reward you for learning the game properly.

---

## 17) Profile screen

The Profile screen has three tabs:

- **Stats**
- **Quests**
- **Achievements**

### Tab controls
| Action | Key |
|---|---|
| Switch tabs | `Left/Right`, `A/D` |
| Jump to Stats | `1` |
| Jump to Quests | `2` |
| Jump to Achievements | `3` |
| Force progress refresh / claim checks | `Space` |
| Go back | `Esc` or `Enter` |

### What you see there
| Tab | What it shows |
|---|---|
| Stats | Your totals, run history, and progress numbers |
| Quests | Daily and weekly quest progress and rewards |
| Achievements | Your unlocked and locked achievements |

---

## 18) Skins

Skins change the look of your bird.

### Skin browser controls
| Action | Key |
|---|---|
| Previous skin | `Left`, `A` |
| Next skin | `Right`, `D` |
| Equip / confirm | `Enter` |
| Back | `Esc` |

### How skins work
- Some skins are unlocked from the beginning.
- Others must be bought with coins.
- Once unlocked, they stay available.
- Your selected skin is saved.

### Beginner advice
Early on, save coins for skins you actually like. A good skin does not change gameplay directly, but it makes the game feel more personal and satisfying.

---

## 19) Options

The Options screen currently includes:

- Sound
- Best Score
- Coin
- Restart

### What each one means
| Option | Meaning |
|---|---|
| Sound | Turn audio on or off |
| Best Score | Shows your saved record |
| Coin | Shows your current coins |
| Restart | Clears your progress data |

### Options controls
| Action | Key |
|---|---|
| Move selection | `Up/Down`, `W/S` |
| Activate selected option | `Enter` |
| Close options | `Esc` |
| Close button | Click X or Close |

### Very important warning
**Restart clears your progress.**  
It resets:

- best scores,
- coins,
- profile totals,
- achievements,
- quest state,
- and related saved progress.

Use it only if you really want a fresh start.

---

## 20) Saving and progress

Your progress is saved automatically to a local file beside the script.

### Saved data includes
- coins
- best scores
- sound setting
- hitbox setting
- unlocked skins
- selected skin
- last boss
- profile totals
- achievements
- quest state
- last run summary

### What this means
You can close the game and come back later without losing your main progress.

---

## 21) Best beginner tips

| Tip | Why it helps |
|---|---|
| Stay calm and make small flaps | Prevents over-correcting |
| Keep the bird near the middle | Gives you room above and below |
| Learn the pipe rhythm first | Makes survival much easier |
| Take safe items only | Greedy item grabs often cause crashes |
| Use shields as emergency tools | They save runs you would otherwise lose |
| Do not chase every coin in Boss Mode | Survival matters more |
| Play lower difficulties first | Lets you learn timing and movement |
| Check Profile often | Quests and achievements give useful goals |

---

## 22) What to focus on first

If you are completely new, this is the best order:

1. Learn the controls.
2. Play **EASY** in Arcade Mode.
3. Practice smooth flapping.
4. Learn how items work.
5. Try to survive longer, not just score higher.
6. Start completing daily quests.
7. Buy a skin you like.
8. Move up to NORMAL.
9. Try Boss Mode after you are comfortable.
10. Save HELL for much later.

---

## 23) Simple beginner strategy

A very safe early-game plan is:

- flap only when you need to rise,
- keep your line steady,
- watch the next pipe, not the current one,
- value shield and revive items highly,
- ignore risky items if the gap is tight,
- treat Boss Mode like a survival test, not a race.

---

## 24) One-line summary

**Sky Pulse Bird** is a polished flappy-style game where you survive pipes, collect items, unlock progress, fight bosses, and slowly grow from a beginner into a consistent pilot.
