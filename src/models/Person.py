class Person:
    def __init__(self, content):
        # __init__: Hàm khởi tạo
        # self: this trong java
        self._content = content # Private

        # Access Modifier
        # Private, Public, Protected, Default
        # Public -> self.content = content
        # Protected -> self._content = content
        # Private -> self.__content = content

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value

