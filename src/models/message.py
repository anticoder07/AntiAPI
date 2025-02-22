class Message:
    def __init__(self, content):
        self.content = content

    def to_dict(self):
        return {
            "content": self.content
        }