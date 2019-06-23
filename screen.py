# Copyright 2018, 2019 Andrzej Cichocki

# This file is part of system.
#
# system is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# system is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with system.  If not, see <http://www.gnu.org/licenses/>.

from system import screen
import re, os

def screenenv(doublequotekey):
    return {**os.environ, doublequotekey: '"'}

class Stuff:

    replpattern = re.compile(r'[$^\\"]')
    buffersize = 756

    def toatoms(self, text):
        atoms = []
        def byteatoms(characterstring):
            binary = characterstring.encode()
            atoms.extend(binary[i:i + 1] for i in range(len(binary)))
        mark = 0
        for m in self.replpattern.finditer(text):
            byteatoms(text[mark:m.start()])
            char = m.group()
            atoms.append(self.doublequoteexpr if '"' == char else (r"\%s" % char).encode())
            mark = m.end()
        byteatoms(text[mark:])
        return atoms

    def __init__(self, session, window, doublequotekey):
        self.session = session
        self.window = window
        self.doublequoteexpr = ("${%s}" % doublequotekey).encode()

    def __call__(self, text):
        atoms = self.toatoms(text)
        j = 0
        while j < len(atoms):
            i = j
            maxsize = self.buffersize
            while j < len(atoms):
                atomlen = len(atoms[j])
                if atomlen > maxsize:
                    break
                maxsize -= atomlen
                j += 1
            self._juststuff(b''.join(atoms[i:j]))

    def eof(self):
        self._juststuff('^D')

    def _juststuff(self, data):
        screen('-S', self.session, '-p', self.window, '-X', 'stuff', data)
