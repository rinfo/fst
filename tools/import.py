#!/usr/bin/env python
# -*- coding: utf-8 -*-
def loaddata():
    return {'Myndighetsforeskrift':[
            {'identifierare':'FFFS 2011:1',
             'arsutgava':'2011',
             'lopnummer':'1',
             'forfattningssamling': 'FFFS', # Forfattningssamling.kortnamn
             'titel': 'Föreskrifter om ersättningssystem i kreditinstitut, värdepappersbolag och fondbolag med tillstånd för diskretionär portföljförvaltning',
             'sammafattning': 'Finansinspektionen har beslutat ... utan av FFFS 2011:2',
             'content':'uploads/foreskrift/FFFS-2010-2.pdf',
             'beslutsdatum':'2011-02-17', # sträng, inte datetime
             'utkom_fran_tryck':'2011-02-24',
             'ikrafttradandedatum':'2011-03-01',
             'omtryck': False,
             'bemyndiganden': [
                    {'titel': 'Förordning (2044:329) om bank- och finansieringsrörelse',
                     'sfs-nummer':'2044:329',
                     'kapitelnummer':'5',
                     'paragrafnummer':'2'},
                    ],
             'andringar': [], # se upphaver
             'upphavningar': ['DVFS 2009:6'], # MyndighetsForeskrift.identifierare
             'celexreferenser': ['32010L0076'], # CelexReferens.celexnummer
             'amnesord': ['Banker'], # Amnesord.titel
             'bilagor': [], # dict som motsvarar Bilaga-objektet
             'ovrigtdokument': [{'titel': 'Besluts-pm om bonusregler',
                                 'file':'uploads/ovrigt/besluts_pm_11-1.pdf'}],
             'beslutad_av': 'Finansinspektionen', # Myndighet.namn
             'utgivare': 'Finansinspektionen', # Myndighet.namn
             }
            ],
            'KonsolideradForeskrift':[
            ],
            'AllmannaRad':[
            ]
            }

if __name__ == "__main__":
    from pprint import pprint
    pprint(loaddata())
