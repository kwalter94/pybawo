import random
import threading
import sys
import time

import bao
import baoAgent

MAX_INT = sys.maxsize
MIN_INT = -(MAX_INT - 1)

# Player types:
PL_HUMAN   = 0
PL_MACHINE = 1


class Player(baoAgent.BaoAgent):
    def __init__(self):
        self.id = 'Player'
        self.type = PL_HUMAN

    def get_id(self):
        return self.id

    def set_id(self, id_):
        self.id = id_

    def get_type(self):
        return self.type

    def set_type(self, type_):
        self.type = type_

    def set_arbiter(self, arbiter):
        '''Set arbiter which must be a BaoAgent.'''
        pass


class Malume(Player):
    def __init__(self):
        Player.__init__(self)
        self.game_history = None

        self.ponder_thread = None
        self.stop_ponder = False
        self.vars = {
            'ponder_depth': 6,
            'stop_ponder': 0,
            'verbose': 1
        }

        self.type = PL_MACHINE
        self.id = 'Malume'

        self.arbiter = None

    def set_arbiter(self, arbiter):
        self.arbiter = arbiter

    def new_game(self, field='ab', **kwargs):
        if self.ponder_thread:
            self.stop_ponder = True
            self.ponder_thread.join()
            self.ponder_thread = None
        self.game_history = bao.new_game(**kwargs)
        self.field = field

    def move(self, mv):
        if self.game_history.get_player() == self.field:
            self.arbiter.ack(baoAgent.RQ_MOVE,
                             baoAgent.STS_REJECT,
                             'Not your turn')
            return None

        try:
            self.game_history.branch(mv)
            self.arbiter.ack(baoAgent.RQ_MOVE, baoAgent.STS_ACCEPT, None)
        except bao.InvalidMoveError:
            self.arbiter.ack(baoAgent.RQ_MOVE, baoAgent.STS_REJECT,
                             'Invalid move')
        except bao.LongMoveError:
            self.arbiter.ack(baoAgent.RQ_MOVE, baoAgent.STS_REJECT,
                             'Invalid move: Long move')

        if self.game_history.get_player() == self.field:
            self.make_move()

    def stop_ponder(self):
        if self.ponder_thread:
            self.stop_ponder = True
            self.ponder_thread.join()
            self.ponder_thread = None
            return True
        else:
            return False

    def message(self, m, from_=None):
        vcmd = m.split(None, 1)
        if len(vcmd) > 1:
            cmd = vcmd[0]
            argv = vcmd[1].strip().split()
        else:
            cmd = vcmd[0]
            argv = []

        if cmd == 'set':
            if len(argv) != 2:
                self.arbiter.message(
                    'Error: Invalid command ({})\n'.format(m)
                        +  'do \'set variable flag/value\'')
                return None
            if argv[0] in self.vars:
                if argv[0] == 'ponder_depth' and self.ponder_thread:
                    self.arbiter.message('Can\'t change that while pondering.')
                    return None
                self.vars[argv[0]] = int(argv[1])
                self.arbiter.message('set ok')
            else:
                self.arbiter.message(
                    'Error: var ({}) not known'.format(argv[0]))
        elif cmd == 'stop' or cmd == 'hault':
            self.stop_ponder()
            self.arbiter.message('Pondering haulted, will restart on go')
        elif cmd == 'go':
            if self.game_history.get_player() == self.field:
                self.arbiter.message('Wait for it...')
                self.make_move()
            elif self.ponder_thread:
                self.arbiter.message('Already pondering...')
            else:
                self.arbiter.message('Not my turn yet')
        elif cmd == 'vars':
            response = ''
            for key, value in list(self.vars.items()):
                response += key + ': ' + str(value) + '\n'
            self.arbiter.message(response)
        else:
            # self.arbiter.message('Whatever that was... Ignoring it')
            pass

    def forfeit(self):
        self.stop_ponder = True

    def undo(self):
        print("Malume undo!")
        self.game_history.pop_node()
        self.arbiter.ack(baoAgent.RQ_UNDO, baoAgent.STS_ACCEPT, None)
        self.arbiter.message('Undo OK, say \'go\' for me to make my move')

