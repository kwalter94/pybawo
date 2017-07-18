import sleekxmpp


class JabberNetwork(object):
    def __init__(self, jid, password):
        self.connection = sleekxmpp.ClientXMPP(jid, password)
        self.connection.add_event_handler('session_start', self.connected)
        self.connection.add_event_handler('got_online', self.node_online)
        self.connection.add_event_handler('got_offline', self.node_offline)
        self.connection.add_event_handler('message', self.got_message)

        self.callbacks = {}

        self.status = 'online'

    def connected(self, event):
        self.callbacks['connected'](True)
        self.connection.send_presence(pstatus=self.status)

    def node_online(self, event):
        self.callbacks['got_online'](event['jid'], event['pstatus'])
