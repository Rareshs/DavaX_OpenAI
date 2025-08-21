book_summaries_dict = {
    "1984": (
        "In a dystopian future ruled by the omnipresent Big Brother, individual freedom is obliterated through constant surveillance and thought control. "
        "Winston Smith, a low-ranking worker, begins to question the regime and dreams of rebellion and truth. "
        "As he falls in love and seeks personal freedom, he confronts the terrifying consequences of defiance. "
        
    ),
    "The Hobbit": (
        "Bilbo Baggins, a comfort-loving hobbit, is swept into a grand quest with a group of dwarves to reclaim their homeland from the dragon Smaug. "
        "Reluctant at first, Bilbo discovers his own courage and cleverness in battles, riddles, and dark forests. "
        "This prelude to The Lord of the Rings is filled with magic, monsters, and moral growth. "
        
    ),
    "To Kill a Mockingbird": (
        "Set in 1930s Alabama, young Scout Finch witnesses the harsh realities of racial injustice as her father, Atticus, defends a Black man falsely accused of rape. "
        "Through her innocent eyes, we explore prejudice, honor, and moral complexity in a divided society. "
        "The novel blends childhood wonder with adult injustice in a powerful coming-of-age story. "
        
    ),
    "The Great Gatsby": (
        "Narrated by Nick Carraway, this novel follows Jay Gatsby, a mysterious millionaire obsessed with rekindling his past love for Daisy Buchanan. "
        "Set in the opulent, shallow 1920s, Gatsby’s glamorous parties mask the emptiness of the American Dream. "
        "It's a tale of illusion, longing, and the consequences of obsessive idealism. "
        
    ),
    "Pride and Prejudice": (
        "Elizabeth Bennet, a smart and independent young woman, clashes with the proud and reserved Mr. Darcy in a world dominated by class and social expectations. "
        "Through misunderstandings, wit, and eventual understanding, they overcome their prejudices. "
        "A timeless romantic satire that explores love, reputation, and personal growth. "
        
    ),
    "Brave New World": (
        "In a technologically advanced society where pleasure and conformity are mandatory, individuals are manufactured and conditioned to serve the collective. "
        "Bernard Marx and others begin to question their purpose in a world without love, family, or choice. "
        "The novel critiques blind consumerism, dehumanization, and the cost of artificial happiness. "
       
    ),
    "Moby-Dick": (
        "Captain Ahab embarks on a monomaniacal pursuit of Moby Dick, the great white whale that once maimed him. "
        "Told by Ishmael, a sailor aboard the doomed ship Pequod, the journey dives deep into themes of revenge, fate, and madness. "
        "A philosophical sea-epic exploring man’s struggle against nature and obsession. "
        
    ),
    "Harry Potter and the Sorcerer's Stone": (
        "Harry Potter, an orphan mistreated by his relatives, learns on his 11th birthday that he is a wizard. "
        "At Hogwarts School of Witchcraft and Wizardry, he makes friends, uncovers secrets, and faces the dark legacy of the villain who killed his parents. "
        "It’s the start of a magical journey filled with discovery, danger, and destiny. "
        
    ),
    "Fahrenheit 451": (
        "In a society where books are outlawed and critical thinking is suppressed, fireman Guy Montag burns books for a living. "
        "When he begins to question his role and the emptiness of his world, he seeks meaning in forbidden knowledge. "
        "This novel explores the power of ideas and the dangers of censorship and conformity. "
        
    ),
    "The Alchemist": (
        "Santiago, a young shepherd from Spain, dreams of treasure buried near the Egyptian pyramids. "
        "Guided by omens and wise mentors, he embarks on a journey of spiritual discovery, learning that true treasure lies in following one’s personal legend. "
        "A poetic fable about purpose, destiny, and faith in the universe. "
        
    ),
    "All Quiet on the Western Front": (
        "Paul Bäumer, a young German soldier, enlists in World War I filled with youthful enthusiasm. "
        "He soon confronts the brutal horrors of trench warfare, where idealism is shattered by death, fear, and psychological trauma. "
        "The novel is a haunting portrayal of a lost generation broken by war. "
        
    )
}


def get_summary_by_title(title: str) -> str:
    try:
        if not title or not isinstance(title, str):
            return "⚠️ Invalid book title provided."

        title_key = title.strip().lower()
        for key in book_summaries_dict:
            if key.strip().lower() == title_key:
                return book_summaries_dict[key].strip()

        return f"Summary not found for: '{title}'."
    except Exception as e:
        print(f"[ERROR] Failed to get summary for title '{title}': {e}")
        return "⚠️ An error occurred while retrieving the book summary."

