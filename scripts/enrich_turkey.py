#!/usr/bin/env python3
"""Enrich turkey.tr.csv / turkey.en.csv: emails, sample games, notes.

Only uses publicly verifiable emails (scraped from official pages or
known press/career listings). Never invents email domains.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
TR_PATH = ROOT / "data" / "turkey.tr.csv"
EN_PATH = ROOT / "data" / "turkey.en.csv"
SCRAPE_PATH = ROOT / "scripts" / ".cache" / "scraped_emails.json"

TR_FIELDS = [
    "Firma",
    "Bölge",
    "Şehir",
    "Kuruluş",
    "Çalışan",
    "Gelir_fon",
    "Web",
    "E-posta",
    "Türler",
    "Örnek_oyunlar",
    "Staj",
    "Uzaktan",
    "Sahiplik",
    "Not",
]
EN_FIELDS = [
    "Company",
    "Region",
    "City",
    "Founded",
    "Employees",
    "Revenue_funding",
    "Web",
    "Email",
    "Genres",
    "Sample_games",
    "Internship",
    "Remote",
    "Ownership",
    "Notes",
]

# Manually verified public emails (official pages / career listings / press).
# Format: list of (email, tr_role, en_role)
MANUAL_EMAILS: dict[str, list[tuple[str, str, str]]] = {
    "Dream Games": [
        ("contact@dreamgames.com", "genel", "general"),
        ("info@dreamgames.com", "genel", "general"),
        ("hr@dreamgames.com", "İK", "HR"),
    ],
    "Peak Games": [
        ("contact@peak.com", "genel", "general"),
        ("press@peak.com", "basın", "press"),
        ("partnerships@peak.com", "iş geliştirme", "partnerships"),
        ("hr@peak.com", "İK", "HR"),
    ],
    "TaleWorlds Entertainment": [
        ("info@taleworlds.com", "genel", "general"),
        ("jobs@taleworlds.com", "İK", "HR"),
        ("support@taleworlds.com", "destek", "support"),
    ],
    "Masomo": [
        ("support@masomo.com", "destek", "support"),
        ("peopleandculture@masomo.com", "İK", "HR"),
        ("ik@masomo.com", "İK", "HR"),
    ],
    "Mayadem": [
        ("iletisim@mayadem.com", "genel", "general"),
    ],
    "Crytek Istanbul": [
        ("infoistanbul@crytek.com", "genel", "general"),
        ("contact@crytek.com", "genel", "general"),
        ("press@crytek.com", "basın", "press"),
        ("business@crytek.com", "iş geliştirme", "business"),
    ],
    "Gram Games": [
        ("pr@gram.gs", "basın", "press"),
        ("jobs@gram.gs", "İK", "HR"),
        ("support@gram.gs", "destek", "support"),
    ],
    "Ace Games": [
        ("info@ace.games", "genel", "general"),
        ("support@ace.games", "destek", "support"),
        ("hr@ace.games", "İK", "HR"),
    ],
    "Spyke Games": [
        ("info@spykegames.com", "genel", "general"),
        ("support@spykegames.com", "destek", "support"),
    ],
    "Softgames (İstanbul ofisi)": [
        ("help@softgames.de", "destek", "support"),
        ("privacy@softgames.de", "gizlilik", "privacy"),
        ("publishers@softgames.com", "iş geliştirme", "publishing"),
    ],
    "Creasaur Entertainment": [
        ("mail@creasaur.com", "genel", "general"),
    ],
    "Bigger Games": [
        ("info@biggergames.com", "genel", "general"),
    ],
    "Panteon": [
        ("info@panteon.games", "genel", "general"),
    ],
    "Digitoy Games": [
        ("info@digitoygames.com", "genel", "general"),
        ("support@digitoygames.com", "destek", "support"),
    ],
    "Joygame": [
        ("bizdev@joygame.com", "iş geliştirme", "bizdev"),
    ],
    "Vento Games": [
        ("info@ventogames.com", "genel", "general"),
    ],
    "Grand Games": [
        ("info@grand.gs", "genel", "general"),
    ],
    "Fuse Games": [
        ("fuse@fusegam.es", "genel", "general"),
        ("support@fusegam.es", "destek", "support"),
    ],
    "Mega Fortuna": [
        ("info@megafortuna.co", "genel", "general"),
    ],
    "Libra Softworks": [
        ("librasoftworks@gmail.com", "genel", "general"),
    ],
    "Otsimo": [
        ("support@otsimo.com", "destek", "support"),
    ],
    "Gamegos": [
        ("info@gamegos.com", "genel", "general"),
        ("jobs@gamegos.com", "İK", "HR"),
    ],
    "Vertigo Games": [
        ("info@vertigogames.co", "genel", "general"),
        ("jobs@vertigogames.co", "İK", "HR"),
        ("support@vertigogames.co", "destek", "support"),
    ],
    "Studio Billion": [
        ("info@studiobillion.com", "genel", "general"),
        ("hr@studiobillion.com", "İK", "HR"),
        ("business@studiobillion.com", "iş geliştirme", "business"),
    ],
    "MildMania": [
        ("contact@mildmania.com", "genel", "general"),
        ("hr@mildmania.com", "İK", "HR"),
    ],
    "Games United": [
        ("hello@gamesunited.co", "genel", "general"),
        ("hr@gamesunited.co", "İK", "HR"),
    ],
    "Aden Games": [
        ("info@adengames.com", "genel", "general"),
        ("ik@adengames.com", "İK", "HR"),
    ],
    "TOGED": [
        ("info@toged.org", "genel", "general"),
    ],
    "skgames": [
        ("info@skgames.net", "genel", "general"),
    ],
    "Unico Studio": [
        ("unico@unicostudio.co", "genel", "general"),
    ],
    "Agave Games": [
        ("contact@agavegames.com", "genel", "general"),
    ],
    "Circle Games": [
        ("contact@circle.gs", "genel", "general"),
    ],
    "TaleMonster Games": [
        ("contact@talemonster.games", "genel", "general"),
        ("support@talemonster.games", "destek", "support"),
    ],
    "FOMO Games": [
        ("hello@fomo.gs", "genel", "general"),
    ],
    "Revel Games": [
        ("info@revel.gs", "genel", "general"),
    ],
    "Hyperlab": [
        ("hello@hyperlab.games", "genel", "general"),
    ],
    "Noho Games": [
        ("hello@noho.games", "genel", "general"),
    ],
    "ATTA Games": [
        ("hi@atta.games", "genel", "general"),
        ("partner@atta.games", "iş geliştirme", "partnerships"),
    ],
    "Playable Factory": [
        ("hello@playablefactory.com", "genel", "general"),
    ],
    "Paxie Games": [
        ("hey@paxiegames.com", "genel", "general"),
        ("support@paxiegames.com", "destek", "support"),
    ],
    "Mission Control Games": [
        ("contact@missioncontrol.gs", "genel", "general"),
    ],
    "SKEB Studios": [
        ("hello@skebstudios.com", "genel", "general"),
        ("press@skebstudios.com", "basın", "press"),
    ],
    "Red Axe Games": [
        ("info@redaxegames.com", "genel", "general"),
        ("contact@redaxegames.com", "genel", "general"),
    ],
    "Althera Games": [
        ("info@altheragames.com", "genel", "general"),
        ("press@altheragames.com", "basın", "press"),
    ],
    "BoomHits": [
        ("support@boomhits.com", "destek", "support"),
    ],
    "Good Job Games": [
        ("contact@goodjobgames.com", "genel", "general"),
        ("people@goodjobgames.com", "İK", "HR"),
    ],
    "Zuuks Games": [
        ("support@zuuks.com", "destek", "support"),
        ("dmca@zuuks.com", "yasal", "legal"),
    ],
    "Fugo Games": [
        ("info@fugo.com.tr", "genel", "general"),
        ("jobs@fugo.com.tr", "İK", "HR"),
        ("wow@fugo.com.tr", "destek", "support"),
        ("privacy@fugo.com.tr", "gizlilik", "privacy"),
    ],
    "MadByte Games": [
        ("info@madbytegames.com", "genel", "general"),
    ],
    "Alictus": [
        ("info@alictus.com", "genel", "general"),
    ],
    "Cypher Games": [
        ("privacy@cyphergames.com", "gizlilik", "privacy"),
    ],
    "Pine Games": [
        ("info@pinegames.com", "genel", "general"),
        ("careers@pinegames.com", "İK", "HR"),
    ],
    "Yolo Game Studios": [
        ("contact@yologamestudio.com", "genel", "general"),
    ],
    "Toon Metal Games": [
        ("support@toonmetal.games", "destek", "support"),
    ],
    "Digidodo Games": [
        ("support@digidodo.net", "destek", "support"),
        ("work@digidodo.net", "İK", "HR"),
    ],
    "Soft Towel Games": [
        ("support@softtowelgames.com", "destek", "support"),
    ],
    "Lokum Games": [
        ("contact-mobile@lokumgames.com", "genel", "general"),
    ],
    "Lost Panda Games": [
        ("info@lostpandagames.com", "genel", "general"),
    ],
    "BitRaiders Games": [
        ("info@bitraiders.games", "genel", "general"),
    ],
    "HOGO Games": [
        ("hogogames@hogogames.com", "genel", "general"),
    ],
    "Ruby Games": [
        ("rubygames.privacy@rovio.com", "gizlilik", "privacy"),
        ("rubygames.info@rovio.com", "genel", "general"),
        ("info@rubygamestudio.com", "genel", "general"),
        ("hr@rubygamestudio.com", "İK", "HR"),
    ],
    # Rollic: contact forms only on rollicgames.com — no public inbox (skip Take-Two parent emails).
}

# Additional sample games to merge (semicolon-separated titles). Keep existing; add these.
GAMES_ADD: dict[str, list[str]] = {
    "Dream Games": ["Royal Match", "Royal Kingdom"],
    "Peak Games": [
        "Toy Blast",
        "Toon Blast",
        "Match Factory!",
        "Lost Bubble",
        "Lost Jewels",
        "Spades Plus",
        "Gin Rummy Plus",
        "Okey Plus",
    ],
    "Zuuks Games": [
        "Bus Simulator: Ultimate",
        "Truck Simulator Ultimate",
        "City Bus Driver Simulator",
        "Off The Road",
        "Minibus Simulator",
    ],
    "Good Job Games": [
        "Match Villains",
        "Wonder Blast",
        "Zen Match",
        "Fun Race 3D",
        "Let's Be Cops 3D",
        "Draw Joust",
    ],
    "Gram Games": ["1010!", "Merge Dragons!", "Merge Magic!"],
    "Rollic": [
        "Tangle Master 3D",
        "Color Block Jam",
        "High Heels",
        "Idle Lumber Empire",
        "Hair Challenge",
        "Screw Them All",
    ],
    "Joygame": ["Wolfteam", "Legend Online", "Supremacy: World War 3"],
    "Spyke Games": ["Tile Busters", "Blitz Busters", "Royal Riches", "Cube Busters"],
    "Ace Games": ["Fiona's Farm", "Travel Town", "Clue Chase"],
    "Bigger Games": ["Kitchen Masters", "Mergedom", "Match Masters"],
    "Crytek Istanbul": ["Warface", "Hunt: Showdown", "CRYENGINE"],
    "MadByte Games": ["Zula", "Zula Mobile", "Calypso: Brethren of the Coast", "Zula Strike"],
    "Fugo Games": [
        "Words of Wonders",
        "Words of Wonders: Search",
        "Words of Wonders: Guru",
        "Words of Wonders: Zen",
        "Word Master",
        "Solitaire Sunday",
        "Sort Out",
    ],
    "Vertigo Games": ["Critical Strike", "Critical Strike Portable", "Critical Force"],
    "Grand Games": ["Magic Sort", "Car Match", "Goods Sort", "Tile Match"],
    "Agave Games": ["Find The Cat", "What The Hex", "Hexa Sort"],
    "Cypher Games": ["Match Squad"],
    "Loom Games": ["Pixel Flow!", "Water Sort"],
    "TaleMonster Games": ["Match Valley", "Merge Grove"],
    "Playable Factory": ["playable ads / UA creatives"],
    "VLMedia": ["Waplog", "Joi"],
    "Happy Crab": [
        "Zatonya Chasing Asteroid",
        "CDS - Car Drifting Simulator 2023",
    ],
    "Pine Games": ["Viking Island: Merge Adventure", "Word Weaver", "Number Paint", "Merge Island"],
    "FOMO Games": ["Traffic Escape!", "Color Blocks 3D", "Seat Jam 3D", "Bus Escape"],
    "Revel Games": ["Merge Now", "Idle Merge"],
    "Mavis Games": ["Slidey: Block Puzzle", "Block Puzzle Guardian"],
    "Tiramisu Studios": ["Drift Max", "Drift Max Pro", "Drift Max World", "Drift Max Japanese Drift"],
    # Mayadem: already filled with localized TR/EN titles in CSV — skip GAMES_ADD
    "Narcade": ["Farm Blast", "Zen Master", "Bubble Friends", "Merge Farm"],
    "Yolo Game Studios": ["Find Differences", "Find Hidden Objects", "Find Master", "Spot the Difference"],
    "Core Studios": ["Outlets Rush", "Suzy's Restaurant", "Idle Outlets"],
    "SuperGears Games": ["Racing Kingdom", "Car Race"],
    "Vento Games": ["Blossom Word Search", "Word Search Adventure", "Flower Word Search"],
    "Bold Games": ["Market Match!", "Supermarket Match"],
    "Nowhere Studios": ["Monochroma", "Monochroma 2"],
    "BitRaiders Games": ["Summer Delicious Simulator", "Hexa Castle", "Cooking Simulator Idle"],
    "Funverse Games": ["Hit and Boom"],
    "TaleWorlds Entertainment": [
        "Mount & Blade",
        "Mount & Blade: Warband",
        "Mount & Blade II: Bannerlord",
        "Mount & Blade: With Fire & Sword",
        "Napoleonic Wars",
        "Viking Conquest",
    ],
    "UDO": ["Basketball Master", "Mafia Life", "Goons.io", "Basketball Arena Idle"],
    "Alictus": [
        "Candy Challenge 3D",
        "Rob Master 3D",
        "Deep Clean Inc.",
        "Going Balls",
        "Count Masters",
        "Collect Em All!",
        "Money Collector",
    ],
    "Panteon": [
        "Raid Rush",
        "Airport Master",
        "Arcane Arena",
        "Hotel Frenzy",
    ],
    "Loop Games": ["Match 3D", "Match Tile 3D", "Find Difference"],
    "Lost Panda Games": ["Put the Nuts", "Thread Master", "Sort'n Merge", "Find the Panda", "Nut Sort"],
    "Backpack Games": ["Sushi Craft", "Burger Craft", "Clean The Sea!", "Food Craft"],
    "MildMania": ["Darklings", "Rop", "Darklings: Idle RPG"],
    "Momend": ["Mech Wars", "Mech Arena"],
    "Kuixo": ["Triple Star", "Match Puzzle"],
    "Otsimo": ["Otsimo Special Education", "Otsimo Speech Therapy", "Otsimo ABA"],
    "Pixofun": ["Footbo City", "QuizGame", "Football Manager lite"],
    "Masomo": ["Head Ball 2", "Basketball Arena", "Online Head Ball"],
    "Digitoy Games": ["Okey Extra", "101 Okey Extra", "Poker Extra", "Backgammon Extra", "Batak Extra"],
    "MythraTech": ["Sailor's Journey", "Opie the Defender"],
    "Mobge": ["Oddmar", "Hand Strike", "Oddmar: World Adventurer"],
    "Mage Games": ["Goal Battle", "Football Clash"],
    "Ruff Games": ["Hidden Case", "Factory Jam", "Cap Sort", "Case Hunter"],
    "Furtle Game": ["Pest Office!", "Gold Panning!", "Bakery Idle!", "Idle Office"],
    "Pyro Games": ["K-Sniper Challenge", "Merge Battle Tactics", "Netherwyn"],
    "Teneke Kafalar Studios": ["Feign", "Feather Party", "Throwia", "Party Game Night"],
    "Pundun Games": ["Smash Ball Up", "Merge and Battle!", "Chaos Arena"],
    "Keby Games": ["Nightcore", "VegaOnline", "Word Busters", "Wonder Boys"],
    "SPT Studios": ["Glow Tiles", "Squad Ops", "Boost Raid", "Lost Haven"],
    "Spell Factory": ["Clashub", "The Infected Soul"],
    "TAMU Games": ["King Slayer"],
    "Pokuch": ["Blind Descent"],
    "Rubedo Games": ["Soulbind: Tales of the Underworld"],
    "Arkhe Games": ["Human Fortune", "Battery Run"],
    "Wide Game Studio": [
        "Flare Frenzy",
        "Flare Frenzy 2",
        "Santa Climber",
        "GRAVI",
        "Wizard's Tower",
    ],
    "Ruby Games": [
        "Draw Climber",
        "Tall Man Run",
        "Bridge Race",
        "Fun Race 3D (yayın)",
    ],
    "Paxie Games": ["Merge Studio: Fashion Makeover", "Tile Star", "Mahjong Infinity", "Merge Fashion"],
    "Lokum Games": ["Tactical Strike", "Idle Strike"],
    "Leap Games": ["Hidden Tales", "Search It", "Hidden Object Mysteries"],
    "Fortune Mine Games": ["Coin Chef", "Merge Cooking"],
    "Gleam Games": ["EverBlast", "Match Blast"],
    "Biotech Gameworks": ["Kebab Chefs!", "Cooking Idle"],
    "Apphic Games": ["Nusrat", "Fetih İstanbul", "Ottoman Empire Strategy"],
    "Studio Billion": [
        "Construction Simulator 3D",
        "HR Master",
        "Spin Warriors Istanbul",
        "Idle Construction",
    ],
    "Gnarly Games": ["Frontline Heroes", "Agent Hunt", "Sea Lords", "War Heroes"],
    "Gulliver's Games": [
        "Word Tiles GO",
        "Restaurant Tycoon",
        "Plant Shop Tycoon",
        "Word Connect Tycoon",
    ],
    "Veloxia": ["Space Colony: Idle", "Idle Port", "Embershard"],
    "Soft Towel Games": ["Words of Paradise", "Calming Word Puzzles", "Word Zen"],
    "Boom Games": ["Puppet Master Run", "Flip Carve", "Draw Bullets", "Grocery 3D"],
    "Nomad Monkey": ["Tunnels", "Downhill Bike", "Machine Shop Simulator"],
    "GameGuru": ["Slap Kings", "Fruit Clinic", "Flick Goal", "Street Hustle", "Army Commander"],
    "Metaverse Game Studios": ["Angelic: Dark Symphony"],
    "Phoelix Games": ["Excavator Simulator 2025", "Construction Simulator"],
    "OXS Games": ["Arena Blast", "Online Drift Arena", "Challenger X", "Highway Truck"],
    "SekGames": ["Police Station Idle", "My Shopping Mall", "Airport Idle", "Idle Tycoon"],
    "Wendigo Games": [
        "Orpheus: Tale of a Lover",
        "WHAT THE PAK?!",
        "Wrap House Simulator",
    ],
    "Rotten Games": ["Quick Chess", "Ball Climber", "Chess Blitz"],
    "Rotatelab": ["Cube Land", "Sort Land", "Puzzle Land"],
    "Nokta Games": ["Supermarket Simulator", "Toy Of War", "Retail Simulator"],
    "skgames": ["Traffic Rider", "Traffic Racer", "Wings on Fire", "Racing Fever"],
    "Curve Animation": ["Liar's Bar", "Chicken Away"],
    "Pixega Studio": ["Twelve Labours of Hercules", "Hercules Adventures"],
    "Zibumi": ["2Seksen", "Monster Kartz"],
    "2DOT Games": ["Unbelievers"],
    "Skyloft Studios": ["Hyper Survive 3D", "Hyper Knight", "Hyper Casual Arena"],
    "BoomHits": ["Shoe Race", "Cat Life Sim", "Crazy Traffic Control", "Hyper Touchdown"],
    "Joinco Games": ["Angry Goals", "Football Arcade"],
    "Teos Games": ["Help Me", "Puzzle Escape"],
    "Room Games": ["Recharge", "Idle Charge"],
    "HOGO Games": ["Marble Race", "Travel Jam!", "Fill The Bucket", "Race Puzzle"],
    "Red Axe Games": [
        "Car For Sale Simulator 2023",
        "Gym Simulator 24",
        "Banker Simulator",
        "Gas Station Simulator",
    ],
    "Oldmoustache": ["No70: Eye of Basir", "Haunt Chaser", "Demonologist"],
    "Unico Studio": [
        "Brain Test",
        "Woody Sort",
        "2248",
        "Screw Out 3D",
        "Who is?",
        "Word Perfect",
        "Brain Test 2",
        "Brain Test 3",
    ],
    "Gamegos": ["Cafeland", "Manor Cafe", "Adventure Bay", "Marketland", "Fashland", "Petsland"],
    "Fiber Games": [
        "Weld It 3D",
        "Beauty Center",
        "Kral Şakir: Macera Adası",
        "Opet Ulusal",
    ],
    "Moon Star Games": [
        "Motorcycle Driving: Cop Chase",
        "Bike Rider",
        "Car Crash Simulator",
        "Traffic Rider style racing",
    ],
    "SKEB Studios": ["Colony", "Slice Master", "Color Rush", "Hyper Dunk", "Loot Town"],
    "Pax Animi Games": ["Money to Billions", "Pure Farm", "FishAway", "Idle Billionaire"],
    "Aden Games": ["Weapon Craft Run", "Gold Rush 3D", "MarbleVerse", "Craft Run"],
    "Duello Games": ["iSlash", "iSlash Heroes", "TripTrap", "Bellyfish"],
    "Inventuna Games": ["Heroes Chained", "Blockchain RPG"],
    "Softgames (İstanbul ofisi)": [
        "Family Feud",
        "Wheel of Fortune",
        "Jeopardy!",
        "Name That Tune",
        "Crossword Puzzle Collection",
    ],
    "Frostline Games": ["Kaçka", "Naipler", "Dünyalar Savaşı"],
    "Madcraft Studios": ["Crowalt: Traces of the Lost Colony"],
    "Moonstar Games (3D Evi)": ["Castle Capture Topkapı", "Despot Zombie", "Historical Strategy"],
    "ByteTyper": ["Racing Online", "Firefighter Hero", "Touchdrawn"],
    "ZeroSum": ["Barista Life", "Long Nails 3D", "Off-Road Race"],
    "Pinq Games": ["Politon", "Still Two Minutes"],
    "Oreon Studios": [
        "Monster Draft",
        "Slice Master",
        "Draw Army",
        "Mask Evolution",
        "Build Masters",
    ],
    "Hypermonk Games": ["Highway Overtake", "Dyno 2 Race", "Drift 2 Drag", "Count Bounce"],
    "Kodgraf Game Studio": ["Boğaz Harbi", "Protector M", "Hürriyet Kelime"],
    "Creasaur Entertainment": ["Money Maker 3D", "Hit Guys", "Idle Cash"],
    "Quok Games": ["Screw Jam", "Blob Runner", "Hoard Master", "Repair Master"],
    "396 Animation & Game Studios": [
        "TRT Çocuk: Anadolu Rock ve Tuhafiye",
        "Mercanya",
        "Akıncı",
    ],
    "Craftbridge Games": ["The Carnival of Company", "Ginga Cantina"],
    "Skunkworks Studios": [
        "Master of Cigkofte",
        "Craft & Deliver",
        "The Dismissed Case: Blackout",
    ],
    "ValenGate Game Studio": ["Trade Empire"],
    "Ash & Pause": ["TaterUp", "Loop 13"],
    "Narradive Studios": ["Will You Be My Disciple?", "Command Pocket"],
    "Lumos İnteraktif": ["LUMI", "Kukuli", "Giligilis", "Serra"],
    "Libra Softworks": [
        "Joy Blast",
        "Word Universe",
        "Goodwill Tiles",
        "Hidden Wordz",
    ],
    "Fuse Games": [
        "Kitchen Match",
        "Park Match - Car Sort Puzzle",
        "Hexa Flow",
        "Solitaire Connections",
        "Jewel Sort",
        "Word Match",
        "Mahjong Match",
        "Block Crunch",
    ],
    "Mega Fortuna": ["Richie Games", "Earnimo", "PunkteWelt"],
    "Gorgonize Games": ["Crime Scene (Suç Mahalli)"],
    "Analiz Games": ["Stress Ball"],
    "Dinomore Games": ["Ducks In Disguise"],
    "SciPlay (Ankara varlığı)": ["Jackpot Party Casino", "Gold Fish Casino", "Quick Hit Casino"],
    "Mobge Eskişehir ofisi": ["Oddmar", "Hand Strike", "Oddmar: World Adventurer"],
}

# Concise note supplements (appended if not already present). TR / EN.
NOTES_ADD: dict[str, tuple[str, str]] = {
    "Dream Games": (
        "Londra ofisi; CVC stratejik ortaklığı ~$5B değerleme (2025).",
        "London office; CVC strategic partnership ~$5B valuation (2025).",
    ),
    "Peak Games": (
        "Zynga/Take-Two bünyesinde; Toy Blast & Toon Blast evergreen.",
        "Under Zynga/Take-Two; Toy Blast & Toon Blast evergreen.",
    ),
    "Gram Games": (
        "Zynga satın alımı; Merge Dragons! küresel marka.",
        "Zynga acquisition; Merge Dragons! global brand.",
    ),
    "Rollic": (
        "Zynga/Take-Two yayıncı kolu; Popcore dahil stüdyo alımları.",
        "Zynga/Take-Two publishing arm; studio acquisitions include Popcore.",
    ),
    "Ace Games": (
        "Travel Town / Fiona's Farm; Clue Chase (Hasbro CLUE lisanslı).",
        "Travel Town / Fiona's Farm; Clue Chase (Hasbro CLUE licensed).",
    ),
    # Spyke/Ace base notes are maintained in CSV; NOTES_ADD phrases must be same-language only.
    "Creasaur Entertainment": (
        "Hyper-casual / idle yayıncı-geliştirici.",
        "Hyper-casual / idle publisher-developer.",
    ),
    "Bigger Games": (
        "Match Masters ile forever-franchise hedefi.",
        "Forever-franchise push via Match Masters.",
    ),
    "Crytek Istanbul": (
        "CRYENGINE ve Warface/Hunt ekosistemine katkı.",
        "Contributes to CRYENGINE and Warface/Hunt ecosystem.",
    ),
    "Fugo Games": (
        "Words of Wonders serisiyle kelime/puzzle evergreen.",
        "Word/puzzle evergreen via Words of Wonders series.",
    ),
    "TaleWorlds Entertainment": (
        "Bannerlord ile PC/konsol; Türkiye'nin amiral PC stüdyosu.",
        "Bannerlord on PC/console; Turkey's flagship PC studio.",
    ),
    "Alictus": (
        "SciPlay/Light & Wonder bünyesinde; Going Balls küresel hit.",
        "Part of SciPlay/Light & Wonder; Going Balls global hit.",
    ),
    "Masomo": (
        "Miniclip bünyesinde; İzmir & Londra ofisleri.",
        "Part of Miniclip; Izmir & London offices.",
    ),
    "Ruby Games": (
        "Rovio bünyesinde (İzmir); Draw Climber dönemi erken hyper-casual exit örneği.",
        "Part of Rovio (Izmir); early hyper-casual exit example from Draw Climber era.",
    ),
    "Libra Softworks": (
        "Yüksek yatırım alan puzzle/kelime stüdyosu.",
        "Well-funded puzzle/word studio.",
    ),
    "Softgames (İstanbul ofisi)": (
        "Berlin HQ; TV quiz/word yayıncısı; İstanbul ofis varlığı.",
        "Berlin HQ; TV quiz/word publisher; Istanbul office presence.",
    ),
    "Unico Studio": (
        "Brain Test serisiyle küresel trivia/puzzle başarısı.",
        "Global trivia/puzzle success via Brain Test series.",
    ),
    "Gamegos": (
        "Cafeland başta olmak üzere cafe-sim evergreen portföy.",
        "Cafe-sim evergreen portfolio led by Cafeland.",
    ),
    "skgames": (
        "Traffic Rider/Racer erken mobil racing hitleri.",
        "Early mobile racing hits Traffic Rider/Racer.",
    ),
    "SciPlay (Ankara varlığı)": (
        "Light & Wonder; Alictus satın alımıyla Ankara bağlantısı.",
        "Light & Wonder; Ankara link via Alictus acquisition.",
    ),
    "HAVELSAN": (
        "Savunma sanayi simülasyon/eğitim (klasik oyun stüdyosu değil).",
        "Defense sim/training (not a classic game studio).",
    ),
    "TOGED": (
        "Türkiye Oyun Geliştiricileri Derneği.",
        "Turkish Game Developers Association.",
    ),
    "Good Job Games": (
        "Match Villains / Wonder Blast; Levent ofisi; organik büyüme sonrası büyük yatırım.",
        "Match Villains / Wonder Blast; Levent office; large funding after organic growth.",
    ),
    "Zuuks Games": (
        "Bus/Truck Simulator Ultimate ile simülasyon kategorisinde küresel hacim.",
        "Global sim volume via Bus/Truck Simulator Ultimate.",
    ),
    "Spyke Games": (
        "Peak veteranları; forever-franchise odaklı match/puzzle.",
        "Peak Games alumni; forever-franchise match/puzzle focus.",
    ),
    "Cypher Games": (
        "Match Squad ile match-3 + zar hibriti.",
        "Match-3 + dice hybrid via Match Squad.",
    ),
    "Loom Games": (
        "Pixel Flow sonrası hızlı ölçek / exit hikâyesi.",
        "Rapid scale/exit story after Pixel Flow.",
    ),
    "Panteon": (
        "Ankara kökenli; Raid Rush / Airport Master hiper-casual-hybrid.",
        "Ankara-rooted; Raid Rush / Airport Master hyper-casual hybrid.",
    ),
    "Digitoy Games": (
        "Okey/101 Okey Extra ile Türkiye sosyal kutu oyunu liderlerinden.",
        "Leading TR social board-game apps via Okey/101 Okey Extra.",
    ),
    "Joygame": (
        "Wolfteam / Legend Online döneminin yayıncı-geliştiricisi.",
        "Publisher-developer of the Wolfteam / Legend Online era.",
    ),
    "Vento Games": (
        "Word-search / kelime casual portföyü.",
        "Word-search / word casual portfolio.",
    ),
    "Grand Games": (
        "Magic Sort / Goods Sort ile sort-puzzle hattı.",
        "Sort-puzzle line via Magic Sort / Goods Sort.",
    ),
    "Fuse Games": (
        "Kitchen Match ve App Store sort/puzzle portföyü; AI destekli üretim vurgusu.",
        "Kitchen Match and App Store sort/puzzle portfolio; AI-assisted production emphasis.",
    ),
    "Mega Fortuna": (
        "Richie Games / Earnimo ile ödüllü oyun / loyalty hattı.",
        "Rewarded/loyalty line via Richie Games / Earnimo.",
    ),
    "Otsimo": (
        "Özel eğitim / konuşma terapisi uygulamaları (oyun + edtech).",
        "Special-education / speech-therapy apps (games + edtech).",
    ),
    "Mayadem": (
        "TRT Çocuk lisanslı çocuk oyunları.",
        "TRT Kids licensed children's games.",
    ),
}

PLACEHOLDER_EMAILS = {
    "user@domain.com",
    "your@email.com",
    "you@email.com",
    "name@email.com",
    "email@domain.com",
    "info@mysite.com",
    "test@test.com",
}

BAD_EMAIL_SUBSTR = (
    "sentry",
    "wixpress",
    "schema.org",
    "example.com",
    "sentry.io",
    "revenuecat",
    "kep.tr",
    "u003e",
    "%20",
    "wix.com",
)


def role_for(email: str, lang: str) -> str:
    local = email.split("@")[0].lower()
    if any(x in local for x in ("hr", "career", "job", "ik", "people", "talent", "recruit", "work")):
        return "İK" if lang == "tr" else "HR"
    if any(x in local for x in ("press", "media", "pr", "comms")):
        return "basın" if lang == "tr" else "press"
    if any(x in local for x in ("partner", "bizdev", "bd", "business", "publishing", "monetization")):
        return "iş geliştirme" if lang == "tr" else "business"
    if any(x in local for x in ("support", "help")):
        return "destek" if lang == "tr" else "support"
    if any(x in local for x in ("privacy", "kvkk", "dpo", "gdpr")):
        return "gizlilik" if lang == "tr" else "privacy"
    if any(x in local for x in ("dmca", "legal", "law")):
        return "yasal" if lang == "tr" else "legal"
    if local in ("iletisim", "iletişim"):
        return "genel" if lang == "tr" else "general"
    return "genel" if lang == "tr" else "general"


def host_of(url: str) -> str:
    if not url:
        return ""
    return urlparse(url).netloc.lower().removeprefix("www.")


def related_domain(email_domain: str, web_host: str) -> bool:
    if not web_host or not email_domain:
        return False
    ed = email_domain.lower()
    wh = web_host.lower()
    if ed == wh or ed.endswith("." + wh) or wh.endswith("." + ed):
        return True
    # soft allow close variants (fusegam.es / fusegames.io)
    base = wh.split(".")[0]
    return base and base in ed.split(".")[0]


def is_personal_local(local: str) -> bool:
    # first.last or firstname patterns — skip unless manually allowlisted
    if "." in local and not any(
        x in local for x in ("info", "contact", "hello", "support", "press", "hr", "jobs", "team")
    ):
        parts = local.split(".")
        if len(parts) == 2 and all(p.isalpha() and 2 <= len(p) <= 15 for p in parts):
            return True
    return False


def clean_scraped(name: str, emails: list[str], web: str) -> list[str]:
    host = host_of(web)
    out = []
    for e in emails:
        e = e.strip().lower().lstrip(">")
        if e in PLACEHOLDER_EMAILS:
            continue
        if any(b in e for b in BAD_EMAIL_SUBSTR):
            continue
        if not re.match(r"^[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}$", e):
            continue
        local, _, domain = e.partition("@")
        if is_personal_local(local):
            continue
        # Prefer same/related domain; allow gmail only if already in MANUAL or Libra-style
        if host and not related_domain(domain, host):
            if domain not in {"gmail.com"}:
                continue
            # only keep gmail if company has no better domain emails and name matches cache intent
            if name not in {"Libra Softworks", "Oldmoustache", "Analiz Games", "Valvolex", "Stormling Studios"}:
                continue
        out.append(e)
    # de-dupe preserve order
    seen = set()
    uniq = []
    for e in out:
        if e not in seen:
            seen.add(e)
            uniq.append(e)
    return uniq[:4]


def format_emails(entries: list[tuple[str, str]], empty: str) -> str:
    if not entries:
        return empty
    # de-dupe by email
    seen = set()
    parts = []
    for email, role in entries:
        if email in seen:
            continue
        seen.add(email)
        parts.append(f"{email} ({role})")
    return "; ".join(parts)


def _norm_title(s: str) -> str:
    s = s.lower().strip()
    for noise in (" katkısı", " ekosistemi", " (ekosistem katkısı)", " (yayın)", " (demo)"):
        s = s.replace(noise, "")
    for prefix in ("mount & blade ii: ", "mount & blade: ", "mount & blade "):
        if s.startswith(prefix):
            s = s[len(prefix) :]
            break
    # Collapse "Truck Simulator" vs "Truck Simulator Ultimate"
    for suffix in (" ultimate", " pro", " 3d", "!"):
        if s.endswith(suffix) and len(s) > len(suffix) + 3:
            s = s[: -len(suffix)].strip()
    return s.strip()


def merge_games(existing: str, extra: list[str], empty_tokens: set[str]) -> tuple[str, bool]:
    cur = []
    if existing and existing.strip().lower() not in empty_tokens and existing.strip() != "—":
        cur = [x.strip() for x in existing.split(";") if x.strip()]
    before = len(cur)
    lower = {c.lower() for c in cur}
    norms = {_norm_title(c) for c in cur}
    for g in extra:
        g = g.strip()
        if not g:
            continue
        if g.lower() in lower or _norm_title(g) in norms:
            # Prefer cleaner / more specific title if a variant already present
            noise = ("katkısı", "ekosistemi", "yayın", "demo")
            for i, c in enumerate(cur):
                if _norm_title(c) != _norm_title(g):
                    continue
                c_noisy = any(n in c.lower() for n in noise)
                g_noisy = any(n in g.lower() for n in noise)
                if (c_noisy and not g_noisy) or (not g_noisy and not c_noisy and len(g) > len(c)):
                    cur[i] = g
                    lower.discard(c.lower())
                    lower.add(g.lower())
            continue
        cur.append(g)
        lower.add(g.lower())
        norms.add(_norm_title(g))
    # Cap at 8
    cur = cur[:8]
    expanded = len(cur) > before or cur != (
        [x.strip() for x in existing.split(";") if x.strip()]
        if existing and existing.strip().lower() not in empty_tokens and existing.strip() != "—"
        else []
    )
    if not cur:
        return existing if existing else ("bilinmiyor" if "bilinmiyor" in empty_tokens else "unknown"), False
    return "; ".join(cur), expanded and len(cur) >= before


def merge_note(existing: str, addition: str) -> tuple[str, bool]:
    if not addition:
        return existing, False
    if not existing or not existing.strip():
        return addition, True
    # avoid duplicate if key phrase already present
    key = addition.split(";")[0].strip()[:40].lower()
    if key and key in existing.lower():
        return existing, False
    if addition.lower() in existing.lower():
        return existing, False
    return f"{existing.rstrip('. ')}. {addition}", True


def load_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def main() -> None:
    scraped = {}
    if SCRAPE_PATH.exists():
        scraped = json.loads(SCRAPE_PATH.read_text(encoding="utf-8"))

    tr_rows = load_csv(TR_PATH)
    en_rows = load_csv(EN_PATH)
    en_by = {r["Company"]: r for r in en_rows}

    emails_filled = 0
    games_expanded = 0
    notes_enriched = 0
    samples = []

    for tr in tr_rows:
        name = tr["Firma"]
        en = en_by.get(name)
        if en is None:
            raise SystemExit(f"EN missing company key: {name}")

        web = tr.get("Web") or ""

        # --- Emails ---
        # Prefer MANUAL (if non-empty), else scraped, else keep existing CSV values.
        entries_tr: list[tuple[str, str]] = []
        entries_en: list[tuple[str, str]] = []
        manual = MANUAL_EMAILS.get(name)
        if manual:
            for email, rtr, ren in manual:
                entries_tr.append((email.lower(), rtr))
                entries_en.append((email.lower(), ren))
        else:
            cleaned = clean_scraped(name, scraped.get(name, []), web)

            def rank(e: str) -> tuple:
                loc = e.split("@")[0]
                prio = 50
                for i, key in enumerate(
                    ("info", "contact", "hello", "hi", "hr", "jobs", "press", "support", "privacy")
                ):
                    if key in loc:
                        prio = i
                        break
                return (prio, e)

            cleaned = sorted(cleaned, key=rank)
            for e in cleaned:
                entries_tr.append((e, role_for(e, "tr")))
                entries_en.append((e, role_for(e, "en")))

        old_tr = (tr.get("E-posta") or "").strip()
        old_en = (en.get("Email") or "").strip()
        old_tr_empty = old_tr.lower() in ("bilinmiyor", "unknown", "")
        old_en_empty = old_en.lower() in ("bilinmiyor", "unknown", "")

        if entries_tr:
            new_tr_email = format_emails(entries_tr, "bilinmiyor")
            new_en_email = format_emails(entries_en, "unknown")
        elif not old_tr_empty:
            # Preserve previously verified CSV emails
            new_tr_email = old_tr
            new_en_email = old_en if not old_en_empty else old_tr  # fallback sync
            # Re-label EN roles if EN was empty but TR had values — keep EN as-is if present
            if old_en_empty:
                # best-effort: copy structure with EN role labels
                parts = []
                for chunk in old_tr.split(";"):
                    chunk = chunk.strip()
                    m = re.match(r"(.+?)\s*\(([^)]+)\)\s*$", chunk)
                    if m:
                        parts.append((m.group(1).strip().lower(), role_for(m.group(1).strip(), "en")))
                    elif "@" in chunk:
                        parts.append((chunk.lower(), role_for(chunk, "en")))
                new_en_email = format_emails(parts, "unknown") if parts else "unknown"
        else:
            new_tr_email = "bilinmiyor"
            new_en_email = "unknown"

        if new_tr_email != "bilinmiyor" and (
            old_tr_empty or new_tr_email.lower() != old_tr.lower()
        ):
            emails_filled += 1
        tr["E-posta"] = new_tr_email
        en["Email"] = new_en_email

        # --- Games ---
        extra = GAMES_ADD.get(name, [])
        tr_games, exp_tr = merge_games(tr.get("Örnek_oyunlar", ""), extra, {"bilinmiyor", ""})
        en_games, exp_en = merge_games(en.get("Sample_games", ""), extra, {"unknown", "bilinmiyor", ""})
        if exp_tr or exp_en:
            games_expanded += 1
        tr["Örnek_oyunlar"] = tr_games
        en["Sample_games"] = en_games

        # --- Notes ---
        if name in NOTES_ADD:
            ntr, nen = NOTES_ADD[name]
            tr_note, ch1 = merge_note(tr.get("Not", ""), ntr)
            en_note, ch2 = merge_note(en.get("Notes", ""), nen)
            if ch1 or ch2:
                notes_enriched += 1
            tr["Not"] = tr_note
            en["Notes"] = en_note

        if (
            new_tr_email != "bilinmiyor"
            or exp_tr
            or name in NOTES_ADD
        ) and len(samples) < 10:
            samples.append(
                {
                    "company": name,
                    "email": new_tr_email,
                    "games": tr["Örnek_oyunlar"],
                    "note": (tr.get("Not") or "")[:120],
                }
            )

    write_csv(TR_PATH, tr_rows, TR_FIELDS)
    write_csv(EN_PATH, en_rows, EN_FIELDS)

    # Stats
    tr2 = load_csv(TR_PATH)
    email_ok = sum(
        1
        for r in tr2
        if (r.get("E-posta") or "").strip().lower() not in ("bilinmiyor", "unknown", "")
    )
    games_ge3 = sum(
        1
        for r in tr2
        if r.get("Örnek_oyunlar")
        and r["Örnek_oyunlar"].strip().lower() not in ("bilinmiyor", "—", "")
        and len([x for x in r["Örnek_oyunlar"].split(";") if x.strip()]) >= 3
    )

    print("=== ENRICHMENT STATS ===")
    print(f"Emails newly filled/upgraded this run: {emails_filled}")
    print(f"Emails currently filled (TR): {email_ok}/222")
    print(f"Game lists expanded this run: {games_expanded}")
    print(f"Companies with 3+ sample games (TR): {games_ge3}/222")
    print(f"Notes enriched this run: {notes_enriched}")
    print("\n=== SAMPLE 10 ENRICHED ROWS ===")
    for s in samples:
        print(f"- {s['company']}")
        print(f"  email: {s['email']}")
        print(f"  games: {s['games']}")
        print(f"  note: {s['note']}")


if __name__ == "__main__":
    main()
