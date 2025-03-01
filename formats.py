FG_DEFAULT = "\x1b[39m"
FMT_RESET = "\x1b[0m"


class Format:
    def __init__(self, value, reset):
        self.value = value
        self.reset = reset

    def fmt(self, string):
        return self.value + string + self.reset

    def __add__(self, other):
        """
        Supports combining multiple formatters.
        e.g., Formats.RED + Formats.BOLD
        or
        formatters = Formats.EMPTY
        formatters += Formats.RED
        """
        return Format(self.value + other.value, self.reset + other.reset)

    def add(self, other):
        """
        For combining multiple formatters as a chain.
        e.g., Formats.RED.add(Formats.BOLD).add(Formats.UNDERLINE)
        """
        return self + other


class Formats:
    RED = Format("\x1b[31m", FG_DEFAULT)
    GREEN = Format("\x1b[32m", FG_DEFAULT)
    YELLOW = Format("\x1b[33m", FG_DEFAULT)
    BLUE = Format("\x1b[34m", FG_DEFAULT)

    BOLD = Format("\x1b[1m", FMT_RESET)
    ITALIC = Format("\x1b[3m", FMT_RESET)
    UNDERLINE = Format("\x1b[4m", FMT_RESET)
    INVERSE = Format("\x1b[7m", FMT_RESET)

    # The start value for building a chain/sum of formats.
    EMPTY = Format("", "")
