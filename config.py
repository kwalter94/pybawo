import configparser
import os

config = configparser.ConfigParser()

config['DEFAULT'] = {
    'theme': 'default'
}

config['cpu-player'] = {
    'ponder-depth': 5
}

config['xmpp'] = {
    'username': '',
    'password': '',
    'host': 'ajabber.me'
}

def load_config(path):
    config.read(path)

def save_config(path):
    config.write(path)

def get_config():
    return config
