class ParserException(Exception):
    def __init__(self, line_number: int, line_content: str, message: str):
        super().__init__(f'{message} -- line {line_number}, content: {line_content}')

