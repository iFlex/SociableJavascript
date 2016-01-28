/*
 * Copyright (C) 2011, 2012 Purdue University
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

JSBNG.Replay = new (function() {
    eval(Narcissus.definitions.consts);

    var replayScript = (
        JSBNG.Util.readFile("instrumentation/client-replayable.js") + "\n" +
        JSBNG.Util.readFile("instrumentation/client-replay.js")
    );
    var subScripts = {};

    // create a simulation Narcissus node FIXME: duplicated from record
    function fakeNode(n, type, children, other) {
        if (typeof children === "undefined" || children === null) children = [];
        if (typeof other === "undefined") other = {};

        var ret = {
            type:type,
            parenthesized:true,
            children:children
        };
        if (n !== null) ret.orig = n;
        for (var k in other) ret[k] = other[k];
        return ret;
    }

    // make sure this is safe for a variable name
    function safeName(v) {
        if (typeof(v) === "string") {
            return v.replace(/[^A-Za-z0-9_]/g, "_");
        } else {
            return v;
        }
    }

    JSBNG.Instrumentation.pushPreInst(function(url, doc) {
        // GET-only
        if (doc === "/JSBENCH_NG_REPLAY.js") return ({
            "content-type": "text/javascript",
            "x-jsbench-ng-no-cache": "true",
            data: replayScript
        });

        if (/^\/JSBENCH_NG\//.test(doc)) {
            var scr = doc.substring(12, doc.length - 3);
            return ({
                "content-type": "text/javascript",
                "x-jsbench-ng-no-cache": "true",
                data: subScripts[scr]
            });
        }

        return ({
            "content-type": "text/html; charset=UTF-8",
            "x-jsbench-ng-no-cache": "true",
            data: "<!doctype html><html><head><title></title></head><body>" +
                  "<script type=\"text/javascript\" src=\"/JSBENCH_NG_REPLAY.js\"></script>" +
                  "</body></html>"
        });
    });

    this.replayScript = function() {
        return replayScript;
    }

    // sid of the current script
    var sid = null;

    // sfids to be remembered
    var rememberSfids = {};

    // for..in IDs
    var lastFInId = 0;

    JSBNG.Instrumentation.pushJSInst(function(tree) {
        function rename(ident) {
            if (JSBNG.Objects.doInstrument.hasOwnProperty(ident) ||
                JSBNG.Objects.onInstrument.hasOwnProperty(ident) ||
                ident === "random") {
                return "JSBNG__" + ident;
            }
            return ident;
        }

        var lastFid = 0;

        return JSBNG.JSI.instrument(tree, function(n) {
            if ("orig" in n) return n;

            if (!JSBNG.Options.enableIframes) {
                // iframes
                if (n.type === STRING && n.value.toLowerCase() === "iframe") {
                    n.value = "div";
                }
            }

            // gets
            if (n.type === IDENTIFIER || n.type === STRING) {
                if (n.type === STRING && /\./.test(n.value)) {
                    // maybe a .-separated list
                    var valueSplit = n.value.split(".");
                    for (var i = 0; i < valueSplit.length; i++) {
                        valueSplit[i] = rename(valueSplit[i]);
                    }
                    n.value = valueSplit.join(".");
                } else {
                    // perhaps rename it
                    n.value = rename(n.value);
                }
            }

            if (n.type === VAR) {
                for (var i = 0; i < n.children.length; i++) {
                    n.children[i].value = rename(n.children[i].value);
                    n.children[i].name = rename(n.children[i].name);
                }
            }

            if (n.type === DOT) {
                // if the right-hand side should be instrumented, do so
                n.children[1].value = rename(n.children[1].value);
            }

            // assignments
            if (n.type === ASSIGN) {
                if (n.children[0].type === DOT) {
                    // recreate it as an INDEX
                    n.children[0].children[1].value = rename(n.children[0].children[1].value);
                }
            }

            // for..ins
            if (n.type === FOR_IN) {
                var fInId = "fin" + (lastFInId++);
                n.object.parenthesized = true;

                var varnm = "???";
                if (n.varDecl) {
                    varnm = n.varDecl.children[0].name;
                } else {
                    varnm = n.iterator.value;
                }

                n = fakeNode(n, BLOCK, [
                    fakeNode(n, VAR, [
                        fakeNode(n, IDENTIFIER, null, {
                            name: fInId + "keys",
                            value: fInId + "keys",
                            initializer: fakeNode(n, CALL, [
                                fakeNode(n, IDENTIFIER, null, {value:"window.top.JSBNG_Replay.forInKeys"}),
                                fakeNode(n, LIST, [
                                    n.object
                                ], {parenthesized:false})
                            ])
                        }),
                        fakeNode(n, IDENTIFIER, null, {
                            name: fInId + "i",
                            value: fInId + "i",
                            initializer: fakeNode(n, NUMBER, null, {value: 0})
                        })
                    ], {parenthesized:false}),
                    (n.varDecl ? n.varDecl : fakeNode(n, NUMBER, null, {value: 0})),
                    fakeNode(n, FOR, null, {
                        isLoop: true,
                        condition: fakeNode(n, IDENTIFIER, null, {value:
                            fInId + "i < " + fInId + "keys.length"
                        }),
                        update: fakeNode(n, IDENTIFIER, null, {value:
                            fInId + "i++"
                        }),
                        body: fakeNode(n, BLOCK, [
                            fakeNode(n, ASSIGN, [
                                fakeNode(n, IDENTIFIER, null, {value:varnm}),
                                fakeNode(n, IDENTIFIER, null, {value:
                                    fInId + "keys[" + fInId + "i]"
                                })
                            ], {assignOp: null}),
                            n.body
                        ], {parenthesized:false}),
                        parenthesized:false
                    })
                ], {parenthesized:false});
            }

            // functions
            if (n.type === FUNCTION && !("functionHandled" in n)) {
                var sfid = sid + "_" + lastFid;
                lastFid++;
                n.functionHandled = true;

                // rename it
                if ("name" in n) {
                    n.name = rename(n.name);
                }

                // rename the parameters
                for (var i = 0; i < n.params.length; i++) {
                    n.params[i] = rename(n.params[i]);
                }

                // if we're verifying the call path, log it
                if (optim.verifiedPath) {
                    n.body.topScript = true;
                    n.body = fakeNode(null, SCRIPT, [
                        fakeNode(n, CALL, [
                            fakeNode(n, IDENTIFIER, null, {value:"window.top.JSBNG_Replay.path"}),
                            fakeNode(n, LIST, [
                                fakeNode(n, STRING, null, {value:sfid})
                            ], {parenthesized:false})
                        ]),
                        n.body
                    ], {parenthesized:false});
                }

                // if we need to remember this, do so
                if (sfid in rememberSfids) {
                    delete rememberSfids[sfid];

                    if (n.functionForm != 1) { // EXPRESSED_FORM
                        // declared function, save in a separate statement
                        n = fakeNode(null, SCRIPT, [
                            n,
                            fakeNode(n, CALL, [
                                fakeNode(n, IDENTIFIER, null, {value:"window.top.JSBNG_Replay." + sfid + ".push"}),
                                fakeNode(n, LIST, [
                                    fakeNode(n, IDENTIFIER, null, {value:n.name})
                                ], {parenthesized:false})
                            ])
                        ], {parenthesized:false});
                    } else {
                        // anonymous function, save inline
                        n = fakeNode(null, CALL, [
                            fakeNode(n, IDENTIFIER, null, {value:"window.top.JSBNG_Replay.push"}),
                            fakeNode(null, LIST, [
                                fakeNode(n, IDENTIFIER, null, {value:"window.top.JSBNG_Replay." + sfid}),
                                n
                            ], {parenthesized:false})
                        ]);
                    }
                }
            }

            return n;
        }, null);
    });

    // calculate dependencies in the log
    function calculateDependencies(log) {
        var objs = {};

        // first, just number every element
        for (var i = 0; i < log.length; i++) {
            log[i].index = i;
        }

        // now start figuring out deps
        var curEvent = null;
        for (var i = 0; i < log.length; i++) {
            var e = log[i];
            var curIsEvent = false;
            e.deps = [];
            e.dants = [];

            switch (e.type) {
                case "scriptload":
                case "event":
                    curEvent = e;
                    curIsEvent = true;
                    break;

                case "getter":
                    e.deps.push(objs[e.obj]);
                case "fundec":
                case "objdec":
                    objs[e.id] = e;
                    break;

                case "get":
                    if (e.val in objs) e.deps.push(objs[e.val]);
                case "set":
                    if (e.obj in objs) e.deps.push(objs[e.obj]);
                    break;

                case "call":
                case "new":
                    if (e.func in objs) e.deps.push(objs[e.func]);
                    // FIXME: Arguments
                    break;
            }

            if (!curIsEvent && curEvent !== null) {
                e.deps.push(curEvent);
            }
        }

        // and the dependants
        for (var i = 0; i < log.length; i++) {
            var e = log[i];
            for (var di = 0; di < e.deps.length; di++) {
                e.deps[di].dants.push(e);
            }
        }

        return log;
    }

    // all the various optimizing log instrumentations
    var optim = {
        useScriptTags: false,
        s: function(log) { // scripts first, load with script tags
            var slog = [];
            var elog = [];
            optim.useScriptTags = true;
            return log;
        },

        split: false,
        S: function(log) {
            optim.split = true;
            return log;
        },

        r: function(log) { // remove redundancies
            var olog = [];
            var vals = {};

            for (var i = 0; i < log.length; i++) {
                var redundant = false;
                var e = log[i];

                function assertOP(obj, prop) {
                    if (!(obj in vals)) vals[obj] = {};
                    if (!(prop in vals[obj])) vals[obj][prop] = "";
                    return vals[obj][prop];
                }

                switch (e.type) {
                    case "fundec":
                    case "objdec":
                    case "getter":
                        vals[e.id] = {};
                        break;

                    case "get":
                        if (assertOP(e.obj, e.prop) === e.val) redundant = true;
                        vals[e.obj][e.prop] = e.val;
                        break;

                    case "set":
                        assertOP(e.obj, e.prop);
                        vals[e.obj][e.prop] = e.val;
                        break;
                }

                if (!redundant)
                    olog.push(e);
            }

            return olog;
        },

        E: function(log) { // only call events in the replay proper
            var slog = [];
            var elog = [];

            for (var i = 0; i < log.length; i++) {
                var e = log[i];

                switch (e.type) {
                    case "start":
                    case "end":
                    case "scriptload":
                    case "event":
                        elog.push(e);
                        break;

                    default:
                        slog.push(e);
                }
            }

            return slog.concat(elog);
        },

        e: function(log) { // like E, but best-effort, only moves object setup that it knows is safe
            var slog = [];
            var elog = [];
            var vals = {};

            for (var i = 0; i < log.length; i++) {
                var e = log[i];

                switch (e.type) {
                    case "start":
                    case "end":
                    case "scriptload":
                    case "event":
                        elog.push(e);
                        break;

                    case "objdec":
                        slog.push(e);
                        vals[e.id] = {};
                        break;

                    case "get":
                        if (!(e.obj in vals)) vals[e.obj] = {};
                        if (!(e.prop in vals[e.obj])) {
                            slog.push(e);
                            vals[e.obj][e.prop] = e.val;
                        } else {
                            elog.push(e);
                        }
                        break;

                    default:
                        slog.push(e);
                }
            }

            return slog.concat(elog);
        },

        m: function(log) { return log; },
        mp: function(log) { // minimize memory usage
            var vars = [];
            var olog = [];
            var seen = {};
            var lastevent = null;

            function evforeach(e, fun) {
                function ifobj(e, m) {
                    if (/^[o][0-9]/.test(e[m])) e[m] = fun(e[m]);
                }

                switch (e.type) {
                    case "objdec":
                        ifobj(e, "id");
                        break;

                    case "getter":
                        ifobj(e, "obj");
                        break;

                    case "get":
                    case "set":
                        ifobj(e, "obj");
                        ifobj(e, "val");
                        break;

                    case "call":
                    case "new":
                        ifobj(e, "func");
                        ifobj(e, "ret");
                        break;

                    case "event":
                        // tear apart the args and put them back together
                        var eargs = e.args.substring(1, e.args.length - 1).split(",");
                        for (var j = 0; j < eargs.length; j++) {
                            ifobj(eargs, j);
                        }
                        e.args = "[" + eargs.join(",") + "]";
                        break;
                }
            }

            // first, figure out the /last/ use of everything
            for (var i = log.length - 1; i >= 0; i--) {
                var e = log[i];
                e.lastFor = {__proto__: null};
                evforeach(e, function(obj) {
                    if (!(obj in seen)) {
                        seen[obj] = true;
                        e.lastFor[obj] = true;
                    }
                    return obj;
                });
            }

            // then rename everything
            lastevent = null;
            for (var i = 0; i < log.length; i++) {
                var e = log[i];
                olog.push(e);

                // rename existing things
                evforeach(e, function(obj) {
                    for (var j = 0; j < vars.length; j++) {
                        if (vars[j] === obj) {
                            return "o" + j;
                        }
                    }

                    for (var j = 0; j < vars.length; j++) {
                        if (vars[j] === null) {
                            vars[j] = obj;
                            return "o" + j;
                        }
                    }

                    vars.push(obj);
                    return "o" + (vars.length - 1);
                });

                // then remove things for which this is the last element
                for (var l in e.lastFor) {
                    for (var j = 0; j < vars.length; j++) {
                        if (vars[j] === l) {
                            vars[j] = null;
                            olog.push({"type": "nullify", "id": "o" + j});
                            break;
                        }
                    }
                }
                delete e.lastFor;
            }

            return olog;
        },

        useHTML: false,
        d: function(log) { // remove document
            var olog = [];
            var docobj = "";
            optim.useHTML = true;

            calculateDependencies(log);

            // don't instrument it
            delete JSBNG.Objects.doInstrument.document;
            var events = {"addEventListener":true, "removeEventListener":true, "focus":true};

            remLoop: for (var i = 0; i < log.length; i++) {
                var e = log[i];

                // if this is the core declaration of document, remove it
                if (e.type === "get" && e.obj === "window" && e.prop === "JSBNG__document") {
                    e.removed = true;
                    docobj = e.val;

                    // now add some necessary functions
                    for (var ta in events) {
                        olog.push({type: "get", obj: "Document.prototype", prop: "JSBNG__" + ta, val: "(function(){})"});
                        olog.push({type: "get", obj: "Node.prototype", prop: "JSBNG__" + ta, val: "(function(){})"});
                    }

                    continue;
                }

                /* if this is something instrumented under document, keep it
                 * (there are a few examples of these other than
                 * addEventListener and removeEventListener, namely location)
                 * */
                if (e.type === "get" && e.obj === docobj && /^JSBNG__/.test(e.prop) &&
                    !(e.prop.substring(7) in events)) {
                    e.obj = "document";
                    e.deps = [];
                }

                // otherwise, add it if we ought to
                for (var di = 0; di < e.deps.length; di++) {
                    if ("removed" in e.deps[di]) {
                        e.removed = true;
                        continue remLoop;
                    }
                }

                // not removed, keep it
                olog.push(e);
            }

            return olog;
        },

        verifiedGetsSets: false,
        V: function(log) { // get/set verification
            optim.verifiedGetsSets = true;
            var seen = {};

            var olog = [{type: "fundec", id: "fgetter"}, {type: "fundec", id: "fsetter"}];
            for (var i = 0; i < log.length; i++) {
                var e = log[i];
                switch (e.type) {
                    case "objdec":
                        e.getterSetter = true;
                        break;

                    case "get":
                        if (!/^ow/.test(e.obj)) {
                            // getting a value out of an instrumented object, make it a getter
                            var nm = e.obj + "." + e.prop;
                            if (!seen[nm]) {
                                olog.push({type: "regetter", obj: e.obj, prop: e.prop, id: "fgetter", setId: "fsetter"});
                                seen[nm] = true;
                            }
                            e = {type: "call", pageid: e.pageid, func: "fgetter",
                                args: "[" + e.obj + "," + JSON.stringify(e.prop) + "]",
                                ret: e.val};
                        }
                        break;

                    case "set":
                        var nm = e.obj + "." + e.prop;
                        if (!seen[nm]) {
                            olog.push({type: "regetter", obj: e.obj, prop: e.prop, id: "fgetter", setId: "fsetter"});
                            seen[nm] = true;
                        }
                        e = {type: "call", pageid: e.pageid, func: "fsetter",
                             args: "[" + e.obj + "," + JSON.stringify(e.prop) + "," + e.val + "]",
                             ret: "void 0"};
                        break;
                }
                olog.push(e);
            }

            return olog;
        },

        verifiedCalls: false,
        verifiedPath: false,
        v: function(log) { // verification
            var olog = [];
            var vlog = [];
            var vi;
            var en = 0;
            optim.verifiedCalls = true;
            if (JSBNG.Options.enablePath) optim.verifiedPath = true;

            for (var i = 0; i < log.length; i++) {
                var e = log[i];
                olog.push(e);

                switch (e.type) {
                    case "call":
                    case "new":
                        // this is verifiable, add {call,new}verifies
                        olog.push({type:(e.type+"verify"), func: e.func, args: e.args, ret: e.ret});
                        break;

                    case "scriptload":
                    case "event":
                    case "end":
                        olog = olog.concat(vlog);
                        vlog = [];
                        break;
                }
            }

            return olog;
        },

        removeExceptions: false,
        x: function(log) {
            optim.removeExceptions = true;
            return log;
        },

        u: function(log) { // remove unused objects
            var olog = [];
            var i;
            calculateDependencies(log);

            // get all of the events before the first scriptload
            beforeload: for (i = 0; i < log.length; i++) {
                var e = log[i];

                switch (e.type) {
                    case "fundec":
                    case "objdec":
                    case "getter":
                        if (e.dants.length <= 1) {
                            // only dependant is the initial set, remove this
                            e.removed = true;
                            continue beforeload;
                        }
                        break;

                    case "scriptload":
                        break beforeload;
                }

                // if anything depended on was removed, remove
                for (var di = 0; di < e.deps.length; di++) {
                    if ("removed" in e.deps[di]) {
                        e.removed = true;
                        continue beforeload;
                    }
                }

                olog.push(e);
            }

            for (; i < log.length; i++) {
                olog.push(log[i]);
            }
            return olog;
        },

        usePostMessage: false,
        þ: function(log) {
            optim.usePostMessage = true;
            return log;
        }
    };

    // mark lines
    JSBNG.Instrumentation.pushLogInst(function(log) {
        for (var i = 0; i < log.length; i++) {
            var e = log[i];
            e.line = i;
        }
        return log;
    });

    // convert gets with multiple values into getters
    JSBNG.Instrumentation.pushLogInst(function(log) {
        var multis = {};
        var multiSeen = {};
        var vals = {};
        var olog = [];

        // look for any getters with multiple values
        for (var i = 0; i < log.length; i++) {
            var e = log[i];
            switch (e.type) {
                case "script":
                case "event":
                    // reset our values
                    vals = {};
                    break;

                case "get":
                    var objprop = e.obj + "_" + safeName(e.prop);
                    if (objprop in vals && vals[objprop] !== e.val) {
                        // this one's a problem!
                        multis[objprop] = true;
                    } else {
                        vals[objprop] = e.val;
                    }
                    break;
            }
        }

        // then rewrite them as getters
        for (var i = 0; i < log.length; i++) {
            var e = log[i];
            switch (e.type) {
                case "get":
                    var objprop = e.obj + "_" + safeName(e.prop);
                    if (objprop in multis) {
                        // needs to be rewritten
                        if (!(objprop in multiSeen)) {
                            // declare the getter
                            olog.push({"type":"getter", "pageid":e.pageid, "id":"f" + objprop, "obj":e.obj, "prop":e.prop});
                            multiSeen[objprop] = true;
                        }
                        e = {"type":"call", "func":"f" + objprop, "args":"[" + e.obj + "]", "ret":e.val};
                    }
                    break;
            }
            if (e !== null) olog.push(e);
        }

        return olog;
    });

    // add all the optional instrumentation
    var options = JSBNG.Options.replayOptions;
    var post = [];
    for (var i = 0; i < options.length; i++) {
        JSBNG.Instrumentation.pushLogInst(optim[options[i]]);
        if ((options[i] + "p") in optim) post.push(optim[options[i] + "p"]);
    }

    // push forward "scriptload" and "event" events to after the events they use, and remember events to call
    JSBNG.Instrumentation.pushLogInst(function(log) {
        var olog = [];
        var curEvent = null;

        for (var i = 0; i < log.length; i++) {
            var e = log[i];
            if (e.type === "scriptload" || e.type === "event" || e.type === "start" || e.type === "end") {
                if (curEvent !== null) olog.push(curEvent);
                curEvent = e;

                if (e.type === "event")
                    rememberSfids[e.func] = true;
            } else {
                olog.push(e);
            }
        }

        if (curEvent !== null) olog.push(curEvent);

        return olog;
    });

    // any post-filters
    for (var i = 0; i < post.length; i++) {
        JSBNG.Instrumentation.pushLogInst(post[i]);
    }

    // the final log instrumentation is the actual generation
    JSBNG.Instrumentation.pushLogInst(function(log) {
        var replayFun = "";
        function as(s) {
            replayScript += s;
        }
        function af(s) {
            replayFun += s;
        }

        var vars = {__proto__: null};
        var seenEvents = {};
        var topFrame = null;
        var eventNo = 0;

        for (var i = 0; i < log.length; i++) {
            var e = log[i];
            af("// " + e.line + "\n");
            switch (e.type) {
                case "start":
                    if (optim.useScriptTags || optim.split) {
                        af("var cb; JSBNG_Replay$ = function(real, realcb) { if (!real) return; cb = realcb;\n");
                    } else {
                        af("JSBNG_Replay$ = function(real, cb) { if (!real) return;\n");
                    }
                    break;

                case "end":
                    af("cb(); return null; }\n");
                    break;

                case "init":
                    if (topFrame === null) {
                        // this is the top frame
                        topFrame = e.pageid;
                        as("var ow" + e.pageid + " = window;\n");
                    } else {
                        as("var ow" + e.pageid + " = iframe(\"" + e.pageid + "\");\n");
                    }
                    break;

                case "fundec":
                case "getter":
                    //as("var " + e.id + " = function() { return JSBNG_Replay.fun(" + e.id + ".cases, this, arguments); };\n");
                    if (!(e.id in vars)) {
                        as("var " + e.id + ";\n");
                        vars[e.id] = true;
                    }
                    if (optim.verifiedCalls) {
                        af(e.id + " = function() { return verifyCall(this.constructor !== " + e.id + ", " + e.id + ", this, arguments); };\n" +
                           e.id + ".callArgs = [];\n");
                    } else {
                        af(e.id + " = function() { return " + e.id + ".returns[" + e.id + ".inst++]; };\n");
                    }
                    af(e.id + ".returns = [];\n" +
                       e.id + ".inst = 0;\n");

                    if (e.type === "getter") {
                        // additionally, make this actually a getter
                        af("defineGetter(" + e.obj + ", " + JSON.stringify(e.prop) + ", " + e.id + ", " + e.setId + ");\n");
                    }
                    break;

                case "regetter":
                    af("defineRegetter(" + e.obj + ", " + JSON.stringify(e.prop) + ", " + e.id + ", " + e.setId + ");\n");
                    break;

                case "objdec":
                    if (!(e.id in vars)) {
                        as("var " + e.id + ";\n");
                        vars[e.id] = true;
                    }
                    af(e.id + " = {};\n");
                    break;

                case "nullify":
                    af(e.id + " = null;\n");
                    break;

                case "get":
                    e.prop = ""+e.prop; // FIXME: This should not need to be here!
                    if (/^[A-Za-z$_][A-Za-z0-9$_]*$/.test(e.prop) && e.prop !== "null") {
                        af(e.obj + "." + e.prop + " = " + e.val + ";\n");
                    } else {
                        af(e.obj + "[" + JSON.stringify(e.prop) + "] = " + e.val + ";\n");
                    }
                    break;

                case "call":
                case "new":
                    af(e.func + ".returns.push(" + e.ret + ");\n");
                    break;

                case "callverify":
                case "newverify":
                    af(e.func + ".callArgs.push(" + e.args + ");\n");
                    break;

                case "pageload":
                    if (optim.useHTML) {
                        // load the actual page
                        af("document.open(); document.write(" + JSON.stringify(e.data.replace(/<script([^<]|<[^\/]|<\/[^s]|<\/s[^c])*<\/script[^>]*>/gi, "").replace(/on(load|click|mouse|key)/gi, "non")) + "); document.close();\n");
                    }
                    break;

                case "scriptload":
                    var scr = e.data;
                    sid = e.sid;
                    if (!e.uninstrumented)
                        scr = JSBNG.Instrumentation.applyJSInsts("scriptload", 1, scr);
                    if (optim.useScriptTags) {
                        af("var scr = document.createElement(\"script\"); " +
                           "scr.src=\"/JSBENCH_NG/" + sid + ".js\"; " +
                           "scr.onload = onload" + sid + "; " +
                           "document.body.appendChild(scr); }\n" +
                           "function onload" + sid + "() {\n");
                        subScripts[sid] = scr;
                    } else {
                        if (topFrame !== null && topFrame !== e.pageid) {
                            af("ow" + e.pageid + ".JSBNG_Replay_geval(");
                        } else {
                            af("geval(");
                        }
                        af("" + JSON.stringify(scr) + ");\n");
                    }
                    break;

                case "event":
                    if (!(e.func in seenEvents)) {
                        seenEvents[e.func] = true;
                        as("JSBNG_Replay." + e.func + " = [];\n");
                    }

                    if (optim.usePostMessage) {
                        as("var JSBNG_Replay$" + eventNo + ";\n");
                        af("setTimeout(function() { JSBNG_Replay$" + eventNo + "(cb); }, 0);\n" +
                           "}\n" +
                           "JSBNG_Replay$" + eventNo + " = function(cb) {\n");
                    } else if (optim.split) {
                        if ((eventNo % 64) == 0) {
                            as("var JSBNG_Replay$" + eventNo + ";\n");
                            af("return JSBNG_Replay$" + eventNo + ";\n" +
                               "}\n" +
                               "JSBNG_Replay$" + eventNo + " = function(cb) {\n");
                        }
                    }
                    eventNo++;

                    if (optim.removeExceptions) af("try {");

                    // how shall we handle the args?
                    var args = e.args.split(",");
                    if (args[0] == "[ow" + e.pageid || args[0] == "[ow" + e.pageid + "]") {
                        // don't use fpc.apply for global functions called on window
                        af("JSBNG_Replay." + e.func + "[" + e.inst + "](" + args.slice(1).join(",").slice(0,-1) + ");\n");
                    } else {
                        af("fpc.call(JSBNG_Replay." + e.func + "[" + e.inst + "], " + e.args.slice(1,-1) + ");\n");
                    }
                    if (optim.removeExceptions) af('} catch (ex) { replayMessage(\'/"event".*"func":"' + e.func + '"/d ; \'); }');
                    break;


                // verification only
                case "setverify":
                    af("verifySet(" + JSON.stringify(e.obj) + ", " + e.obj + 
                       ", " + JSON.stringify(e.prop) + ", " +
                       JSON.stringify(e.val) + ", " + e.val + ");\n");
                    break;

                case "path":
                    if (optim.verifiedPath)
                        as("callpath.push(" + JSON.stringify(e.func) + ");\n");
                    break;

                case "info":
                    af("// record generated by JSBench " + e.version.replace(/ .*/, "") + " at " + e.date + "\n");
                    break;

                case "fin":
                case "set":
                case "path":
                    break;

                default:
                    JSBNG.Util.debug("Unrecognized log operation " + e.type + "!");
            }
        }

        as(replayFun + "finalize(); })();\n");

        return log;
    });

    // now actually instrument the log
    var log = JSON.parse("[{\"type\":\"start\"}," + JSBNG.Options.input + "{\"type\":\"end\"}]");
    JSBNG.Instrumentation.applyLogInsts(log);
    JSBNG.Util.debug("Ready");
})();
