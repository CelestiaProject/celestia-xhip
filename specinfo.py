#!/usr/bin/python
#
# specinfo.py: Representation of stellar spectra and conversions
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

class SpecInfo(object):
    def __init__(self, **kwargs):
        self.tclass = kwargs.get("tclass", None)
        self.subclass = kwargs.get("subclass", None)
        self.lclass = kwargs.get("lclass", None)
        self.pecs = kwargs.get("pecs", [])
        self.comp = kwargs.get("comp", None)
    
    def __repr__(self):
        r = []
        if self.tclass is not None:
            r.append("tclass=" + repr(self.tclass))
        if self.subclass is not None:
            r.append("subclass=" + repr(self.subclass))
        if self.lclass is not None:
            r.append("lclass=" + repr(self.lclass))
        if self.pecs:
            r.append("pecs=" + repr(self.pecs))
        if self.comp is not None:
            r.append("comp=" + repr(self.comp))
        
        return "SpecInfo(" + ", ".join(r) + ")"
    
    def earlier_than(self, other):
        t1 = self._spec_seq()
        t2 = other._spec_seq()
        if t1 is None or t2 is None or t2 > t1:
            return False
        elif t1 < t2:
            return True
        elif self.subclass is None or other.subclass is None:
            return False
        else:
            return self.subclass < other.subclass
    
    def later_than(self, other):
        t1 = self._spec_seq()
        t2 = other._spec_seq()
        if t1 is None or t2 is None or t2 < t1:
            return False
        elif t1 > t2:
            return True
        elif self.subclass is None or other.subclass is None:
            return False
        else:
            return self.subclass > other.subclass

    def _spec_seq(self):
        if self.tclass is None:
            return None

        TT = IvoaSpectrum.TT_CODES.get(self.tclass, None)
        if TT is None:
            return None
        elif 10 <= TT < 20:
            return TT
        else:
            return None
#end class SpecInfo

