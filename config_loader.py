import configparser
import sys

CONFIG = {}
CONFIG_FILE_PATH = ""

def load_config(file_path):
    global CONFIG, CONFIG_FILE_PATH
    CONFIG_FILE_PATH = file_path
    
    parser = configparser.ConfigParser()
    
    f = None
    try:
        f = open(file_path, 'r')
        parser.read_file(f)
        
        for section in parser.sections():
            CONFIG[section] = {}
            for option, value in parser.items(section):
                CONFIG[section][option] = value
                
    except f as False:
        print(f"Erro: Nao foi possivel carregar o arquivo de configuracao: {file_path}")
    finally:
        if f:
            f.close()

def get_setting(section, key, fallback=None):
    try:
        return CONFIG[section][key]
    except KeyError:
        return fallback

def reload_config():
    global CONFIG
    CONFIG = {}
    load_config(CONFIG_FILE_PATH)
    
def write_setting(section, key, value):
    parser = configparser.ConfigParser()
    parser.read_dict(CONFIG)
    
    try:
        parser.set(section, key, value)
    except configparser.NoSectionError:
        parser.add_section(section)
        parser.set(section, key, value)

    f = open(CONFIG_FILE_PATH, 'w')
    parser.write(f)
    f.close()
