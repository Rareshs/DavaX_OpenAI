# process_books.py

from rag_core import setup_chroma, parse_books, generate_id, get_embedding

collection = setup_chroma()
books = parse_books("book_summ.txt")

for book in books:
    book_id = generate_id(book["title"])
    collection.add(
        documents=[book["summary"]],
        metadatas=[{"title": book["title"]}],
        ids=[book_id],
        embeddings=[get_embedding(book["summary"])]
    )

print("Vector store populat cu succes.")
print(collection.peek(5))
