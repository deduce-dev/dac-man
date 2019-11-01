from dacman.compare.base import Comparator
from dacman.compare.adaptor import DacmanRecord
import json

class DefaultPlugin(Comparator):
    def __init__(self):
        self.p_change_header = 0.0
        self.p_change_data = 0.0

    def supports(self):
        support = ['default']
        return support

    def description(self):
        description = '''Default DacMan comparator that transforms
                         data into DacMan records and compares the
                         changes.'''
        return description

    def compare(self, a, b, *args):
        a_record = DacmanRecord(a)
        b_record = DacmanRecord(b)
        header_changes = self._compare_records(a_record.get_header(),
                                               b_record.get_header())
        data_changes = self._compare_records(a_record.get_data(),
                                             b_record.get_data())
        if len(a_record.get_header()) > 0:
            self.p_change_header = len(header_changes['modified']) / len(a_record.get_header()) * 100.0
        if len(a_record.get_data()) > 0:
            self.p_change_data = len(data_changes['modified']) / len(a_record.get_data()) * 100.0

        changes = {'headers': header_changes,
                   'values': data_changes}
        return changes

    def _compare_records(self, record_list1, record_list2):
        nrecs1 = len(record_list1)
        nrecs2 = len(record_list2)
        changes = {}
        added = []
        deleted = []
        modified = []
        unchanged = []
        if nrecs1 < nrecs2:
            n_add = nrecs2 - nrecs1
            nrecs = nrecs1
            edit_list = record_list2[:]
            edit_list[nrecs1:nrecs2] = [1] * n_add
            for rec in record_list2[nrecs1:nrecs2]:
                added.append(rec)
        elif nrecs1 > nrecs2:
            n_del = nrecs1 - nrecs2
            nrecs = nrecs2
            edit_list = record_list1[:]
            edit_list[nrecs2:nrecs1] = [1] * n_del
            for rec in record_list1[nrecs2:nrecs1]:
                deleted.append(rec)
        else:
            nrecs = nrecs1
            edit_list = record_list1[:]
        for i in range(nrecs):
            data1 = record_list1[i]
            data2 = record_list2[i]
            if str(data1) == str(data2):
                edit_list[i] = 0
                unchanged.append(data1)
            else:
                edit_list[i] = 0.5
                edit = {'old': str(data1), 'new': str(data2)}
                modified.append(edit)

        changes['added'] = added
        changes['deleted'] = deleted
        changes['modified'] = modified
        changes['unchanged'] = unchanged

        return changes

    def percent_change(self):
        # change_perc = []
        # for a, b in self.comparisons:
        #     similarity = difflib.SequenceMatcher(None, a, b)
        #     approx_change_perc = (1.0 - similarity.quick_ratio()) * 100
        #     change_perc.append(approx_change_perc)
        # avg_change_perc = sum(change_perc)/len(change_perc)
        p_change = (self.p_change_header + self.p_change_data)/2
        return p_change

    def stats(self, changes):
        data = {}
        print("Changes in headers:")
        data['header_changes'] = self._element_stats(changes['headers'])
        print("\t % Change = {}".format(self.p_change_header))
        data['header_changes']['perc_change'] = self.p_change_header
        
        print("Changes in values:")
        data['value_changes'] = self._element_stats(changes['values'])
        print("\t % Change = {}".format(self.p_change_data))
        data['value_changes']['perc_change'] = self.p_change_data
        #return json.dumps(data, indent=4)
        return data

    def _element_stats(self, changes):
        added = len(changes['added'])
        deleted = len(changes['deleted'])
        modified = len(changes['modified'])
        unchanged = len(changes['unchanged'])
        print("\t Added={}, Deleted={}, Modified={}, Unchanged={}".format(added,
                                                                          deleted,
                                                                          modified,
                                                                          unchanged))
        change_summary = {'added': added, 'deleted': deleted,
                          'modified': modified, 'unchanged': unchanged}
        return change_summary




