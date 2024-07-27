class Message:
    def __init__(self, user : str, msg_id : int, content : str):
        self.__user = user
        self.__id = msg_id
        self.__replies = []
        self.__content = content
        self.__likes = 0
        self.__liked = False

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

    @likes.setter
    def likes(self, likes : int):
        self.__likes = likes

    @property
    def liked(self) -> bool:
        return self.__liked

    @liked.setter
    def liked(self, liked : bool):
        self.__liked = liked
