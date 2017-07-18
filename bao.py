'''Module implements Bao as defined by www.gamecabinet.com/rules/Bao2.html
with the additional rule that takata moves exceeding the long move limit
(see function get_rules) are flagged illegal. This is in conformance to the
findings by Tom Kronenburg, Jeroen Donkers, and Alex J. de Voogt in
Never-Ending Moves in Bao (2006).
'''
import copy
import sys


INFINITE_MOVE_THRESHOLD = 500


class _Cursor(object):
    '''A Board iterator that loosely mimicks a human hand operating on a bao
    board.
    '''

    def __init__(self, board, hole, direction, stock):
        self.board = board
        self.hole = hole
        self.stock = stock
        self.direction = direction

    def step(self):
        '''Move a single step in self.direction.

        Rows are alternated within a player's field(territory) and
        self.direction is changed when the _Cursor steps out of bounds (ie
        beyond a8/A8 or a1/A1)
        '''
        row, col = self.hole
        if (col == '8' and self.direction == 'R'
                or col == '1' and self.direction == 'L'):
            self._switch_row_within_field()
            self.reverse_direction()
        elif self.direction == 'R':
            self.hole = row + str(int(col) + 1)
        elif self.direction == 'L':
            self.hole = row + str(int(col) - 1)
        else:
            print(self.__dict__)
            raise RuntimeError(
                    '_Cursor: _Cursor.direction or _Cursor.hole is corrupted.')

    def capture(self, count=-1):
        '''Capture count seeds/nkhomo at current cursor's position.

        A count of less than 1 is interpreted as a capture all. No more
        than what is cursor's current position can be captured.
        '''
        if count > self.board[self.hole]:
            raise ValueError('count exceeds seeds that can be captured')
        elif count < 0:
            count = self.board[self.hole]
        self.stock += count
        self.board[self.hole] -= count

    def sow(self, count=-1):
        '''Sow count nkhomo at current cursor's position.
        
        A count of less than 1 is interpreted as a sow all. No more than
        what is in stock can be sown.
        '''
        if count == -1:
            count = self.stock
        self.stock -= count
        self.board[self.hole] += count

    def reverse_direction(self):
        '''Reverse cursor's stepping direction.'''
        if self.direction == 'R':
            self.direction = 'L'
        elif self.direction == 'L':
            self.direction = 'R'
        else:
            raise RuntimeError(
                    '_Cursor: Invalid direction {}'.format(self.direction))

    def switch_field(self):
        '''Jump to a hole on the rival field that rivals current hole.'''
        self.hole = self.board.rival_hole(self.hole)

    def _switch_row_within_field(self):
        row, col = self.hole
        if row == 'A':
            self.hole = 'B' + col
        elif row == 'B':
            self.hole = 'A' + col
        elif row == 'a':
            self.hole = 'b' + col
        elif row == 'b':
            self.hole = 'a' + col
        else:
            raise RuntimeError('_Cursor: Invalid hole {}'.format(self.hole))


