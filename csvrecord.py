# (c) 2013, Jan-Piet Mens <jpmens(at)gmail.com>
# (c) 2016, Osvaldo Toja <osvaldo.toja(at)gmail.com>
#
# This file is not part of Ansible but same licence applies to it:
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import codecs
import csv

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.utils.unicode import to_bytes, to_str, to_unicode

class CSVRecoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding='utf-8'):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class CSVReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding='utf-8', **kwds):
        f = CSVRecoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [to_unicode(s) for s in row]

    def __iter__(self):
        return self

class LookupModule(LookupBase):

    def read_csv(self, filename, delimiter, encoding='utf-8', dflt=None, type='dict',groupby=''):

        try:
            f = codecs.open(filename, 'r', encoding='utf-8')
            creader = list(csv.reader(f, delimiter=delimiter))
            f.close

            headers = creader.pop(0)
            rows = []

            for row in creader:
                lista = dict(zip(headers,row))
                lista = {k: v for k, v in lista.items() if v}
                if groupby:
                  if groupby in lista:
                    rows.append(lista)
                else:
                  rows.append(lista)
        except Exception as e:
            raise AnsibleError("csvfile: %s" % to_str(e))

        if type == 'dict':
            return [ rows ]
        else: 
            return rows

    def run(self, terms, variables=None, **kwargs):

        basedir = self.get_basedir(variables)

        ret = []

        for term in terms:
            params = term.split()

            paramvals = {
                'col' : "1",          # column to return
                'default' : None,
                'groupby' : "",
                'delimiter' : ",",
                #'delimiter' : "TAB",
                'file' : 'ansible.csv',
                'type' : "dict",
                'encoding' : 'utf-8',
            }

            # parameters specified?
            try:
                for param in params:
                    name, value = param.split('=')
                    assert(name in paramvals)
                    paramvals[name] = value
            except (ValueError, AssertionError) as e:
                raise AnsibleError(e)

            if paramvals['delimiter'] == 'TAB':
                paramvals['delimiter'] = "\t"

            lookupfile = self._loader.path_dwim_relative(basedir, 'files', paramvals['file'])
            ret = self.read_csv(lookupfile, paramvals['delimiter'], paramvals['encoding'], paramvals['default'], paramvals['type'],paramvals['groupby'])
        return ret
