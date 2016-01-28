var fs = require("fs");
var sys = require("util");

var dat = fs.readFileSync(process.argv[2], "utf8");

try {
    dat = JSON.parse("[" + dat + "{\"type\":\"end\"}]");
} catch (ex) {
    sys.debug("Failed to parse JSON!");

    var odat = [];
    var st = 0;
    var depth = 0;
    var inq = null;
    for (var i = 0; i < dat.length; i++) {
        var ch = dat[i];
        if (inq) {
            if (ch === "\\") {
                i++;
            } else if (ch === inq) {
                inq = null;
            }

        } else if (ch === "\"" || ch == "'") {
            inq = ch;

        } else if (ch === "{") {
            if (depth++ == 0) {
                st = i;
            }

        } else if (ch === "}") {
            if (--depth == 0) {
                odat.push(dat.substring(st, i+1));
            }

        }
    }

    dat = [];
    for (var i = 0; i < odat.length; i++) {
        var el = odat[i];
        if (el === "") continue;
        try {
            var pel = JSON.parse(el);
            dat.push(pel);
        } catch (ex2) {
            sys.debug(el);
        }
    }
}

var out = "";
for (var i = 0; i < dat.length - 1; i++) {
    out += JSON.stringify(dat[i]) + ",\n";
}

fs.writeFileSync(process.argv[3], out, "utf8");
