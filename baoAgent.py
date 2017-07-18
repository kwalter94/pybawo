RQ_MOVE    = 1
RQ_FORFEIT = 2
RQ_MESSAGE = 3
RQ_UNDO    = 4

STS_ACCEPT = 1
STS_REJECT = 2


class BaoAgent(object):
    '''An interface used to communicate with a bao arbiter or player.'''
    def new_game(self, field, **kwargs):
        pass

    def message(self, message, from_=None):
        '''Send message to agent.
        
        from_ is the id of the original sender, if None then the message was
        sent by the arbiter
        '''
        pass

    def move(self, m):
        '''Send move made to agent.'''
        pass

    def forfeit(self):
        '''Notify agent of forfeit.'''
        pass

    def undo(self):
        '''Request agent to undo last move.'''
        pass

    def ack(self, request, status, reason=None):
        '''Report whether a previous move, forfeit, or undo request failed.

        requests can take the following values: RQ_MOVE, RQ_UNDO

        status may be either STS_ACCEPT or STS_REJECT

        reason must be a string explaining what went wrong.
        '''
        pass