class IvoaSpectrum(object):
    TT_CODES = {
        "O": 10, "OC": 10, "ON": 10,
        "B": 11, "BC": 11, "BN": 11,
        "A": 12,
        "F": 13,
        "G": 14,
        "K": 15,
        "M": 16,
        "L": 17,
        "T": 18,
        "Y": 19,
        "C": 20,
        "C-R": 21, "R": 21,
        "C-N": 22, "N": 22,
        "C-J": 23,
        "C-H": 24,
        "C-Hd": 26,
        "S": 26, "SC": 26, "MS": 26,
        "sd": 30,
        "sdO": 31, "sdON": 31, "sdOC": 31, "sdOB": 31,
        "sdB": 32, "sdBN": 32, "sdBC": 32,
        "sdA": 33,
        "D": 40, "WD": 40, "wd": 40,
        "DA": 41,
        "DB": 42,
        "DC": 43,
        "DO": 44,
        "DZ": 46, "DF": 46, "DG": 46, "DK": 46, "DM": 46, "DX": 46,
        "DQ": 46,
        "PG": 47,
        "NS": 60,
        "WR": 61, "W": 61,
        "WN": 62,
        "WC": 63,
        "WO": 64,
        "OB": 66, "OBN": 66, "OBC": 66,
    }

    LL_CODES = {
        '0': 10,
        '0-Ia': 11, 'Ia0': 11, 'Ia-0': 11, 'Ia+': 11,
        'Ia': 12, 'Ia0-Ia': 12, 'Ia0/Ia': 12,
        'Ia-Iab': 13, 'Ia-ab': 13,
        'Iab': 14, 'I': 14,
        'Iab-Ib': 16, 'Iab-b': 16,
        'Ib': 16, 'I-II': 16,
        'Ib-II': 17, 'Ib-IIa': 17,
        'IIa': 18,
        'II': 19, 'IIab': 19, 'I-III': 19,
        'IIb': 20,
        'II-III': 21, 'IIb-III': 21, 'IIb-IIIa': 22,
        'IIIa': 22,
        'III': 23, 'IIIa-III': 23, 'IIIab': 23, 'III-IIIa': 23, 'g': 23,
        'IIIb': 24, 'III-IIIb': 24,
        'III-IV': 26, 'IIIb-IV': 26, 'IIIb-IVa': 26,
        'IVa': 26,
        'IV': 27, 'IVab': 27, 'III-V': 27,
        'IVb': 28,
        'IV-V': 29, 'IVa-V': 29,
        'Va': 30, 'V': 30, 'Va+': 30, 'Va-': 30, 'Va-V': 30, 'Vab': 30, 'd': 23,
        'Vb': 31, 'Vz': 31, 'Vb-Vz': 31,
        'VI': 32, 'sd': 32,
        'VII': 33, 'esd': 33,
        'VIII': 34,
        'IX': 36,
    }

    P1P2_CODES = {
        '+': 1,
        'p': 2, 'pec': 2,
        'e': 3, 'em': 3,
        '[e]': 4, 'q': 4,
        'v': 6, 'var': 6,
        's': 6,
        'n': 7, 'nn': 7,
    }

    P3_WR_CODES = {
        'b': 1,
        '(h)': 2,
        'h' : 3,
        'ha': 4,
    }

    P3_OB_GROUP_CODES = [
        {'elements': {'He'}, 'value': 1},
        {'elements': {'Hg'}, 'value': 2},
        {'elements': {'Mn'}, 'value': 2},
        {'elements': {'Hg','Mn'}, 'value': 2},
        {'elements': {'Si'}, 'value': 3},
        {'elements': {'Si','Sr'}, 'value': 3},
        {'elements': {'Si','Cr','Eu'}, 'value': 4},
        {'elements': {'Si','Cr'}, 'value': 4},
        {'elements': {'Sr','Cr','Eu'}, 'value': 5},
        {'elements': {'Si','Eu'}, 'value': 6},
        {'elements': {'Cr'}, 'value': 7},
        {'elements': {'Sr'}, 'value': 8},
    ]

    P4_OB_CODES = {
        'PCyg': 1, 'P Cyg': 1, 'w': 1,
        # 'f': 2,
        # 'f+': 3,
        'f*': 4,
        'metal strong': 5, # 'Fe+': 5, 'Fe': 5, 'm+': 5, 'm': 5,
        'metal-weak': 6, 'metal weak': 6, '(metal weak)': 6, '(metal-weak)': 6, # 'Fe-': 6, 'm-': 6, 'wk': 6,
        'sh': 7, 'shell': 7,
        # 'C': 8, 'N': 8
    }

    P3_AF_GROUP_CODES = [
        {'elements': {'Hg'}, 'value': 1},
        {'elements': {'Mn'}, 'value': 1},
        {'elements': {'Hg','Mn'}, 'value': 1},
        {'elements': {'Si'}, 'value': 2},
        {'elements': {'Si','Cr','Eu'}, 'value': 3},
        {'elements': {'Sr','Cr','Eu'}, 'value': 4},
        {'elements': {'Si','Eu'}, 'value': 5},
        {'elements': {'Cr'}, 'value': 6},
        {'elements': {'Sr'}, 'value': 7},
    ]    

    P4_AF_CODES = {
        'PCyg': 1, 'P Cyg': 1,
        'lam Boo': 2, 'lambda Boo': 2,
        'w': 3, 'wk': 3, 'metal-weak': 3, 'metal weak': 3, '(metal weak)': 3, '(metal-weak)': 3, # 'Fe-': 3, 'm-': 3,
        # 'Fe+': 4, 'm+': 4,
        # 'm': 5,
        'sh': 6, 'shell': 6,
        'Ba': 7,
        'rho Pup': 8
    }

    P3_GK_GROUP_CODES = [
        {'elements': {'CN+'}, 'value': 1},
        {'elements': {'CN-'}, 'value': 2},
        {'elements': {'CH+'}, 'value': 3},
        {'elements': {'CH-'}, 'value': 4},
        {'elements': {'CN+','CH+'}, 'value': 5},
        {'elements': {'CN+','CH-'}, 'value': 6},
        {'elements': {'CN-','CH+'}, 'value': 7},
        {'elements': {'CN-','CH-'}, 'value': 8},
    ]

    P3P4_D_CODES = {
        'A': 1,
        'B': 2,
        'O': 3,
        'Q': 4,
        'Z': 6,
        'H': 6,
        'P': 7,
        'd': 8
    }

    def __init__(self, **kwargs):
        self.TT_code = kwargs.get('TT_code', 0)
        self.tt_code = kwargs.get('tt_code', 0)
        self.LL_code = kwargs.get('LL_code', 0)
        self.PPPP_code = kwargs.get('PPPP_code', 0)
        self.code = ((self.TT_code<<25) + (self.tt_code<<20) +
                     (self.LL_code<<14) + self.PPPP_code)
    
    @staticmethod
    def create(specinfo):
        if not specinfo:
            return IvoaSpectrum()

        TT_code = IvoaSpectrum._get_TT(specinfo.tclass)
        
        tt_code = 0
        if specinfo.subclass is not None and 0 <= specinfo.subclass <= 10:
            if (specinfo.subclass>=9.6 and
                    TT_code in (10, 11, 31, 32, 62, 63, 64, 66)):
                tt_code = 20
            else:
                tt_code = int(specinfo.subclass) + 10
        
        LL_code = 0
        if specinfo.lclass:
            if specinfo.lclass in IvoaSpectrum.LL_CODES:
                LL_code = IvoaSpectrum.LL_CODES[specinfo.lclass]
            else:
                split = [s for s in specinfo.lclass.split('-') if s]
                if len(split) == 1 and split[0] in IvoaSpectrum.LL_CODES:
                    LL_code = IvoaSpectrum.LL_CODES[split[0]]
                elif len(split) >= 2:
                    lclass_reversed = split[1]+'-'+split[0]
                    if lclass_reversed in IvoaSpectrum.LL_CODES:
                        LL_code = IvoaSpectrum.LL_CODES[lclass_reversed]
                    elif split[0] in IvoaSpectrum.LL_CODES:
                        LL_code = IvoaSpectrum.LL_CODES[split[0]]
                    elif split[1] in IvoaSpectrum.LL_CODES:
                        LL_code = IvoaSpectrum.LL_CODES[split[1]]
        
        PPPP_code = IvoaSpectrum._get_PPPP(specinfo, TT_code, LL_code)

        return IvoaSpectrum(TT_code=TT_code, tt_code=tt_code, LL_code=LL_code, PPPP_code=PPPP_code)

    @staticmethod
    def _get_PPPP(specinfo, TT_code, ll_code):
        global_pecs = set()
        
        if specinfo.comp:
            global_pecs.add(IvoaSpectrum.P1P2_CODES['+'])
            P3_code, P4_code = divmod(IvoaSpectrum._get_TT(specinfo.comp), 10)
        elif TT_code in (10,11,31,32,33,66) and specinfo.tclass[-1] in ('C','N'):
            P3_code = 10
            P4_code = 8
        elif TT_code == 26:
            if specinfo.tclass == 'MS':
                P3_code = 1
            elif specinfo.tclass == 'SC':
                P3_code = 4
            else:
                P3_code = 10
            P4_code = 10
        elif 20 <= TT_code <= 25:
            P3_code = 2 if 29 <= ll_code <= 32 else 10
            P4_code = 10
        elif 40 <= TT_code <= 49:
            P3_code, P4_code = IvoaSpectrum._get_P3P4_D(specinfo)
        else:
            P3_code = 10
            P4_code = 10

        ep = ''
        sisr = ''
        elements = set()
        for pec in specinfo.pecs:
            if pec[0] in IvoaSpectrum.P1P2_CODES:
                global_pecs.add(IvoaSpectrum.P1P2_CODES[pec[0]])
                if (pec[0] == 'e' and (ep == '' or ep == 'p') or
                        pec[0] == 'p' and (ep == '' or ep == 'e')):
                    ep += pec[0]
            elif not specinfo.comp:
                if 51 <= TT_code <= 55:
                    pec_code = IvoaSpectrum.P3_WR_CODES.get(pec[0], 10)
                    if pec_code < P3_code:
                        P3_code = pec_code
                elif TT_code in (10,11,31,32,33,66):
                    pec_code = IvoaSpectrum.P4_OB_CODES.get(pec[0], 10)
                    if pec_code == 10:
                        if pec[0] in ('Fe', 'm'):
                            if pec[1].startswith('-'):
                                pec_code = 6
                            else:
                                pec_code = 5
                        elif pec[0] == 'f':
                            if pec[1].startswith('+'):
                                pec_code = 3
                            else:
                                pec_code = 2
                        elif (pec[0] in ('He','Hg','Mn','Si','Sr','Cr','Eu') and
                                not pec[1].startswith('-')):
                            elements.add(pec[0])
                            if sisr == '' and pec[0] in ('Si','Sr'):
                                sisr = pec[0]
                    if pec_code < P4_code:
                        P4_code = pec_code
                elif TT_code in (12,13):
                    pec_code = IvoaSpectrum.P4_AF_CODES.get(pec[0], 10)
                    if pec_code == 10:
                        if pec[0] in ('Fe', 'm'):
                            if pec[1] == '':
                                if pec[0] == 'm':
                                    pec_code = 5
                            if pec[1].startswith('-'):
                                pec_code = 3
                            else:
                                pec_code = 4
                        elif (pec[0] in ('Hg','Mn','Si','Cr','Eu','Sr') and
                                not pec[1].startswith('-')):
                            elements.add(pec[0])
                    if pec_code < P4_code:
                        P4_code = pec_code
                elif TT_code in (14,15):
                    final = '-' if pec[1].startswith('-') else '+'
                    elements.add(pec[0]+final)
                elif 16 <= TT_code <= 19:
                    if pec[0] == 'Ba':
                        if not pec[1].startswith('-'):
                            P3_code = 1
                    elif pec[0] == 'sd' and P3_code > 2:
                        P3_code = 2
                    elif pec[0] == 'esd' or pec[0] == 'usd' and P3_code > 3:
                        P3_code = 3
                    elif pec[0] == 'Fe':
                        P4_code = 2 if pec[1].startswith('-') else 1
                elif 20 <= TT_code <= 25:
                    if pec[0] == 'MS':
                        P3_code = 1
                    elif pec[0] == 'd' and P3_code > 2:
                        P3_code = 2
                    elif pec[0] == 'j':
                        P4_code = 1
                elif TT_code == 26:
                    if pec[0] == '/' and pec[1] != '':
                        if pec[1] == '1-':
                            P3_code = 1
                        elif pec[1][0] in ('1','2','3') and P3_code > 2:
                            P3_code = 2
                        elif pec[1][0] in ('4','5','6') and P3_code > 3:
                            P3_code = 3
                        elif pec[1][0] in ('7','8','9','10') and P3_code > 4:
                            P3_code = 4
                    elif pec[0] == 'Tc':
                        if pec[1].startswith('-'):
                            P4_code = 2
                        else:
                            P4_code = 1

        if not specinfo.comp:
            if TT_code in (10,11,31,32,33,56):
                if 'Sr' in elements and 'Si' in elements and sisr == 'Sr':
                    elements.remove('Si')
                for groupcodes in IvoaSpectrum.P3_OB_GROUP_CODES:
                    if elements == groupcodes['elements']:
                        P3_code = groupcodes['value']
                        break
            elif TT_code in (12,13):
                for groupcodes in IvoaSpectrum.P3_AF_GROUP_CODES:
                    if elements == groupcodes['elements']:
                        P3_code = groupcodes['value']
                        break
            elif TT_code in (14,15):
                cnch = {e for e in elements if len(e)==3 and e[0:2] in ('CN','CH')}
                for groupcodes in IvoaSpectrum.P3_GK_GROUP_CODES:
                    if cnch == groupcodes['elements']:
                        P3_code = groupcodes['value']
                        break
                if 'Ba+' in elements:
                    if 'Fe+' in elements or 'm+' in elements:
                        P4_code = 2
                    elif 'Fe-' in elements or 'm-' in elements:
                        P4_code = 3
                    elif 'C2+' in elements:
                        P4_code = 7
                    else:
                        P4_code = 1
                elif 'Fe+' in elements or 'm+' in elements:
                    P4_code = 4
                elif 'Fe-' in elements or 'm-' in elements:
                    P4_code = 5
                elif 'C2+' in elements:
                    P4_code = 6
                elif 'Ca+' in elements:
                    P4_code = 7

        global_values = sorted(global_pecs)[0:2]
        if 'p' in global_values and 'e' in global_values:
            global_values[0] = IvoaSpectrum.P1P2_CODES[ep[0]]
            global_values[1] = IvoaSpectrum.P1P2_CODES[ep[1]]
        
        while len(global_values) < 2:
            global_values.append(0)
        
        if P3_code == 10:
            P3_code = 0

        if P4_code == 10:
            P4_code = 0
        
        return (global_values[0]*1000 + global_values[1]*100 +
                P3_code*10 + P4_code)

    @staticmethod
    def _get_TT(tclass):
        if tclass:
            if tclass.startswith('D'):
                return IvoaSpectrum.TT_CODES.get(tclass[0:2],
                                                 IvoaSpectrum.TT_CODES['D'])
            else:
                return IvoaSpectrum.TT_CODES.get(tclass, 0)
        else:
            return 0

    @staticmethod
    def _get_P3P4_D(specinfo):
        codes = []
        for tpec in specinfo.tclass[2:]:
            if tpec == specinfo.tclass[1]:
                continue

            if tpec in IvoaSpectrum.P3P4_D_CODES:
                codes.append(IvoaSpectrum.P3P4_D_CODES[tpec])
        
        for pec in specinfo.pecs:
            if pec[0] in IvoaSpectrum.P3P4_D_CODES:
                codes.append(IvoaSpectrum.P3P4_D_CODES[pec[0]])
        
        while len(codes) < 2:
            codes.append(0)
        
        return codes[0], codes[1]
