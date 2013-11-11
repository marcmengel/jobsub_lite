import cherrypy
import json
import base64
import os
import re

try:
    import htcondor as condor
    import classad
except:
    import traceback
    traceback.print_exc()

from subprocess import Popen, PIPE
from shutil import copyfileobj

@cherrypy.popargs('exp_id')
class ExperimentsResource(object):
    def __init__(self):
        self.jobs = JobsResource()

@cherrypy.popargs('job_id')
class JobsResource(object):
    @cherrypy.expose
    def index(self, exp_id, job_id=None, **kwargs):
        try:
            if cherrypy.request.method == 'POST':
                if job_id is None:
                    cherrypy.request.app.log.error('kwargs: ' + str(kwargs))
                    jobsub_args = kwargs.get('jobsub_args_base64')
                    if jobsub_args is not None:
                        jobsub_args = base64.b64decode(jobsub_args)
                        cherrypy.request.app.log.error('jobsub_args: ' + str(jobsub_args))
                        jobsub_command = kwargs.get('jobsub_command')
                        cherrypy.request.app.log.error('jobsub_command: ' + str(jobsub_command))
                        if jobsub_command is not None:
                            # TODO: get the command path root from the configuration
                            command_path_root = '.'
                            # TODO: create sub directories for the user and request id or timestamp
                            command_path = os.path.join(command_path_root, jobsub_command.filename)
                            cherrypy.request.app.log.error('command_path: ' + str(command_path))
                            with open(command_path, 'wb') as dst_file:
                                copyfileobj(jobsub_command.file, dst_file)
                            # replace the command file name in the arguments with the path on the local machine
                            command_tag = '@(.*)%s' % jobsub_command.filename
                            jobsub_args = re.sub(command_tag, command_path, jobsub_args)
                            cherrypy.request.app.log.error('jobsub_args (subbed): ' + str(jobsub_args))

                        jobsub_args = jobsub_args.split(' ')
                        #TODO: the path to the jobsub tool should be configurable
                        command = ['/opt/jobsub/jobsub_env_runner.sh'] + jobsub_args
                        cherrypy.request.app.log.error('command: ' + str(command))
                        pp = Popen(command, stdout=PIPE, stderr=PIPE)
                        result = {
                            'out': pp.stdout.readlines(),
                            'err': pp.stderr.readlines()
                        }
                        return str(json.dumps(result))
                    else:
                        #TODO: return an error because no command was supplied
                        pass
                else:
                    #TODO: return an error because job_id has been supplied but POST is for creating new jobs
                    pass
            elif cherrypy.request.method == 'GET':
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