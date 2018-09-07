"""
`dacman.core.persistence`
====================================

.. currentmodule:: dacman.core.persistence

:platform: Unix, Mac
:synopsis: Module for future enhancements, serializing filesystem data and metadata (e.g. shelve) 

.. moduleauthor:: Devarshi Ghoshal <dghoshal@lbl.gov>

"""

import os
import shelve
import hashlib
import sys
import dacman.core.utils as dacman_utils

class DirectoryTree():
   def __init__(self, root, deducedir):
      self._tree = {}
      self._root = os.path.abspath(root)
      #self._parent = os.path.dirname(self._root)
      root_hash = hashlib.md5(self._root.encode('utf-8')).hexdigest()
      dbpath = os.path.join(deducedir, root_hash)
      self._serializer = shelve.open(dbpath)

   def add(self, path):
      dirname = os.path.relpath(os.path.dirname(path), self._root)
      filename = os.path.basename(path)
      if dirname in self._tree:
         self._tree[dirname].append(filename)
      else:
         self._tree[dirname] = [filename]

   def save(self):
       self._serializer[self._root] = self._tree

   def display(self):
      try:
         dirtree = self._serializer[self._root]
         print(dirtree)
      except Exception as e:
         print(e)

   def close(self):
       self._serializer.close()
       

class DiffStore():
   def __init__(self, dbpath):
      self.dbpath = os.path.join(dbpath, 'diffs')
      if not os.path.exists(dbpath):
         os.makedirs(dbpath)

   '''
   commits diff outputs to deduce
   - diff_objects is a list of objects (currently, files) containing the information about the file differences
   - currently, it stores the data within the deduce fs as directories
     but the data can be stored in a database as well
   '''
   def commit(self, new_file, old_file, analyzer_name, diff_objects):
      change_id = hashlib.md5(new_file + old_file)
      analyzer_id = hashlib.md5(analyzer_name)
      diff_dir = os.path.join(self.dbpath, change_id, analyzer_id)
      if not os.path.exists(diff_dir):
         os.makedirs(diff_dir)
      if isinstance(diff_objects, list): # change this later to is_type(diff_objects, list)
         for obj in diff_objects:
            #if is_type(obj, DiffObject):
            if os.path.exists(obj):
               if os.path.isfile(obj):
                  # copy both data and metadata
                  shutil.copy2(obj, diff_dir)
               else:
                  dest_dir = os.path.join(diff_dir, os.path.basename(obj))
                  # need to throw a warning here
                  if os.path.exists(dest_dir):
                     shutil.rmtree(dest_dir)
                  shutil.copytree(obj, dest_dir)
            else:
               raise ValueError('Path {} does not exist'.format(obj))
      else:
         raise TypeError('diff_objects should be a list')

      analyzer_file = os.path.join(self.dbpath, change_id, 'ANALYZERS')
      data = {analyzer_name: analyzer_id}
      dacman_utils.update_yaml(data, analyzer_file)
      
      return change_id
              

   def get_analyzers(self, new_file, old_file):
      change_id = hashlib.md5(new_file + old_file)
      analyzer_file = os.path.join(self.dbpath, change_id, 'ANALYZERS')
      data = dacman_utils.load_yaml(analyzer_file)
      analyzers = []
      for key in data:
         analyzers.append(key)
      
      return analyzers


   def retrieve_diff(self, new_file, old_file, analyzer_name, outdir=None):
      change_id = hashlib.md5(new_file + old_file)
      analyzer_id = hashlib.md5(analyzer_name)
      diff_dir = os.path.join(self.dbpath, change_id, analyzer_id)
      if not os.path.exists(diff_dir):
         print('No diff data exists for {} and {}'.format(new_file, old_file))
         return None

      output = os.path.abspath('output')
      if not outdir:
         output = os.path.abspath(outdir)

      if not os.path.exists(output):
         os.makedirs(output)
      
      for entry in scandir(diff_dir):
         diff_path = os.path.join(diff_dir, entry.name)
         outpath = os.path.join(output, os.path.basename(entry.name))
         if entry.is_dir(follow_symlinks=False):
            shutil.copytree(diff_path, outpath)
         else:
            shutil.copy2(diff_path, outpath)
         
      print('Diff data saved to {}'.format(output))
      return output


if __name__ == '__main__':
   path = sys.argv[1]
   deducedir = sys.argv[2]
   dirtree = DirectoryTree(path, deducedir)
   dirtree.display()
   dirtree.close()