# private:
    def make_move(self):
        def move_listener(move):
            if move:
                self.arbiter.message('Moving ' + move)
                self.game_history.branch(move, exec_move=False)
                self.arbiter.move(move)
                if self.game_history.get_player() == self.field:
                    self.make_move()
            else:
                self.arbiter.message('I give up!')
                self.arbiter.forfeit()
        self.arbiter.message('Pondering... Please Wait.')
        self.ponder(move_listener)
        

    def ponder(self, callback, threaded=True):
        """Start pondering on next move if possible."""
        if threaded:
            self.ponder_thread = threading.Thread(target=self.ponder,
                                                   args=(callback, False))
            self.ponder_thread.start()
        else:
            self.nodes_pondered = 0
            self.stop_ponder = False
            state = self.game_history.get_current_node()[1]
            start_time = time.time()
            move, score = self.get_best_move(state,
                                             state.get_player(),
                                             self.vars['ponder_depth'])
            ponder_time = time.time() - start_time
            if self.vars['verbose']:
                self.arbiter.message(
                    'Ponder done: searched {} nodes in {} seconds'.format(
                        self.nodes_pondered, ponder_time, move))
            callback(move)
            self.ponder_thread = None

    def get_best_move(self, state, max_player, depth, alpha=MIN_INT,
                       beta=MAX_INT):
        # Using negamax ponder
        moves = [m for m in state.get_moves() if m is not None]
        if len(moves) == 1:
            return moves[0], self.eval_state(state, max_player, depth)
        elif depth == 0 or not moves:
            return None, self.eval_state(state, max_player, depth)

        best_moves = []
        best_score = MIN_INT

        for move in moves:
            child = state.get_child(move)
##            if child == None:
##                continue    # long move...
            if self.stop_ponder:
                raise SystemExit()
            hole, direction, mod = move.split_move(move)
            if (state.in_namua_phase()
                and state.is_mtaji()
                and (hole[1] in '12' and direction == 'L')
                or (hole[1] in '78' and direction == 'R')):
                # redundant moves (similar to those going in opposite direction)
                continue

            if state.get_player() == child.get_player():
                # score does not change sign if player does not change
                # (min-max requires sign change), hence search 1 more ply
                # down to get moves with similar signs only        
                _, score = self.get_best_move(child.copy(),
                                              max_player,
                                              depth,
                                              -beta,
                                              -max(alpha, best_score))
            else:
                _, score = self.get_best_move(child.copy(),
                                              max_player,
                                              depth - 1,
                                              -beta,
                                              -max(alpha, best_score))
                score = -score
            self.nodes_pondered += 1

            if score > best_score:
                best_score = score
                best_moves = [move]

                if best_score >= beta:
                    break
            elif score == best_score:
                best_moves.append(move)

            # if depth == self.vars['ponder_depth']:
            #     if self.vars['verbose']:
            #         self.arbiter.message(
            #             '{} score {} and current {} scores {}'.format(
            #                 best_moves, best_score, move, score))
            if depth == self.vars['ponder_depth']:
                print(score, move)
        if depth == self.vars['ponder_depth']:
            print(best_score, best_moves)
            print("---------------------------------------------\n")

        if best_moves:
            return random.choice(best_moves), best_score
        else:
            return None, 0

    def eval_state(self, state, max_player, depth):
        if state.is_game_over():
            return 0
            
        score = 0.0
        board = state.get_board()

        for hole in board.holes():
            v = board[hole]
            if board.hole_in_field(hole, state.get_player()):
                score += v
            else:
                if state.in_namua_phase():
                    if v == 0:
                        score += 1
                else:
                    if v <= 1:
                        score += 1
            
        if state.get_player() == max_player:
            return int(score)
        else:
            return -int(score)
