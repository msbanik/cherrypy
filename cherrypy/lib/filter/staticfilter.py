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

import os, time, mimetypes
from basefilter import BaseFilter


class StaticFilter(BaseFilter):
    """Filter that handles static content."""
    
    def beforeMain(self):
        # We have to dynamically import cpg because Python can't handle
        #   circular module imports :-(
        global cpg, _cphttptools, cperror
        from cherrypy import cpg, _cphttptools, cperror
        
        if not cpg.config.get('staticFilter.on', False):
            return
        
        filename = cpg.config.get('staticFilter.file')
        if not filename:
            staticDir = cpg.config.get('staticFilter.dir')
            section = cpg.config.get('staticFilter.dir', returnSection=True)
            extraPath = cpg.request.path[len(section) + 1:]
            filename = os.path.join(staticDir, extraPath)
        
        # Serve filename
        try:
            stat = os.stat(filename)
        except OSError:
            raise cperror.NotFound(cpg.request.path)
        
        modifTime = stat.st_mtime
        strModifTime = time.strftime("%a, %d %b %Y %H:%M:%S GMT",
                                     time.gmtime(modifTime))
        if cpg.request.headerMap.has_key('If-Modified-Since'):
            # Check if if-modified-since date is the same as strModifTime
            if cpg.request.headerMap['If-Modified-Since'] == strModifTime:
                cpg.response.status = "304 Not Modified"
                cpg.response.body = []
                return
        cpg.response.headerMap['Last-Modified'] = strModifTime
        
        # Set Content-Length and use an iterable (file object)
        #   this way CP won't load the whole file in memory
        cpg.response.headerMap['Content-Length'] = stat[6]
        cpg.response.body = open(filename, 'rb')
        
        # Set content-type based on filename extension
        i = filename.rfind('.')
        if i != -1:
            ext = filename[i:]
        else:
            ext = ""
        contentType = mimetypes.types_map.get(ext, "text/plain")
        cpg.response.headerMap['Content-Type'] = contentType
