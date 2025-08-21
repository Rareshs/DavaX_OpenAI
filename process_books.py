# process_books.py

from rag_core import setup_chroma, parse_books, generate_id, get_embedding

try:
    collection = setup_chroma()
    if collection is None:
        raise Exception("ChromaDB collection could not be initialized.")

    books = parse_books("data/book_summ.txt")
    if not books:
        raise Exception("No books found or failed to parse book summaries.")

    for book in books:
        try:
            book_id = generate_id(book["title"])
            embedding = get_embedding(book["summary"])
            if not embedding:
                print(f"Warning: No embedding generated for '{book['title']}'. Skipping.")
                continue
            collection.add(
                documents=[book["summary"]],
                metadatas=[{"title": book["title"]}],
                ids=[book_id],
                embeddings=[embedding]
            )
        except Exception as e:
            print(f"Error adding book '{book['title']}': {e}")

    print("Vector store populat cu succes.")
    try:
        print(collection.peek(3))
    except Exception as e:
        print(f"Error peeking into collection: {e}")

except Exception as e:
    print(f"Fatal error: {e}")