class Board(object):
    def __init__(self, other=None):
        if other:
            self._holes = other._holes.copy()
            self._store = other._store.copy()
        else:
            self._holes = dict((i + j, 0) for i in 'ABab' for j in '12345678')
            self._store = {'ab': 0, 'AB': 0}

    def update(self, board_conf):
        for h, v in list(board_conf.items()):
            self[h] = v

    def copy(self):
        return Board(self)
        
    def cursor(self, hole, direction, stock):
        return _Cursor(self, hole, direction, stock)

    def holes(self):
        return tuple(self._holes.keys()) + ('A9', 'B9', 'a9', 'b9')

    @staticmethod
    def get_target_hole(move, n_steps):
        '''Returns hole move will capture first from (ie the hole that rivals
        this move's marker.'''
        return Board.rival_hole(Board.get_marker_hole(move, n_steps))

    @staticmethod
    def get_marker_hole(move, n_steps):
        hole, direction, mod = Move.split_move(move)
        cursor = _Cursor(None, hole, direction, 0)
        if n_steps < 0:
            raise ValueError('Expected n_steps >= 0, got {}'.format(n_steps))
        while n_steps:
            cursor.step()
            n_steps -= 1
        return cursor.hole

    @staticmethod
    def hole_in_field(hole, field):
        '''Test if hole is contained in field.'''
        if hole[0] in field and hole[1].isdigit():
            return True
        return False

    @staticmethod
    def hole_in_front_row(hole):
        '''Test if hole belongs to any field's front row.'''
        return hole[0] == 'A' or hole[0] == 'a'

    @staticmethod
    def hole_in_back_row(hole):
        '''Test if hole belongs to any field's back row.'''
        return hole[0] == 'B' or hole[0] == 'b'

    @staticmethod
    def rival_field(field):
        '''Returns field that rivals/opposes given field.'''
        if field == 'ab':
            return 'AB'
        elif field == 'AB':
            return 'ab'
        else:
            raise ValueError('Invalid field {}'.format(field))

    @staticmethod
    def rival_hole(hole):
        '''Returns hole on rival field that rivals given hole.'''
        row, col = hole
        if row == 'A':
            return 'a' + str(9 - int(col))
        elif row == 'a':
            return 'A' + str(9 - int(col))
        elif row == 'B':
            return 'b' + str(9 - int(col))
        elif row == 'b':
            return 'B' + str(9 - int(col))
        else:
            raise ValueError('Invalid hole {}'.format(hole))


    def __getitem__(self, hole):
        return self._grep_hole(hole,
                               lambda : self._store['ab'],
                               lambda : self._store['AB'],
                               lambda : self._holes[hole])
        
    def __setitem__(self, hole, value):
        def set_store(i, value):
            self._store[i] = value

        def set_hole(i, value):
            self._holes[i] = value

        self._grep_hole(hole,
                        lambda : set_store('ab', value),
                        lambda : set_store('AB', value),
                        lambda : set_hole(hole, value))

    def _grep_hole(self, hole, fn_store_ab, fn_store_AB, fn_other):
        # Name's quite unfortunate...
        if hole[1] == '9':
            if hole[0] in 'ab':
                return fn_store_ab()
            elif hole[0] in 'AB':
                return fn_store_AB()
            else:
                raise ValueError('Invalid hole: {}'.format(hole))
        elif hole in self._holes:
            return fn_other()
        else:
            raise ValueError('Invalid hole: {}'.format(hole))

    def __str__(self):
        return str(self.__dict__)

    __repr__ = __str__



TAKATA_STOP      = 1
TAKASIA_STOP     = 2
MTAJI_STOP       = 3
LSOW_NYUMBA_STOP = 4
RSOW_NYUMBA_STOP = 5

class BaoException(Exception): pass
class LongMoveError(BaoException): pass
class InvalidMoveError(BaoException): pass


class Move(str):
    @staticmethod
    def split_move(move):
        '''Splits move into (hole, direction, modifier).'''
        if len(move) == 4:
            return (move[0:2], move[2], move[3])
        elif len(move):
            return (move[0:2], move[2], '')
        else:
            raise ValueError('Invalid move {}'.format(move))


