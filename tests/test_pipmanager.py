# Copyright 2015 Facundo Batista, Nicolás Demarchi
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# For further info, check  https://github.com/PyAr/fades

""" Tests for pip related code. """

import unittest
from unittest.mock import patch

import logassert

from fades.pipmanager import PipManager
from fades import helpers


class PipManagerTestCase(unittest.TestCase):
    """ Check parsing for `pip show`. """

    def setUp(self):
        logassert.setup(self, 'fades.pipmanager')

    def test_get_parsing_ok(self):
        mocked_stdout = ['Name: foo',
                         'Version: 2.0.0',
                         'Location: ~/.local/share/fades/86cc492/lib/python3.4/site-packages',
                         'Requires: ']
        mgr = PipManager('/usr/bin', pip_installed=True)
        with patch.object(helpers, 'logged_exec') as mock:
            mock.return_value = mocked_stdout
            version = mgr.get_version('foo')
        self.assertEqual(version, '2.0.0')

    def test_get_parsing_error(self):
        mocked_stdout = ['Name: foo',
                         'Release: 2.0.0',
                         'Location: ~/.local/share/fades/86cc492/lib/python3.4/site-packages',
                         'Requires: ']
        mgr = PipManager('/usr/bin', pip_installed=True)
        with patch.object(helpers, 'logged_exec') as mock:
            version = mgr.get_version('foo')
            mock.return_value = mocked_stdout
        self.assertEqual(version, '')
        self.assertLoggedError('Fades is having problems getting the installed version. '
                               'Run with -v or check the logs for details')

    def test_real_case_levenshtein(self):
        mocked_stdout = [
            'Metadata-Version: 1.1',
            'Name: python-Levenshtein',
            'Version: 0.12.0',
            'License: GPL',
        ]
        mgr = PipManager('/usr/bin', pip_installed=True)
        with patch.object(helpers, 'logged_exec') as mock:
            mock.return_value = mocked_stdout
            version = mgr.get_version('foo')
        self.assertEqual(version, '0.12.0')

    def test_install(self):
        mgr = PipManager('/usr/bin', pip_installed=True)
        with patch.object(helpers, 'logged_exec') as mock:
            mgr.install('foo')
            mock.assert_called_with(['/usr/bin/pip', 'install', 'foo'])

    def test_install_with_options(self):
        mgr = PipManager('/usr/bin', pip_installed=True, options=['--bar baz'])
        with patch.object(helpers, 'logged_exec') as mock:
            mgr.install('foo')
            mock.assert_called_with(['/usr/bin/pip', 'install', 'foo', '--bar', 'baz'])

    def test_install_with_options_using_equal(self):
        mgr = PipManager('/usr/bin', pip_installed=True, options=['--bar=baz'])
        with patch.object(helpers, 'logged_exec') as mock:
            mgr.install('foo')
            mock.assert_called_with(['/usr/bin/pip', 'install', 'foo', '--bar=baz'])

    def test_install_raise_error(self):
        mgr = PipManager('/usr/bin', pip_installed=True)
        with patch.object(helpers, 'logged_exec') as mock:
            mock.side_effect = Exception("Kapow!")
            with self.assertRaises(Exception):
                mgr.install('foo')
        self.assertLoggedError("Error installing foo: Kapow!")

    def test_install_without_pip(self):
        mgr = PipManager('/usr/bin', pip_installed=False)
        with patch.object(helpers, 'logged_exec') as mocked_exec:
            with patch.object(mgr, '_brute_force_install_pip') as mocked_install_pip:
                mgr.install('foo')
                self.assertEqual(mocked_install_pip.call_count, 1)
            mocked_exec.assert_called_with(['/usr/bin/pip', 'install', 'foo'])
