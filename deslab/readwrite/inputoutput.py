"""Saving and loading automata (pickle files with extension .des)"""
import pickle
import os


def save(self, filename='default'):
    """ saves the automaton in the file filename.des (by default
    the name of the automaton is used)"""
    if filename == 'default':
        filename = self.name
    path, ext = os.path.splitext(filename)
    if ext == '':
        filename = filename + '.des'
    with open(filename, 'wb') as fileobj:
        pickle.dump(self, fileobj)
    return filename


def load(filename):
    """ loads an automaton saved with the function save"""
    path, ext = os.path.splitext(filename)
    if ext == '':
        filename = filename + '.des'
    with open(filename, 'rb') as fileobj:
        self = pickle.load(fileobj)
    return self