class State(object):
    """Create a new bao State.

    State(rules=rules[, player_starting=player])
        Creates a new state initialised according to rules.

        if player_starting is not defined

    State(other=other_state)
        Creates a copy of other_state.

        Use State.copy() instead.
    """
    def __init__(self, **kwargs):
        if 'other' in kwargs:
            other = kwargs['other']
            self.board = other.board.copy()
            self.nyumba = other.nyumba.copy()
            self.takata = other.takata
            self.takasia = other.takasia
            self.player = other.player
            self.rules = other.rules
            self._last_move_ending = other._last_move_ending
            self._transitions = {}
        elif 'rules' in kwargs:
            rules = copy.deepcopy(kwargs['rules'])
            self.board = Board()
            self.board.update(rules.board_config)
            self.nyumba = rules.nyumba_state.copy()
            self.takata = True
            self.takasia = None
            if 'player_starting' in kwargs:
                self.player = kwargs['player_starting']
            else:
                self.player = rules.player_starting
            self.rules = rules
            self._last_move_ending = None # How the last move ended...
            self._transitions = {}
        else:
            raise ValueError("State must be instantiated with rules")

    def copy(self):
        return State(other=self)

    def get_board(self):
        return self.board.copy()

    def has_nyumba(self, player):
        try:
            return self.nyumba[player]
        except KeyError:
            raise ValueError('Invalid player: {}'.format(player))

    def get_player(self):
        return self.player

    def get_takasia(self):
        return self.takasia

    def get_rules(self):
        return copy.deepcopy(self.rules)

    def get_moves(self):
        return list(self._get_transitions_dict().keys())

    def get_transitions(self):
        return list(self._get_transitions_dict().items())

    def get_child(self, move):
        try:
            return self._get_transitions_dict()[move]
        except KeyError:
            raise InvalidMoveError()

    def get_closest_move(self, move):
        transitions = self._get_transitions_dict()
        if move in transitions:
            return move
        elif move + '>' in transitions:
            return move + '>'
        elif move + '$' in transitions:
            return move + '$'
        else:
            return None

    def exec_move(self, move, *args, **kwargs):
        if self.get_child(move) is None:
            raise LongMoveError()
        return self._exec_move(move, *args, **kwargs)

    def is_valid_move(self, move):
        if self.get_closest_move(move):
            return True
        else:
            return False

    def is_takata(self):
        if not self._transitions: # takata flag may not have been set
            self._get_transitions_dict()
        return self.takata

    def is_mtaji(self):
        return not self.is_takata()

    def in_namua_phase(self):
        return self.board[self.player[0] + '9'] > 0

    def in_mtaji_phase(self):
        return self.board[self.player[0] + '9'] == 0

    def is_game_over(self):
        '''Test for gameover for current player (ie if the player has no legal
        moves)'''
        if [_f for _f in list(self._get_transitions_dict().values()) if _f]:
            return False
        else:
            return True

