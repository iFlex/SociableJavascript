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

JSBNG.Instrumentation = new (function() {
    var preInsts = [];
    var htmlInsts = [];
    var jsInsts = [];
    var logInsts = [];

    function pushInst(to, inst) { to.push(inst); }
    this.pushPreInst = function(inst) { pushInst(preInsts, inst); };
    this.pushHTMLInst = function(inst) { pushInst(htmlInsts, inst); };
    this.pushJSInst = function(inst) { pushInst(jsInsts, inst); };
    this.pushLogInst = function(inst) { pushInst(logInsts, inst); };

    function applyInsts(to, insts) {
        if (insts.length == 0) return null;
        for (var i = 0; i < insts.length; i++) {
            to = insts[i](to);
        }
        return to;
    }

    var applyJSInsts = this.applyJSInsts = function(url, line, data) {
        try {
            var jsp = Narcissus.parser.parse(data, url, line);
            if (jsInsts.length > 0) jsp = applyInsts(jsp, jsInsts);
            var res = Narcissus.decompiler.pp(jsp);
            return res;
        } catch (ex) {
            JSBNG.Util.debug("Failed to parse " + url + "! " + ex.toString() + " in " + JSON.stringify(ex.source));
            JSBNG.Util.data(JSON.stringify({"type": "parseerror", "code": ex.source}));
            //return "alert(\"Failed to instrument JavaScript!\");";
            return data;
        }
    };

    var applyLogInsts = this.applyLogInsts = function(log) {
        return applyInsts(log, logInsts);
    }

    var preInstrument = this.preInstrument = function(url) {
        var doc = url.replace(/^[^:]*:\/\/[^\/]*/, "");
        for (var i = 0; i < preInsts.length; i++) {
            var ret = preInsts[i](url, doc);
            if (ret !== null) return ret;
        }
        return null;
    };

    function isHTML(url, ctype, data) {
        if (/\.js$/i.test(url) ||
            /\.css$/i.test(url))
            return false;

        if (/\.html$/i.test(url) ||
            /\.htm$/i.test(url) ||
            ctype === "text/html" ||
            /<!doctype\s+html/i.test(data) ||
            /<html>/i.test(data) ||
            /<head>/i.test(data))
            return true;
        return false;
    }

    function isJS(url, ctype, data) {
        if (/\.html$/i.test(url) ||
            /\.htm$/i.test(url) ||
            /\.css$/i.test(url))
            return false;

        if (/\.js$/i.test(url) ||
            ctype === "text/javascript" ||
            ctype === "application/javascript" ||
            (/window/.test(data) && /function/.test(data)))
            return true;

        return false;
    }

    var parseTag = this.parseTag = function(data, loc) {
        var ret = {
            name: "",
            attribs: {},
            isEnd: false,
            isSingleton: false,
            start: loc,
            end: loc
        };

        var ws = /\s/;
        var wsoe = /\s|>/;
        var wseoeq = /\s|>|=/;

        loc++;

        // first, is this an end tag?
        if (data[loc] === "/") {
            ret.isEnd = true;
            loc++;
        }

        // then should be the name
        var nstart = loc;
        for (; loc < data.length && !wsoe.test(data[loc]); loc++);
        ret.name = data.substring(nstart, loc).toLowerCase();

        // then find any attributes
        while (data[loc] !== ">") {
            for (; loc < data.length && ws.test(data[loc]); loc++);

            // OK, we're either at an attribute or the end
            if (data[loc] === ">") break;

            // not the end, must be an attribute!
            var astart = loc;
            for (; loc < data.length && !wseoeq.test(data[loc]); loc++);
            var aname = data.substring(astart, loc).toLowerCase();
            for (; loc < data.length && ws.test(data[loc]); loc++);

            // if this is just /, this is actually the /> at the end
            if (aname === "/") {
                ret.isSingleton = true;
                continue;
            }

            // does the attribute have a value?
            if (data[loc] !== "=") {
                // nope
                ret.attribs[aname] = true;

            } else {
                loc++;
                for (; loc < data.length && ws.test(data[loc]); loc++);

                // yes, look for the end
                var avstart = loc;
                if (data[loc] === "\"") {
                    avstart++;
                    for (loc++; loc < data.length && data[loc] !== "\""; loc++) {
                        if (data[loc] === "\\") loc++;
                    }
                    ret.attribs[aname] = data.substring(avstart, loc++);

                } else if (data[loc] === "'") {
                    avstart++;
                    for (loc++; loc < data.length && data[loc] !== "'"; loc++);
                    ret.attribs[aname] = data.substring(avstart, loc++);

                } else {
                    for (; loc < data.length && !wsoe.test(data[loc]); loc++);
                    ret.attribs[aname] = data.substring(avstart, loc);

                }
            }
        }

        ret.end = loc + 1;
        return ret;
    };

    var deparseTag = this.deparseTag = function(tag) {
        var ret = "<" + tag.name;

        var attribs = Object.keys(tag.attribs);
        for (var i = 0; i < attribs.length; i++) {
            var attrib = attribs[i];
            var val = tag.attribs[attrib];
            ret += " " + attrib;
            if (val !== true)
                ret += "=\"" + val + "\"";
        }

        ret += ">";
        return ret;
    }

    var instTagInHTML = this.instTagInHTML = function(html, tagnm, inst, noend) {
        if (typeof noend === "undefined") noend = false;
        var start, cur = 0;
        
        var stag = new RegExp("<" + tagnm, "gi");
        var etag = new RegExp("<\\/" + tagnm, "gi");
        var ftags = [];

        // just look for the tags
        while (cur < html.length) {
            stag.lastIndex = cur;
            var tags = stag.exec(html);
            if (tags !== null) {
                start = tags.index;
                var tag = parseTag(html, start);
                cur = tag.end;

                etag.lastIndex = cur;
                var etags = etag.exec(html);
                if (!noend && !tag.isSingleton && etags !== null) {
                    var tage = parseTag(html, etags.index);
                    ftags.push([start, cur, etags.index, tage.end]);
                    cur = etags.index;
                } else {
                    ftags.push([start, cur]);
                }
            } else {
                cur = html.length;
            }
        }

        // then call the instrumentation
        for (var i = ftags.length - 1; i >= 0; i--) {
            inst(ftags[i]);
        }
    }

    function dehtmlentities(code) {
        return code
            .replace(/\&quot;/g, "\"")
            .replace(/\&amp;/g, "&")
            .replace(/\&#039;/g, "'")
            .replace(/\&#123;/g, "{")
            .replace(/\&#125;/g, "}");
    }

    var instJSInHTML = this.instJSInHTML = function(html) {
        // script tags
        instTagInHTML(html, "script", function(tag) {
            var tagi = parseTag(html, tag[0]);
            if (!("src" in tagi.attribs) && !("xjsbngnotouch" in tagi.attribs)) {
                var script = html.slice(tag[1], tag[2]);
                // remove <!-- comments -->
                script = script.replace(/^(\s*<!--[^\r\n]*\r?\n)+/g, "").replace(/(-->\s*)+$/g, "");
                // then instrument it
                script = applyJSInsts(":" + tag[0], 1, script); //.replace(/^ */mg, "").replace(/\n/g, "");
                html = html.slice(0, tag[1]) + script + html.slice(tag[2]);
            }

            if ("src" in tagi.attribs && tagi.isSingleton && tag.length === 2) {
                // <script />, damn you XHTML!
                html = html.slice(0, tag[0]) + html.slice(tag[0], tag[1]).replace(/\/>/, "></script>") + html.slice(tag[1]);
            }
        });

        // and "on" events
        instTagInHTML(html, "[a-zA-Z]+", function(tag) {
            var tagi = parseTag(html, tag[0]);
            var hason = false;

            // check for any on events
            for (var attrib in tagi.attribs) if (/^on/i.test(attrib)) hason = true;

            // if there are any, instrument them
            if (hason) {
                var pre = "";
                for (var attrib in tagi.attribs) {
                    if (/^on/i.test(attrib) && typeof(tagi.attribs[attrib]) === "string") {
                        var temp = "e" + JSBNG.Util.hash(html + ":" + tag[0] + ":" + attrib);
                        var script = applyJSInsts(":" + tag[0] + ":" + attrib, 1, "function " + temp + "(event) { " +
                            dehtmlentities(tagi.attribs[attrib]) +
                            "}");
                        pre += "<script type=\"text/javascript\">" + script + "</script>";
                        tagi.attribs[attrib] = "return " + temp + ".call(this, event);";
                    }
                }
                html = html.slice(0, tag[0]) + pre + deparseTag(tagi) + html.slice(tag[1]);
            }
        }, true);

        return html;
    }

    var instrument = this.instrument = function(url, ctype, data) {
        // check its type
        if (isHTML(url, ctype, data)) {
            // first apply all the direct instrumentations
            var ret = applyInsts(data, htmlInsts);
            if (ret === null) ret = data;

            // then instrument JS
            return instJSInHTML(ret);

        } else if (isJS(url, ctype, data)) {
            return applyJSInsts(url, 1, data);

        }
        return null;
    };
})();
