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

require("./narcissus/lib/jsdefs");
require("./narcissus/lib/jslex");
require("./narcissus/lib/jsparse");
require("./narcissus/lib/jsdecomp");
Narcissus.options.version = 160;

JSBNG = {};

require("./cache");
require("./instrumentation");
require("./jsinstrumentation");
require("./instrumentation/objects");

// options to be loaded by the host
JSBNG.Options = {
    record: false,
    replay: false,
    replayOptions: "",
    loadOnly: false,
    cacheOnly: false,
    noCache: false,
    enableIframes: false,
    enablePath: false,
    input: null,
    output: null,

    shortArgs: {"c": {"record": true},
                "p": {"replay": true},
                "O": {next: "replayOptions"},
                "n": {noCache: true},
                "i": {next: "input"},
                "o": {next: "output"}},
    longArgs: {"record": "c",
               "replay": "p",
               "load-only": {loadOnly: true},
               "replay-options": "O",
               "cache-only": {cacheOnly: true},
               "no-cache": "n",
               "enable-iframes": {enableIframes: true},
               "enable-path": {enablePath: true},
               "input": "i",
               "output": "o"},

    usage: "\t-c|--record: Record instrumentation.\n" +
           "\t-p|--replay: Replay instrumentation.\n" +
           "\t-O|--replay-options: Replay options, if not default.\n" +
           "\t--load-only: window.close() immediately after window.onload.\n" +
           "\t-n|--no-cache: Never use cached pages.\n" +
           "\t--cache-only: Only use cached pages.\n" +
           "\t--enable-iframes: Enable iframes (do not rewrite and remove them) (experimental).\n" +
           "\t--enable-path: Enable full callpath tracing/verification.\n" +
           "\t-i|--input <file>: Get input from <file>.\n" +
           "\t-o|--output <file>: Send output to <file>.\n",

    applyOpt: function(opt) {
        if (typeof(opt) === "object") {
            for (var prop in opt) {
                this[prop] = opt[prop];
            }
            return true;
        } else if (typeof(opt) === "string") {
            return applyOpt(this.shortArgs[opt]);
        } else {
            return false;
        }
    },

    next: null,

    acceptArg: function(arg) {
        if (this.next !== null) {
            this[this.next] = arg;
            this.next = null;
            return true;
        } else {
            if (arg[0] === "-") {
                if (arg[1] === "-") {
                    arg = arg.slice(2);
                    if (arg in this.longArgs) {
                        return this.applyOpt(this.longArgs[arg]);
                    }
                } else {
                    var res = true;
                    for (var i = 1; i < arg.length; i++) {
                        if (arg[i] in this.shortArgs) {
                            res = res && this.applyOpt(this.shortArgs[arg[i]]);
                        } else {
                            res = false;
                        }
                    }
                    return res;
                }
            } else {
                return arg;
            }
        }
    },

    load: function() {
        if (this.next !== null)
            JSBNG.Util.die("Invalid arguments.");
        if (this.input !== null)
            this.input = JSBNG.Util.readFile(this.input);
        if (this.record)
            require("./instrumentation/record");
        if (this.replay)
            require("./instrumentation/replay");
        if (this.loadOnly)
            require("./instrumentation/loadonly");
    }
};
