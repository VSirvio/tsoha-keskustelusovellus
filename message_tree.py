class Message:
    def __init__(self, user : str, id : int, content : str, likes : int, liked : bool):
        self.__user = user
        self.__id = id
        self.__replies = []
        self.__content = content
        self.__likes = likes
        self.__liked = liked

    @property
    def user(self) -> str:
        return self.__user

    @property
    def id(self) -> int:
        return self.__id

    @property
    def replies(self):
        return self.__replies

    def add_reply(self, reply):
        self.__replies.append(reply)

    @property
    def content(self) -> str:
        return self.__content

    @property
    def likes(self) -> int:
        return self.__likes

    @property
    def liked(self) -> bool:
        return self.__liked
