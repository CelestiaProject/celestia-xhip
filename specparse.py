#!/usr/bin/python
#
# specparse.py: Parse spectral type strings into machine-usable form
# Copyright (C) 2016  Andrew Tribick
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.

from __future__ import print_function
from __future__ import division
from builtins import range

import string
import ply.lex as lex
import ply.yacc as yacc

from specinfo import SpecInfo

class SpecLexer(object):

    tokens = (
        'TCLASS',
        'LPREFIX',
        'SPREFIX',
        'NUMBER',
        'NUMPLUS',
        'NUMMINUS',
        'ROMAN',
        'PECULIARITY',
        'ELEMENT',
        'WORD',
        'MS',
        'ELLIPSIS'
    )

    states = (
        ('peculiar', 'exclusive'),
        ('codes', 'exclusive'),
    )
    
    words = (
        'Boo',
        'Cyg',
        'Del',
        'He-weak',
        'Nova',
        'Shell',
        'delta',
        'lambda',
        'lines',
        'met',
        'metal',
        'metal-strong',
        'metal-weak',
        'metallic',
        'metals',
        'pec',
        'P',
        'PCyg',
        'Pup',
        'rho',
        'shell',
        'strong',
        'var',
        'vwk',
        'weak'
    )

    roman_canonicalize = string.maketrans('ivxABZ/', 'IVXabz-')

    literals = ',+/-'
    t_INITIAL_ignore = ' \t:'
    t_codes_ELEMENT = r'([A-Z][A-Za-z]?[0-9]?)[+\-]?([0-9]+(\.[0-9]*)?|[IVX]+([\-/][IVX]+)?)?'
    t_codes_PECULIARITY = r'([bdjq]|em?|f\*?|ha?|nn?|p(ec)?|sh?|v(ar)?|wk?|m)[+\-]?([0-9]+(\.[0-9]*)?)?'
    t_peculiar_ignore = ' \t:'
    t_codes_ignore = ':'

    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)
        self._has_tclass = False
        self._has_subclass = False
        self._has_lclass = False
        self._is_mspectrum = False
        self._is_plusminus = False

    def t_TCLASS(self, t):
        r'[AFGKLTYR]|OB?[CN]?|B[CN]?|MS?|C(-([RNJ]|Hd?))?|SC?|D[ABCOQXZ]*[HP]*|NS?|PG|W[DRNCO]?|wd'
        nextchar = t.lexer.lexdata[t.lexer.lexpos:t.lexer.lexpos+1]
        if not nextchar:
            nextchar = ' '

        if t.value == 'S':
            if (self._is_mspectrum and
                    (self._has_tclass or self._is_plusminus) and
                    nextchar not in 'Bir'):
                t.type = 'MS'
                t.value = 'MS'
                return t
            elif nextchar in 'Bir':
                t.lexer.begin('peculiar')
                t.lexer.skip(-1)

        if self._has_tclass or (t.value == 'C' and nextchar in 'HIN'):
            t.lexer.begin('peculiar')
            t.lexer.skip(-len(t.value))
        else:
            self._has_tclass = True
            self._is_mspectrum = t.value == 'M'
            return t

    def t_NUMBER(self, t):
        r'\d+(\.\d*)?'
        lastsymbol = t.lexer.lexdata[:t.lexer.lexpos-len(t.value)].strip()[-1:]
        if (self._has_lclass or self._has_subclass or lastsymbol == '+'):
            t.type = 'PECULIARITY'
            t.lexer.begin('peculiar')
        elif (t.lexer.lexdata[t.lexer.lexpos:t.lexer.lexpos+3] == '-Ia' or
                t.lexer.lexdata[t.lexer.lexpos:t.lexer.lexpos+3] == '-IA'):
            t.type = 'ROMAN'
            t.value = '0-Ia'
            t.lexer.skip(3)
        else:
            self._has_subclass = True
            t.value = float(t.value)

        self._has_tclass = True
        return t

    def t_ROMAN(self, t):
        r'[IVX]+[abzABZ]*([\-/][IVX0]*[abzABZ]*)?'
        if self._has_lclass:
            t.type = 'PECULIARITY'
            t.lexer.begin('peculiar')
        else:
            t.value = t.value.translate(SpecLexer.roman_canonicalize)
            self._has_tclass = True
            self._has_subclass = True
            self._has_lclass = True

        return t
        
    def t_LPREFIX(self, t):
        r'g|d|sd|esd'
        if self._has_tclass:
            t.lexer.begin('peculiar')
            t.lexer.skip(-len(t.value))
        else:
            return t

    def t_spfxorpec(self, t):
        r'[ghkm]|He'
        nextchar = t.lexer.lexdata[t.lexer.lexpos:t.lexer.lexpos+1]
        if not nextchar:
            nextchar = ' '

        if nextchar in 'OBAFGKM':
            t.type = 'SPREFIX'
            self._has_tclass = False
            self._has_subclass = False
            self._has_lclass = False
            return t
        else:
            self._has_tclass = True
            t.lexer.begin('peculiar')
            t.lexer.skip(-len(t.value))

    def t_INITIAL_peculiar_codes_plus(self, t):
        r'\+'
        if (t.lexer.lexpos > 1 and
                t.lexer.lexdata[t.lexer.lexpos-2:t.lexer.lexpos-1] in string.digits):
            t.type = 'NUMPLUS'
        else:
            t.type = '+'
        t.lexer.begin('INITIAL')
        self._has_tclass = False
        self._has_subclass = False
        self._has_lclass = False
        self._is_plusminus = True
        return t

    def t_ANY_minus(self, t):
        r'-'
        if (t.lexer.lexpos > 1 and
                t.lexer.lexdata[t.lexer.lexpos-2:t.lexer.lexpos-1] in string.digits):
            t.type = 'NUMMINUS'
        else:
            t.type = '-'

        self._has_tclass = False
        self._has_subclass = False
        self._has_lclass = False
        self._is_plusminus = True
        return t

    def t_slash(self, t):
        r'/'
        t.type = '/'
        self._has_tclass = False
        self._has_subclass = False
        self._has_lclass = False
        return t

    def t_comma(self, t):
        r','
        t.type = ','
        self._has_subclass = False
        return t

    def t_peculiarswitch(self, t):
        r'[^,.\-/+()]'
        t.lexer.begin('peculiar')
        t.lexer.skip(-1)

    def t_INITIAL_peculiar_codes_ELLIPSIS(self, t):
        r'\.{3}.*$'
        if self._is_plusminus:
            return t

    def t_peculiar_WORD(self, t):
        r'[A-Za-z0-9][a-z0-9\-]*'
        if t.value in SpecLexer.words:
            return t
        else:
            t.lexer.begin('codes')
            t.lexer.skip(-len(t.value))
    
    def t_codes_space(self, t):
        r'\s+'
        t.lexer.begin('peculiar')
    
    def t_ANY_paren(self, t):
        r'\('
        level = 1
        curpos = 1
        for c in t.lexer.lexdata[t.lexer.lexpos:]:
            if c == '(':
                level += 1
            elif c == ')':
                level -= 1
                if level == 0:
                    break
            curpos += 1

        t.type = 'PECULIARITY'
        t.value = t.lexer.lexdata[t.lexer.lexpos-1:t.lexer.lexpos+curpos]
        t.lexer.skip(curpos)
        t.lexer.begin('peculiar')
        return t

    def t_ANY_bracket(self, t):
        r'\['
        level = 1
        curpos = 1
        for c in t.lexer.lexdata[t.lexer.lexpos:]:
            if c == '[':
                level += 1
            elif c == ']':
                level -= 1
                if level == 0:
                    break
            curpos += 1

        t.type = 'PECULIARITY'
        t.value = t.lexer.lexdata[t.lexer.lexpos-1:t.lexer.lexpos+curpos]
        t.lexer.skip(curpos)
        t.lexer.begin('peculiar')
        return t

    def t_INITIAL_peculiar_error(self, t):
        t.lexer.skip(1)
    
    def t_codes_error(self, t):
        t.type = 'PECULIARITY'
        t.value = t.value[0:1]
        t.lexer.skip(1)
        return t

    def t_ANY_eof(self, t):
        self._has_tclass = False
        self._has_subclass = False
        self._has_lclass = False
        self._is_mspectrum = False
        self._is_plusminus = False
        self._level = 0
        t.lexer.begin("INITIAL")
    
    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)
