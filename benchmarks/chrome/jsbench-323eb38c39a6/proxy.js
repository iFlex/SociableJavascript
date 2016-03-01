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

var fs = require("fs");
var http = require("http");
var https = require("https");
var sys = require("util");
var child_process = require("child_process");

require("./jsbenchng");
require("./nodeutil");

// Load options
for (var argi = 2; argi < process.argv.length; argi++) {
    var arg = process.argv[argi];
    if (JSBNG.Options.acceptArg(arg) !== true) {
        sys.error("Use: proxy.js <options>\nOptions:\n" + JSBNG.Options.usage);
        process.exit(-1);
    }
}
JSBNG.Options.load();

// If we have an output file, use it
if (JSBNG.Options.output !== null) {
    (function() {
        var fh = fs.openSync(JSBNG.Options.output, "w");
        JSBNG.Util.data = function(msg) {
            fs.writeSync(fh, msg + ",");
        };
    })();
}

// combine all our chunks into a regular string
function combineChunks(data) {
    var out = "";
    for (var i = 0; i < data.length; i++) {
        out += data[i].toString("utf8");
    }
    return out;
}

// extract this gzip
function gzipExtract(data, then) {
    var gzip = child_process.spawn("gzip", ["-d", "-f"]);
    var odata = [];

    gzip.stdout.on("data", function(chunk) {
        odata.push(chunk);
    });

    gzip.stdout.on("end", function(code) {
        then(odata);
    });

    for (var i = 0; i < data.length; i++) {
        gzip.stdin.write(data[i], "binary");
    }
    gzip.stdin.end();
}

http.createServer(function(request, response) {
    function respond(statusCode, headers, data, fromCache, noInst) {
        if (typeof fromCache === "undefined") fromCache = false;
        if (typeof noInst === "undefined") noInst = false;

        sys.debug(request.url + ", " + (fromCache?"":"not ") + "from cache, code " + statusCode);

        // if it wasn't cached, cache it
        if (!fromCache /*&& statusCode >= 200 && statusCode < 300*/ && !("x-jsbench-ng-no-cache" in headers)) {
            JSBNG.Cache.setCache(request.url, statusCode, headers, data);
        }

        // consider instrumenting it
        if (!noInst) {
            var datastr = combineChunks(data);
            var ctype = headers["content-type"];
            var ins = JSBNG.Instrumentation.instrument(request.url, ctype, datastr);
            if (ins !== null) {
                data = [new Buffer(ins)];
                if (/html/.test(ctype)) {
                    // make sure this isn't XHTML
                    headers["content-type"] = ctype = "text/html";
                }
            }
        }

        // figure out its correct length
        var len = 0;
        for (var i = 0; i < data.length; i++) {
            len += data[i].length;
        }
        headers["content-length"] = ""+len;
        delete headers["transfer-encoding"];

        // un-secure any cookies (for https nonsense)
        if ("set-cookie" in headers) {
            var cookies = headers["set-cookie"];
            if (!(cookies instanceof Array)) {
                cookies = [cookies];
            }
            for (var i = 0; i < cookies.length; i++) {
                cookies[i] = cookies[i].replace(/; *Secure/i, "");
            }
        }

        // if this is a redirect, make sure we don't lead to SSL
        if ("location" in headers && /^https:\/\//.test(headers.location)) {
            headers.location = headers.location.replace(/^https:\/\//, "http://jsbngssl.");
        }

        // write it out
        response.writeHead(statusCode, headers);
        for (var i = 0; i < data.length; i++) {
            response.write(data[i], "binary");
        }
        response.end();
    }

    function handlePreInst(o) {
        // don't even make the request
        data.push(new Buffer(o.data));
        respond(o.statusCode?o.statusCode:200, {
            "content-type": o["content-type"]?o["content-type"]:"text/html",
            "content-length": data[0].length
        }, data, true, true);
    }

    var data = [];

    // see if it's pre-instrumented
    var ins = JSBNG.Instrumentation.preInstrument(request.url);
    if (ins !== null) {
        if (typeof ins === "function") {
            ins(request, handlePreInst);
        } else {
            handlePreInst(ins);
        }
        return;
    }

    // see if it's in the cache
    var cache = JSBNG.Options.noCache ? null : JSBNG.Cache.getCache(request.url);
    if (cache !== null) {
        respond(cache.statusCode, cache.headers, cache.data, true);

    } else {
        if (JSBNG.Options.cacheOnly) {
            respond(404, [], new Buffer(""), true, true);
            return;
        }

        // function to respond to the proxy request
        function proxyRequestHandler(proxyResponse) {
            proxyResponse.addListener("data", function(chunk) {
                data.push(chunk);
            });
            proxyResponse.addListener("end", function() {
                delete proxyResponse.headers["x-webkit-csp"];

                // first extract it
                if ("content-encoding" in proxyResponse.headers &&
                    proxyResponse.headers["content-encoding"] === "gzip") {
                    delete proxyResponse.headers["content-encoding"];
                    gzipExtract(data, function(data) {
                        respond(proxyResponse.statusCode, proxyResponse.headers, data);
                    });
    
                } else {
                    respond(proxyResponse.statusCode, proxyResponse.headers, data);
                }
    
            });
        }

        // create the proxy request
        var usessl = false;
        var path = request.url.replace(/^[^:]*:\/\/[^\/]*/, "");
        var proxyRequest;
        if (/^jsbngssl\./.test(request.headers.host)) {
            sys.debug("Got an SSL request to " + request.headers.host);
            // this is an https request
            usessl = true;
            request.headers.host = request.headers.host.replace(/^(jsbngssl\.)*/, "");
            proxyRequest = https.request({
                host: request.headers.host, port: 443, method: request.method, path: path, headers: request.headers
            }, proxyRequestHandler).addListener("error", function() {});
        } else {
            proxyRequest = http.request({
                host: request.headers.host, port: 80, method: request.method, path: path, headers: request.headers
            }, proxyRequestHandler).addListener("error", function() {});
        }
        proxyRequest.addListener("error", function() {});
        request.addListener("data", function(chunk) {
            proxyRequest.write(chunk, "binary");
        });
        request.addListener("end", function() {
            proxyRequest.end();
        });
        request.addListener("error", function() {});

    }
}).listen(8888);
