"""Configuration handler"""
import yaml

def parse_config(config_file):
    """Parse a YAML configuration file"""
    try:
        with open(config_file, 'r') as f:
            return yaml.load(f)
    except IOError:
        print "Configuration file {} not found or not readable.".format(config_file)
        raise
