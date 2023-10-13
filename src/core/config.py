import configparser
import os


config_file_path = os.path.join(os.path.dirname(__file__), '../../config.ini')
config = configparser.ConfigParser()
config.read(config_file_path)
