/*
 * Copyright (C) 2011 Purdue University
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

var crypto = require("crypto");
var fs = require("fs");
var sys = require("util");
var child_process = require("child_process");

// Node utility functions
JSBNG.Util = {
    hash: function(str) {
        var sha1 = crypto.createHash("sha1");
        sha1.update(new Buffer(str));
        return sha1.digest("hex").toString("utf8");
    },

    readFile: function(nm) {
        return fs.readFileSync(nm, "utf8");
    },

    readFileBuffer: function(nm) {
        return fs.readFileSync(nm);
    },

    writeFile: function(nm, data) {
        fs.writeFileSync(nm, data, "utf8");
    },

    writeFileBuffer: function(nm, data) {
        if (data instanceof Array) {
            var fd = fs.openSync(nm, "w");
            for (var i = 0; i < data.length; i++) {
                fs.writeSync(fd, data[i], 0, data[i].length, null);
            }
            fs.closeSync(fd);
        } else {
            fs.writeFileSync(nm, data);
        }
    },

    debug: function(str) {
        sys.debug(str);
    },

    die: function(str) {
        sys.error(str);
        process.exit(1);
    },

    data: function(str) {
        sys.print(str);
    },

    version: function(cb) { // callback? Yukk
        var child = child_process.spawn("hg", ["id"]);
        var dataStr = "";
        child.stdout.on("data", function(data) {
            dataStr += data.toString("utf8").replace("\n", "");
        });
        child.stdout.on("end", function() {
            cb(dataStr);
        });
    }
}

