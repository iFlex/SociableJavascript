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

JSBNG.JSI = new (function() {
    eval(Narcissus.definitions.consts);

    var instrument = this.instrument = function(n, tdf, buf) {
        function sub(n) { return instrument(n, tdf, buf); }

        // first do top-down
        if (tdf !== null) n = tdf(n);

        // then recurse
        switch (n.type) {
            case FUNCTION:
            case GETTER:
            case SETTER:
                n.body = sub(n.body);
                break;

            case SCRIPT:
            case BLOCK:
                for (var i = 0, j = n.children.length; i < j; i++) {
                    n.children[i] = sub(n.children[i]);
                }
                break;

            case LET_BLOCK:
                n.variables = sub(n.variables);
                if (n.expression)
                    n.expression = sub(n.expression);
                else
                    n.block = sub(n.block);
                break;

            case IF:
                n.condition = sub(n.condition);
                n.thenPart = sub(n.thenPart);
                if (n.elsePart) n.elsePart = sub(n.elsePart);
                break;

            case SWITCH:
                n.discriminant = sub(n.discriminant);
                for (var i = 0, j = n.cases.length; i < j; i++) {
                    n.cases[i] = sub(n.cases[i]);
                }
                break;

            case CASE:
                n.caseLabel = sub(n.caseLabel);
            case DEFAULT:
                n.statements = sub(n.statements);
                break;

            case FOR:
                if (n.setup) n.setup = sub(n.setup);
                if (n.condition) n.condition = sub(n.condition);
                if (n.update) n.update = sub(n.update);
                if (n.body) n.body = sub(n.body);
                break;

            case WHILE:
                n.condition = sub(n.condition);
                if (n.body) n.body = sub(n.body);
                break;

            case FOR_IN:
                if (n.varDecl)
                    n.varDecl = sub(n.varDecl);
                else
                    n.iterator = sub(n.iterator);
                n.object = sub(n.object);
                if (n.body) n.body = sub(n.body);
                break;

            case DO:
                n.body = sub(n.body);
                n.condition = sub(n.condition);
                break;

            case TRY:
                n.tryBlock = sub(n.tryBlock);
                for (var i = 0, j = n.catchClauses.length; i < j; i++) {
                    var t = n.catchClauses[i];
                    if (t.guard) t.guard = sub(t.guard);
                    t.block = sub(t.block);
                }
                if (n.finallyBlock) n.finallyBlock = sub(n.finallyBlock);
                break;

            case THROW:
                n.exception = sub(n.exception);
                break;

            case RETURN:
                if (n.value) n.value = sub(n.value);
                break;

            case YIELD:
                if (n.value.type) n.value = sub(n.value);
                break;

            case GENERATOR:
                n.expression = sub(n.expression);
                n.tail = sub(n.tail);
                break;

            case WITH:
                n.object = sub(n.object);
                n.body = sub(n.body);
                break;

            case LET:
            case VAR:
            case CONST:
                for (var i = 0, j = n.children.length; i < j; i++) {
                    var u = n.children[i];
                    if (u.initializer) u.initializer = sub(u.initializer);
                }
                break;

            case SEMICOLON:
                if (n.expression) n.expression = sub(n.expression);
                break;

            case LABEL:
                n.statement = sub(n.statement);
                break;

            // easy things:
            case COMMA:
            case LIST:
            case ASSIGN:
            case HOOK:
            case OR:
            case AND:
            case BITWISE_OR:
            case BITWISE_XOR:
            case BITWISE_AND:
            case EQ:
            case NE:
            case STRICT_EQ:
            case STRICT_NE:
            case LT:
            case LE:
            case GE:
            case GT:
            case IN:
            case INSTANCEOF:
            case LSH:
            case RSH:
            case URSH:
            case PLUS:
            case MINUS:
            case MUL:
            case DIV:
            case MOD:
            case DELETE:
            case VOID:
            case TYPEOF:
            case NOT:
            case BITWISE_NOT:
            case UNARY_PLUS:
            case UNARY_MINUS:
            case INCREMENT:
            case DECREMENT:
            case DOT:
            case INDEX:
            case CALL:
            case NEW:
            case NEW_WITH_ARGS:
            case ARRAY_INIT:
            case ARRAY_COMP:
            case COMP_TAIL:
            case OBJECT_INIT:
            case PROPERTY_INIT:
            case GROUP:
                for (var i = 0, j = n.children.length; i < j; i++) {
                    if (n.children[i] !== null)
                        n.children[i] = sub(n.children[i]);
                }
                break;

            // no-children things:
            case BREAK:
            case CONTINUE:
            case DEBUGGER:
            case NULL:
            case THIS:
            case TRUE:
            case FALSE:
            case IDENTIFIER:
            case NUMBER:
            case REGEXP:
            case STRING:
                break;

            default:
                JSBNG.Util.debug("Unrecognized node type " + n.type + "!");
                throw new Error();
        }

        // then do bottom-up
        if (buf !== null) n = buf(n, b);

        return n;
    };
})();
