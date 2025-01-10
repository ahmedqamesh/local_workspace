########################################################
"""
    This file is part of the MOPS-Hub project.
    Author: Ahmed Qamesh (University of Wuppertal)
    email: ahmed.qamesh@cern.ch  
    Date: 29.01.2022
"""
########################################################
import os
import sys
import time
import datetime
import logging
from colorama import init
from clint.textui import colored
init()
from logging.handlers import RotatingFileHandler
import colorlog

class Logger(object):

    def __init__(self,
                 log_format = '%(log_color)s%(asctime)s - %(name)s -  [%(levelname)-7s] - %(message)s',
                 log_file_format = '%(asctime)s - %(name)s -  [%(levelname)-7s] - %(message)s',
                 name=None, console_loglevel=logging.INFO, logger_file=None):
        
        self.log_format = log_format
        self.log_file_format = log_file_format
        self.console_loglevel = console_loglevel
        self.logger_file = logger_file
        self.name = name
        #self.logger = self.setup_main_logger()
        return None
        

    def setup_main_logger(self):
        # Set color  
        streamhandler = colorlog.StreamHandler(sys.stderr)
        streamhandler.setLevel(self.console_loglevel)
        logger = logging.getLogger(self.name)
        formatter = self._setup_coloredlogs(logger)
        streamhandler.setFormatter(formatter)
        if not len(logger.handlers):
            # Add Logger level
            logger.setLevel(self.console_loglevel)
            self._add_success_level(logger)
            self._add_notice_level(logger)
            self._add_warning_level(logger)
            self._add_report_level(logger)
            self._add_status_level(logger)
            # Add logger file
            if self.logger_file:
                fh = self.setup_logfile(self.logger_file, console_loglevel=console_loglevel, format=formatter)
                self._add_logfiles_to(logger, fh)
            logger.propagate = False    
            logger.addHandler(streamhandler)    
        return logger

    def setup_file_logger(self): 
        formatter = logging.Formatter(self.log_file_format)
        logger = logging.getLogger(self.name)
        logger.setLevel(self.console_loglevel)
        self._add_success_level(logger)
        self._add_warning_level(logger) 
        self._add_notice_level(logger)
        self._add_report_level(logger)
        self._add_info_level(logger)
        self._add_status_level(logger)
        fh = self.setup_logfile(self.logger_file, console_loglevel=console_loglevel, format=formatter)
        self._add_logfiles_to(logger, fh)
        logger.propagate = False
        return logger
    
    def setup_logfile(self, filename, console_loglevel=None, format=None):
        fh = RotatingFileHandler(filename + 'log', backupCount=10,
                                        maxBytes=10 * 1024 * 1024)
        fh.setLevel(self.console_loglevel)
        fh.setFormatter(format)
        return fh
    
    def _add_logfiles_to(self, logger, fh):
        fhs = [fh]
        for lg in logging.Logger.manager.loggerDict.values():
            if isinstance(lg, logging.Logger):
                for handler in lg.handlers[:]:
                    if isinstance(handler, logging.FileHandler):
                        fhs.append(handler)
        for fh in fhs:
            logger.addHandler(fh)
                
    def add_logfile_to_loggers(self, fh):
        # Add filehandler to all active loggers
        for lg in logging.Logger.manager.loggerDict.values():
            if isinstance(lg, logging.Logger):
                lg.addHandler(fh)
    
    def close_logfile(self, fh):
        # Remove filehandler from all active loggers
        for lg in logging.Logger.manager.loggerDict.values():
            if isinstance(lg, logging.Logger):
                lg.removeHandler(fh)
    
    def _setup_coloredlogs(self, logger):
        colors = {'DEBUG': 'bold_green',
                  'INFO': 'green',
                  'SUCCESS': 'bold_green',
                  'NOTICE':'cyan',
                  'REPORT': 'blue',
                  'STATUS': 'yellow',
                  'WARNING': 'white,bg_yellow',
                  'ERROR': 'white,bg_red',
                  'CRITICAL': 'bold_purple'}
        formatter = colorlog.ColoredFormatter(self.log_format, log_colors=colors) 
        return  formatter      
    
    def _add_success_level(self, logger):
        logging.SUCCESS = 45
        logging.addLevelName(logging.SUCCESS, 'SUCCESS')
        logger.success = lambda msg, *args, **kwargs: logger.log(logging.SUCCESS, colored.yellow(msg), *args, **kwargs)
    
    def _add_notice_level(self, logger):
        logging.NOTICE = 26
        logging.addLevelName(logging.NOTICE, 'NOTICE ')
        logger.notice = lambda msg, *args, **kwargs: logger.log(logging.NOTICE, msg, *args, **kwargs)
    
    def _add_report_level(self, logger):
        logging.REPORT = 25
        logging.addLevelName(logging.REPORT, 'REPORT ')
        logger.report = lambda msg, *args, **kwargs: logger.log(logging.REPORT, colored.magenta(msg), *args, **kwargs)

    def _add_info_level(self, logger):
        logging.INFO = 20
        logging.addLevelName(logging.INFO, '   INFO  ')
        logger.info = lambda msg, *args, **kwargs: logger.log(logging.INFO, colored.green(msg), *args, **kwargs)
                
    def _add_status_level(self, logger):
        logging.STATUS = 30
        logging.addLevelName(logging.STATUS, 'STATUS')
        logger.status = lambda msg, *args, **kwargs: logger.log(logging.STATUS, colored.yellow(msg), *args, **kwargs)
                
                    
    def _add_warning_level(self, logger):
        logging.WARNING = 35
        logging.addLevelName(logging.WARNING, 'WARNING')
        logger.warning = lambda msg, *args, **kwargs: logger.log(logging.WARNING, msg, *args, **kwargs)
        
    def _reset_all_loggers(self):
        logging.root.handlers = []
        
if __name__ == "__main__":
    pass