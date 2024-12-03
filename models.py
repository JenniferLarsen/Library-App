class Book:
    def __init__(self, title, author, genre, chelsey_status="Unread", jenny_status="Unread"):
        self.title = title
        self.author = author
        self.genre = genre
        self.chelsey_status = chelsey_status
        self.jenny_status = jenny_status

    def to_dict(self):
        return {
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "chelsey_status": self.chelsey_status,
            "jenny_status": self.jenny_status,
        }

    @staticmethod
    def from_dict(data):
        return Book(
            title=data["title"],
            author=data["author"],
            genre=data["genre"],
            chelsey_status=data.get("chelsey_status", "Unread"),
            jenny_status=data.get("jenny_status", "Unread"),
        )