#end class IvoaSpectrum

class CelestiaSpectrum(object):
    MAP_TT = {
        10: 0,
        11: 1,
        12: 2,
        13: 3,
        14: 4,
        15: 5,
        16: 6,
        17: 13,
        18: 14,
        #19 Y unsupported, use T9 instead
        20: 15,
        21: 7, # C-R -> R
        22: 9, # C-N -> N
        23: 15, # C-J not supported, use C instead
        24: 15, # C-H not supported, use C instead
        25: 15, # C-Hd not supported, use C instead
        26: 8,
        30: 12, # sd use unknown
        # 31 also set luminosity
        # 32 also set luminosity
        # 33 also set luminosity
        40: 22,
        41: 16,
        42: 17,
        43: 18,
        44: 19,
        45: 21,
        46: 20,
        47: 12, # PG1159
        50: 32,
        51: 10, # WR use WC instead
        52: 11,
        53: 10,
        54: 10, # WO use WC instead
        # 56 OB unsupported, use B0 instead
    }
    
    def __init__(self, **kwargs):
        self.code = kwargs.get('code', 0x0ca8)
    
    @staticmethod
    def create(specinfo):
        ivoa = IvoaSpectrum.create(specinfo)
        kt = 12
        s = 10
        l = 8
        if ivoa.TT_code in CelestiaSpectrum.MAP_TT:
            kt = CelestiaSpectrum.MAP_TT[ivoa.TT_code]
        elif ivoa.TT_code == 19:
            kt = 14
            s = 9
        elif ivoa.TT_code == 31:
            kt = 0
            l = 7
        elif ivoa.TT_code == 32:
            kt = 1
            l = 7
        elif ivoa.TT_code == 33:
            kt = 2
            l = 7
        elif ivoa.TT_code == 56:
            kt = 1
            s = 0
        
        if kt < 16 and kt != 12:
            if s == 10:
                if 10 <= ivoa.tt_code <= 19:
                    s = ivoa.tt_code - 10
                elif ivoa.tt_code == 20:
                    # 10 unsupported, use 9
                    s = 9
            
            if l == 8:
                if ivoa.LL_code in (10,11):
                    l = 0
                elif ivoa.LL_code in (12,13,14):
                    l = 1
                elif ivoa.LL_code in (15,16,17):
                    l = 2
                elif ivoa.LL_code in (18,19,20,21):
                    l = 3
                elif ivoa.LL_code in (22,23,24,25):
                    l = 4
                elif ivoa.LL_code in (26,27,28,29):
                    l = 5
                elif ivoa.LL_code in (30,31):
                    l = 6
                elif ivoa.LL_code in (32,33,34,35):
                    l = 7
        else:
            l = 0
            if kt >= 32:
                s = 0
        
        return CelestiaSpectrum(code=(kt<<8) + (s<<4) + l)