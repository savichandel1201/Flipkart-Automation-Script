import configparser

config = configparser.RawConfigParser()
config.read("config.ini")

class ReadConfig:

    @staticmethod
    def get_base_url():
        return config.get("common info", "baseURL")

    @staticmethod
    def get_browser():
        return config.get("common info", "browser")

    @staticmethod
    def get_implicit_wait():
        return config.getint("common info", "implicit_wait")

    @staticmethod
    def get_page_load_timeout():
        return config.getint("common info", "page_load_timeout")


def read_config():
    return None