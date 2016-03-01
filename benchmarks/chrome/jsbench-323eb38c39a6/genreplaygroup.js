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

var child_process = require("child_process");
var fs = require("fs");

var log = process.argv[2];
var dir = process.argv[3];

fs.mkdir(dir, 0777);

for (var i = 4; i < process.argv.length; i++) {
    var mode = process.argv[i];
    console.log(mode);
    child_process.spawn("node", ["genreplay.js", "-i", log, "-o", dir + "/" + mode + ".js", "-O", mode])
        .addListener("exit", function() { console.log("."); });
    fs.writeFileSync(dir + "/" + mode + ".html",
        "<!doctype html><html><head><title></title></head><body>" +
        "<script type=\"text/javascript\" src=\"" + mode + ".js\"></script>" +
        "</body></html>",
        "utf8");
}

child_process.spawn("cp", ["-f", log, dir + "/log"]).on("exit", function() {
    child_process.spawn("xz", [dir + "/log"]);
});
