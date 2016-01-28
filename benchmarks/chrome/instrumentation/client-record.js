/*
 * Copyright (C) 2010-2013 Purdue University
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

JSBNG_Record = new (function() {
    function stringWrap(str) {
        if (typeof JSON !== "undefined" && JSON.stringify) {
            return JSON.stringify(str+"");
        } else {
            return "\"" +
                str
                .replace(/\\/g, "\\\\")
                .replace(/"/g, "\\\"")
                .replace(/\r/g, "\\r")
                .replace(/\n/g, "\\n")
                "\"";
        }
    }

    /* Workaround for array functions to behave consistently when the array is
     * memoizing */
    if (typeof Array.prototype.slice !== "undefined") {
        var aps = Array.prototype.slice;
        Array.prototype.slice = function(from) {
            var len = window.top.JSBNG_Record.get(this, "length").length;
            for (var i = 0; i < len; i++) {
                window.top.JSBNG_Record.get(this, i);
            }

            return aps.apply(this, arguments);
        };
    }

    // Function to assure ordered for..in
    this.forInKeys = function(of) {
        var keys = [];
        for (var k in of)
            keys.push(k);
        return keys.sort();
    }

    /* Workaround for JSON.stringify to not go nutty if it ends up fed an
     * instrumented object */
    var realJSONstringify = JSON.stringify;
    var fakeJSONstringify = JSON.stringify = function(from) {
        var ret, wobj;
        switch (typeof from) {
            case "object":
                if ((wobj = getMemoizationWrapper(from)) !== null) {
                    return fakeJSONstringify(from.obj);

                } else if (from instanceof Array) {
                    ret = "[";
                    for (var i = 0; i < from.length; i++) {
                        if (i !== 0) ret += ",";
                        ret += fakeJSONstringify(from[i]);
                    }
                    ret += "]";
                } else {
                    ret = "{";
                    var first = true;
                    for (var key in from) {
                        if (/^__JSBNG/.test(key)) continue;
                        if (!first) ret += ",";
                        first = false;
                        ret += realJSONstringify(key) + ":" + fakeJSONstringify(from[key]);
                    }
                    ret += "}";
                }
                break;

            default:
                ret = realJSONstringify(from);
        }
        return ret;
    };

    var msgs = "";

    var sendMessage = this.sendMessage = function(msg, imm) {
        if (msgs == "") {
            msgs = msg;
        } else if (msg != "") {
            msgs += "," + msg;
        }

        if (msgs.length >= 10240 || imm) {
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "/JSBENCH_NG_MSG", false);
            xhr.send(msgs);
            msgs = "";
        }
    }

    var instrumentScript = this.instrumentScript = function(scr) {
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/JSBENCH_NG_INSTR", false);
        xhr.send(scr);
        return xhr.responseText;
    }

    // each page has a hopefully-unique ID
    var pageId = this.pageId = Math.floor(Math.random() * 1000000000);

    // and maybe a separate parent pageId
    var ppageId = null;
    try {
        if (window.parent !== window && "JSBNG_Record" in window.parent) {
            ppageId = window.parent.JSBNG_Record.pageId;
        }
    } catch (ex) {}

    // store a reference to the top here to avoid shadowing issues
    this.top = window.top;

    function sendMessageStmt(type, ct) {
        var msg = "{\"type\":\"" + type + "\",\"pageid\":" + pageId;
        for (var prop in ct) {
            var val = ct[prop];
            msg += ",\"" + prop + "\":";
            switch (typeof(val)) {
                case "boolean":
                case "number":
                    msg += val;
                    break;

                case "string":
                    msg += stringWrap(val);
                    break;

                default:
                    msg += "null";
                    break;
            }
        }
        msg += "}";
        if (window !== top) {
            top.JSBNG_Record.sendMessage(msg);
        } else {
            sendMessage(msg);
        }
    }
    this.sendMessageStmt = sendMessageStmt;;

    // initial events
    var inito = {url: document.location.href};
    if (ppageId !== null) inito.parent = ppageId;
    sendMessageStmt("init", inito);

    var scriptLoad = this.scriptLoad = function(scr, sid, uninstrumented) {
        sendMessageStmt("scriptload", {"data": scr, "sid": sid, "uninstrumented": (uninstrumented ? true : false)});
    }

    // some generic wrappers
    function ael(to, of, fun) {
        if (window.addEventListener) {
            to.addEventListener(of, fun, false);
        } else if (window.attachEvent) {
            to.attachEvent("on" + of, fun);
        } else {
            if (("on" + of) in to) {
                (function(origfun) {
                    to["on" + of] = function(ev) {
                        if (origfun.call(this, ev) === false) return false;
                        return fun.call(this, ev);
                    };
                })(to["on" + of]);
            } else {
                to["on" + of] = fun;
            }
        }
    }

    function setUnenum(obj, prop, val) {
        if (Object.defineProperty) {
            Object.defineProperty(obj, prop, {value: val, configurable: true});
        } else {
            obj[prop] = val;
        }
    }

    var ophop = Object.prototype.hasOwnProperty;
    function hasOwnProp(obj, prop) {
        if (ophop) {
            return ophop.call(obj, prop);
        } else {
            if (
                (prop in obj) &&
                (!(prop in obj.prototype.constructor) ||
                 (obj[prop] !== obj.prototype.constructor[prop]))
               ) {
                return true;
            } else {
                return false;
            }
        }
    }

    var arraymap = Array.prototype.map;


    // finalization
    function fin() {
        sendMessageStmt("fin", {});
        top.JSBNG_Record.sendMessage("", true);
    }
    ael(window, "unload", fin);

    // and error handling
    function fonerror() {
        sendMessageStmt("error", {});
    }
    ael(window, "error", fonerror);

    // check what needs to be instrumented
    var wmembers;
    if (typeof(window.getOwnProperties) !== "undefined") {
        wmembers = window.getOwnProperties();
    } else {
        wmembers = [];
        for (var k in window) {
            wmembers.push(k);
        }
    }

    // make sure it's all instrumented
    var badmembers = [];
    function reportBadMembers() {
        var html = "ERROR: " + badmembers.length + " members of window uninstrumented!<hr/>";
        var msg = "{\"type\":\"error\",\"msg\":\"uninstrumented\",\"data\":[";
        var doInstrument = "", dontInstrument = "";
        for (var i = 0; i < badmembers.length; i++) {
            var bm = badmembers[i];
            html += bm + ": " + typeof(window[bm]) + "<br/>";
            if (/^on/.test(bm)) {
                dontInstrument += "\"" + bm + "\":true, ";
            } else {
                doInstrument += "\"" + bm + "\":true, ";
            }
        }
        document.body.innerHTML = html;

        msg += "{" + doInstrument + "},{" + dontInstrument + "}]}";
        top.JSBNG_Record.sendMessage(msg, true);
    }
    for (var i = 0; i < wmembers.length; i++) {
        var mem = wmembers[i];
        if (/^JSBNG/.test(mem)) continue;
        if (!(mem in JSBNG_Record_doInstrument) &&
            !(mem in JSBNG_Record_onInstrument) &&
            !(mem in JSBNG_Record_dontInstrument) &&
            !(mem in JSBNG_Record_destroy)) {
            badmembers.push(mem);
        }
    }
    if (badmembers.length > 0) {
        ael(window, "load", reportBadMembers);
    }

    // destroy bad global members (usually falsey, thus unreplayable, objects)
    for (var k in JSBNG_Record_destroy) {
        delete window[k];
        if (k in window)
            window[k] = void 0;
    }

    // deferred events, for events that may or may not be synchronous depending on implementation
    var deferredEvents = [];
    this.deferEvents = false;
    this.deferEvent = function(fun, fthis, args) {
        deferredEvents.push([fun, fthis, args]);
    }
    this.flushDeferredEvents = function() {
        if (deferredEvents.length > 0) {
            var de = deferredEvents.shift();
            Function.prototype.apply.call(de[0], de[1], de[2]);
        }
    }

    // since arrays tend to be reused, duplicate them
    function isArrayLike(obj) {
        try {
            return !!(obj &&
                    typeof obj === 'object' && 
                    'length' in obj && 
                    !({}.propertyIsEnumerable.call(obj, 'length')));
        } catch (ex) {
            return false;
        }
    }

    // memoization wrappers
    var mwid = 0;
    function MemoizationWrapper(obj) {
        this.obj = obj;
        this.id = "o" + pageId + "_" + (mwid++);
        this.__JSBNG_data = this;
        sendMessageStmt("objdec", {"id": this.id});
    }

    var declfuncs = {};

    function MemoizingFunction(owner, nm, fun, id) {
        var mfothis = this;
        if (typeof id === "undefined") {
            id = "f" + pageId + "_" + (mwid++);
        }
        if (!(id in declfuncs)) {
            declfuncs[id] = true;
            sendMessageStmt("fundec", {"id": id});
        }
        this.id = id;
        this.name = nm;
        var mfun = this[nm] = function() {
            var uthis = this;
            var args = arraymap.call(arguments, getUnwrappedObject);
            var ret = null;
            var type = "call";

            if (this === mfothis) uthis = owner;

            try {
                if (this.constructor === mfun) {
                    // constructed function, worst case
                    type = "new";
                    switch (args.length) {
                        case 0:  ret = wrap(new fun()); break;
                        case 1:  ret = wrap(new fun(args[0])); break;
                        case 2:  ret = wrap(new fun(args[0], args[1])); break;
                        case 3:  ret = wrap(new fun(args[0], args[1], args[2])); break;
                        case 4:  ret = wrap(new fun(args[0], args[1], args[2], args[3])); break;
                        case 5:  ret = wrap(new fun(args[0], args[1], args[2], args[3], args[4])); break;
                        case 6:  ret = wrap(new fun(args[0], args[1], args[2], args[3], args[4], args[5])); break;
                        case 7:  ret = wrap(new fun(args[0], args[1], args[2], args[3], args[4], args[5], args[6])); break;
                        case 8:  ret = wrap(new fun(args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7])); break;
                        case 9:  ret = wrap(new fun(args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8])); break;
                        case 10: ret = wrap(new fun(args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9])); break;
                        default: ret = wrap(new fun());
                    }

                } else if ("JSBNG_isInstrumented" in fun) {
                    // this is an instrumented function, pass it wrapped values
                    ret = Function.prototype.apply.call(fun, uthis, arguments);

                } else if (mfothis.name === "appendChild" &&
                           args.length === 1 &&
                           (""+args[0].tagName).toLowerCase() === "script" &&
                           !args[0].src) {
                    /* Special case for adding a script to the document. Defer
                     * it as a scriptload. */
                    ret = undefined;
                    top.JSBNG_Record.deferEvent(function() {
                        var scr = args[0].innerHTML;
                        var iscr = instrumentScript(scr);
                        scriptLoad(scr, ("s" + Math.random()).replace(/\./g, ""), false);
                        top.JSBNG_Record.callerJS = true;
                        try {
                            var geval = eval;
                            geval(iscr);
                        } catch (ex) {
                            top.JSBNG_Record.callerJS = false;
                            throw ex;
                        }
                        top.JSBNG_Record.callerJS = false;
                    }, {}, []);

                } else {
                    // sometimes this will fire synchronous events, so "forget" that we're in JS for a while
                    top.JSBNG_Record.callerJS = false;
                    top.JSBNG_Record.deferEvents = true;
                    try {
                        ret = Function.prototype.apply.call(fun, getUnwrappedObject(uthis), args);
                    } catch (ex) {
                        top.JSBNG_Record.callerJS = true;
                        top.JSBNG_Record.deferEvents = false;
                        throw ex;
                    }
                    top.JSBNG_Record.callerJS = true;
                    top.JSBNG_Record.deferEvents = false;

                    // make sure we duplicate arrays, since they tend to be reused which screws up our record
                    if (isArrayLike(ret)) {
                        ret = [].slice.call(ret, 0);
                    }
                    ret = wrap(ret);

                }

            } catch (ex) {
                throw ex;
            }

            var retstr = stringify(ret);

            // convert the args to strings
            var argstr = "[" + stringify(uthis);
            for (var i = 0; i < arguments.length; i++)
                argstr += "," + stringify(arguments[i]);
            argstr += "]";

            // now log it
            sendMessageStmt(type, {"func": mfothis.id, "args": argstr, "ret": retstr});

            return ret;
        };

        // make mfun (to whatever degree is possible) be a MemoizationWrapper
        mfun.__JSBNG_data = {
            obj: fun,
            fun: mfun,
            box: this,
            id: this.id
        };

        // and store the reference back in fun too
        try {
            setUnenum(fun, "__JSBNG_data", mfun.__JSBNG_data);
        } catch (ex) {}
    }

    function getMemoizationWrapper(obj) {
        if (obj === null) return null;
        if (typeof obj !== "object" && typeof obj !== "function") {
            return null;
        }
        if (obj instanceof MemoizationWrapper) return obj;
        try {
            if (hasOwnProp(obj, "__JSBNG_data")) return obj.__JSBNG_data;
        } catch (ex) {}
        return null;
    }

    function getUnwrappedObject(obj) {
        var w = getMemoizationWrapper(obj);
        if (w === null) return obj;
        return w.obj;
    }

    function stringify(obj) {
        var w;
        if ((w = getMemoizationWrapper(obj)) !== null) {
            return w.id;
        }

        switch (typeof(obj)) {
            case "object":
                if (obj === null) {
                    return "null";
                } else if (obj === window) {
                    return "ow" + pageId;
                } else if ("JSBNG_Record" in obj) { /* another window */
                    return "ow" + obj.JSBNG_Record.pageId;
                } else if (obj instanceof RegExp) {
                    return obj.toString();
                } else {
                    return "{__JSBNG_unknown_object:true}";
                }

            case "function":
                return "{__JSBNG_unknown_function:true}";

            case "string":
                return stringWrap(obj);

            default:
                return ""+obj;
        }
    }

    /* this simplistic wrapping case works for anything other than functions
     * referenced by memoized objects, and additionally has workarounds for
     * unusual, ECMAScript-incompatible browser behavior */
    function wrap(thing, name) {
        var w = thing;
        var type = typeof(thing);

        // browser workarounds

        /* WebKit presents some globals as objects that are really functions,
         * so we use a heuristic to change them */
        try {
            if (type === "object" &&
                thing !== null &&
                typeof(thing.prototype) === "object" &&
                /^\[object [^ ]*Constructor\]$/.test(thing.toString())) {
                type = "function";
            }
        } catch (ex) {}

        if (typeof name === "undefined") name = "";
        switch (type) {
            case "object":
                try {
                    if (thing !== null && thing !== window && !("JSBNG_Record" in thing)) {
                        if ((w = getMemoizationWrapper(thing)) === null) {
                            try {
                                if (hasOwnProp(thing, "__JSBNG_wrapper")) {
                                    w = thing.__JSBNG_wrapper;
                                }
                            } catch (ex) {}

                            if (w === null) {
                                w = new MemoizationWrapper(thing);
                                if (!/Storage$/.test(name)) {
                                    try {
                                        setUnenum(thing, "__JSBNG_wrapper", w);
                                    } catch (ex) {}
                                }
                            }
                        }
                    }
                } catch (ex) {}
                break;

            case "function":
                if (hasOwnProp(thing, "__JSBNG_data")) {
                    w = thing.__JSBNG_data.fun;
                } else {
                    w = (new MemoizingFunction(window, "fun", thing)).fun;
                }
                break;
        }
        return w;
    }

    function wrapMajor(obj, objstr, prop) {
        var wo = obj["JSBNG__" + prop] = wrap(obj[prop], prop);
        var w;
        var val = "undefined";
        try {
            if ((w = getMemoizationWrapper(wo)) !== null) {
                val = w.id;
            } else if (wo === null) {
                val = "null";
            } else if (wo === window) {
                val = "ow" + pageId;
            } else if (typeof wo === "object" && "JSBNG_Record" in wo) { /* another window */
                val = "ow" + wo.JSBNG_Record.pageId;
            } else if (typeof wo === "string") {
                val = "\"" + wo + "\"";
            } else {
                val = wo+"";
            }
        } catch (ex) {}
        sendMessageStmt("get", {"obj": objstr, "prop": "JSBNG__" + prop, "val": val});
    }

    // wrap things that should be instrumented
    for (var prop in JSBNG_Record_doInstrument) {
        if (prop in window) {
            if (window[prop] === void 0) {
                /* Probably a "hidden" property for compatibility reasons, such
                 * as Opera's window.attachEvent, though this also could just
                 * have the value undefined. If the former case, this cannot be
                 * replayed since it does not follow the ECMAScript spec, so we
                 * just delete it (or try to) */
                delete window[prop];
            } else {
                wrapMajor(window, "ow" + pageId, prop);
            }
        }
    }
    wrapMajor(Math, "ow" + pageId + ".Math", "random");
    for (var prop in JSBNG_Record_onInstrument) {
        (function(prop) {
            window[prop] = function() {
                var e = window["JSBNG__" + prop];
                if (e) return e.apply(this, arguments);
            }
        })(prop);
    }

    // workaround for navigator on Firefox
    delete window.navigator.__JSBNG_wrapper;

    // get a member of an object which may be instrumented
    this.get = function(obj, name) {
        var mobj;
        if ((mobj = getMemoizationWrapper(obj)) !== null) {
            var value = mobj.obj[name];
            var cov = mobj.obj["__JSBNG_client_owned_" + name];

            // if the client owns this value, don't log anything
            if (typeof cov !== "undefined" && value === cov)
                return mobj.obj;

            // allow instrumented names
            var renamed = false;
            if (typeof value === "undefined" && /^JSBNG__/.test(name)) {
                value = mobj.obj[name.substring(7)];
                renamed = true;
            }

            var wv;
            var ret = mobj.obj;

            // a special case for document.location for SSL issues
            if (mobj.obj === document.location) {
                if (name === "href" && /^http:\/\/jsbngssl/.test(value)) {
                    // don't let them see the non-SSL-ness
                    value = value.replace(/^http:\/\/jsbngssl\./, "https://");
                    ret = {};
                    ret[name] = value;
                } else if (name === "protocol" && value === "http:" && /^http:\/\/jsbngssl/.test(document.location.href)) {
                    // don't let them see the fake SSL
                    value = "https:";
                    ret = {};
                    ret[name] = value;
                } else {
                    ret = {};
                    ret[name] = value;
                }
                if (typeof value === "string")
                    value = stringWrap(value);

            // another special case for Function.prototype.{call,apply}
            } else if (typeof obj === "function" &&
                       (name === "call" || name === "apply" || name === "bind") &&
                       value === Function.prototype[name]) {
                // nothing to do here
                return obj;

            } else {
                if (renamed) {
                    ret = {};
                    ret[name] = value;
                }

                switch (typeof value) {
                    case "object":
                        if (value !== null && value !== window &&
                            !(value instanceof RegExp)) {
                            // wrap it up for return
                            wv = wrap(value);
                            value = wv.id;
                            ret = {};
                            ret[name] = wv;
                        } else {
                            value = stringify(value);
                        }
                        break;

                    case "function":
                        if (hasOwnProp(value, "__JSBNG_data")) {
                            ret = new MemoizingFunction(obj, name, value, value.__JSBNG_data.id);
                        } else {
                            ret = new MemoizingFunction(obj, name, value);
                        }
                        value = ret.id;
                        break;

                    case "boolean":
                    case "number":
                        value = "" + value;
                        break;

                    case "string":
                        value = stringWrap(value);
                        break;

                    case "undefined":
                        value = "void 0";
                        break;

                    default:
                        value = "\"" + value + "\"";
                }
            }
            sendMessageStmt("get", {"obj": mobj.id, "prop": name, "val": value});
            return ret;

        } else if (typeof(obj) !== "undefined" && obj !== null && /^JSBNG__/.test(name)) {
            // a load to window
            var sname = name.replace(/^JSBNG__/, "");
            try {
                if ("JSBNG_Record" in obj) {
                    // still need to record this global reference
                    var value = obj[name];
                    var svalue = obj[sname];

                    // members may have shown up late, particularly event/JSBNG__event
                    if (typeof(value) === "undefined" && typeof(svalue) !== "undefined") {
                        wrapMajor(obj, "ow" + obj.JSBNG_Record.pageId, sname);
                        value = obj[name];
                        delete obj[name];
                        var ret = {};
                        ret[name] = value;
                        return ret;
                    }

                    // if it's something we can record the value of, do so
                    if (typeof(value) !== "object" && typeof(value) !== "function") {
                        sendMessageStmt("get", {"obj": "ow" + obj.JSBNG_Record.pageId, "prop": name, "val": stringify(value)});
                    }

                    return obj;
                }

                if (name in obj) {
                    // OK, got renamed
                    return obj;
                }

                if (!(sname in obj)) {
                    // OK, didn't have it in the first place
                    return obj;
                }
            } catch (ex) {}

            alert("Read to instrumented name " + name + " in uninstrumented object!");
            //throw new Error();
            return obj;

        } else if (obj === window) {
            if (name in JSBNG_Record_doInstrument && !(name in Object.prototype)) {
                var value = obj[name];
                if (typeof(value) !== "object" && typeof(value) !== "function") {
                    sendMessageStmt("get", {"obj": stringify(obj), "prop": name, "val": stringify(value)});
                }
                alert("WARNING: Read to uninstrumented name " + name + " in window!");
            }
            return obj;

        } else {
            return obj;
        }
    }

    // get the bare object underlying this
    this.getUnwrapped = function(obj) {
        var mobj;
        if ((mobj = getMemoizationWrapper(obj)) !== null) {
            return mobj.obj;
        } else {
            return obj;
        }
    }

    // set a member of an object, perhaps with an assignment op
    this.set = function(obj, name, value, assignOp) {
        var mobj;
        if (typeof assignOp != "undefined") {
            // OK, get it first
            var oldvalue = this.get(obj, name)[name];

            // then change the value
            value = Function("x", "y", "return (x " + assignOp + " y);")(oldvalue, value);
        }

        // now update it
        if ((mobj = getMemoizationWrapper(obj)) !== null) {
            sendMessageStmt("set", {"obj": mobj.id, "prop": name, "val": stringify(value)});

            // sometimes this will fire synchronous events, so "forget" that we're in JS for a while
            top.JSBNG_Record.callerJS = false;
            top.JSBNG_Record.deferEvents = true;
            try {
                mobj.obj[(typeof name === "string") ? name.replace(/^JSBNG__/, "") : name] = value;

                // mark that this is owned by the client, not the browser
                Object.defineProperty(mobj.obj, "__JSBNG_client_owned_" + name, {
                    writable: true, configurable: true, enumerable: false,
                    value: value
                });
            } catch (ex) {
                top.JSBNG_Record.callerJS = true;
                top.JSBNG_Record.deferEvents = false;
                throw ex;
            }
            top.JSBNG_Record.callerJS = true;
            top.JSBNG_Record.deferEvents = false;
        } else {
            obj[name] = value;
        }

        // cheap hack for window.location = whatever
        if (name === "JSBNG__location") {
            obj.location = value;
        }

        return value;
    }

    // delete a member of an object
    this.deletee = function(obj, name) {
        var mobj;

        // now update it
        if ((mobj = getMemoizationWrapper(obj)) !== null) {
            sendMessageStmt("set", {"obj": mobj.id, "prop": name, "val": "undefined"});
            delete mobj.obj[(typeof name === "string") ? name.replace(/^JSBNG__/, "") : name];
        } else {
            delete obj[name];
        }

        return true;
    }


    // callpath recording
    this.path = function(fun) {
        sendMessageStmt("path", {"func": fun});
    }

    // browser called an event
    this.callerJS = false;
    this.eventCall = function(fun, sfid, instance, cthis, cargs) {
        if (top.JSBNG_Record.deferEvents) {
            // if this isn't really an event at all, don't defer
            if (cargs.length === 1 && cargs[0] instanceof Event)
                top.JSBNG_Record.deferEvent(fun, cthis, cargs);
            return;
        }

        top.JSBNG_Record.callerJS = true;

        // wrap up the arguments
        var wthis = wrap(cthis);
        var wargs = [];
        for (var i = 0; i < cargs.length; i++)
            wargs.push(wrap(cargs[i]));

        // make a string to send back
        var sargs = "[" + stringify(wthis);
        for (var i = 0; i < wargs.length; i++)
            sargs += "," + stringify(wargs[i]);
        sargs += "]";

        sendMessageStmt("event", {"func": sfid, "inst": instance, "args": sargs});

        var ret = undefined;
        try {
            ret = Function.prototype.apply.call(fun, wthis, wargs);
        } catch (ex) {
            top.JSBNG_Record.callerJS = false;
            this.flushDeferredEvents();
            throw ex;
        }

        top.JSBNG_Record.callerJS = false;
        this.flushDeferredEvents();
        return ret;
    }

    // logged a potential event
    var sfinsts = {};
    this.eventInstance = function(sfid) {
        if (!(sfid in sfinsts)) sfinsts[sfid] = 0;
        return sfinsts[sfid]++;
    }

    // mark a function as instrumented
    this.markFunction = function(fun) {
        fun.JSBNG_isInstrumented = true;
        return fun;
    }

    // temporary space for recording
    this.temps = {};
})();

(function() {
    // replacement for Function.prototype.bind
    var scr = "Function.prototype.bind = function(to) { var f = this; return function() { Function.prototype.apply.call(f, to, arguments); }; };";
    var iscr = JSBNG_Record.instrumentScript(scr);
    JSBNG_Record.scriptLoad(scr, ("s" + Math.random()).replace(/\./g, ""), false);
    eval(iscr);
})();
