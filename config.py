from configparser import ConfigParser, ParsingError
from re import search


class SettingsFile:
    @staticmethod
    def _create():
        config = ConfigParser()
        config["SETTINGS"] = {
            "Point_Color": "#FF0000",
            "Line_Color": "#FFFF00",
            "Point_Radius": 7,
            "Line_Width": 2
        }
        with open('settings.ini', 'w') as file:
            config.write(file)

    @staticmethod
    def _is_valid(point_color, line_color, point_radius, line_width):
        is_hex = lambda color: search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color)
        is_valid_radius = lambda r: r.isdigit() and 1 <= int(r) <= 25
        is_valid_width = lambda w: w.isdigit() and 1 <= int(w) <= 10

        return is_hex(point_color) and is_hex(line_color) \
               and is_valid_radius(point_radius) and is_valid_width(line_width)

    @staticmethod
    def get_fields():
        try:
            config = ConfigParser()
            config.read("settings.ini")
            point_color = config["SETTINGS"]["Point_Color"]
            line_color = config["SETTINGS"]["Line_Color"]
            point_radius = config["SETTINGS"]["Point_Radius"]
            line_width = config["SETTINGS"]["Line_Width"]
            if not SettingsFile._is_valid(point_color, line_color, point_radius, line_width):
                raise Exception
            return point_color, line_color, point_radius, line_width
        except:
            SettingsFile._create()
            return SettingsFile.get_fields()

    @staticmethod
    def set_fields(point_color=None, line_color=None, point_radius=None, line_width=None):
        try:
            config = ConfigParser()
            config.read("settings.ini")

            if point_color:
                config["SETTINGS"]["Point_Color"] = point_color
            if line_color:
                config["SETTINGS"]["Line_Color"] = line_color
            if point_radius:
                config["SETTINGS"]["Point_Radius"] = str(point_radius)
            if line_width:
                config["SETTINGS"]["Line_Width"] = str(line_width)

            with open('settings.ini', 'w') as file:
                config.write(file)
        except:
            SettingsFile._create()
            SettingsFile.set_fields(point_color, line_color, point_radius, line_width)