# end class SpecLexer


class SpecParser(object):

    def __init__(self, lexer=None, **kwargs):
        if lexer is None:
            self.lexer = SpecLexer().lexer
        else:
            if isinstance(lexer, SpecLexer):
                self.lexer = lexer.lexer
            else:
                self.lexer = lexer
        self.parser = yacc.yacc(module=self, **kwargs)
    
    tokens = SpecLexer.tokens
    literals = SpecLexer.literals

    phrases = {
        'delta': {'Del'},
        'lambda': {'Boo'},
        'metal': {'strong', 'weak'},
        'metallic': {'lines'},
        'P': {'Cyg'},
        'rho': {'Pup'},
    }

    def p_spectrum_core(self, p):
        '''spectrum : core
                    | core '+'
                    | core '+' peculiarities'''
        p[0] = p[1]
    
    def p_spectrum_peculiar(self, p):
        '''spectrum : core peculiarities'''
        p[0] = p[1]
        p[0].pecs += p[2]
    
    def p_spectrum_comp(self, p):
        '''spectrum : core '+' core
                    | core '+' core peculiarities'''
        p[0] = p[1]
        p[0].comp = p[3].tclass
    
    def p_spectrum_compellipsis(self, p):
        '''spectrum : core '+' ELLIPSIS'''
        p[0] = p[1]
        p[0].comp = '?'
    
    def p_spectrum_peculiarcomp(self, p):
        '''spectrum : core peculiarities '+' core
                    | core peculiarities '+' core peculiarities'''
        p[0] = p[1]
        p[0].pecs += p[2]
        p[0].comp = p[4].tclass
    
    def p_spectrum_peculiarcompellipsis(self, p):
        '''spectrum : core peculiarities '+' ELLIPSIS'''
        p[0] = p[1]
        p[0].pecs += p[2]
        p[0].comp = '?'

    def p_core_lprefixtemp(self, p):
        '''core : lprefixtemp'''
        p[0] = p[1]
    
    def p_core_luminosity(self, p):
        '''core : lprefixtemp ROMAN'''
        p[0] = p[1]
        if p[1].comp is None:
            p[0].lclass = p[2]
    
    def p_core_special(self, p):
        '''core : special'''
        keys = set(p[1].keys())
        keys.remove('lclass')

        comp = None
        if 'comp' in keys:
            comp = p[1]['comp']
            keys.remove('comp')

        has_He = False
        if 'He' in keys:
            has_He = True
            keys.remove('He')

        if keys == {'h','k','m'}:
            p[0] = p[1]['h']
            p[0].pecs.append(('m', ''))
        elif keys == {'h','m'}:
            p[0] = p[1]['h']
            if p[1]['m'].earlier_than(p[1]['h']):
                p[0].pecs.append(('m', '-'))
            else:
                p[0].pecs.append(('m', ''))
        elif keys in ({'h','g','m'},{'h','g','k','m'}):
            p[0] = p[1]['h']
            if (p[1]['m'].earlier_than(p[1]['h']) or
                    p[1]['m'].earlier_than(p[1]['g'])):
                p[0].pecs.append(('m', '-'))
            else:
                p[0].pecs.append(('m', ''))
        elif keys == {'k','h'}:
            p[0] = p[1]['h']
            if p[1]['k'].later_than(p[1]['h']):
                p[0].pecs.append(('m', '+'))
            else:
                p[0].pecs.append(('m', '-'))
        elif keys == {'k','m'}:
            p[0] = p[1]['k']
            p[0].pecs.append(('m', ''))
        elif len(keys) == 1 and p[1].keys()[0] in {'h','k'}:
            p[0] = p[1].values()[0]
        else:
            p[0] = SpecInfo()
            return
        
        if has_He:
            p[0].pecs.append(('He', ''))
        
        if p[0].lclass is None:
            p[0].lclass = p[1]['lclass']
            
        p[0].comp = comp

    def p_core_lprefixspecial(self, p):
        '''core : lprefixtemp special'''
        p[0] = p[1]
        if 'm' in p[2]:
            p[0].pecs.append(('m', ''))
    
    def p_core_lprefixromanspecial(self, p):
        '''core : lprefixtemp ROMAN special'''
        p[0] = p[1]
        p[0].lclass = p[2]
        if 'm' in p[3]:
            p[0].pecs.append(('m', ''))

    def p_lprefixtemp_tempclass(self, p):
        '''lprefixtemp : tempclass'''
        p[0] = p[1]
    
    def p_lprefixtemp_lprefixonly(self, p):
        '''lprefixtemp : LPREFIX'''
        if p[1] == 'sd':
            p[0] = SpecInfo(tclass='sd')
        else:
            p[0] = SpecInfo(lclass=p[1])

    def p_lprefixtemp_lprefixsubclass(self, p):
        '''lprefixtemp : LPREFIX tempclass'''
        p[0] = p[2]
        if (p[1] == 'sd' and
                p[2].tclass in ('O','ON','OC','OB','B','BN','BC','A')):
            p[0].tclass = 'sd'+p[2].tclass
        elif p[1] == 'sd' and p[2].tclass in ('A','F','G','K'):
            p[0].pecs.append(('Fe','-'))
            p[0].lclass = p[1]
        elif (p[1] in ('sd', 'esd', 'usd') and
                p[2].tclass in ('M','L','T','Y')):
            p[0].pecs.append((p[1], ''))
            if p[1] != 'esd':
                p[0].lclass = p[1]
        elif (p[1] == 'd'
              and p[2].tclass in ('C','C-R','C-N','C-J','C-H','C-Hd','R','N')):
            p[0].pecs.append(('d',''))
            p[0].lclass = p[1]
        else:
            p[0].lclass = p[1]

    def p_special_single(self, p):
        '''special : sprefixtemp'''
        p[0] = { p[1][0]: p[1][1], 'lclass': p[1][1].lclass }
        if p[1][1].comp is not None:
            p[0]['comp'] = p[1][1].comp
    
    def p_special_multi(self, p):
        '''special : special sprefixtemp'''
        p[0] = p[1]
        if 'comp' not in p[0]:
            p[0][p[2][0]] = p[2][1]
            p[0]['lclass'] = p[2][1].lclass
            if p[2][1].comp is not None:
                p[0]['comp'] = p[2][1].comp

    def p_sprefixtemp_tempclass(self, p):
        '''sprefixtemp : SPREFIX tempclass'''
        p[0] = (p[1], p[2])
    
    def p_sprefixtemp_roman(self, p):
        '''sprefixtemp : SPREFIX tempclass ROMAN'''
        info = p[2]
        info.lclass = p[3]
        p[0] = (p[1], info)
    
    def p_tempclass_tclass(self, p):
        '''tempclass : TCLASS
                     | TCLASS '-'
                     | TCLASS '-' TCLASS
                     | TCLASS '/' TCLASS'''
        p[0] = SpecInfo(tclass=p[1])
    
    def p_tempclass_subclass(self, p):
        '''tempclass : TCLASS numbers'''
        p[0] = SpecInfo(tclass=p[1], subclass=p[2]['n'])
        if '/' in p[2]:
            p[0].pecs.append(('/',str(p[2]['/'])))

    def p_tempclass_rangetemp(self, p):
        '''tempclass : TCLASS numbers TCLASS
                     | TCLASS numbers TCLASS numbers
                     | TCLASS numbers TCLASS numbers TCLASS
                     | TCLASS numbers TCLASS numbers TCLASS numbers
                     | TCLASS numbers TCLASS numbers TCLASS numbers TCLASS
                     | TCLASS numbers TCLASS numbers TCLASS numbers TCLASS numbers'''
        p[0] = SpecInfo(tclass=p[1], subclass=p[2]['n'])
        has_slash = False
        for i in (x*2+2 for x in range((len(p)-1) // 2)):
            if '/' in p[i] and not has_slash:
                p[0].pecs.append(('/', str(p[i]['/'])))
                has_slash = True
            if p[i]['end'] == '+':
                p[0].comp = p[i+1]
                break

    def p_tempclass_ellipsis(self, p):
        '''tempclass : TCLASS numbers ELLIPSIS'''
        p[0] = SpecInfo(tclass=p[1], subclass=p[2]['n'])
        if '/' in p[2]:
            p[0].pecs.append(('/', str(p[2]['/'])))
        if p[2]['end'] == '+':
            p[0].comp = '?'

    def p_tempclass_ms(self, p):
        '''tempclass : TCLASS numbers MS
                     | TCLASS numbers TCLASS numbers MS
                     | TCLASS numbers MS '-' TCLASS numbers MS
                     | TCLASS numbers MS '/' TCLASS numbers MS'''
        p[0] = SpecInfo(tclass='MS', subclass=p[2]['n'])

    def p_numbers_single(self, p):
        '''numbers : NUMBER'''
        p[0] = dict(n=p[1],end='')
        
    def p_numbers_open(self, p):
        '''numbers : NUMBER NUMMINUS
                   | NUMBER NUMPLUS
                   | NUMBER '/' '''
        p[0] = dict(n=p[1],end=p[2])
    
    def p_numbers_multi(self, p):
        '''numbers : NUMBER '-' numbers
                   | NUMBER NUMMINUS numbers
                   | NUMBER '/' numbers
                   | NUMBER ',' numbers'''
        p[0] = dict(n=p[1],end=p[3]['end'])
        if p[2] == '/':
            p[0]['/'] = p[3]['n']
        elif '/' in p[3]:
            p[0]['/'] = p[3]['/']
        
    def p_numbers_openmulti(self, p):
        '''numbers : NUMBER NUMMINUS '/' numbers
                   | NUMBER NUMPLUS '/' numbers
                   | NUMBER NUMMINUS ',' numbers
                   | NUMBER NUMPLUS ',' numbers'''
        p[0] = dict(n=p[1],end=p[4]['end'])
        if p[3] == '/':
            p[0]['/'] = p[4]['n']
        elif '/' in p[4]:
            p[0]['/'] = p[4]['/']

    def p_peculiarities_single(self, p):
        '''peculiarities : peculiarity'''
        p[0] = [p[1]]
    
    def p_peculiarities_multi(self, p):
        '''peculiarities : peculiarities peculiarity'''
        p[0] = p[1]
        if p[1][-1][1] == '' and p[2][1] == '':
            nextwords = SpecParser.phrases.get(p[1][-1][0], set())
            if p[2][0] in nextwords:
                p[0][-1] = (p[1][-1][0]+' '+p[2][0], '')
                return

        p[0].append(p[2])
    
    def p_peculiarities_split(self, p):
        '''peculiarities : peculiarities '/' peculiarity
                         | peculiarities '-' peculiarity
                         | peculiarities ',' peculiarity
                         | peculiarities '+' peculiarity'''
        p[0] = p[1]
        p[0].append(p[3])
    
    def p_peculiarity(self, p):
        '''peculiarity : PECULIARITY
                       | ELEMENT'''
        pos = 0
        for c in p[1]:
            if c in string.digits:
                p[0] = (p[1][:pos], p[1][pos:])
                return
            elif c in '-+':
                nextchar = p[1][pos+1:pos+2]
                if nextchar == '' or nextchar in string.digits:
                    p[0] = (p[1][:pos], p[1][pos:])
                    return
            pos += 1
        p[0] = (p[1], '')
    
    def p_peculiarity_word(self, p):
        '''peculiarity : WORD'''
        p[0] = (p[1], '')
    
    def p_peculiarity_plusminus(self, p):
        '''peculiarity : PECULIARITY NUMMINUS
                       | PECULIARITY NUMPLUS
                       | ELEMENT NUMMINUS
                       | ELEMENT NUMPLUS'''
        combined = p[1]+p[2]
        pos = 0
        for c in combined:
            if c in string.digits:
                p[0] = (combined[:pos], combined[pos:])
                return
            elif c in '-+':
                nextchar = combined[pos+1:pos+2]
                if nextchar == '' or nextchar in string.digits:
                    p[0] = (combined[:pos], combined[pos:])
                    return
            pos += 1
        p[0] = (p[1], p[2])

    def p_error(self, p):
        if p:
            self.parser.errok()

    def parse(self, data, **kwargs):
        result = self.parser.parse(data, **kwargs)
        return result
#end class SpecParser
