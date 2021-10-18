class GeneralException(Exception):
    """总体异常"""

    def __init__(self, message, code=500):
        self.code = code
        self.message = message