# private:
    def _exec_move(self, move, move_watcher=lambda h, v: None):
        hole, direction, mod = Move.split_move(move)

        if (not self.board.hole_in_field(hole, self.player)
                or self.board[hole] == 0):
            return False
        elif mod == '$':
            self._last_move_ending = MTAJI_STOP
            self._setup_for_next_player()
            return True
        elif self.in_namua_phase():
            if hole[0] == 'b' or hole[0] == 'B':
                return False
            elif hole[1] == '5' and self.nyumba[self.player]:
                if self.takata and mod != '>':
                    # tax the nyumba
                    store = hole[0] + '9'
                    self.board[store] -= 1
                    move_watcher(store, self.board[store])
                    cursor = self.board.cursor(hole, direction, 1)
                    cursor.capture(1)
                    move_watcher(hole, self.board[hole])
                    cursor.step()
                    return self._exec_move_iter(cursor, 2, move_watcher)
                elif mod == '>':
                    cursor = self.board.cursor(hole, direction, 0)
                    self.nyumba[self.player] = False
                    return self._exec_move_iter(cursor, 0, move_watcher)
                else:
                    store = hole[0] + '9'
                    self.board[store] -= 1
                    move_watcher(store, self.board[store])
                    cursor = self.board.cursor(hole, direction, 1)
                    return self._exec_move_iter(cursor, 1, move_watcher)
            else:
                store = hole[0] + '9'
                self.board[store] -= 1
                move_watcher(store, self.board[store])
                cursor = self.board.cursor(hole, direction, 1)
                return self._exec_move_iter(cursor, 1, move_watcher)
        elif (self.board[hole] == 1
                  or ((hole == 'A5' or hole == 'a5')
                          and self.nyumba[self.player]
                          and mod != '>')):
            return False
        else:
            cursor = self.board.cursor(hole, direction, 0)
            cursor.capture()
            if hole in ('a5', 'A5') and self.nyumba[self.player]:
                self.nyumba[self.player] = False
            cursor.step()
            move_watcher(hole, self.board[hole])
            return self._exec_move_iter(cursor, 1, move_watcher)

    def _exec_move_iter(self, cursor, steps_execd, move_watcher):
        while True:
            if steps_execd > INFINITE_MOVE_THRESHOLD:
                sys.stderr.write('Error: Possible infinite mtaji move\n')
                # raise LongMoveError()
                return False
            if self.takata and steps_execd >= self.rules.long_move_limit:
                return False
            elif self.board.hole_in_field(cursor.hole, self.player):
                if cursor.stock == 0:
                    if self.board[cursor.hole] == 1:
                        if self.takata:
                            self._last_move_ending = TAKATA_STOP
                            break
                        else:
                            self._last_move_ending = MTAJI_STOP
                            break
                    elif (cursor.hole[0] == self.player[0]
                            and self.board[self.board.rival_hole(cursor.hole)]
                            and not self.takata):
                        cursor.switch_field()
                        cursor.capture()
                        if cursor.stock == 0:
                            cursor.switch_field()
                            cursor.capture()
                        elif cursor.hole[1] == '5':
                            opponent = self.board.rival_field(self.player)
                            self.nyumba[opponent] = False
                    elif cursor.hole == self.takasia and self.takata:
                        self._last_move_ending = TAKASIA_STOP
                        break
                    elif ((cursor.hole == 'A5' or cursor.hole == 'a5')
                            and self.nyumba[self.player]):
                        if self.takata:
                            self._last_move_ending = TAKATA_STOP
                            break
                        elif cursor.direction == 'R':
                            self._last_move_ending = RSOW_NYUMBA_STOP
                            break
                        else:
                            self._last_move_ending = LSOW_NYUMBA_STOP
                            break
                    else:
                        cursor.capture()
                else:
                    cursor.sow(1)
            else:
                cursor.switch_field()
                if cursor.hole in ('A1', 'A2', 'a1', 'a2'):
                    cursor.hole = cursor.hole[0] + '1'
                    cursor.direction = 'R'
                elif cursor.hole in ('A7', 'A8', 'a7', 'a8'):
                    cursor.hole = cursor.hole[0] + '8'
                    cursor.direction = 'L'
                elif cursor.direction == 'L':
                    cursor.hole = cursor.hole[0] + '8'
                else:
                    cursor.hole = cursor.hole[0] + '1'
                continue

            move_watcher(cursor.hole, self.board[cursor.hole])

            if cursor.stock and cursor.hole[0] in self.player:
                cursor.step()
            steps_execd += 1
        self._setup_for_next_player()
        return True

    def _get_transitions_dict(self):
        if not self._transitions:
            self._update_transitions()
        return self._transitions

    def _update_transitions(self):
        # Moves are _updated in the following order:
        #   (1) Mtaji moves
        #   (2) Front row takatas if (1) fails
        #   (3) Nyumba takata if in namua stage and (2) fails
        #   (4) Back row takatas if in mtaji stage and (2) fails
        #   (5) Nyumba takata if in mtaji stage and (4) fails
        self._updated = True
        if self._last_move_ending == LSOW_NYUMBA_STOP:
            for move in (self.player[0] + '5L>', self.player[0] + '5-$'):
                self.takata = False
                child = self.copy()
                move = Move(move)
                child._exec_move(move)
                self._transitions[move] = child
            return True
        elif self._last_move_ending == RSOW_NYUMBA_STOP:
            for move in (self.player[0] + '5R>', self.player[0] + '5-$'):
                self.takata = False
                child = self.copy()
                move = Move(move)
                child._exec_move(move)
                self._transitions[move] = child
            return True

        self.takata = True
        nyumba_takata = False
        back_row_takata = False
        front_row_takata = False
        front_row_is_empty = True
        
        for move in (h + d for d in 'LR'
                           for h in self.board.holes()
                           if self.board.hole_in_field(h, self.player)
                                and h[1] != '9'):
            hole, direction, mod = Move.split_move(move)

            if (front_row_is_empty and self.board.hole_in_front_row(hole)
					and self.board[hole]):
                front_row_is_empty = False

            if not self._is_possible_move(move):
                continue
            elif self._is_mtaji_move(move):
                if self.takata:
                    self.takata = False
                    self._transitions.clear()
            elif not self.takata:
                continue
            elif self.board.hole_in_front_row(hole):
                if (hole[1] == '5' and self.nyumba[self.player]):
                    if self.in_namua_phase():
                        if front_row_takata:
                            continue
                        elif not nyumba_takata:
                            nyumba_takata = True
                            self._transitions.clear()
                        if self.board[hole] < self.rules.board_config[hole]:
                            # Nyumba has fewer than the minimum number of seeds
                            # for takasa, nyumba must be sown
                            move += '>'
                    else:
                        if not nyumba_takata:
                            front_row_takata = True
                            nyumba_takata = True
                            self._transitions.clear()
                        move += '>'
                elif nyumba_takata and self.in_mtaji_phase():
                    continue    # nyumba_takata takes precedence in mtaji phase
                elif not front_row_takata:
                    front_row_takata = True
                    self._transitions.clear()
            elif front_row_takata:
                continue
            elif not back_row_takata:
                back_row_takata = True
                self._transitions.clear()

            child = self.copy()
            move = Move(move)
            if child._exec_move(move):
                self._transitions[move] = child
            else: # Long move
                self._transitions[move] = None

        if front_row_is_empty:
            self._transitions.clear()

        return bool(self._transitions)

    def _is_possible_move(self, move):
        hole, direction, mod = Move.split_move(move)
        if self.in_namua_phase():
            if self.board.hole_in_back_row(hole) or self.board[hole] == 0:
                return False
            else:
                return True
        else:
            if self.board[hole] > 1:
                return True
            else:
                return False

    def _is_mtaji_move(self, move):
        hole, direction, mod = Move.split_move(move)
        if self.in_namua_phase():
            if (self.board.hole_in_front_row(hole)
                    and self.board[hole]
                    and self.board[self.board.rival_hole(hole)]):
                return True
            else:
                return False
        else:
            if (self.board[hole] < 2
                    or self.board[hole] > self.rules.max_seeds_for_mtaji):
                return False
            end_hole = self.board.get_marker_hole(hole + direction,
                                                  self.board[hole])
            if (self.board.hole_in_front_row(end_hole)
                    and self.board[end_hole]
                    and self.board[self.board.rival_hole(end_hole)]):
                return True
            else:
                return False

    def _setup_for_next_player(self):
        if self.takata and not self.in_namua_phase() and self.rules.use_takasia:
            self._update_takasia()
        if (self._last_move_ending == LSOW_NYUMBA_STOP
                or self._last_move_ending == RSOW_NYUMBA_STOP):
            self.takata = False
        else:
            self.takata = True
            self.player = self.board.rival_field(self.player)
        self._transitions.clear()

    def _update_takasia(self):
        self.takasia = None


