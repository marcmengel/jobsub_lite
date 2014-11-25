import cherrypy
import logger

from auth import check_auth
from format import format_response
from condor_commands import ui_condor_q,constructFilter
from history import HistoryResource
from summary import JobSummaryResource
from jobid import QueuedJobsByJobIDResource
from queued_long import QueuedLongResource





#@cherrypy.popargs('acctgroup')
@cherrypy.popargs('user_id')
@cherrypy.popargs('job_id')
class QueuedJobsResource(object):

    def __init__(self):
        self.history=HistoryResource()
	self.summary=JobSummaryResource()
        self.jobid=QueuedJobsByJobIDResource()
	self.long=QueuedLongResource()

    def doGET(self, user_id,job_id=None, kwargs=None):
        """ Query list of user_ids. Returns a JSON list object.
	    API is /acctgroups/<group>/users/<uid>/jobs
        """
        #acctgroup=kwargs.get('acctgroup')
        #job_id=kwargs.get('job_id')
        if user_id is None and kwargs is not None:
            user_id=kwargs.get('user_id')
        filter = constructFilter(None,user_id,job_id)
        logger.log("filter=%s"%filter)
	history = ui_condor_q( filter  )
        return {'out': history.split('\n')}

    @cherrypy.expose
    @format_response
    def index(self, user_id=None,job_id=None, **kwargs):
        try:
            subject_dn = cherrypy.request.headers.get('Auth-User')
            logger.log("user_id %s"%user_id)
            logger.log("job_id %s"%job_id)
            logger.log("kwargs %s"%kwargs)
            if subject_dn is not None:

                logger.log('subject_dn: %s' % subject_dn)
                if cherrypy.request.method == 'GET':
                    rc = self.doGET(user_id,job_id,kwargs)
                else:
                    err = 'Unsupported method: %s' % cherrypy.request.method
                    logger.log(err)
                    rc = {'err': err}
            else:
                # return error for no subject_dn
                err = 'User has not supplied subject dn'
                logger.log(err)
                rc = {'err': err}
        except:
            err = 'Exception on QueuedJobsResouce.index'
            cherrypy.response.status = 500
            logger.log(err, traceback=True)
            rc = {'err': err}

        return rc