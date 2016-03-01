/*
 * Copyright (C) 2010, 2011 Purdue University
 * Written by Gregor Richards
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 * 
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

JSBNG.Cache = new (function() {
    function cacheName(url) {
        return JSBNG.Util.hash(url);
    }

    var getCacheByName = this.getCacheByName = function(name) {
        var name = "cache/" + name;
        var cname = name + ".cache";
        var plname = name + ".payload";

        try {
            var cache = JSON.parse(JSBNG.Util.readFile(cname));
            cache.data = [JSBNG.Util.readFileBuffer(plname)];
            return cache;
        } catch (ex) {}
        return null;
    };

    var getCache = this.getCache = function(url) {
        return getCacheByName(cacheName(url));
    };

    var getCacheByFile = this.getCacheByFile = function(filename) {
        return getCacheByName(filename.replace(/\.cache$/, ""));
    };

    var setCache = this.setCache = function(url, statusCode, headers, data) {
        var name = "cache/" + cacheName(url);
        var cname = name + ".cache";
        var plname = name + ".payload";
        JSBNG.Util.debug("Caching " + url);

        var cacheObj = {
            url: url,
            statusCode: statusCode,
            headers: headers
        };
        
        // first write the cache object in JSON form to the cache
        JSBNG.Util.writeFile(cname, JSON.stringify(cacheObj));

        // then write the data
        JSBNG.Util.writeFileBuffer(plname, data);
    };
})();
