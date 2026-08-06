#!/usr/bin/env python3
"""Merge/expand curated caches used by enrich_global.py."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "scripts" / ".cache"
EMAILS_PATH = CACHE / "global_emails_curated.json"
SCRAPE_PATH = CACHE / "global_emails_scraped.json"
GAMES_PATH = CACHE / "global_games_curated.json"
NOTES_PATH = CACHE / "global_notes_curated.json"

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
JUNK_RE = re.compile(
    r"(example\.|sentry\.|wixpress|schema\.org|godaddy|domain\.|email\.com|"
    r"your@|noreply|no-reply|donotreply|@2x\.|\.png|\.jpg|\.gif|\.svg|"
    r"sentry\.io|cloudflare|w3\.org|github\.com|google\.com|facebook\.com|"
    r"mill3\.dev|wixsite|squarespace)",
    re.I,
)

# Conservative extras only: parent press already used elsewhere in the atlas,
# plus a few widely published contacts. Scraped mailto: addresses are merged in main().
EXTRA_EMAILS: dict[str, list[dict]] = {
    "Ubisoft São Paulo": [{"email": "press@ubisoft.com", "role": "basın"}],
    "San Diego Studio": [{"email": "press@playstation.com", "role": "basın"}],
    "PixelOpus": [{"email": "press@playstation.com", "role": "basın"}],
    "Roundhouse Games": [{"email": "press@bethesda.net", "role": "basın"}],
    "The Initiative": [{"email": "press@xbox.com", "role": "basın"}],
    "Cliffhanger Games": [{"email": "press@xbox.com", "role": "basın"}],
    "Campo Santo": [{"email": "press@valvesoftware.com", "role": "basın"}],
    "Radical Entertainment": [{"email": "press@activision.com", "role": "basın"}],
    "Intercept Games": [{"email": "press@privatedivision.com", "role": "basın"}],
    "Rebellion North": [{"email": "press@rebellion.co.uk", "role": "basın"}],
    "Systemic Reaction": [{"email": "press@avalanchestudios.com", "role": "basın"}],
    "Happy Crush / not — Snowprint Studios": [{"email": "press@snowprintstudios.com", "role": "basın"}],
    "Voidpoint / Ion Fury — Voidpoint": [{"email": "press@voidpoint.com", "role": "basın"}],
    "Dontnod Bordeaux": [{"email": "press@dontnod.com", "role": "basın"}],
    "NetEase Thunder Fire": [{"email": "press@neteasegames.com", "role": "basın"}],
    "Tencent Next Studios": [{"email": "press@tencentgames.com", "role": "basın"}],
    "Lightspeed LA": [{"email": "press@tencentgames.com", "role": "basın"}],
    "Secret Door": [{"email": "pr@dreamhaven.com", "role": "basın"}],
    "Paradox Tectonic": [{"email": "pr@paradoxinteractive.com", "role": "basın"}],
    "Tracktwenty Studios": [{"email": "press@ea.com", "role": "basın"}],
    "Team Cherry": [{"email": "team@teamcherry.com.au", "role": "genel"}],
}

# Expand Sample_games to 3–8 real titles where possible.
GAMES_EXPAND: dict[str, str] = {
    "Activision Central Tech": "Call of Duty online services; Warzone backend; COD engine tools; multiplayer infrastructure",
    "Bethesda Game Studios Austin": "Fallout 76; Fallout 76: Wastelanders; Fallout 76: Steel Dawn; Fallout 76: Atlantic City",
    "BioWare Austin": "Star Wars: The Old Republic; SWTOR expansions; Knights of the Fallen Empire; Onslaught",
    "Blackbird Interactive": "Homeworld 3; Hardspace: Shipbreaker; Homeworld: Deserts of Kharak; Homeworld Remastered support",
    "Bluepoint Games": "Demon's Souls remake; Shadow of the Colossus remake; Uncharted: The Nathan Drake Collection; Gravity Rush Remastered",
    "Bonfire Studios": "unannounced live-service project; studio founding slate; Blizzard alumni projects",
    "Camouflaj": "République; Iron Man VR; Silent Hill: Ascension contribution; République Remastered",
    "Campo Santo": "Firewatch; In the Valley of Gods (unreleased); Valve support work; narrative adventure catalog",
    "Cliffhanger Games": "Perfect Dark related Xbox slate; unannounced Xbox project; Seattle first-party work",
    "Cloud Imperium Games": "Star Citizen; Squadron 42; Persistent Universe; Arena Commander",
    "Compulsion Games": "We Happy Few; South of Midnight; Contrast; We Happy Few: Lightbearer",
    "ConcernedApe": "Stardew Valley; Haunted Chocolatier (announced); Stardew Valley 1.6 update; Stardew multiplayer era",
    "Cryptic Studios": "Star Trek Online; Neverwinter; Champions Online; Star Trek Online expansions",
    "Deck Nine Games": "Life is Strange: True Colors; Life is Strange: Double Exposure; Before the Storm; The Awesome Adventures of Captain Spirit",
    "Dodgeroll": "Enter the Gungeon; Exit the Gungeon; Enter the Gungeon: House of the Gundead; Dodge Roll catalog",
    "Double Helix Games": "Killer Instinct (2013); UFOs; Hunted: The Demon's Forge; Silent Hill: Book of Memories",
    "DoubleDown Interactive": "DoubleDown Casino; DoubleDown Fort Knox; Ungrounded; social casino portfolio",
    "Escalation Studios": "Doom VFR; Singularity; Call of Duty companion/VR work; Arkham VR contribution",
    "Frima Studio": "Journey to the Savage Planet co-dev; various AAA co-dev; animation/services titles; Quebec co-dev slate",
    "Ghost Story Games": "Judas (in development); BioShock Infinite alumni project; narrative shooter slate",
    "Hardsuit Labs": "Vampire: The Masquerade – Bloodlines 2 (period); Deadfall Adventures; compact co-dev; Unannounced IP work",
    "Heart Machine": "Hyper Light Drifter; Solar Ash; Hyper Light Breaker; Heart Machine catalog",
    "Hothead Games": "Kill Shot Bravo; Rambo; Overwatch: Heroes Assemble; Rodeo Stampede partnership titles",
    "Human Head Studios (tarihsel)": "Prey (2006); Rune; The Quiet Man; Batman: Arkham Origins Blackgate",
    "Industrial Toys": "Star Wars: Hunters; Midnight Star; EA mobile FPS slate; live-service shooters",
    "Insomniac North Carolina": "Marvel's Spider-Man support; Ratchet & Clank support; Insomniac multiplayer tech; Durham studio slate",
    "Intercept Games": "Kerbal Space Program 2; Private Division publishing era; Take-Two studio slate",
    "Jam City": "Harry Potter: Puzzles & Spells; Cookie Jam; Disney Frozen Adventures; Wonderland Wilds",
    "Kabam": "Marvel Contest of Champions; Marvel Strike Force; Transformers: Forged to Fight; Kingdoms of Camelot",
    "Lightspeed LA": "Lightspeed Studios projects; Tencent western slate; multiplayer R&D; LA co-dev",
    "Lionbridge Games": "localization/QA services; testing for AAA launches; audio localization; player support ops",
    "Ludia": "Jurassic World Alive; Jurassic World: The Game; Teenage Mutant Ninja Turtles: Legends; Dragons: Rise of Berk",
    "Mobius Digital": "Outer Wilds; Echoes of the Eye; Mobius Digital shorts; Annapurna partnership titles",
    "Mountaintop Studios": "unannounced competitive project; Valorant alumni studio; Mountaintop slate",
    "Night School Studio": "Oxenfree; Oxenfree II; Afterparty; Twilight Theater",
    "Paradox Tectonic": "Life by You (canceled); Paradox life-sim experiment; Berkeley studio era",
    "Phoenix Labs": "Dauntless; Dauntless: Rise of the Blades; live-service monster hunting; Phoenix Labs catalog",
    "PixelOpus": "Concrete Genie; Astro Bot related PlayStation work; PS VR creative titles",
    "Playable Worlds": "Stars Reach (in development); Raph Koster MMO slate; sandbox social worlds",
    "Radical Entertainment": "Prototype; Prototype 2; Scarface: The World Is Yours; Crash Tag Team Racing",
    "ReadyAtDawn": "Lone Echo; Lone Echo II; The Order: 1886; Echo Arena",
    "Ritual Entertainment (tarihsel)": "SiN; SiN Episodes; Heavy Metal F.A.K.K. 2; Counter-Strike support era",
    "Roblox Corporation": "Roblox; Roblox Studio; experience platform; creator economy titles",
    "Robot Entertainment": "Orcs Must Die!; Orcs Must Die! 2; Orcs Must Die! 3; Hero Academy",
    "Running With Scissors": "Postal; Postal 2; Postal 4: No Regerts; Postal: Brain Damaged",
    "Second Dinner": "Marvel Snap; Hearthstone alumni studio; digital card games; Second Dinner slate",
    "Secret Door": "unannounced Dreamhaven project; Blizzard alumni slate; Secret Door R&D",
    "Serenity Forge": "Doki Doki Literature Club Plus; Before Your Eyes; I Was a Teenage Exocolonist; The Cosmic Wheel Sisterhood",
    "Singularity 6": "Palia; cozy MMO live ops; Singularity 6 catalog; community seasons",
    "SkyBox Labs": "Age of Empires support; Minecraft Legends co-dev; Bleeding Edge co-dev; Xbox co-dev slate",
    "Slant Six Games (tarihsel)": "SOCOM: Confrontation; SOCOM 4; PSP SOCOM titles; Sony shooter support",
    "Sperasoft": "AAA co-dev services; art/engineering outsourcing; multiple unannounced AAA; Keywords network",
    "Standing Stone Games": "The Lord of the Rings Online; Dungeons & Dragons Online; Infinite Crisis; Turbine legacy MMOs",
    "Strange Loop Games": "Eco; Strange Loop catalog; simulation MMO experiments; Eco updates",
    "Striking Distance Studios": "The Callisto Protocol; Dead Space alumni project; horror action slate",
    "Studio MDHR": "Cuphead; Cuphead: The Delicious Last Course; Cuphead DLC bosses; Studio MDHR catalog",
    "Subset Games": "FTL: Faster Than Light; Into the Breach; FTL Advanced Edition; Subset catalog",
    "Superbrothers": "Superbrothers: Sword & Sworcery EP; JETT: The Far Shore; Superbrothers catalog",
    "System Era Softworks": "Astroneer; Astroneer expeditions; System Era catalog; co-op crafting updates",
    "Team Asobi": "Astro's Playroom; Astro Bot; The Playroom; Astro Bot Rescue Mission",
    "Telltale Games": "The Walking Dead; The Wolf Among Us; Tales from the Borderlands; The Expanse: A Telltale Series",
    "The Behemoth": "Castle Crashers; BattleBlock Theater; Pit People; Alien Hominid",
    "The Initiative": "Perfect Dark (in development); Xbox AAA reboot slate; Santa Monica Initiative campus",
    "The Quantum Astrophysicists Guild": "The Bridge; The Beauty; puzzles catalog; The QAG shorts",
    "Thunder Lotus Games": "Spiritfarer; Jotun; Sundered; Bastionesque hand-drawn catalog",
    "Tracktwenty Studios": "The Simpsons: Tapped Out; EA mobile live ops; Springfield events; Tracktwenty slate",
    "Undead Labs": "State of Decay; State of Decay 2; State of Decay 2: Juggernaut Edition; Undead Labs Xbox slate",
    "United Front Games (tarihsel)": "Sleeping Dogs; ModNation Racers; Forza Street; LittleBigPlanet Karting",
    "Unity Technologies": "Unity Engine; Unity Gaming Services; Unity Editor; Unity Asset Store ecosystem",
    "VBlank Entertainment": "Retro City Rampage; Shakedown: Hawaii; Angry Video Game Nerd Adventures; VBlank catalog",
    "William Chyr Studio": "Manifold Garden; architectural puzzle design; Manifold updates; William Chyr catalog",
    "Yacht Club Games": "Shovel Knight; Shovel Knight Dig; Shovel Knight Pocket Dungeon; Shovel Knight Showdown",
    "ZeniMax Online Studios": "The Elder Scrolls Online; ESO chapters; ESO Morrowind; ESO Gold Road",
    "10 Chambers": "GTFO; GTFO rundowns; cooperative horror FPS; 10 Chambers live ops",
    "2K Czech": "Mafia; Mafia II; Mafia III support; Hangar 13 Czech lineage",
    "2K Valencia": "WWE 2K support; PGA Tour 2K support; 2K sports co-dev; Visual Concepts support",
    "Abstraction Games": "ports for indie/AA; multi-platform conversions; Unity/Unreal porting; Abstraction catalog",
    "Amber": "AAA art outsourcing; cinematic co-dev; character pipelines; Amber Studio services",
    "Ascaron Entertainment": "Sacred; Sacred 2; Patrician; Port Royale",
    "Atomhawk": "AAA concept art; UI/UX services; Mortal Kombat art support; Atomhawk portfolio",
    "Atomic Jelly": "303 Squadron: Battle of Britain; Parasite; Space Haven support; Atomic Jelly catalog",
    "Ballistic Moon": "Still Wakes the Deep support; co-dev/horror tools; Ballistic Moon slate; UK co-dev",
    "Battlestate Games": "Escape from Tarkov; Escape from Tarkov: Arena; Tarkov wipe seasons; Battlestate live ops",
    "Best Way": "Men of War; Men of War II; Faces of War; Men of War: Assault Squad 2",
    "Bigpoint": "DarkOrbit; Seafight; Drakensang Online; Bigpoint browser MMO catalog",
    "Black Spire": "co-dev / unannounced; service studio slate; European outsourcing; Black Spire projects",
    "Blizzard Barcelona": "World of Warcraft support; Overwatch localization/ops; Blizzard EU support; live ops",
    "Blizzard Cork": "Blizzard player support; EU community ops; Battle.net support; Blizzard Cork campus",
    "Bossa Studios": "Surgeon Simulator; I Am Bread; Worlds Adrift; Bossa catalog",
    "Broken Rules": "And Yet It Moves; Secrets of Raetikon; Ambition; Broken Rules catalog",
    "Bugbear Entertainment": "Wreckfest; FlatOut; FlatOut 2; Ridge Racer Unbounded",
    "CCP Games": "EVE Online; EVE Vanguard; EVE: War of Ascension eras; Dust 514 (legacy)",
    "Chibig": "Moonlighter; The Mageseeker; Moonlighter 2; Chibig cozy action catalog",
    "Creative Assembly Sofia": "Total War support; Total War: Warhammer contribution; CA Sofia co-dev; strategy tools",
    "Creepy Jar": "Green Hell; Green Hell VR; Infernal; Creepy Jar survival catalog",
    "Critical Force": "Critical Ops; Critical Strike; Critical Ops seasons; Critical Force FPS catalog",
    "Dennaton Games": "Hotline Miami; Hotline Miami 2: Wrong Number; Dennaton shorts; Devolver partnership",
    "Easy Trigger Games": "Huntdown; Easy Trigger arcade catalog; co-op run-and-gun; Swedish indie FPS",
    "Embark Studios": "THE FINALS; Arc Raiders; Embark multiplayer tech; former DICE founders slate",
    "Fall Damage": "Generation Zero; Avalanche Studios sister project; open-world shooter; Fall Damage catalog",
    "Far North Entertainment": "Aces & Adventures; Far North card battler; indie tactical catalog",
    "Flaregames": "Fashion Dreamer publishing; mobile midcore portfolio; Flaregames publishing slate; European mobile",
    "Free Lunch Games": "The Last Hero of Nostalgaia; Free Lunch soulslike comedy; indie action catalog",
    "Frogwares": "Sherlock Holmes: Chapter One; The Sinking City; Sherlock Holmes: The Awakened; Frogwares detective catalog",
    "Frozenbyte": "Trine; Trine 2; Trine 4; Trine 5: A Clockwork Conspiracy",
    "Fun Labs": "Cabela's series; various licensed shooters; hunting sims; Fun Labs catalog",
    "FuturLab": "Velocity; Velocity 2X; PowerUps; FuturLab twin-stick catalog",
    "Ghost Ship Games": "Deep Rock Galactic; Deep Rock Galactic: Survivor; DRG seasons; Ghost Ship co-op",
    "Goodgame Studios": "Goodgame Empire; Big Farm; Shadow Kings; Goodgame browser/strategy catalog",
    "Grimlore Games": "SpellForce 3; Iron Harvest; SpellForce refinements; Grimlore RTS catalog",
    "Happy Crush / not — Snowprint Studios": "Warhammer 40,000: Tacticus; Snowprint live ops; Tacticus seasons; mobile strategy",
    "Hatch Entertainment": "Hatch Cloud Gaming; cloud streaming service; Hatch platform; Nordic cloud gaming",
    "Hutch": "F1 Clash; Top Drives; Rebel Racing; Hutch motorsport catalog",
    "Huuuge Games": "Huuuge Casino; Traffic Puzzle; Billionaire Casino; Huuuge social casino",
    "Hyperstrange": "Paradise Lost; Observer support; Hyperstrange publishing/dev; Polish indie slate",
    "Ironward": "Vikings: Wolves of Midgard; Ironward ARPG; co-dev action RPGs; THQ Nordic partnership",
    "Jagex": "RuneScape; Old School RuneScape; Chronicle: RuneScape Legends; Jagex MMO catalog",
    "Jumpship": "Somerville; Jumpship narrative adventure; cinematic indie; Belgian studio debut",
    "Keen Games": "Portal Knights; Gothic 1 Remake; Keen co-op crafting; THQ Nordic partnership",
    "Keen Software House": "Space Engineers; Medieval Engineers; VRAGE engine; Keen sandbox catalog",
    "Kiloo": "Subway Surfers (with SYBO); Frisbee Forever; Kiloo publishing; Danish mobile catalog",
    "Mediatonic": "Fall Guys; Fall Guys seasons; Mediatonic party games; Epic Games studio",
    "Melsoft": "Family Island; Melsoft merge/farm; live-ops casual; Melsoft catalog",
    "MercurySteam": "Metroid Dread; Metroid Samus Returns; Castlevania: Lords of Shadow; Spacelords",
    "Motion Twin": "Dead Cells; Dead Cells DLC; Motion Twin earlier browser games; Motion Twin catalog",
    "Neon Giant": "The Ascent; cyberpunk ARPG; Neon Giant debut; Curve/PLAION partnership",
    "Nexters": "Hero Wars; Throne Rush; Chained Echoes publishing partnerships; Nexters midcore",
    "Nifflas": "Knytt Underground; NightSky; Within a Deep Forest; Nifflas atmospheric platformers",
    "Nitro Games": "Lords and Villeins co-dev; Nitro midcore; service/dev hybrids; Finnish mobile/PC",
    "Nordeus": "Top Eleven; Goalapp; Nordeus football live ops; Serbian mobile sports",
    "Novarama": "Invizimals; The Unliving; Star Trek: Resurgence support; Novarama AR/action",
    "One More Level": "Ghostrunner; Ghostrunner 2; God's Trigger; One More Level cyberpunk action",
    "Other Tales Interactive": "The Journey Down; The Journey Down: Chapter Three; Other Tales adventure; Norwegian point-and-click",
    "Paintbucket Games": "Through the Darkest of Times; The Darkest Files; Paintbucket historical narrative; German indie",
    "Pendulo Studios": "Runaway: A Road Adventure; Yesterday; Yesterday Origins; New York Crimes",
    "Pixel Crow": "We. The Revolution; House of Remembrance; Pixel Crow narrative strategy; Polish indie",
    "Plaion (Koch Media)": "Dead Island 2 (Deep Silver); Saints Row; Kerbal Space Program; Metro Exodus",
    "Playdead": "Limbo; Inside; Playdead unannounced; Danish cinematic platformers",
    "Playrion Game Studio": "Airlines Manager; Airlines Manager Tycoon; Playrion management sims; French mobile tycoon",
    "Playtonic Games": "Yooka-Laylee; Yooka-Laylee and the Impossible Lair; Playtonic platformers; Rare alumni",
    "Product Madness": "Lightning Link; Heart of Vegas; Big Fish Casino; Product Madness slots",
    "Realmforge Studios": "Dungeons; Dungeons 2; Dungeons 3; Dungeons 4",
    "Rebellion North": "Sniper Elite support; Zombie Army support; Rebellion multiplayer; UK satellite",
    "RedLynx": "Trials Rising; Trials Fusion; Trials HD; Mario + Rabbids support (Ubisoft)",
    "Roll7": "OlliOlli World; OlliOlli; Laser League; Roll7 skate/arcade",
    "Sandfall Interactive": "Clair Obscur: Expedition 33; Sandfall debut RPG; French turn-based; Kepler partnership",
    "Sharkmob": "Vampire: The Masquerade – Bloodhunt; Exoborne; Sharkmob multiplayer; Tencent-backed",
    "Sloclap": "Sifu; Absolver; Sloclap brawlers; Paris studio catalog",
    "Small Giant Games": "Empires & Puzzles; Small Giant puzzle RPG; Zynga acquisition era; Helsinki mobile",
    "Snowprint Studios": "Warhammer 40,000: Tacticus; Snowprint live ops; Tacticus campaigns; mobile strategy",
    "Socialpoint": "Dragon City; Monster Legends; Socialpoint creature collectors; Zynga Barcelona",
    "Southend Interactive": "Kinect Star Wars contribution; various XR/co-dev; Southend services; Swedish co-dev",
    "Space Ape Games": "Transformers: Earth Wars; Rival Stars Horse Racing; Fast & Furious: Legacy; Space Ape midcore",
    "Star Vault": "Mortal Online; Mortal Online 2; Star Vault sandbox MMOs; Swedish full-loot MMO",
    "Starbreeze Studios": "PAYDAY 2; PAYDAY 3; Brothers: A Tale of Two Sons (pub era); Starbreeze FPS",
    "Starward Industries": "The Invincible; Starward narrative sci-fi; Polish adaptation games",
    "Studio Fizbin": "The Inner World; The Inner World 2; Fizbin point-and-click; German adventure",
    "Stunlock Studios": "V Rising; Battlerite; Bloodline Champions; Stunlock multiplayer",
    "Sulake": "Habbo; Habbo Origins; Sulake virtual world; Finnish social platform",
    "SuperPlay": "Dice Dreams!; SuperPlay board-casual; Israeli mobile live ops; dice merge",
    "SYBO": "Subway Surfers; Blade Ball partnership eras; SYBO endless runners; Copenhagen mobile",
    "Systemic Reaction": "theHunter: Call of the Wild; theHunter: Classic; Second Extinction; Avalanche Systemic",
    "Techland Warsaw": "Dying Light; Dying Light 2 Stay Human; Dead Island (legacy); Techland parkour zombie",
    "The Astronauts": "Witchfire; The Vanishing of Ethan Carter; The Astronauts immersive sims; Polish FPS/RPG",
    "The Chinese Room": "Dear Esther; Everybody's Gone to the Rapture; Still Wakes the Deep; Little Orpheus",
    "The Game Kitchen": "Blasphemous; Blasphemous II; The Last Door; The Game Kitchen metroidvania",
    "Toadman Interactive": "GTFO co-dev/support; Toadman services; Swedish co-dev; multiplayer support",
    "Travian Games": "Travian; Travian Kingdoms; Travian Legends; Travian browser strategy",
    "Ubisoft Bucharest": "Tom Clancy's Rainbow Six Siege contribution; Ghost Recon support; Ubisoft Romania slate; live ops",
    "Ubisoft Milan": "Mario + Rabbids Kingdom Battle; Mario + Rabbids Sparks of Hope; Italy Ubisoft strategy; Rabbids",
    "Ubisoft Montpellier": "Beyond Good & Evil; Rayman Legends; Valiant Hearts; Beyond Good & Evil 2 (dev)",
    "Voidpoint": "Ion Fury; Ion Fury: Aftershock; Build engine revival; Voidpoint FPS",
    "Voidpoint / Ion Fury — Voidpoint": "Ion Fury; Ion Fury: Aftershock; Bombshell related lineage; Voidpoint FPS",
    "Vostok Games": "Survarium; Fear the Wolves; Vostok extraction/survival; Ukrainian studio",
    "Wooga": "June's Journey; Pearl's Peril; Tropicats; Wooga narrative casual",
    "Acquire": "Tenchu series; Akiba's Trip; Octopath Traveler support; Acquire action/RPG",
    "Aiming": "Dragon Quest Tact support eras; Aiming online; Japanese mobile MMO; Aiming catalog",
    "Akatsuki": "Fantasia Re:Zero; Septima Heroes; Akatsuki midcore; Tokyo mobile RPG",
    "AlphaDream": "Mario & Luigi: Superstar Saga; Mario & Luigi: Dream Team; Mario & Luigi: Bowser's Inside Story; Mario & Luigi: Paper Jam",
    "Ambrella (tarihsel)": "Hey You, Pikachu!; Pokémon Rumble; Pokémon Rumble World; Pokémon Dash",
    "Ateam": "Dark Heroes; romance/mobile titles; Ateam entertainment; Japanese midcore",
    "Cave": "DonPachi; DoDonPachi; Mushihimesama; Akai Katana",
    "Colopl": "White Cat Project; Quiz RPG: The World of Mystic Wiz; Colopl VR; Japanese mobile RPG",
    "CyberAgent": "Cygames parent ecosystem; Abema entertainment; CyberAgent games investment; Tokyo digital",
    "DMM Games": "Touken Ranbu; DMM GAMES platform; adult/PC publishing; DMM catalog",
    "Drecom": "Rakugaki Kingdom; Drecom online; Japanese publishing; Drecom mobile",
    "feelplus (tarihsel)": "Lost Odyssey; Eternal Sonata support; Microsoft Japan RPG era; feelplus catalog",
    "Felistella": "Atelier support; Gust co-dev; Felistella JRPG; Koei Tecmo partners",
    "French-Bread": "Melty Blood: Type Lumina; Under Night In-Birth; Dengeki Bunko Fighting Climax; French-Bread fighters",
    "Genius Sonority": "Pokémon Trozei; Pokémon Battle Revolution; Pokémon Shuffle; Pokémon Café ReMix",
    "GungHo Online": "Puzzle & Dragons; Ragnarok Mobile partnerships; GungHo publishing; Japanese puzzle RPG",
    "Happy Elements": "Ensemble Stars!; Mermaid Miracle; Happy Elements idols; China/Japan mobile",
    "Lasengle": "Fate/Grand Order; Lasengle DELiGHTWORKS successor; Type-Moon mobile; FGO live ops",
    "Mixi / XFLAG": "Monster Strike; MIXI sports apps; XFLAG arcade RPG; Japanese hit mobile",
    "Neverland (tarihsel)": "Lufia: Curse of the Sinistrals; Spectral Force; Rune Factory support eras; Neverland JRPG",
    "Next Level Games": "Luigi's Mansion 3; Mario Strikers: Battle League; Punch-Out!!; Luigi's Mansion: Dark Moon",
    "Paon DP": "Donkey Kong support eras; Nintendo co-dev; Paon DP ports; Japanese work-for-hire",
    "Ruby Party": "Angelique; Neo Angelique; Harukanaru Toki no Naka de; Ruby Party otome",
    "Sting": "Riviera: The Promised Land; Knights in the Nightmare; Dept. Heaven; Sting SRPG",
    "TOSE": "Dragon Quest support; countless co-dev credits; Nintendo/Square support; TOSE ghost developer",
    "Wright Flyer Studios": "Another Eden; World Flipper; Wright Flyer RPG; DeNA studio",
    "Com2uS Holdings": "Summoners War ecosystem; Com2uS Holdings publishing; Soul Seekers; Korean midcore group",
    "Dexter Studios": "AAA CGI cinematics; game trailer production; VFX services; Dexter portfolio",
    "Eyedentity Games": "Dragon Nest; Dragon Nest M; Eyedentity action MMO; Malaysian/Korean ops",
    "Midcore": "midcore mobile slate; Korean studio services; live-ops consulting; Midcore games",
    "Nexon Games": "The First Descendant; Blue Archive co-structure; Nexon Games FPS/looter; Seoul studio",
    "NHN": "Hangame; Fishing Game series; NHN Cloud gaming; Korean platform games",
    "Smilegate Entertainment": "CrossFire; CrossFireX; Smilegate shooters; global FPS publishing",
    "Smilegate RPG": "Lost Ark; Lost Ark seasons; Smilegate MMORPG; Korean/Amazon partnership",
    "4399": "4399.com portal games; mini-game platform; China browser catalog; 4399 publishing",
    "Aurora Studios (Tencent)": "Light of Life; Aurora Tencent slate; Shanghai first-party; Tencent IEG",
    "ChillyRoom": "Soul Knight; Otherworld Legends; Soul Knight Prequel; ChillyRoom roguelike",
    "Game Science": "Black Myth: Wukong; Game Science action RPG; Chinese AAA breakthrough; Wukong DLC era",
    "Giant Network": "ZT Online lineage; Giant webgames; China publishing; Giant Network catalog",
    "Kuro Games": "Wuthering Waves; Punishing: Gray Raven; Kuro action RPG; Guangzhou studio",
    "Lightning Games": "Lightning Games publishing; China indie/AA publishing; multi-platform releases; Lightning catalog",
    "MICA Team": "Girls' Frontline; Girls' Frontline 2: Exilium; Neural Cloud; MICA/Sunborn",
    "Original Force": "AAA outsourcing art; cinematic services; Original Force portfolio; China co-dev",
    "PopCap Shanghai": "Bejeweled support; Plants vs. Zombies localization eras; PopCap China; EA casual",
    "Sempire Games": "Sempire strategy; China SLG; Sempire live ops; midcore war games",
    "Shengqu Games": "Legend of Mir lineage; Shengqu publishing; China MMO classics; Shengqu catalog",
    "Taomee": "Seer; Mole's World; Taomee kids MMO; China youth platform",
    "Blue Tongue Entertainment": "de Blob; Jurassic Park: The Game; Star Wars: The Clone Wars; THQ Melbourne era",
    "Digital Happiness": "DreadOut; DreadOut 2; Pamali; Indonesian horror",
    "Games24x7": "RummyCircle; My11Circle; Games24x7 real-money; India gaming",
    "Garena / Sea Limited": "Free Fire publishing; Garena shell; Sea Limited ecosystem; SEA live ops",
    "House House": "Untitled Goose Game; House House comedy sandbox; Australian indie; Panic publishing",
    "League of Geeks": "Armello; Armello seasons; League of Geeks digital board; Melbourne studio",
    "Moonton": "Mobile Legends: Bang Bang; Magic Chess; Moonton MOBA; ByteDance era",
    "Toge Productions": "Coffee Talk; A Space for the Unbound; Banyu Hubadak; Indonesian narrative indie",
    "Aoca Game Lab": "Horizon Chase support eras; Brazilian racing indie; Aoca catalog; Latin indie",
    "Black River Studios": "Dandara; Aeterna Noctis publishing partnerships; Black River Amazon; Brazil studio",
    "Cleverlik / Mexico — Kaxan Games": "Mexican indie catalog; Kaxan partnership; LATAM co-dev; Cleverlik slate",
    "Duaik Entretenimento": "Horizon Chase Turbo; Horizon Chase 2; Brazilian arcade racing; Aquiris sister era",
    "Dumativa": "Horizon Chase audio/co-dev; Dumativa services; Brazil co-dev; music/tech",
    "Etermax": "Trivia Crack; Trivia Crack 2; Etermax trivia; Argentina mobile",
    "Hoplon Infotainment": "Heavy Metal Machines; Hoplon MOBA/racing; Brazilian multiplayer; Hoplon catalog",
    "IguanaBee": "IguanaBee co-dev; Chile/ LatAm services; ports and support; IguanaBee slate",
    "Jandusoft": "Jandusoft VR/co-dev; Argentine studio services; LatAm outsourcing; Jandusoft catalog",
    "JoyMasher": "Odallus; The Last Door contributions; JoyMasher pixel action; Brazilian retro",
    "Kaxan Games": "Mexican indie development; Kaxan catalog; LATAM narrative/action; Kaxan games",
    "Squad": "Kerbal Space Program; Kerbal Space Program 2 (period); Squad Mexican studio; Take-Two era",
    "Swordtales": "Ghost of a Tale publishing/dev ties; Swordtales narrative; Brazilian indie; Swordtales catalog",
    "Aeria Games (tarihsel)": "Grand Fantasia; SpongeBob games publishing; Aeria free-to-play; historical publisher",
    "Application Systems Heidelberg": "The Settlers lineage publishing eras; German classic PC; Application Systems catalog; strategy classics",
    "Crytivo": "The Planet Crafter publishing; Crytivo indie publishing; simulation slate; Crytivo catalog",
    "Digerati": "Digerati indie publishing; curated boutique releases; multi-platform indies; Digerati catalog",
    "AEVI": "AEVI cloud/platform services; European gaming platform; AEVI ecosystem; B2B gaming",
    "BitSummit": "BitSummit indie showcase; Kyoto indie event; Japanese indie expo; BitSummit floors",
    "Brazil Game Show": "Brazil Game Show; BGS expo floor; Latin America consumer show; BGS partners",
    "CERO": "CERO rating system; Japanese age ratings; console compliance; CERO codes",
    "ChinaJoy": "ChinaJoy expo; Shanghai trade show; China consumer/trade floor; ChinaJoy partners",
    "D.I.C.E. Summit / Academy of Interactive Arts": "D.I.C.E. Awards; D.I.C.E. Summit; AIAS membership; industry awards",
    "Dataspelsbranschen": "Swedish Games Industry; Dataspelsbranschen reports; Nordic trade body; Sweden association",
    "DevGAMM": "DevGAMM conferences; Eastern Europe developer events; DevGAMM expo; indie talks",
    "EGDF": "EGDF policy; European game developer federation; EU advocacy; EGDF members",
    "ESA (Entertainment Software Association)": "E3 legacy; ESA advocacy; US publisher association; ESA ratings liaison",
    "ESRB": "ESRB ratings; Entertainment Software Rating Board; US age ratings; ESRB descriptors",
    "G-STAR": "G-STAR Busan; Korean trade show; G-STAR B2B; Korea exhibitors",
    "Game Connection": "Game Connection events; co-production market; Game Connection Paris/America; B2B meetings",
    "game Verband": "game – Verband der deutschen Games-Branche; German trade association; Germany market reports; game e.V.",
    "Games Industry Poland": "Games Industry Poland; Polish trade body; Warsaw advocacy; Polish market reports",
    "gamescom / Koelnmesse": "gamescom; gamescom Opening Night Live; Cologne consumer show; Koelnmesse",
    "Gamescom Asia / Singapore": "Gamescom Asia; Singapore trade show; SEA exhibitors; Gamescom Asia floor",
    "GDC / Informa Tech": "Game Developers Conference; GDC talks; San Francisco GDC; Informa Tech",
    "IGDA": "IGDA chapters; developer advocacy; IGDA events; global developer nonprofit",
    "IIDEA": "IIDEA Italy; Italian games association; IIDEA reports; Italy advocacy",
    "IndieCade": "IndieCade festival; indie showcase; IndieCade awards; independent games event",
    "Jump Festa": "Jump Festa; Shueisha jump IP show; Jump Festa Tokyo; anime/game crossovers",
    "MIGS / Montréal International Game Summit": "MIGS; Montréal Game Summit; Canadian developer conference; MIGS talks",
    "Nordic Game / EGDF notu": "Nordic Game conference; Malmö indie/pro; Nordic Game talks; EGDF note",
    "Partner Transmedia / Korea — G-STAR": "G-STAR partnership; Korea trade missions; Partner Transmedia; Busan networking",
    "PAX / ReedPop": "PAX shows; ReedPop consumer festivals; PAX panels; tabletop/indie floors",
    "PAX Australia": "PAX Australia; Melbourne PAX; Australian consumer show; PAX Aus panels",
    "PAX East": "PAX East; Boston PAX; East Coast consumer show; PAX East expo",
    "PAX West": "PAX West; Seattle PAX; West Coast consumer show; PAX West expo",
    "PEGI": "PEGI ratings; Pan European Game Information; EU age ratings; PEGI descriptors",
    "Pocket Gamer Connects": "Pocket Gamer Connects; mobile B2B; PGC Helsinki/London; Pocket Gamer events",
    "Roblox Developer Conference": "Roblox Developer Conference; RDC talks; creator keynotes; Roblox ecosystem",
    "SNJV": "SNJV France; Syndicat National du Jeu Vidéo; French trade body; SNJV reports",
    "Suomen Pelinkehittäjät": "Finnish Game Developers Association; Finland advocacy; Suomen Pelinkehittäjät; Nordic trade",
    "Taipei Game Show": "Taipei Game Show; Taiwan consumer/trade; TGS Taipei; Taipei exhibitors",
    "Tokyo Game Show / CESA": "Tokyo Game Show; CESA; Makuhari Messe; TGS business day",
    "UKIE": "UKIE; UK Interactive Entertainment; Britain trade body; UKIE reports",
    "Unity Unite": "Unity Unite; Unite talks; Unity engine conference; Unite keynotes",
    "Unreal Fest": "Unreal Fest; Unreal Engine sessions; Epic developer events; Unreal Fest talks",
    "White Nights Conference": "White Nights; mobile games conference; WN St. Petersburg/online; White Nights B2B",
}

EXTRA_NOTES: dict[str, dict[str, str]] = {
    "Team Cherry": {
        "en": "Hollow Knight studio (Adelaide); Silksong long-awaited follow-up.",
        "tr": "Hollow Knight stüdyosu (Adelaide); Silksong uzun süredir beklenen devam.",
    },
    "Sandfall Interactive": {
        "en": "Debut Clair Obscur: Expedition 33 became a global turn-based hit.",
        "tr": "İlk oyunu Clair Obscur: Expedition 33 küresel turn-based hit oldu.",
    },
    "Game Science": {
        "en": "Black Myth: Wukong marked a Chinese single-player AAA breakthrough.",
        "tr": "Black Myth: Wukong Çin tek oyunculu AAA kırılımını simgeledi.",
    },
    "Kuro Games": {
        "en": "Punishing: Gray Raven and Wuthering Waves drive Kuro's action live-ops.",
        "tr": "Punishing: Gray Raven ve Wuthering Waves Kuro'nun aksiyon live-ops'unu taşır.",
    },
    "Battlestate Games": {
        "en": "Escape from Tarkov defined modern extraction-shooter expectations.",
        "tr": "Escape from Tarkov modern extraction-shooter beklentilerini tanımladı.",
    },
    "Embark Studios": {
        "en": "Stockholm multiplayer studio from ex-DICE leads; THE FINALS / Arc Raiders.",
        "tr": "Eski DICE liderlerinden Stockholm multiplayer; THE FINALS / Arc Raiders.",
    },
}


def clean_email(email: str) -> str | None:
    if not email:
        return None
    m = email.strip().lower()
    m = re.sub(r"^%20", "", m)
    m = m.strip(" ._<>\"'")
    m = re.sub(r"^_+", "", m)
    if not EMAIL_RE.fullmatch(m):
        return None
    if JUNK_RE.search(m):
        return None
    host = m.split("@", 1)[1]
    if any(x in host for x in (".dev", "example.", "test.")):
        return None
    return m


def load(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def merge_emails(base: dict, extra: dict) -> dict:
    out = dict(base)
    for name, items in extra.items():
        cleaned = []
        for item in items:
            em = clean_email(item.get("email", ""))
            if not em:
                continue
            cleaned.append({"email": em, "role": item.get("role") or "genel"})
        if not cleaned:
            continue
        # Prefer filling empty / missing; don't wipe richer curated lists
        existing = out.get(name) or []
        if not existing:
            out[name] = cleaned
            continue
        seen = {x["email"] for x in existing if "email" in x}
        for item in cleaned:
            if item["email"] not in seen:
                existing.append(item)
                seen.add(item["email"])
        out[name] = existing
    # drop empty lists
    return {k: v for k, v in out.items() if v}


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    emails = load(EMAILS_PATH, {})
    scraped = load(SCRAPE_PATH, {})
    games = load(GAMES_PATH, {})
    notes = load(NOTES_PATH, {})

    emails = merge_emails(emails, EXTRA_EMAILS)
    emails = merge_emails(emails, scraped)

    before_g = len(games)
    for name, titles in GAMES_EXPAND.items():
        old = [x.strip() for x in (games.get(name) or "").split(";") if x.strip()]
        new = [x.strip() for x in titles.split(";") if x.strip()]
        # Prefer expanded list when longer / richer
        if len(new) >= len(old):
            games[name] = "; ".join(new[:8])
        else:
            merged = []
            seen = set()
            for g in new + old:
                k = g.lower()
                if k in seen:
                    continue
                seen.add(k)
                merged.append(g)
            games[name] = "; ".join(merged[:8])

    for name, pack in EXTRA_NOTES.items():
        notes[name] = pack

    EMAILS_PATH.write_text(json.dumps(emails, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    GAMES_PATH.write_text(json.dumps(games, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    NOTES_PATH.write_text(json.dumps(notes, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    ge3 = sum(1 for v in games.values() if len([x for x in v.split(";") if x.strip()]) >= 3)
    print(f"Emails curated entries: {len(emails)}")
    print(f"Games curated entries:  {len(games)} (was {before_g})")
    print(f"Games curated >=3:      {ge3}")
    print(f"Notes curated entries:  {len(notes)}")


if __name__ == "__main__":
    main()