class History(object):
    def __init__(self, root_state):
        self._nodes = [(None, root_state.copy())]
        self._watchers = set()

    def add_watcher(self, watcher):
        self._watchers.add(watcher)

    def remove_watcher(self, watcher):
        self._watchers.remove(watcher)

    def get_rules(self):
        return self._nodes[-1][1].get_rules()

    def get_player(self):
        return self._nodes[-1][1].get_player()

    def get_closest_move(self, move):
        return self._nodes[-1][1].get_closest_move(move)

    def branch(self, move, exec_move=False, **kwargs):
        # Duplicates current node and place new node on top
        parent = self._nodes[-1][1]
        takata = parent.is_takata()

        if move[-1] == '*':
            if not takata:
                raise InvalidMoveError(
                    'Can\'t make takata move on mtaji state')
            else:
                move = move[:-1]

        child = parent.get_child(move)
        if child == None:
            raise LongMoveError()
        elif exec_move:
            child = parent.copy()
            if not child.exec_move(move, **kwargs):
                # this is not supposed to happen but it is...
                raise RuntimeError('Undesignated Long Move...')

        if takata:
            node = (move + '*', child)
        else:
            node = (move, child)

        self._nodes.append(node)

        for watcher in self._watchers:
            watcher(node, self.branch)

    def get_moves(self):
        return self._nodes[-1][1].get_moves()

    def get_current_node(self):
        # Returns node on top
        move, node = self._nodes[-1]
        return (move, node.copy())

    def is_game_over(self):
        return self.get_current_node()[1].is_game_over()

    def pop_node(self):
        # Returns node on top and removes it from stack if it is not the
        # root node.
        if len(self._nodes) > 1:
            node = self._nodes.pop()
            for watcher in self._watchers:
                watcher(node, self.pop)
            return node
        else:
            return self._nodes[0]

    def __len__(self):
        return len(self._nodes)

    def __iter__(self):
        return reversed(self._nodes)

    def __getitem__(self, i):
        return self._nodes[i]


