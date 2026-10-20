"""Exception classes of DESlab."""
#    Copyright (C) 2011-2012 by
#    Leonardo Bermeo <lbermeoc@unal.edu.co>
#    Joao Carlos Basilio <basilio@poli.ufrj.br>
#    GNU license.


##### These are the classes defining the software and user common errors


class desError(Exception):
    #Base class for exceptions in this module.
    pass


class inputError(Exception):
    #Base class for exceptions in this module.
    pass


class _MessageMixin:
    """Stores the message and prefixes it with the kind of error."""
    prefix = ''

    def __init__(self, msg=''):
        super().__init__(msg)
        self.message = msg

    def __str__(self):
        return "%s %s" % (self.prefix, self.message)


class DFAerror(desError):
    pass


class notDFAError(_MessageMixin, DFAerror):
    prefix = "It is not a DFA."


class stateError(_MessageMixin, desError):
    prefix = "Invalid State."


class deslabError(_MessageMixin, desError):
    prefix = "DESlab error."


class stateMembershipError(_MessageMixin, desError):
    prefix = "Undefined state."


class eventMembershipError(_MessageMixin, desError):
    prefix = "Undefined event."


class markedSetError(_MessageMixin, desError):
    prefix = "Error in marked set Xm."


class initialStateError(_MessageMixin, desError):
    prefix = "Bad definition of X0 state."


class epsilonDFAError(_MessageMixin, DFAerror):
    prefix = "It is not a DFA because it has epsilon events."


class inputStringError(_MessageMixin, desError):
    prefix = "It is not a valid input string."


class invalidAutomaton(_MessageMixin, desError):
    prefix = "It is not a valid automaton."


class invalidArgument(_MessageMixin, inputError):
    prefix = "Invalid input argument."


class invalidLabel(_MessageMixin, inputError):
    prefix = "Invalid label."


class invalidTransition(_MessageMixin, inputError):
    prefix = "Invalid transition."
