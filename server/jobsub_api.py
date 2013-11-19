import cherrypy
import json
import base64
import os
import re
import errno

try:
    import htcondor as condor
    import classad
except:
    import traceback
    traceback.print_exc()

from subprocess import Popen, PIPE
from shutil import copyfileobj
from datetime import datetime


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

@cherrypy.popargs('experiment')
class ExperimentsResource(object):
    def __init__(self):
        self.jobs = JobsResource()

@cherrypy.popargs('job_id')
class JobsResource(object):

    def execute_jobsub_command(self, jobsub_args):
        #TODO: the path to the jobsub tool should be configurable
        command = ['/opt/jobsub/jobsub_env_runner.sh'] + jobsub_args
        cherrypy.request.app.log.error('jobsub command: %s' % command)
        pp = Popen(command, stdout=PIPE, stderr=PIPE)
        result = {
            'out': pp.stdout.readlines(),
            'err': pp.stderr.readlines()
        }
        cherrypy.request.app.log.error('jobsub command result: %s' % str(result))
        return result

    def execute_gums_command(self, subject_dn, experiment):
        command = '/usr/bin/gums-host|mapUser|-g|https://gums.fnal.gov:8443/gums/services/GUMSXACMLAuthorizationServicePort|"%s"|-f|"/fermilab/%s"' % (subject_dn, experiment)
        command = command.split('|')
        cherrypy.request.app.log.error('gums command: %s' % command)
        pp = Popen(command, stdout=PIPE, stderr=PIPE)
        result = {
            'out': pp.stdout.readlines(),
            'err': pp.stderr.readlines()
        }
        cherrypy.request.app.log.error('gums command result: %s' % str(result))
        return result

    def gums_auth(self, subject_dn, experiment):
        result = self.execute_gums_command(subject_dn, experiment)
        if result['out'] == 'null' or len(result['err']) > 0:
            return False
        else:
            return True

    def is_supported_experiemtn(self, experiment):
        # TODO: get list of experiments from jobsub config
        return True

    def get_uid(self, subject_dn):
        uid = 'unknown'
        try:
            uid = subject_dn.split(':')[1]
        except:
            cherrypy.request.app.log.error('Exception getting uid', traceback=True)
        return uid

    def POST(self, subject_dn, experiment, job_id=None, **kwargs):
        if job_id is None:
            cherrypy.request.app.log.error('kwargs: %s' % str(kwargs))
            jobsub_args = kwargs.get('jobsub_args_base64')
            if jobsub_args is not None:
                jobsub_args = base64.b64decode(jobsub_args).rstrip()
                cherrypy.request.app.log.error('jobsub_args: %s' % jobsub_args)
                jobsub_command = kwargs.get('jobsub_command')
                cherrypy.request.app.log.error('jobsub_command: %s' % jobsub_command)
                if jobsub_command is not None:
                    # TODO: get the command path root from the configuration
                    command_path_root = '/opt/jobsub/uploads'
                    uid = self.get_uid(subject_dn)
                    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
                    command_path = '%s/%s/%s/%s' % (command_path_root, experiment, uid, ts)
                    mkdir_p(command_path)
                    command_file_path = os.path.join(command_path, jobsub_command.filename)
                    cherrypy.request.app.log.error('command_file_path: %s' % command_file_path)
                    with open(command_file_path, 'wb') as dst_file:
                        copyfileobj(jobsub_command.file, dst_file)
                    # replace the command file name in the arguments with the path on the local machine
                    command_tag = '@(.*)%s' % jobsub_command.filename
                    jobsub_args = re.sub(command_tag, command_file_path, jobsub_args)
                    cherrypy.request.app.log.error('jobsub_args (subbed): %s' % jobsub_args)

                jobsub_args = jobsub_args.split(' ')
                result = self.execute_jobsub_command(jobsub_args)
                return str(json.dumps(result))
            else:
                #TODO: return an error because no command was supplied
                pass
        else:
            #TODO: return an error because job_id has been supplied but POST is for creating new jobs
            pass

    def GET(self, subject_dn, experiment, job_id=None, **kwargs):
        if job_id is not None:
            job_id = int(job_id)
            schedd = condor.Schedd()
            results = schedd.query()
            for job in results:
                if job['ClusterId'] == job_id:
                    return str(job)
        else:
            #TODO: return an error because job_id has not been supplied but GET is for querying jobs
            pass

    @cherrypy.expose
    def index(self, experiment, job_id=None, **kwargs):
        try:
            subject_dn = cherrypy.request.headers.get('Auth-User')
            if subject_dn is not None and experiment is not None:
                cherrypy.request.app.log.error('subject_dn: %s, experiment: %s' % (subject_dn, experiment))
                if self.is_supported_experiemtn(experiment):
                    if self.gums_auth(subject_dn, experiment):
                        if cherrypy.request.method == 'POST':
                            self.POST(subject_dn, experiment, job_id, kwargs)
                        elif cherrypy.request.method == 'GET':
                            self.GET(subject_dn, experiment, job_id, kwargs)
                    else:
                        # TODO: return error for failed gums auth
                        pass
                else:
                    # TODO: return error for unsupported experiment
                    pass
            else:
                # TODO: return error for no subject_dn and experiment
                pass
        except:
            cherrypy.request.app.log.error('Exception on JobsResouce.index', traceback=True)


class Root(object):
    pass

root = Root()

root.experiments = ExperimentsResource()

if __name__ == '__main__':
    cherrypy.quickstart(root, '/jobsub')
else:
    cherrypy.config.update({
        'environment': 'embedded',
        'lob.screen': False,
        'log.error_file': '/opt/jobsub/jobsub_error.log',
        'log.access_file': '/opt/jobsub/jobsub_access.log'
    })
    application = cherrypy.Application(root, script_name=None, config=None)


"""
import cherrypy

from experiments import Experiments


class Root(object):
    pass

root = Root()

root.experiments = Experiments()

# TODO: conf should be in seperate module for difference between dev and prod
conf = {
    'global': {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8080,
    },
    '/': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
    }
}

#TODO: server start will be different for dev and prod. Prod will be WSGI
cherrypy.quickstart(root, '/jobsub', conf)
"""
