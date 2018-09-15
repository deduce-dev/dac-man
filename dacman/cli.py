"""
`dacman.cli`
====================================

.. currentmodule:: dacman.cli

:platform: Unix, Mac
:synopsis: Entry-point to Dac-Man CLI

.. moduleauthor:: Devarshi Ghoshal <dghoshal@lbl.gov>

"""

import argparse
import os
import sys
from dacman.core import scanner
from dacman.core import indexer
from dacman.core import change
from dacman.core import diff
from dacman.core import cleanup
from dacman.core import mpi_indexer

def _addScanParser(subparsers):
    parser_worker = subparsers.add_parser('scan',
                                          formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                          help=""" Scans a data directory for tracking """)

    parser_worker.set_defaults(action="scan")
    #parser_worker.add_argument('-d','--datapath', help='path to the dataset', required=True)    
    parser_worker.add_argument(dest='datapath', help='path to the dataset')    
    parser_worker.add_argument('-s','--stage', dest='stagingdir', help='(optional) directory where indexes and metadata information will be saved')    
    parser_worker.add_argument('-i', '--ignore', help='(optional) ignores files of specific types', nargs='*')
    parser_worker.add_argument('--nonrecursive', help='(optional) only scans specified directory contents, ignoring subdirectory contents', action='store_true')
    parser_worker.add_argument('--symlinks', help='(optional) allows recursive scanning symbolic links', action='store_true')
    parser_worker.add_argument('--metadata-details', dest='metadetails', help='(optional) capture detailed filesystem metadata', action='store_true')
    #parser_worker.add_argument('-U','--usermeta', help='optional user-level metadata <to be implemented>')    

def _addIndexParser(subparsers):
    parser_worker = subparsers.add_parser('index',
                                          formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                          help=""" Indexes objects in a data path in parallel """)

    parser_worker.set_defaults(action="index")
    #parser_worker.add_argument('-d','--datapath', help='path to the dataset', required=True)    
    parser_worker.add_argument(dest='datapath', help='path to the dataset')    
    parser_worker.add_argument('-s','--stage', dest='stagingdir', help='(optional) directory where indexes and metadata information will be saved')    
    parser_worker.add_argument('-m','--manager', help='execution manager', choices=['python', 'tigres', 'mpi'], default='python')

def _addChangeParser(subparsers):
    parser_worker = subparsers.add_parser('compare',
                                          formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                          help=""" Calculates and saves directory changes """)

    parser_worker.set_defaults(action="change")
    #parser_worker.add_argument('-o','--oldpath', help='path to the old dataset', required=True)    
    #parser_worker.add_argument('-n','--newpath', help='path to the new dataset', required=True)    
    parser_worker.add_argument(dest='oldpath', help='path to the old dataset')    
    parser_worker.add_argument(dest='newpath', help='path to the new dataset')    
    parser_worker.add_argument('-s','--stage', dest='stagingdir', help='(optional) directory where indexes and metadata information will be saved')    
    parser_worker.add_argument('-F', '--force', help='(optional) force data comparison even if the changes are pre-calculated', action='store_true')
    #parser_worker.add_argument('-N','--newdeducedir', help='optional directory for saving indexes and metadata for new datapath (for read-only data directories)')    

def _addDiffParser(subparsers):
    parser_worker = subparsers.add_parser('diff',
                                          formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                          help=""" Finds the diff between two datasets """)

    parser_worker.set_defaults(action="diff")
    #parser_worker.add_argument('-o','--oldpath', help='path to the old dataset', required=True)    
    #parser_worker.add_argument('-n','--newpath', help='path to the new dataset', required=True)
    parser_worker.add_argument(dest='oldpath', help='path to the old dataset')    
    parser_worker.add_argument(dest='newpath', help='path to the new dataset')    
    parser_worker.add_argument('-s','--stage', dest='stagingdir', help='(optional) directory where indexes and metadata information will be saved')    
    #parser_worker.add_argument('-O','--olddeducedir', help='optional directory for saving indexes and metadata for new datapath (for read-only data directories)')    
    #parser_worker.add_argument('-N','--newdeducedir', help='optional directory for saving indexes and metadata for new datapath (for read-only data directories)')    
    parser_worker.add_argument('-o','--outdir', help='path where change information is saved')    
    parser_worker.add_argument('-a','--analyzer', help='(optional) custom program to analyze changes')    
    parser_worker.add_argument('--datachange', help='(optional) find data changes in modified files', action='store_true')
    parser_worker.add_argument('-e','--executor', help='executor that parallelizes data change calculation', choices=['default', 'mpi', 'tigres'], default='default')

def _addCleanupParser(subparsers):
    parser_worker = subparsers.add_parser('clean',
                                          formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                          help=""" Removes deduce indexes from a data directory """)

    parser_worker.set_defaults(action="clean")
    #parser_worker.add_argument('-d','--datadirs', help='data directories', nargs='*', required=True)    
    parser_worker.add_argument(dest='datadirs', help='data directories', nargs='+')    

##################################
def main():
    parser = argparse.ArgumentParser(description="",
                                     prog="dacman",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    subparsers = parser.add_subparsers()
    _addScanParser(subparsers)
    _addIndexParser(subparsers)
    _addChangeParser(subparsers)
    _addDiffParser(subparsers)
    _addCleanupParser(subparsers)

    args = parser.parse_args()
    if len(args.__dict__) == 0:
        #print("Parser not yet implemented for this phase")
        parser.print_usage()
        sys.exit(1)

    action = args.action

    if action == 'scan':
        scanner.main(args)
    elif action == 'index':
        if args.manager != 'mpi':
            indexer.main(args)
        else:
            mpi_indexer.main(args)
    elif action == 'change':
        change.main(args)
    elif action == 'diff':
        diff.main(args)
    elif action == 'clean':
        cleanup.main(args)
    else:
        print("Invalid action!")

##################################

if __name__ == '__main__':
    main()
