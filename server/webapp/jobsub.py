from subprocess import Popen, PIPE
import logger
import os
import socket


from JobsubConfigParser import JobsubConfigParser


def is_supported_accountinggroup(accountinggroup):
    rc = False
    try:
        p = JobsubConfigParser()
        groups = p.supportedGroups()
        rc = (accountinggroup in groups)
    except:
        logger.log('Failed to get accounting groups: ', traceback=True)

    return rc


def get_supported_accountinggroups():
    rc = list()
    try:
        p = JobsubConfigParser()
        rc = p.supportedGroups()
    except:
        logger.log('Failed to get accounting groups: ', traceback=True)

    return rc


def get_command_path_root():
    rc = '/opt/jobsub/uploads'
    p = JobsubConfigParser()
    submit_host = os.environ.get('SUBMIT_HOST', socket.gethostname())
    if p.has_section(submit_host):
        if p.has_option(submit_host, 'command_path_root'):
            rc = p.get(submit_host, 'command_path_root')

    return rc


def execute_jobsub_command(jobsub_args):
    #TODO: the path to the jobsub tool should be configurable
    command = ['/opt/jobsub/server/webapp/jobsub_env_runner.sh'] + jobsub_args
    logger.log('jobsub command: %s' % command)
    pp = Popen(command, stdout=PIPE, stderr=PIPE)
    result = {
        'out': pp.stdout.readlines(),
        'err': pp.stderr.readlines()
    }
    logger.log('jobsub command result: %s' % str(result))

    return result