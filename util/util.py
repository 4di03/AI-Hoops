from flask import request, copy_current_request_context
from abc import ABC, abstractmethod
import json
import sys

class DataEmitter(ABC):
    '''
    Abstract FunctionObject for emitting json data
    of a certain type from server to client.
    '''

    def __init__(self, name):
        '''
        args:
            game: an instance of Game
            name: name of even to emit to client
        '''
        self.name = name

    @abstractmethod
    def get_data(self):
        '''
        returns json data to emit to client
        args:
            game: an instance of Game
        '''
        raise NotImplementedError

    def emit_data(self,socket):
        '''
        emits data to client.
        args:
            name: name of event to emit to client
            socket: SocketIO object
            game: Game object
        '''
        socket.emit(self.name,self.get_data(), to = request.sid)
        socket.sleep(0)


class ScreenDataEmitter(DataEmitter):

    def __init__(self, game, name):
        super().__init__(name)
        self.game = game
    def get_data(self):
        '''
        Gets jsonified screen data to emit to client
        '''
        balls_data = []
        for ball in self.game.balls:
            balls_data.append(ball.get_data())

        return json.dumps(balls_data)


# class StringDataEmitter(DataEmitter):
#
#
#     def __init__(self, name , text):
#         super().__init__(name)
#         self.text = text
#     def get_data(self):
#         '''
#         Get data from server stdout as string into json format
#         '''
#
#         return text


