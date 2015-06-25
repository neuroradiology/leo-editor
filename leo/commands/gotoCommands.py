# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150624112334.1: * @file ../commands/gotoCommands.py
#@@first
'''Leo's goto commands.'''
import leo.core.leoGlobals as g
# import os
#@+others
#@+node:ekr.20150625050355.1: ** class GoToCommands
class GoToCommands:
    '''A class implementing goto-global-line.'''
    #@+others
    #@+node:ekr.20100216141722.5621: *3* goto.ctor
    def __init__(self, c):
        '''Ctor for GoToCommands class.'''
        self.c = c
    #@+node:ekr.20100216141722.5622: *3* goto.find_file_line
    def find_file_line(self, n, p=None):
        '''
        Place the cursor on the n'th line of an external file.
        Return p, offset, found for unit testing.'''
        trace = False and not g.unitTesting
        c = self.c
        if n < 0:
            return
        p = p or c.p
        root, fileName = self.find_root(p)
        if root:
            # Step 1: Get the lines of external files *with* sentinels,
            # even if the actual external file actually contains no sentinels.
            sentinels = root.isAtFileNode()
            s = self.get_external_file_with_sentinels(root)
            lines = g.splitLines(s)
            if trace:
                aList = ['%3s %s' % (i, s) for i, s in enumerate(lines)]
                g.trace('n: %s script: ...\n%s' % (n, ''.join(aList)))
            # Step 2: scan the lines for line n.
            if sentinels:
                # All sentinels count as real lines.
                gnx, h, offset = self.scan_sentinel_lines(lines, n, root)
            else:
                # Not all sentinels cound as real lines.
                gnx, h, offset = self.scan_nonsentinel_lines(lines, n, root)
            if gnx:
                p, found = self.find_gnx(root, gnx, h)
                self.show_results(found, p, n, offset, lines)
                return p, offset, found
            else:
                self.fail(lines, n, root)
                return None, -1, False
        else:
            return self.find_script_line(n, p)
    #@+node:ekr.20150622140140.1: *3* goto.find_script_line
    def find_script_line(self, n, root):
        '''
        Go to line n (zero based) of the script with the given root.
        Return p, offset, found for unit testing.
        '''
        trace = False and not g.unitTesting
        c = self.c
        if n < 0:
            return None, -1, False
        script = g.getScript(c, root, useSelectedText=False)
        lines = g.splitLines(script)
        if trace:
            aList = ['%3s %s' % (i, s) for i, s in enumerate(lines)]
            g.trace('n: %s script: ...\n%s' % (n, ''.join(aList)))
        # Script lines now *do* have gnx's.
        gnx, h, offset = self.scan_sentinel_lines(lines, n, root)
        if gnx:
            p, found = self.find_gnx(root, gnx, h)
            self.show_results(found, p or root, n, offset, lines)
            return p, offset, found
        else:
            self.fail(lines, n, root)
            return None, -1, False
    #@+node:ekr.20150624085605.1: *3* goto.scan_nonsentinel_lines
    def scan_nonsentinel_lines(self, lines, n, root):
        '''
        Scan a list of lines containing sentinels, looking for the node and
        offset within the node of the n'th (zero-based) line.  Only lines
        that appear in the outline increment count.
        
        Return gnx, h, offset:
        gnx:    the gnx of the #@+node
        h:      the headline of the #@+node
        offset: the offset of line n within the node.
        '''
        trace = False and not g.unitTesting
        delim1, delim2 = self.get_delims(root)
        delim = '#@' ###
        count, gnx, h, offset = 0, root.gnx, root.h, 0
        stack = [(gnx, h, offset),]
        for s in lines:
            if trace: g.trace(s.rstrip())
            s2 = s.strip()
            if s2.startswith(delim + '+node'):
                offset = 0
                    # The node delim does not appear in the outline.
                gnx, h = self.get_script_node_info(s)
                if trace: g.trace('node', gnx, h)
            elif s2.startswith(delim + '+others') or s2.startswith(delim + '+<<'):
                stack.append((gnx, h, offset),)
                offset += 1
            elif s2.startswith(delim + '-others') or s2.startswith(delim + '-<<'):
                gnx, h, offset = stack.pop()
                # These do *not* appear in the outline.
            elif s2.startswith(delim + 'verbatim'):
                pass # Only the following line appears in the outline.
            elif s2.startswith(delim):
                pass # Ignore all other sentinel lines.
            else:
                # All other lines, including Leo directives, do appear in the outline.
                count += 1
                offset += 1
            if trace: g.trace(count, offset, h, '\n')
            if count == n:
                break
        else:
            gnx, h, offset = None, None, -1
        if trace: g.trace('gnx', gnx, 'h', h, 'offset', offset)
        return gnx, h, offset
    #@+node:ekr.20150623175314.1: *3* goto.scan_sentinel_lines
    def scan_sentinel_lines(self, lines, n, root):
        '''
        Scan a list of lines containing sentinels, looking for the node and
        offset within the node of the n'th (zero-based) line.
        
        Return gnx, h, offset:
        gnx:    the gnx of the #@+node
        h:      the headline of the #@+node
        offset: the offset of line n within the node.
        '''
        trace = False and not g.unitTesting
        delim1, delim2 = self.get_delims(root)
        delim = '#@' ### To be removed.
        gnx, h, offset = root.gnx, root.h, 0
        stack = [(gnx, h, offset),]
        if trace: g.trace('=====', n)
        for i, s in enumerate(lines):
            if trace: g.trace(s.rstrip())
            s2 = s.strip()
            if s2.startswith(delim + '+node'):
                offset = 0
                gnx, h = self.get_script_node_info(s)
                if trace: g.trace('node', gnx, h)
            elif s2.startswith(delim + '+others') or s2.startswith(delim + '+<<'):
                stack.append((gnx, h, offset),)
                offset += 1
            elif s2.startswith(delim + '-others') or s2.startswith(delim + '-<<'):
                gnx, h, offset = stack.pop()
                offset += 1
            else:
                offset += 1
            if trace: g.trace(i, offset, h, '\n')
            if i == n:
                break
        else:
            gnx, h, offset = None, None, -1
        if trace: g.trace('----- gnx', gnx, 'h', h, 'offset', offset)
        return gnx, h, offset
    #@+node:ekr.20150624142449.1: *3* goto.Utils
    #@+node:ekr.20150625133523.1: *4* goto.fail
    def fail(self, lines, n, root):
        '''Select the last line of the last node of root's tree.'''
        c = self.c
        p = root.lastNode()
        w = c.frame.body.wrapper
        s = w.getAllText()
        c.redraw(p)
        if not g.unitTesting:
            if len(lines) < n:
                g.warning('only', len(lines), 'lines')
            else:
                g.warning('line', n, 'not found')
        # Put the cursor on the last line of body text.
        w.setInsertPoint(len(s))
        c.bodyWantsFocus()
        w.seeInsertPoint()
    #@+node:ekr.20100216141722.5626: *4* goto.find_gnx
    def find_gnx(self, root, gnx, vnodeName):
        '''
        Scan root's tree for a node with the given gnx and vnodeName.
        return (p,found)
        '''
        trace = False and not g.unitTesting
        if gnx:
            assert g.isString(gnx)
            gnx = g.toUnicode(gnx)
            for p in root.self_and_subtree():
                if p.matchHeadline(vnodeName):
                    if p.v.fileIndex == gnx:
                        return p.copy(), True
            if trace: g.trace('not found! %s, %s' % (gnx, repr(vnodeName)))
            return None, False
        else:
            return root, False
    #@+node:ekr.20100216141722.5627: *4* goto.find_root
    def find_root(self, p):
        '''
        Find the closest ancestor @<file> node, except @all nodes and @edit nodes.
        return root, fileName.
        '''
        c = self.c; p1 = p.copy()
        # First look for ancestor @file node.
        for p in p.self_and_parents():
            if not p.isAtEditNode() and not p.isAtAllNode():
                fileName = p.anyAtFileNodeName()
                if fileName:
                    return p.copy(), fileName
        # Search the entire tree for joined nodes.
        # Bug fix: Leo 4.5.1: *must* search *all* positions.
        for p in c.all_positions():
            if p.v == p1.v and p != p1:
                # Found a joined position.
                for p2 in p.self_and_parents():
                    fileName = not p2.isAtAllNode() and p2.anyAtFileNodeName()
                    if fileName:
                        return p2.copy(), fileName
        return None, None
    #@+node:ekr.20150625123747.1: *4* goto.get_delims
    def get_delims(self, root):
        '''Return the deliminters in effect at root.'''
        c = self.c
        d = c.scanAllDirectives(root)
        delims1, delims2, delims3 = d.get('delims')
        if delims1:
            return delims1, None
        else:
            return delims2, delims3
    #@+node:ekr.20150624143903.1: *4* goto.get_external_file_with_sentinels
    def get_external_file_with_sentinels(self, root):
        '''
        root is an @<file> node.

        Return the result of writing the file *with* sentinels, even if the
        external file would normally *not* have sentinels.
        '''
        at, c = self.c.atFileCommands, self.c
        if root.isAtAutoNode():
            # We must treat @auto nodes specially because
            # Leo does not write sentinels in the root @auto node.
            ok = at.writeOneAtAutoNode(
                root,
                toString=True,
                force=True,
                trialWrite=False,
                forceSentinels=True)
            return ok and at.stringOutput or ''
        ###
        # elif root.isAsisNode():
            # return ''
        # elif root.isAtAutoRstNode():
            # return ''
        else:
            return g.getScript(c, root, useSelectedText=False)
    #@+node:ekr.20150623175738.1: *4* goto.get_script_node_info
    def get_script_node_info(self, s):
        '''Return the gnx and headline of a #@+node.'''
        i = s.find(':', 0)
        j = s.find(':', i + 1)
        if i == -1 or j == -1:
            g.error("bad @+node sentinel", s)
            return None, None
        else:
            gnx = s[i + 1: j]
            h = s[j + 1:]
            h = self.remove_level_stars(h).strip()
            # g.trace(gnx, h, s.rstrip())
            return gnx, h
    #@+node:ekr.20150625124027.1: *4* goto.is_sentinel
    def is_sentinel(self, delim1, delim2, s):
        '''Return True if s is a sentinel line with the given delims.'''
        assert delim1
        i = s.find(delim1 + '@')
        j = s.find(delim2 + '@') if delim2 else len(s) - 1
        return 0 == i < j
    #@+node:ekr.20100728074713.5843: *4* goto.remove_level_stars
    def remove_level_stars(self, s):
        i = g.skip_ws(s, 0)
        # Remove leading stars.
        while i < len(s) and s[i] == '*':
            i += 1
        # Remove optional level number.
        while i < len(s) and s[i].isdigit():
            i += 1
        # Remove trailing stars.
        while i < len(s) and s[i] == '*':
            i += 1
        # Remove one blank.
        if i < len(s) and s[i] == ' ':
            i += 1
        return s[i:]
    #@+node:ekr.20100216141722.5638: *4* goto.show_results
    def show_results(self, found, p, n, n2, lines):
        '''Place the cursor on line n2 of p.b.'''
        trace = False and not g.unitTesting
        c = self.c
        w = c.frame.body.wrapper
        # Select p and make it visible.
        if found:
            if c.p.isOutsideAnyAtFileTree():
                p = c.findNodeOutsideAnyAtFileTree(p)
        else:
            p = c.p
        c.redraw(p)
        # Put the cursor on line n2 of the body text.
        s = w.getAllText()
        if found:
            ins = g.convertRowColToPythonIndex(s, n2 - 1, 0)
        else:
            ins = len(s)
            if not g.unitTesting:
                if len(lines) < n:
                    g.warning('only', len(lines), 'lines')
                else:
                    g.warning('line', n, 'not found')
        if trace:
            i, j = g.getLine(s, ins)
            g.trace('found: %5s %2s %2s %15s %s' % (
                found, n, n2, p.h, repr(s[i: j])))
        w.setInsertPoint(ins)
        c.bodyWantsFocus()
        w.seeInsertPoint()
    #@-others
#@-others
#@-leo