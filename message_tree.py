class Message:
    def __init__(self, content : str):
        self.__replies = []
        self.__content = content

    @property
    def replies(self):
        return self.__replies

    def add_reply(self, reply):
        self.__replies.append(reply)

    @property
    def content(self) -> str:
        return self.__content
