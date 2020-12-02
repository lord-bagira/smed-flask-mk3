from configparser import ConfigParser


class IDMA_Conf:
    def __init__(self, conf_path ):
        ini_parser = ConfigParser()
        ini_parser.read( conf_path )

        self.database = dict()
        self.email = dict()
        self.orientation = dict()
        self.session = dict()
        self.administration = dict()

        self.database['driver'] = ini_parser.get('database', 'driver')
        self.database['user']   = ini_parser.get('database', 'user')
        self.database['pass']   = ini_parser.get('database', 'pass')
        self.database['host']   = ini_parser.get('database', 'host')
        self.database['dbname'] = ini_parser.get('database', 'name')

        self.email['server']    = ini_parser.get('email', 'server')
        self.email['port']      = ini_parser.get('email', 'port')
        self.email['user']      = ini_parser.get('email', 'user')
        self.email['password']  = ini_parser.get('email', 'password')
        self.email['sender']    = ini_parser.get('email', 'sender')

        self.orientation['backend_uri'] = ini_parser.get( 'orientation', 'backend_uri' )
        self.orientation['site_name'] = ini_parser.get( 'orientation', 'site_name' )

        self.session['TTL'] = ini_parser.get( 'sessions', 'TTL' )

        self.administration['admin_group'] = ini_parser.get( 'administration', 'admin_group' )