class _Rules(object):
    board_config = None
    nyumba_state = None
    use_takasia  = False
    long_move_limit = 0
    player_starting = None


def get_variants():
    return ('ntchuwa', 'yabambo', 'yawana')


def get_rules(variant):
    if variant == 'yawana':
        rules = _Rules()
        rules.board_config = {
            'A1': 2, 'A2': 2, 'A3': 2, 'A4': 2, 'A5': 2, 'A6': 2, 'A7': 2,
            'A8': 2, 'B1': 2, 'B2': 2, 'B3': 2, 'B4': 2, 'B5': 2, 'B6': 2,
            'B7': 2, 'B8': 2,
            'a1': 2, 'a2': 2, 'a3': 2, 'a4': 2, 'a5': 2, 'a6': 2, 'a7': 2,
            'a8': 2, 'b1': 2, 'b2': 2, 'b3': 2, 'b4': 2, 'b5': 2, 'b6': 2,
            'b7': 2, 'b8': 2
        }
        rules.nyumba_state = {'AB': False, 'ab': False}
        rules.use_takasia = True
        rules.long_move_limit = 250
        rules.player_starting = 'AB'
        rules.max_seeds_for_mtaji = 16
        return rules
    elif variant == 'ntchuwa':
        rules = _Rules()
        rules.board_config = {
            'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'A5': 1, 'A6': 1, 'A7': 1,
            'A8': 1, 'A9': 24,
            'a1': 1, 'a2': 1, 'a3': 1, 'a4': 1, 'a5': 1, 'a6': 1, 'a7': 1,
            'a8': 1, 'a9': 24
        }
        rules.nyumba_state = {'AB': False, 'ab': False}
        rules.use_takasia = True
        rules.long_move_limit = 250
        rules.player_starting = 'AB'
        rules.max_seeds_for_mtaji = 16
        return rules
    elif variant == 'yabambo':
        rules = _Rules()
        rules.board_config = {
            'A5': 10, 'A6': 2, 'A7': 2, 'A9': 20,
            'a5': 10, 'a6': 2, 'a7': 2, 'a9': 20
        }
        rules.nyumba_state = {'AB': True, 'ab': True}
        rules.use_takasia = True
        rules.long_move_limit = 250
        rules.player_starting = 'AB'
        rules.max_seeds_for_mtaji = 16
        return rules
    else:
        raise ValueError('Invalid variant {}'.format(variant))

def new_game(**kwargs):
    """Returns a new game History.

    new_game(rules=custom_rules)
        Instantiate a new game with custom rules

    new_game(variant=name)
        Instantiate a new game using built-in rules.

        Variants:
            yawana
            ntchuwa
            yabambo

        Call get_variants for more.

    NOTE: rules overrides variant.
    """
    if 'rules' in kwargs:
        rules = kwargs['rules']
    elif 'variant' in kwargs:
        rules = get_rules(kwargs['variant'])
    else:
        raise ValueError(
            'Invalid arguments: predefined rules or variant required')

    if 'player_starting' in kwargs:
        rules.player_starting = kwargs['player_starting']

    return History(State(rules=rules))


if __name__ == '__main__':
    import profile

    game = new_game(variant='ntchuwa')
    moves = None
    state = game.get_current_node()[1]
    profile.run('moves = state.get_moves()')
    print(tuple(sorted(moves)))
