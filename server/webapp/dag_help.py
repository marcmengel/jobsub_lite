import cherrypy
import logger
import uuid
import os
import sys
import socket

from auth import check_auth, get_client_dn
from format import format_response
from jobsub import execute_job_submit_wrapper





class DAGHelpResource(object):
    def doGET(self, acctgroup):
        """ Executes the jobsub tools command with the help argument and returns the output.
            API call is /jobsub/acctgroups/<group_id>/help
        """
        jobsub_args = ['-manual']
        rc = execute_job_submit_wrapper(acctgroup, None, jobsub_args,
                                        submit_type='dag', priv_mode=False)

        return rc


    @cherrypy.expose
    @format_response
    def index(self, acctgroup, **kwargs):
        try:
            subject_dn = get_client_dn()
            if subject_dn is not None:
                logger.log('subject_dn: %s' % subject_dn)
                if cherrypy.request.method == 'GET':
                    rc = self.doGET(acctgroup)
                else:
                    err = 'Unsupported method: %s' % cherrypy.request.method
                    logger.log(err)
                    rc = {'err': err}
            else:
                # return error for no subject_dn
                err = 'User has not supplied subject dn'
                logger.log(err)
                rc = {'err': err}
        except :
            err = 'Exception on DAGHelpResource.index %s'% sys.exc_info()[1]
            logger.log(err, traceback=True)
            rc = {'err': err}

        return rc


