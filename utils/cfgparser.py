class ConfigParserKeyException(Exception):
    pass

class ConfigParserConversionException(Exception):
    pass

class ConfigParserFormatException(Exception):
    pass


class ConfigParser:
    __file_lines: list

    def __init__(self, file_path):
        self.__map = {}
        self.read(file_path)
        self.__parse()

    def read(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            self.__file_lines = f.readlines()


    def __parse(self):
        for x in self.__file_lines:
            if x != "\n":
                self.__parse_line(x)

    def __parse_line(self, line: str):
        if "=" not in line:
            raise ConfigParserKeyException("配置文件格式异常")
        k = line.split('=')[0]
        if not k:
            raise ConfigParserKeyException("配置文件格式异常")
        v = line.replace('{}{}'.format(k, "="), "").replace('\n', '').replace('\r', '')
        self.__map[k] = v

    def get(self, k, default=None):
        if default:
            return self.__map.get(k, default)
        return self.__map.get(k)

    def get_int(self, k, default=None):
        v = self.get(k, default)
        return int(v)

    def get_float(self, k, default=None):
        v = self.get(k, default)
        return float(v)

    def get_boolean(self, k, default=None):
        v = self.get(k, default)
        if v == "false":
            return False
        if v == "true":
            return True
        raise ConfigParserConversionException("{} 不能转换为boolean".format(v))