from __future__ import division
import os
import yaml
import tables as tb
import numpy as np
import pandas as pd
import csv
from pathlib import Path
import coloredlogs as cl


class AnalysisUtils(object):

    def __init__(self):
        pass

    # Conversion functions

    def save_to_h5(self, data=None, outname=None, directory=None, title="Beamspot scan results"):
        if not os.path.exists(directory):
            os.mkdir(directory)
        filename = os.path.join(directory, outname)
        with tb.open_file(filename, "w") as out_file_h5:
            out_file_h5.create_array(out_file_h5.root, name='data', title=title, obj=data)

    def open_yaml_file(self, directory=None, file=None):
        filename = os.path.join(directory, file)
        with open(filename, 'r') as ymlfile:
            cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
        return cfg

    def dump_yaml_file(self, directory=None, file=None, loaded=None):
        filename = os.path.join(directory, file)
        with open(filename, 'w') as ymlfile:
            yaml.dump(loaded, ymlfile, sort_keys=False)

    def save_to_csv(self, data=None, outname=None, directory=None):
        df = pd.DataFrame(data)
        if not os.path.exists(directory):
            os.mkdir(directory)
        filename = os.path.join(directory, outname)
        df.to_csv(filename, index=True)

    def open_h5_file(self, outname=None, directory=None):
        filename = os.path.join(directory, outname)
        with tb.open_file(filename, 'r') as in_file:
            data = in_file.root.data[:]
        return data

    def get_subindex_description_yaml(self, dictionary=None, index=None, subindex=None):
        index_item = [dictionary[i] for i in [index] if i in dictionary]
        subindex_items = index_item[0]["subindex_items"]
        subindex_description_items = subindex_items[subindex]
        return subindex_description_items

    def get_info_yaml(self, dictionary=None, index=None, subindex="description_items"):
        index_item = [dictionary[i] for i in [index] if i in dictionary]
        index_description_items = index_item[0][subindex]
        return index_description_items

    def get_subindex_yaml(self, dictionary=None, index=None, subindex="subindex_items"):
        index_item = [dictionary[i] for i in [index] if i in dictionary]
        subindex_items = index_item[0][subindex]
        return subindex_items.keys()

    def get_project_root(self) -> Path:
        """Returns project root folder."""
        return Path(__file__).parent.parent

    def open_csv_file(self, outname=None, directory=None,
                      fieldnames=['TimeStamp', 'Channel', "Id", "ADCChannel", "ADCData", "ADCDataConverted"]):
        if not os.path.exists(directory):
            os.mkdir(directory)
        filename = os.path.join(directory, outname)
        out_file_csv = open(filename + '.csv', 'w+')
        return out_file_csv

    def save_adc_data(self, directory=None, channel=None):
        File = tb.open_file(directory + "ch_" + str(channel) + ".h5", 'w')
        description = np.zeros((1,), dtype=np.dtype(
            [("TimeStamp", "f8"), ("Channel", "f8"), ("Id", "f8"), ("Flg", "f8"), ("DLC", "f8"), ("ADCChannel", "f8"),
             ("ADCData", "f8"), ("ADCDataConverted", "f8")])).dtype
        table = File.create_table(File.root, name='ADC_results', description=description)
        table.flush()
        row = table.row
        #     for i in np.arange(length_v):
        #         row["TimeStamp"] = voltage_array[i]
        #         row["Channel"] = mean
        #         row["Id"] = std
        #         row["DLC"] = voltage_array[i]
        #         row["ADCChannel"] = mean
        #         row["ADCData"] = std
        #         row["ADCDataConverted"] = std
        #         row.append()
        File.create_array(File.root, 'ADC results', ADC_results, "ADC results")
        File.close()

