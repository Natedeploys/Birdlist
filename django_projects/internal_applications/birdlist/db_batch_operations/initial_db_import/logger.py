

class logger():
    '''
    '''

    def __init__(self, file_name, log_notes=None, writing_mode='append', discard_existing_log=True, log_datetime=True):
        '''
        '''

        self.file_name = file_name
        self.log_notes = log_notes

        self.writing_mode = writing_mode
        self.discard_existing_log = discard_existing_log
        self.log_datetime = log_datetime

        self._generate_logfile()


    def _generate_logfile(self):
        '''
        '''
        if self.discard_existing_log:
            file = open(self.file_name, 'w')

            text = '##  ' + self.log_notes + '\n##  -----------------------------------'
            text += '\n##  writing mode: ' + str(self.writing_mode)
            text = text + '\n##  discard existing log: ' + str(self.discard_existing_log)
            text = text + '\n##  log datetime: ' + str(self.log_datetime)
            text = text + '\n##  -----------------------------------\n'
            
            file.write(text)
            file.close()

        else:
            print
            print 'logger message --------------------------------------------------------------------------'
            print 'you would like to keep old log files.'
            print 'this feature is not fully implemented yet.'
            print 'right now, log entries will simply be appended to the existing file with the same name ..'
            print

        return


    def write_string_to_log(self, logstring):
        '''
        '''
        import time
        log = open(self.file_name, 'a')
        if self.log_datetime:
            logstring = '$$  ' + time.asctime() + ' $$  ' + logstring
        log.write(logstring+'\n')
        log.close()
        
        return


    def write_machine_readable_log(self, dict):
        '''
        '''

        names = ''
        content = ''
        for name in dict:
            names = names + name + '$'
            content = content + str(dict[name]) + '$'

        import time
        log = open(self.file_name, 'a')
        if self.log_datetime:
            logstring = '$$' + time.asctime() + '$$' + names + '$' + content
        else:
            logstring = '$$' + names + '$' + content
        log.write(logstring+'\n')
        log.close()


