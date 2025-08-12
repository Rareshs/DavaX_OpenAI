book_summaries_dict = {
    "1984": (
        "A dystopian story about a totalitarian society controlled by surveillance, "
        "propaganda, and thought police. Winston Smith, the protagonist, secretly rebels against the system "
        "in search of truth and freedom. Themes: surveillance, control, rebellion."
    ),
    "The Hobbit": (
        "Bilbo Baggins, a timid hobbit, embarks on an unexpected adventure with dwarves "
        "to reclaim their homeland from a dragon. Along the way, he discovers courage, friendship, "
        "and the thrill of exploration. Themes: adventure, friendship, self-discovery."
    ),
    "To Kill a Mockingbird": (
        "Set in the racially charged South, the novel follows young Scout Finch as her father, "
        "a lawyer, defends a black man falsely accused of rape. Themes: justice, racism, childhood innocence."
    ),
    "The Great Gatsby": (
        "A tale of ambition and love in the Roaring Twenties, told through the eyes of Nick Carraway. "
        "Gatsby’s pursuit of Daisy reveals the emptiness behind the American Dream. Themes: wealth, illusion, longing."
    ),
    "Pride and Prejudice": (
        "Elizabeth Bennet navigates society, love, and class as she meets the proud Mr. Darcy. "
        "Themes: social norms, love, personal growth."
    ),
    "Brave New World": (
        "In a future society based on consumerism and control, individuality is suppressed for the sake of stability. "
        "Bernard Marx seeks meaning in a dehumanized world. Themes: conformity, technology, individuality."
    ),
    "Moby-Dick": (
        "Captain Ahab’s obsession with a great white whale drives his crew toward doom. "
        "Themes: obsession, revenge, nature vs. man."
    ),
    "Harry Potter and the Sorcerer's Stone": (
        "A young boy discovers he is a wizard and attends Hogwarts, making friends and facing danger in his first year. "
        "Themes: friendship, courage, self-discovery, magic."
    ),
    "Fahrenheit 451": (
        "In a world where books are banned, firemen burn them. Montag begins to question his role and society. "
        "Themes: censorship, knowledge, rebellion."
    ),
    "The Alchemist": (
        "Santiago, a shepherd, dreams of finding treasure in Egypt. On his journey, he learns to follow his heart "
        "and embrace the Soul of the World. Themes: destiny, self-discovery, faith."
    ),
    "All Quiet on the Western Front": (
        "Paul Bäumer, a young German soldier, enlists in World War I alongside his classmates, driven by patriotism and youthful enthusiasm. "
        "However, he is soon confronted by the brutal horrors of trench warfare: constant bombardments, meaningless slaughter, and the psychological toll of surviving while others die. "
        "As the war drags on, Paul becomes emotionally numb and increasingly detached from civilian life, realizing that the glory of war is a lie. "
        "The novel is a stark, honest portrayal of the trauma and futility experienced by a generation of soldiers. "
        "Themes: war, trauma, disillusionment, death, isolation."
    )
}

def get_summary_by_title(title: str) -> str:
    return book_summaries_dict.get(title, "Summary not available for this title.")
