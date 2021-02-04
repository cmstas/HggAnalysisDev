import numpy
import awkward
import json

class CutStats():
    def __init__(self, **kwargs):
        self.debug = kwargs.get("debug")
        self.event_stats = {}
        self.object_stats = {}
        self.objects = {}

    def add_initial_events(self, sample, n_events):
        if sample not in self.event_stats.keys():
            self.event_stats[sample] = { "n_events_initial" : n_events }
        else:
            self.event_stats[sample]["n_events_initial"] += n_events

    def add_initial_objects(self, sample, object, n_objects):
        if object not in self.object_stats.keys():
            self.object_stats[object] = {}

        if sample not in self.object_stats[object].keys():
            self.object_stats[object][sample] = { "n_objects_initial" : n_objects_initial }
        else:
            self.object_stats[object][sample]["n_objects_initial"] += n_objects_initial

    def add_event_cuts(self, events cuts, names, sample):
        if sample not in self.event_stats.keys():
            self.event_stats[sample] = { "n_events_initial" : n_events }
        else:
            self.event_stats[sample]["n_events_initial"] += n_events

        for cut, name in zip(cuts, names):
            if name not in self.event_stats[sample].keys():
                self.event_stats[sample][name] = awkward.sum(events[cut])
            else:
                self.event_stats[sample][name] += awkward.sum(events[cut])

    def add_object_cuts(self, objects, object_name, cuts, names, sample):
        if object_name not in self.object_stats.keys():
            self.object_stats[object_name] = {}

        if sample not in self.object_stats[object_name].keys():
            self.object_stats[object_name][sample] = { "n_objects_initial" : awkward.sum(awkward.num(objects)) }
        else:
            self.object_stats[object_name][sample]["n_objects_initial"] += awkward.sum(awkward.num(objects))

        for cut, name in zip(cuts, names):
            if name not in self.object_stats[object_name][sample].keys():
                self.object_stats[object_name][sample][name] = awkward.sum(awkward.num(objects[cut]))
            else:
                self.object_stats[object_name][sample][name] += awkward.sum(awkward.num(objects[cut]))

    def summarize():
        results = { "event_cuts" : self.event_stats, "object_cuts" : self.object_stats }
        with open("CutStatsSummary.json", "w") as f_out:
            json.dump(results, f_out, sort_keys = True, indent = 4)

