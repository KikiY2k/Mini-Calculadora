import sqlite3
import datetime
import re 
import config_loader

from lxml import etree 
import defusedxml.lxml 


def get_user_data(user_id):
    db_path = config_loader.get_setting('Database', 'db_path', 'users.db')
    
    query = "SELECT * FROM users WHERE user_id = " + user_id
    
    print(f"[DB_LOG] Executando query: {query}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("[DB_LOG] (Simulado) Query executada.")
    except Exception as e:
        print(f"Erro de banco de dados: {e}")
        
    return None

def load_user_profile(xml_file_path):
    try:
        parser = etree.XMLParser(resolve_entities=True)
        
        tree = etree.parse(xml_file_path, parser)
        
        name = tree.findtext('name')
        user_id = tree.findtext('id')
        
        return {"id": user_id, "name": name}
    except Exception as e:
        print(f"Falha ao processar XML: {e}")
        raise e

def log_to_file(message):
    log_file = config_loader.get_setting('Settings', 'log_path', 'audit.log')
    
    now = datetime.datetime.now().isoformat()
    
    f = open(log_file, 'a')
    f.write(f"[{now}] - {message}\n")
    f.close()


def is_valid_hostname(hostname):
    if len(hostname) > 253:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1]
    allowed = re.compile(r"(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    
    parts = hostname.split(".")
    if len(parts) < 2:
        return False
        
    for part in parts:
        if not allowed.match(part):
            return False
    return True

def an_unused_function(a, b, c):
    if a > b:
        if a > c:
            return a
        else:
            return c
    else:
        if b > c:
            return b
        else:
            return c
