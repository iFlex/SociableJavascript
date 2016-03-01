/*
 * Copyright (C) 2010-2012 Purdue University
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

(function() {
    eval(Narcissus.definitions.consts);

    // mark our version and date
    JSBNG.Util.version(function(ver) {
        JSBNG.Util.data(JSON.stringify({"type": "info", "version": ver, "date": new Date().toISOString()}));
    });

    // generate the JS to list objects to instrument
    function generateRecordObjects() {
        var js = "JSBNG_Record_doInstrument={";
        for (var k in JSBNG.Objects.doInstrument) {
            js += k + ":true,";
        }
        js += "0:0};" +
            "JSBNG_Record_onInstrument={";
        for (var k in JSBNG.Objects.onInstrument) {
            js += k + ":true,";
        }
        js += "0:0};" +
            "JSBNG_Record_dontInstrument={";
        for (var k in JSBNG.Objects.dontInstrument) {
            js += k + ":true,";
        }
        js += "0:0};" +
            "JSBNG_Record_destroy={";
        for (var k in JSBNG.Objects.destroy) {
            js += k + ":true,";
        }
        js += "0:0};";
        return js;
    }


    // create a simulation Narcissus node
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

    // make a temporary variable
    function mkTemp(n) {
        while (n.orig) n = n.orig;
        var tname = n.filename + ":" + n.start;
        return fakeNode(n, IDENTIFIER, null, {value:"JSBNG_Record.temps.t" + JSBNG.Util.hash(tname)});
    }

    // replace a DOT with an INDEX
    function dotToIndex(n) {
        return fakeNode(n, INDEX, [
            n.children[0],
            fakeNode(n, STRING, null, {value:n.children[1].value})
        ]);
    }


    function postMessage(request, ret) {
        var msg = "";
        request.addListener("data", function(chunk) {
            msg += chunk.toString("utf8");
        });
        request.addListener("end", function() {
            //JSBNG.Util.debug("Incoming message: " + msg);
            JSBNG.Util.data(msg);
            ret({data: "", "x-jsbench-ng-no-cache": "true"});
        });
    }

    function requestInstrumentation(request, ret) {
        var msg = "";
        request.addListener("data", function(chunk) {
            msg += chunk.toString("utf8");
        });
        request.addListener("end", function() {
            var scr = JSBNG.Instrumentation.applyJSInsts("scriptload", 1, msg);
            ret({data: scr, "x-jsbench-ng-no-cache": "true"});
        });
    }

    // handle special URLs
    JSBNG.Instrumentation.pushPreInst(function(url, doc) {
        // GET-only
        if (doc === "/JSBENCH_NG_RECORD_OBJECTS.js") return ({
            "content-type": "text/javascript",
            "x-jsbench-ng-no-cache": "true",
            data: generateRecordObjects()
        });
        if (doc === "/JSBENCH_NG_RECORD.js") return ({
            "content-type": "text/javascript",
            "x-jsbench-ng-no-cache": "true",
            data: (
                JSBNG.Util.readFile("instrumentation/client-replayable.js") + "\n" +
                JSBNG.Util.readFile("instrumentation/client-record.js")
            )
        });

        // POST-only
        if (doc === "/JSBENCH_NG_MSG") return postMessage;
        if (doc === "/JSBENCH_NG_INSTR") return requestInstrumentation;
        return null;
    });

    // replace pages with a giant page-write event, after loading our data
    JSBNG.Instrumentation.pushHTMLInst(function(data) {
        // remove doctype and XML stuff
        data = data.replace(/<![a-zA-Z][^>]*>/g, "").replace(/<\?([^?]|\?[^>])*\?>/g, "");

        // redirect https
        data = data.replace(/https:\/\//g, "http://jsbngssl.").replace(
                            /https:\\\/\\\//g, "http:\\/\\/jsbngssl.");

        if (!JSBNG.Options.enableIframes) {
            // remove iframes
            JSBNG.Instrumentation.instTagInHTML(data, "iframe", function(tag) {
                if (tag.length === 4) {
                    data = data.slice(0, tag[0]) + data.slice(tag[0], tag[3]).replace(/iframe/gi, "div") + data.slice(tag[3]);
                } else {
                    data = data.slice(0, tag[0]) + data.slice(tag[0], tag[1]).replace(/iframe/gi, "div") + data.slice(tag[1]);
                }
            });
        }

        // and generate our output
        var out = "<!doctype html>" +
            "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\" />" +
            "<script type=\"text/javascript\" src=\"/JSBENCH_NG_RECORD_OBJECTS.js\"></script>" +
            "<script type=\"text/javascript\" src=\"/JSBENCH_NG_RECORD.js\"></script>" +
            "<script type=\"text/javascript\" xjsbngnotouch=\"yes\">" +

            "JSBNG_Record.sendMessageStmt(\"pageload\", {\"data\":" +
            JSON.stringify(data).replace(/</g, "\\u003C").replace(/>/g, "\\u003E") + "});" +

            "</script>" + data;
        return out;
    });

    JSBNG.Instrumentation.pushJSInst(function(tree) {
        function rename(ident) {
            if (JSBNG.Objects.doInstrument.hasOwnProperty(ident) ||
                JSBNG.Objects.onInstrument.hasOwnProperty(ident) ||
                ident === "random") {
                return "JSBNG__" + ident;
            }
            return ident;
        }

        // get the original script
        var scr = Narcissus.decompiler.pp(tree);
        var sid = "s" + JSBNG.Util.hash(scr);

        // keep track of function IDs
        var lastFid = 0;

        // and for..in IDs
        var lastFInId = 0;

        return JSBNG.JSI.instrument(tree, function(n) {
            if ("orig" in n) return n;

            // top-level script
            if (n === tree) {
                // top-level script
                n.children = [
                    fakeNode(n, TRY, null, {
                        parenthesized: false,
                        tryBlock: fakeNode(n, BLOCK, [
                            fakeNode(n, CALL, [
                                fakeNode(n, IDENTIFIER, null, {value:"JSBNG_Record.scriptLoad"}),
                                fakeNode(n, LIST, [
                                    fakeNode(n, STRING, null, {value:scr}),
                                    fakeNode(n, STRING, null, {value:sid})
                                ], {parenthesized:false})
                            ]),
                            fakeNode(n, ASSIGN, [
                                fakeNode(n, IDENTIFIER, null, {value:"window.top.JSBNG_Record.callerJS"}),
                                fakeNode(n, TRUE, null, null)
                            ])
                        ].concat(n.children), {parenthesized:false}),
                        catchClauses: [],
                        finallyBlock: fakeNode(n, BLOCK, [
                            fakeNode(n, ASSIGN, [
                                fakeNode(n, IDENTIFIER, null, {value:"window.top.JSBNG_Record.callerJS"}),
                                fakeNode(n, FALSE, null, null)
                            ]),
                            fakeNode(n, CALL, [
                                fakeNode(n, IDENTIFIER, null, {value:"window.top.JSBNG_Record.flushDeferredEvents"}),
                                fakeNode(n, LIST, [], {parenthesized:false})
                            ])
                        ], {parenthesized:false})
                    })
                ];
            }

            if (!JSBNG.Options.enableIframes) {
                // iframes
                if (n.type === STRING) {
                    if (n.value.toLowerCase() === "iframe") {
                        n.value = "div";
                    } else if (n.value.match(/<iframe/i)) {
                        n.value = n.value.replace(/iframe/gi, "div");
                    }
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

                } else if (n.type === STRING && /^[a-z]+ [a-z ]+$/.test(n.value)) {
                    // absurdly-specific case for jQuery's space-delimited function lists
                    var valueSplit = n.value.split(" ");
                    for (var i = 0; i < valueSplit.length; i++) {
                        valueSplit[i] = rename(valueSplit[i]);
                    }
                    n.value = valueSplit.join(" ");

                } else if (n.type === STRING && /^[a-z]+,[a-z,]+$/.test(n.value)) {
                    // absurdly-specific case for Amazon's comma-delimited function lists
                    var valueSplit = n.value.split(",");
                    for (var i = 0; i < valueSplit.length; i++) {
                        valueSplit[i] = rename(valueSplit[i]);
                    }
                    n.value = valueSplit.join(",");

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

                // recreate it as an INDEX
                n = dotToIndex(n);
            }

            if (n.type === INDEX) {
                // call JSBNG_Record.get instead
                if (n.children[1].type === STRING || n.children[1].type === NUMBER || n.children[1].type === IDENTIFIER) {
                    // RHS is a literal, don't need to store it in a temp
                    n = fakeNode(n, INDEX, [
                        fakeNode(n, CALL, [
                            fakeNode(n, IDENTIFIER, null, {value:"JSBNG_Record.get"}),
                            fakeNode(n, LIST, [
                                n.children[0],
                                n.children[1]
                            ], {parenthesized:false})
                        ]),
                        n.children[1]
                    ]);
                } else {
                    // store computed RHS in a temp
                    var tmp = mkTemp(n);
                    n = fakeNode(n, INDEX, [
                        fakeNode(n, CALL, [
                            fakeNode(n, IDENTIFIER, null, {value:"JSBNG_Record.get"}),
                            fakeNode(n, LIST, [
                                n.children[0],
                                fakeNode(n, ASSIGN, [
                                    tmp,
                                    n.children[1]
                                ])
                            ], {parenthesized:false})
                        ]),
                        tmp
                    ]);
                }
            }

            // assignments
            if (n.type === ASSIGN) {
                if (n.children[0].type === DOT) {
                    // recreate it as an INDEX
                    n.children[0].children[1].value = rename(n.children[0].children[1].value);
                    n.children[0] = dotToIndex(n.children[0]);
                }

                if (n.children[0].type === INDEX) {
                    if (n.assignOp !== null) {
                        n = fakeNode(n, CALL, [
                            fakeNode(n, IDENTIFIER, null, {value:"JSBNG_Record.set"}),
                            fakeNode(n, LIST, [
                                n.children[0].children[0],
                                n.children[0].children[1],
                                n.children[1],
                                fakeNode(n, STRING, null, {value:Narcissus.definitions.tokens[n.assignOp]})
                            ], {parenthesized:false})
                        ]);
                    } else {
                        n = fakeNode(n, CALL, [
                            fakeNode(n, IDENTIFIER, null, {value:"JSBNG_Record.set"}),
                            fakeNode(n, LIST, [
                                n.children[0].children[0],
                                n.children[0].children[1],
                                n.children[1]
                            ], {parenthesized:false})
                        ]);
                    }
                }
            }

            // deletions (similar to assignments)
            if (n.type === DELETE) {
                if (n.children[0].type === DOT) {
                    // recreate it as an INDEX
                    n.children[0].children[1].value = rename(n.children[0].children[1].value);
                    n.children[0] = dotToIndex(n.children[0]);
                }

                if (n.children[0].type === INDEX) {
                    n = fakeNode(n, CALL, [
                        fakeNode(n, IDENTIFIER, null, {value:"JSBNG_Record.deletee"}),
                        fakeNode(n, LIST, [
                            n.children[0].children[0],
                            n.children[0].children[1]
                        ], {parenthesized:false})
                    ]);
                }
            }

            // for..ins
            if (n.type === FOR_IN) {
                var fInId = "fin" + (lastFInId++);
                n.object.parenthesized = true;
                n.object = fakeNode(n, CALL, [
                    fakeNode(n, IDENTIFIER, null, {value:"JSBNG_Record.getUnwrapped"}),
                    fakeNode(n, LIST, [
                        n.object
                    ], {parenthesized:false})
                ]);

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
                                fakeNode(n, IDENTIFIER, null, {value:"JSBNG_Record.forInKeys"}),
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

            // and ins
            if (n.type === IN) {
                n.children[1] = fakeNode(n, CALL, [
                    fakeNode(n, IDENTIFIER, null, {value:"JSBNG_Record.getUnwrapped"}),
                    fakeNode(n, LIST, [
                        n.children[1]
                    ], {parenthesized:true})
                ]);
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

                // replace the body with something to record it
                n.body.topScript = true;
                n.body = fakeNode(null, SCRIPT, [
                    fakeNode(n, IF, null, {
                        condition: fakeNode(n, NOT, [fakeNode(n, IDENTIFIER, null, {value:"JSBNG_Record.top.JSBNG_Record.callerJS"})]),
                        thenPart: fakeNode(n, RETURN, null, {
                            value: fakeNode(n, CALL, [
                                fakeNode(n, IDENTIFIER, null, {value:"JSBNG_Record.eventCall"}),
                                fakeNode(n, LIST, [
                                    fakeNode(n, IDENTIFIER, null, {value:"arguments.callee"}),
                                    fakeNode(n, STRING, null, {value: sfid}),
                                    fakeNode(n, IDENTIFIER, null, {value: sfid + "_instance"}),
                                    fakeNode(n, IDENTIFIER, null, {value:"this"}),
                                    fakeNode(n, IDENTIFIER, null, {value:"arguments"})
                                ], {parenthesized:false})
                            ]),
                            parenthesized:false
                        }),
                        parenthesized:false}),
                    JSBNG.Options.enablePath ? fakeNode(n, CALL, [
                        fakeNode(n, IDENTIFIER, null, {value:"JSBNG_Record.path"}),
                        fakeNode(n, LIST, [
                            fakeNode(n, STRING, null, {value: sfid})
                        ], {parenthesized:false})
                    ]) : fakeNode(n, NULL, null),
                    n.body
                ], {parenthesized:false});

                // stuff we need to mark it
                var varDecl = fakeNode(n, VAR, [
                    fakeNode(n, IDENTIFIER, null, {
                        name: sfid + "_instance",
                        value: sfid + "_instance"
                    }),
                ], {parenthesized:false});
                var varAssign = fakeNode(n, ASSIGN, [
                    fakeNode(n, IDENTIFIER, null, {value: sfid + "_instance"}),
                    fakeNode(n, CALL, [
                        fakeNode(n, IDENTIFIER, null, {value:"JSBNG_Record.eventInstance"}),
                        fakeNode(n, LIST, [
                            fakeNode(n, STRING, null, {value: sfid})
                        ], {parenthesized:false})
                    ])
                ]);


                // then mark it
                //if (n.functionForm !== EXPRESSED_FORM)
                if (n.functionForm !== 1) { /* FIXME: this should be a global */
                    // function declaration, save in a separate statement
                    n = fakeNode(null, SCRIPT, [
                        n, varDecl, varAssign,
                        fakeNode(n, CALL, [
                            fakeNode(n, IDENTIFIER, null, {value: "JSBNG_Record.markFunction"}),
                            fakeNode(n, LIST, [
                                fakeNode(n, IDENTIFIER, null, {value: n.name})
                            ], {parenthesized:false})
                        ])
                    ], {parenthesized:false, topScript:true});
                } else {
                    // anonymous function, save inline
                    n.parenthesized = true;
                    n = fakeNode(null, CALL, [
                        fakeNode(null, FUNCTION, null, {
                            functionHandled: true,
                            params: [],
                            body: fakeNode(null, SCRIPT, [
                                varDecl, varAssign,
                                fakeNode(null, RETURN, null, {
                                    value: fakeNode(null, CALL, [
                                        fakeNode(n, IDENTIFIER, null, {value:"JSBNG_Record.markFunction"}),
                                        fakeNode(null, LIST, [
                                            n
                                        ], {parenthesized:false})
                                    ]),
                                    parenthesized:false
                                })
                            ], {parenthesized:false})
                        }),
                        fakeNode(null, LIST, [], {parenthesized:false})
                    ]);
                }
            }

            return n;
        }, null);
    });
})();
