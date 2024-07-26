class Message:
    def __init__(self, id : int, content : str):
        self.__id = id
        self.__replies = []
        self.__content = content

    @property
    def id(self):
        return self.__id

    @property
    def replies(self):
        return self.__replies

    def add_reply(self, reply):
        self.__replies.append(reply)

    @property
    def content(self) -> str:
        return self.__content
