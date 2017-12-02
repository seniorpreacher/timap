# original: https://stackoverflow.com/a/27871113/2205458
import os
import sys
from datetime import datetime


class ProgressBar:
    MAX_PREFIX_LENGTH = 24
    MAX_SUFFIX_LENGTH = 24
    first_run = True
    total = 0
    count = 0
    prefix = ''

    def __init__(self, total, prefix=''):
        self.total = total
        self.prefix = prefix
        pass

    def write(self, prefix=None, suffix=''):
        if not self.first_run:
            sys.stdout.flush()
        self.first_run = False

        self.count += 1
        terminal_width = self.get_terminal_width()
        prefix = self.trim_string((prefix if prefix is not None else self.prefix), self.MAX_PREFIX_LENGTH)
        suffix = self.trim_string(suffix, self.MAX_SUFFIX_LENGTH, False)
        bar_length = terminal_width - 18 - self.MAX_PREFIX_LENGTH - self.MAX_SUFFIX_LENGTH - (len(str(self.total)) * 2)
        filled_len = int(round(bar_length * self.count / float(self.total)))

        # changes shape in every 0.33 sec
        spinner = ['⋮', '⋯', '⋰', '⋱'][int(float(datetime.utcnow().strftime("%s.%f")) * 3) % 4]

        sys.stdout.write(
            ' {prefix} ▐{bar}▌ {percents: >5}% ({count: >{counter_length}}/{total}) {spinner} {suffix}\r'.format(
                prefix=prefix,
                bar='◼' * filled_len + '◻' * (bar_length - filled_len),
                percents=round(100.0 * self.count / float(self.total), 1),
                count=self.count,
                total=self.total,
                spinner=spinner,
                counter_length=len(str(self.total)),
                suffix=suffix
            ))

    def clear(self, text='', leave_bar=True):
        if leave_bar:
            sys.stdout.write('\r\n')
            sys.stdout.flush()
        print(text + ' ' * (self.get_terminal_width() - len(text)))

    @staticmethod
    def get_terminal_width():
        try:
            return int(os.get_terminal_size(0)[0])
        except OSError:
            return 80

    @staticmethod
    def trim_string(text, length, align_right=True):
        if len(text) > length:
            return '{0: <{length}}'.format(text[:(length - 2)] + '..', length=length)
        else:
            return text.rjust(length) if align_right else text.ljust(length)
