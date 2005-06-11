"""
Copyright (c) 2004, CherryPy Team (team@cherrypy.org)
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, 
are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice, 
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice, 
      this list of conditions and the following disclaimer in the documentation 
      and/or other materials provided with the distribution.
    * Neither the name of the CherryPy Team nor the names of its contributors 
      may be used to endorse or promote products derived from this software 
      without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE 
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from basesession import BaseSession
import cherrypy.cpg

import shelve

from sessionerrors import *

import cPickle as pickle

class DBMSession(BaseSession):
    def __init__(self, sessionName):
        cpg = cherrypy.cpg

        BaseSession.__init__(self, sessionName)
        
        sessionName=cpg.config.get('session.new', None)
        sessionFile=cpg.config.get('%s.dbFile' % sessionName, 'shelfSession.db')
        self.__data = shelve.open(sessionFile, 'c')

    def getSession(self, sessionKey):
        try:
            return self.__data[sessionKey]
        except KeyError:
            raise SessionNotFoundError
    
    def setSession(self, sessionData):
        self.__data[sessionData.key] = sessionData

    def delSession(self, sessionKey):
        try:
            del self.__data[sessionKey]
        except KeyError:
            raise SessionNotFoundError
    
    def cleanUpOldSessions(self):
        deleteList = []
        for sessionKey in self.__data:
            session = self.__data[sessionKey]
            if session.expired():
                deleteList.append(sessionKey)
        for key in deleteList:
            self.delSession(sessionKey)