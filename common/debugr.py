from collections import defaultdict

DEBUG = False
LABEL_MSG = False
OVERRIDE = False


def print_msg(msg, label):
    if LABEL_MSG:
        print(label + ': ' + msg)
    else:
        print(msg)


class Debugr:
    def __init__(self, flags_dict=None):
        self.log_dict = defaultdict(list)
        self.flags = defaultdict(bool)
        self.set_flags(flags_dict)

    def set_flags(self, flags_dict):
        if flags_dict is not None:
            for label, flag in flags_dict.items():
                self.flags[label] = flag

    def add_msg(self, label, msg, set_flag):
        self.log_dict[label].append(msg)

        if not OVERRIDE:
            if set_flag is not None:
                if set_flag: # turn off messages from this label
                    self.flags[label] = True
                    return
                else: # turn off this message
                    return

        if self.flags[label]:
            return # flag set to ignore message

        print_msg(msg, label)


_debug = Debugr()


def set_flags(flags):
    _debug.set_flags(flags)


def log(msg, label, set_flag=None):
    if DEBUG:
        _debug.add_msg(label, msg, set_flag)


def log_f(title, data, data_shape, label, set_flag=None):
    if DEBUG:
        out = format_msg(title, data, data_shape)
        _debug.add_msg(label, out, set_flag)


def format_msg(title, mx, mxshape):
    out = '' + title + '\n'
    width = mxshape.width()
    for i in range(len(mx)):
        out += str(mx[i]) + ' '
        if i % width == width - 1:
            out += '\n'
    return out
