import sys
import re

class ArgParser:
    def __init__(self):
        self.dictionary = self.default_subcommands() | self.default_options() | self.default_flags()
        self.help_message = self.default_help_message()

    '''
    Function of default subcommands for self.dictionary in aplication
    @return dictionary of default subcommands
    @misc for proper parsing of additional subcommands - self.get_subcommands() must be updated
    '''
    def default_subcommands(self):
        return {
        'info_type' : 'read',
        'uuid' : ''
        }

    '''
    Function of default options for self.dictionary in aplication
    @return dictionary of default options
    '''
    def default_options(self):
        return {
        'backend' : 'grcp',
        'grpc-server' : 'localhost:50051',
        'base-url' : 'http://localhost/',
        'output' : '',
        'size' : 10000,
        }

    '''
    Function of default flags for self.dictionary in aplication
    @return dictionary of default flags
    '''    
    def default_flags(self):
        return {
        'error_flag': False,    #technical (dont change)
        'help_flag' : False     #technical (dont change)
        }

    '''
    Function defining help message
    @return help message string
    '''
    def default_help_message(self):
        message = '\n\tUsage:\tfile-client [options] stat UUID\n'
        message += '\t\tfile-client [options] read UUID\n'
        message += '\t\tfile-client --help\n\n'

        message += '\tSubcommands:\n'
        message += '\t stat\t\tPrints the file metadata in a human-readable manner.\n'
        message += '\t read\t\tOutputs the file content.\n\n'

        message += '\tOptions:\n'
        message += '\t --help\t\t\tShow this help message and exit.\n'
        message += '\t --backend=BACKEND\tSet a backend to be used, choices are grpc and rest. Default is grpc.\n'
        message += '\t --grpc-server=NETLOC\tSet a host and port of the gRPC server. Default is localhost:50051.\n'
        message += '\t --base-url=URL\t\tSet a base URL for a REST server. Default is http://localhost/.\n'
        message += '\t --output=OUTPUT\tSet the file where to store the output. Default is -, i.e. the stdout.\n'

        return message

    '''
    Function chceck for help argument
    @param argv is array of arguments
    '''
    def check_help(self, argv):
        if(len(argv) == 2):
            r = re.compile('^--help$')
            matchlist = list(filter(r.match, argv))
            if(len(matchlist) == 1):
                self.dictionary['help_flag'] = True

    '''
    Function for obtaining value of first match
    @param regex is regular expresion
    @param arglist is list to match
    @return value of match if found, '' if not, 'error' if multiple matches
    '''
    def get_first_match(self, regex, arglist):
        matchlist = list(filter(regex.match, arglist))
        if(len(matchlist) == 1):
            return re.sub(regex, '', matchlist[0])
        elif(len(matchlist) > 1):
            return 'error'
        return ''

    '''
    Function sets options to values past in arguments
    @param opt is string representing option
    @param key is key to dictionary passed in self.dictionary
    @param argv is array of arguments
    @return argv is list of unprocessed arguments
    '''
    def set_option(self, opt, key, argv):
        regex = re.compile(opt)
        match = self.get_first_match(regex, argv)
        if(match != '' and match != 'error'):
            self.dictionary[key] = match
        elif(match == 'error'):
            self.dictionary['error_flag'] = True
        argv = [i for i in argv if not regex.match(i)]
        return argv

    '''
    Function sets options to values past in arguments
    @param opt is string representing option
    @param key is key to dictionary passed in self.dictionary
    @param argv is array of arguments
    @return argv is list of unprocessed arguments
    '''
    def set_subcommand(self, opt, key, argv):
        regex = re.compile(opt)
        matchlist = list(filter(regex.match, argv))
        if(len(matchlist) == 1):
            self.dictionary[key] = matchlist[0]
        elif(len(matchlist) > 1):
            self.dictionary['error_flag'] = True
        argv = [i for i in argv if not regex.match(i)]
        return argv

    '''
    Function sets options values to values in arguments
    @param argv is array of arguments
    @return argv is list of unprocessed arguments
    '''
    def set_options(self, argv):
        for key_option in self.default_options():
            opt = '^--' + key_option + '='
            argv = self.set_option(opt, key_option, argv)

        return argv

    '''
    Function sets subcommands values to values in arguments
    @param argv is array of arguments
    @return argv is list of unprocessed arguments
    '''
    def get_subcommands(self, argv):
        if(len(argv) == 3):     #after removal of options there should be exactly 3
            opt = '^stat$'
            key = 'info_type'
            argv = self.set_subcommand(opt, key, argv)

            opt = '^read$'
            key = 'info_type'
            argv = self.set_subcommand(opt, key, argv)

            if(len(argv) == 2):
                self.dictionary['uuid'] = argv[1]
            else:
                self.dictionary['error_flag'] = True
        else:
            self.dictionary['error_flag'] = True

    '''
    Function parsing starting arguments
    @param self.dictionary is dictionary with default self.dictionary
    @return self.dictionary dictionary with self.dictionary
    '''
    def parse_arguments(self):
        argv = sys.argv
        self.check_help(argv)
        if self.dictionary['help_flag'] != True:
            argv = self.set_options(argv)
            self.get_subcommands(argv)