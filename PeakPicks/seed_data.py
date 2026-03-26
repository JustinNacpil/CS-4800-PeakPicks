"""
Run: python seed_data.py
Or visit /seed in the running app.
Seeds community tier lists into the tierlists collection.
"""
import os
from datetime import datetime
from pymongo import MongoClient
from werkzeug.security import generate_password_hash

def seed():
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI is not set.")
    client = MongoClient(uri)
    db = client[os.getenv("MONGODB_DB", "peakpicks")]

    # Create or find community user
    community = db.users.find_one({"username": "PeakPicks"})
    if not community:
        result = db.users.insert_one({
            "username": "PeakPicks",
            "email": "community@peakpicks.app",
            "password_hash": generate_password_hash("notarealpassword"),
            "bio": "Official PeakPicks community tier lists.",
            "avatar_color": "#6366f1",
            "created_at": datetime.utcnow().isoformat() + "Z",
        })
        community_id = str(result.inserted_id)
    else:
        community_id = str(community["_id"])

    # Check if already seeded
    if db.tierlists.count_documents({"created_by_username": "PeakPicks"}) > 5:
        print("Already seeded. Skipping.")
        return 0

    TIER_LISTS = [
        {
            "title": "Ultimate Movie Rankings",
            "category": "Movies",
            "scale_type": "classic",
            "picks": [
                {"rank": "S", "name": "The Godfather", "reason": "The greatest film ever made. Masterclass in storytelling.", "image_url": "", "tags": ["drama", "classic"]},
                {"rank": "S", "name": "The Dark Knight", "reason": "Heath Ledger's Joker is untouchable.", "image_url": "", "tags": ["action", "superhero"]},
                {"rank": "A", "name": "Inception", "reason": "Mind-bending sci-fi at its best.", "image_url": "", "tags": ["sci-fi", "thriller"]},
                {"rank": "A", "name": "Pulp Fiction", "reason": "Tarantino's magnum opus.", "image_url": "", "tags": ["drama", "cult"]},
                {"rank": "A", "name": "Interstellar", "reason": "Visually stunning, emotionally devastating.", "image_url": "", "tags": ["sci-fi", "space"]},
                {"rank": "B", "name": "The Matrix", "reason": "Revolutionized action cinema.", "image_url": "", "tags": ["sci-fi", "action"]},
                {"rank": "B", "name": "Fight Club", "reason": "A cult classic for a reason.", "image_url": "", "tags": ["drama", "cult"]},
                {"rank": "B", "name": "Forrest Gump", "reason": "Heartwarming and iconic.", "image_url": "", "tags": ["drama", "classic"]},
                {"rank": "C", "name": "Avatar", "reason": "Great visuals, thin plot.", "image_url": "", "tags": ["sci-fi", "visual"]},
                {"rank": "C", "name": "Titanic", "reason": "Overhyped but still a spectacle.", "image_url": "", "tags": ["romance", "drama"]},
                {"rank": "D", "name": "Twilight", "reason": "Sparkly vampires? No thanks.", "image_url": "", "tags": ["romance", "fantasy"]},
            ]
        },
        {
            "title": "Best TV Shows Ever",
            "category": "TV Shows",
            "scale_type": "classic",
            "picks": [
                {"rank": "S", "name": "Breaking Bad", "reason": "The gold standard of TV drama.", "image_url": "", "tags": ["drama", "crime"]},
                {"rank": "S", "name": "The Wire", "reason": "The most realistic show ever made.", "image_url": "", "tags": ["drama", "crime"]},
                {"rank": "A", "name": "Game of Thrones", "reason": "Peak TV until the last season.", "image_url": "", "tags": ["fantasy", "drama"]},
                {"rank": "A", "name": "The Sopranos", "reason": "Changed television forever.", "image_url": "", "tags": ["drama", "crime"]},
                {"rank": "A", "name": "Stranger Things", "reason": "Nostalgia done right.", "image_url": "", "tags": ["sci-fi", "horror"]},
                {"rank": "B", "name": "The Office", "reason": "Endlessly rewatchable comedy.", "image_url": "", "tags": ["comedy", "mockumentary"]},
                {"rank": "B", "name": "Friends", "reason": "A classic sitcom comfort show.", "image_url": "", "tags": ["comedy", "classic"]},
                {"rank": "C", "name": "Grey's Anatomy", "reason": "Too many seasons but still addictive.", "image_url": "", "tags": ["medical", "drama"]},
                {"rank": "D", "name": "Riverdale", "reason": "Started strong, went completely off the rails.", "image_url": "", "tags": ["teen", "drama"]},
            ]
        },
        {
            "title": "Video Games GOAT List",
            "category": "Video Games",
            "scale_type": "classic",
            "picks": [
                {"rank": "S", "name": "Zelda: Breath of the Wild", "reason": "Redefined open-world gaming.", "image_url": "", "tags": ["adventure", "open-world"]},
                {"rank": "S", "name": "Elden Ring", "reason": "FromSoftware's masterpiece.", "image_url": "", "tags": ["rpg", "souls-like"]},
                {"rank": "A", "name": "God of War Ragnarok", "reason": "Incredible story and combat.", "image_url": "", "tags": ["action", "story"]},
                {"rank": "A", "name": "Red Dead Redemption 2", "reason": "Arthur Morgan is unforgettable.", "image_url": "", "tags": ["western", "open-world"]},
                {"rank": "A", "name": "The Witcher 3", "reason": "The RPG all others are measured against.", "image_url": "", "tags": ["rpg", "fantasy"]},
                {"rank": "B", "name": "Minecraft", "reason": "Infinite creativity in block form.", "image_url": "", "tags": ["sandbox", "creative"]},
                {"rank": "B", "name": "GTA V", "reason": "Still going strong after 10+ years.", "image_url": "", "tags": ["open-world", "crime"]},
                {"rank": "C", "name": "Fortnite", "reason": "Fun but repetitive.", "image_url": "", "tags": ["battle-royale", "shooter"]},
                {"rank": "D", "name": "Cyberpunk 2077 (Launch)", "reason": "Broken launch, decent after patches.", "image_url": "", "tags": ["rpg", "sci-fi"]},
            ]
        },
        {
            "title": "Anime Worth Watching",
            "category": "Anime",
            "scale_type": "worth_it",
            "picks": [
                {"rank": "S", "name": "Attack on Titan", "reason": "The ending divided fans, but the journey was epic.", "image_url": "", "tags": ["action", "dark"]},
                {"rank": "S", "name": "Fullmetal Alchemist: Brotherhood", "reason": "Near-perfect storytelling.", "image_url": "", "tags": ["action", "story"]},
                {"rank": "A", "name": "Death Note", "reason": "The cat-and-mouse thriller that hooked millions.", "image_url": "", "tags": ["thriller", "psychological"]},
                {"rank": "A", "name": "Demon Slayer", "reason": "Gorgeous animation and great fights.", "image_url": "", "tags": ["action", "supernatural"]},
                {"rank": "A", "name": "One Piece", "reason": "The greatest adventure anime.", "image_url": "", "tags": ["adventure", "long-running"]},
                {"rank": "B", "name": "Naruto", "reason": "Believe it! A classic despite filler.", "image_url": "", "tags": ["action", "classic"]},
                {"rank": "B", "name": "My Hero Academia", "reason": "Superhero anime done well.", "image_url": "", "tags": ["action", "superhero"]},
                {"rank": "C", "name": "Sword Art Online", "reason": "Cool concept, poor execution.", "image_url": "", "tags": ["isekai", "action"]},
                {"rank": "D", "name": "Berserk 2016", "reason": "The CGI ruined an amazing manga.", "image_url": "", "tags": ["dark", "fantasy"]},
            ]
        },
        {
            "title": "Music Artists Ranked",
            "category": "Music Artists",
            "scale_type": "slider",
            "picks": [
                {"rank": "S", "name": "Kendrick Lamar", "reason": "The greatest lyricist alive.", "image_url": "", "tags": ["rap", "lyricist"]},
                {"rank": "S", "name": "Kanye West", "reason": "Genius producer, controversial person.", "image_url": "", "tags": ["rap", "producer"]},
                {"rank": "A", "name": "Drake", "reason": "Dominates the charts consistently.", "image_url": "", "tags": ["rap", "r&b"]},
                {"rank": "A", "name": "Tyler the Creator", "reason": "Evolved more than any artist.", "image_url": "", "tags": ["rap", "experimental"]},
                {"rank": "A", "name": "Travis Scott", "reason": "Created his own sonic universe.", "image_url": "", "tags": ["rap", "trap"]},
                {"rank": "B", "name": "The Weeknd", "reason": "R&B king of the decade.", "image_url": "", "tags": ["r&b", "pop"]},
                {"rank": "B", "name": "Billie Eilish", "reason": "Defined Gen-Z music.", "image_url": "", "tags": ["pop", "indie"]},
                {"rank": "C", "name": "Ed Sheeran", "reason": "Solid but overplayed.", "image_url": "", "tags": ["pop", "folk"]},
                {"rank": "D", "name": "Nickelback", "reason": "The punching bag of rock.", "image_url": "", "tags": ["rock", "meme"]},
            ]
        },
        {
            "title": "Fast Food Bracket Battle",
            "category": "Fast Food",
            "scale_type": "bracket",
            "picks": [
                {"rank": "S", "name": "Chick-fil-A", "reason": "The chicken sandwich GOAT.", "image_url": "", "tags": ["chicken", "american"]},
                {"rank": "S", "name": "In-N-Out", "reason": "Simple menu, perfect execution.", "image_url": "", "tags": ["burgers", "west-coast"]},
                {"rank": "A", "name": "Raising Cane's", "reason": "Best chicken fingers, period.", "image_url": "", "tags": ["chicken", "simple"]},
                {"rank": "A", "name": "Chipotle", "reason": "Build-your-own burrito perfection.", "image_url": "", "tags": ["mexican", "fresh"]},
                {"rank": "A", "name": "Five Guys", "reason": "Burgers and fries done right.", "image_url": "", "tags": ["burgers", "premium"]},
                {"rank": "B", "name": "McDonald's", "reason": "The OG fast food. Consistent worldwide.", "image_url": "", "tags": ["classic", "global"]},
                {"rank": "B", "name": "Popeyes", "reason": "That chicken sandwich changed the game.", "image_url": "", "tags": ["chicken", "cajun"]},
                {"rank": "C", "name": "Burger King", "reason": "Always the backup option.", "image_url": "", "tags": ["burgers", "basic"]},
                {"rank": "D", "name": "Arby's", "reason": "We have the meats... but who asked?", "image_url": "", "tags": ["roast-beef", "niche"]},
            ]
        },
        {
            "title": "Sneaker Rankings",
            "category": "Sneakers",
            "scale_type": "classic",
            "picks": [
                {"rank": "S", "name": "Jordan 1 Chicago", "reason": "The sneaker that started it all.", "image_url": "", "tags": ["jordan", "basketball", "classic"]},
                {"rank": "S", "name": "Yeezy 350 V2", "reason": "Changed sneaker culture forever.", "image_url": "", "tags": ["adidas", "hype", "kanye"]},
                {"rank": "A", "name": "Air Force 1", "reason": "Clean, classic, timeless.", "image_url": "", "tags": ["nike", "classic", "lifestyle"]},
                {"rank": "A", "name": "Nike Dunk Low", "reason": "The comeback king.", "image_url": "", "tags": ["nike", "streetwear", "hype"]},
                {"rank": "B", "name": "Converse Chuck Taylor", "reason": "Simple and stylish.", "image_url": "", "tags": ["classic", "casual", "affordable"]},
                {"rank": "C", "name": "Adidas Stan Smith", "reason": "Clean but overdone.", "image_url": "", "tags": ["adidas", "tennis", "minimalist"]},
                {"rank": "D", "name": "Crocs", "reason": "Comfort over style? Debatable.", "image_url": "", "tags": ["controversial", "comfort"]},
            ]
        },
        {
            "title": "Best Tech Right Now",
            "category": "Tech",
            "scale_type": "worth_it",
            "picks": [
                {"rank": "S", "name": "iPhone 15 Pro", "reason": "The most polished smartphone experience.", "image_url": "", "tags": ["apple", "phone", "premium"]},
                {"rank": "S", "name": "MacBook Pro M3", "reason": "Laptop performance king.", "image_url": "", "tags": ["apple", "laptop", "powerful"]},
                {"rank": "A", "name": "PS5", "reason": "Next-gen gaming powerhouse.", "image_url": "", "tags": ["sony", "gaming", "console"]},
                {"rank": "A", "name": "Steam Deck", "reason": "PC gaming on the go.", "image_url": "", "tags": ["valve", "gaming", "handheld"]},
                {"rank": "B", "name": "Nintendo Switch", "reason": "Portability meets fun.", "image_url": "", "tags": ["nintendo", "gaming", "portable"]},
                {"rank": "B", "name": "iPad Pro", "reason": "The tablet to beat.", "image_url": "", "tags": ["apple", "tablet", "creative"]},
                {"rank": "C", "name": "Microsoft Surface", "reason": "Good hardware, Windows bloat.", "image_url": "", "tags": ["microsoft", "laptop", "2-in-1"]},
                {"rank": "D", "name": "BlackBerry", "reason": "Rest in peace, physical keyboard.", "image_url": "", "tags": ["dead", "classic", "keyboard"]},
            ]
        },
        {
            "title": "Sports Teams All Time",
            "category": "Sports Teams",
            "scale_type": "classic",
            "picks": [
                {"rank": "S", "name": "LA Lakers", "reason": "Showtime legacy lives on.", "image_url": "", "tags": ["nba", "basketball", "la"]},
                {"rank": "S", "name": "Real Madrid", "reason": "The most decorated club ever.", "image_url": "", "tags": ["soccer", "spanish", "champions"]},
                {"rank": "A", "name": "New England Patriots", "reason": "The Brady dynasty.", "image_url": "", "tags": ["nfl", "football", "dynasty"]},
                {"rank": "A", "name": "New York Yankees", "reason": "27 world series rings.", "image_url": "", "tags": ["mlb", "baseball", "classic"]},
                {"rank": "B", "name": "Golden State Warriors", "reason": "The dynasty of the 2010s.", "image_url": "", "tags": ["nba", "basketball", "dynasty"]},
                {"rank": "B", "name": "FC Barcelona", "reason": "Messi's home club.", "image_url": "", "tags": ["soccer", "spanish", "messi"]},
                {"rank": "C", "name": "New York Knicks", "reason": "More hype than wins.", "image_url": "", "tags": ["nba", "basketball", "ny"]},
                {"rank": "D", "name": "Jacksonville Jaguars", "reason": "Perpetual underdogs.", "image_url": "", "tags": ["nfl", "football", "underdog"]},
            ]
        },
        {
            "title": "Food Tier List",
            "category": "Food",
            "scale_type": "worth_it",
            "picks": [
                {"rank": "S", "name": "Pizza", "reason": "The perfect food. Fight me.", "image_url": "", "tags": ["italian", "universal"]},
                {"rank": "S", "name": "Sushi", "reason": "Art on a plate.", "image_url": "", "tags": ["japanese", "raw-fish"]},
                {"rank": "A", "name": "Tacos", "reason": "Versatile and always delicious.", "image_url": "", "tags": ["mexican", "street-food"]},
                {"rank": "A", "name": "Ramen", "reason": "Soul-warming perfection.", "image_url": "", "tags": ["japanese", "noodles"]},
                {"rank": "A", "name": "Burgers", "reason": "An American classic done right.", "image_url": "", "tags": ["american", "grilled"]},
                {"rank": "B", "name": "Pasta", "reason": "Comfort food done right.", "image_url": "", "tags": ["italian", "comfort"]},
                {"rank": "B", "name": "Fried Chicken", "reason": "Crispy, juicy, irresistible.", "image_url": "", "tags": ["southern", "comfort"]},
                {"rank": "C", "name": "Salad", "reason": "Healthy but boring.", "image_url": "", "tags": ["healthy", "boring"]},
                {"rank": "D", "name": "Liver", "reason": "An acquired taste nobody acquires.", "image_url": "", "tags": ["organ", "acquired-taste"]},
            ]
        },
    ]

    now = datetime.utcnow().isoformat() + "Z"
    docs = []
    for tl in TIER_LISTS:
        docs.append({
            "title": tl["title"],
            "category": tl["category"],
            "scale_type": tl.get("scale_type", "classic"),
            "theme": "classic",
            "layout": "rows",
            "picks": tl["picks"],
            "is_draft": False,
            "created_by": community_id,
            "created_by_username": "PeakPicks",
            "created_at": now,
            "updated_at": now,
        })

    if docs:
        db.tierlists.insert_many(docs)

    print(f"Seeded {len(docs)} tier lists.")
    return len(docs)

if __name__ == "__main__":
    count = seed()
    print("Done!")
