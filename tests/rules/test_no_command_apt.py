from subprocess import PIPE
from mock import patch, Mock
import pytest
from thefuck.rules.no_command_apt import match, get_new_command
from thefuck.main import Command


@pytest.fixture
def command_found():
    return b'''No command 'aptget' found, did you mean:
 Command 'apt-get' from package 'apt' (main)
aptget: command not found
'''

@pytest.fixture
def command_not_found():
    return b'''No command 'vom' found, but there are 19 similar ones
vom: command not found
'''


@pytest.fixture
def bins_exists(request):
    p = patch('thefuck.rules.no_command_apt.which',
              return_value=True)
    p.start()
    request.addfinalizer(p.stop)


@pytest.mark.usefixtures('bins_exists')
def test_match(command_found, command_not_found):
    with patch('thefuck.rules.no_command_apt.Popen') as Popen:
        Popen.return_value.stderr.read.return_value = command_found
        assert match(Command('aptget install vim', '', ''), None)
        Popen.assert_called_once_with('/usr/lib/command-not-found aptget',
                                      shell=True, stderr=PIPE)
        Popen.return_value.stderr.read.return_value = command_not_found
        assert not match(Command('ls', '', ''), None)

    with patch('thefuck.rules.no_command_apt.Popen') as Popen:
        Popen.return_value.stderr.read.return_value = command_found
        assert match(Command('sudo aptget install vim', '', ''),
                     Mock(command_not_found='test'))
        Popen.assert_called_once_with('test aptget',
                                      shell=True, stderr=PIPE)


@pytest.mark.usefixtures('bins_exists')
def test_get_new_command(command_found):
    with patch('thefuck.rules.no_command_apt._get_output',
               return_value=command_found.decode()):
        assert get_new_command(Command('aptget install vim', '', ''), None)\
            == 'apt-get install vim'
        assert get_new_command(Command('sudo aptget install vim', '', ''), None) \
            == 'sudo apt-get install vim'