import numpy as np
import pandas as pd
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show

raw_between = pd.read_pickle("default_mutual_information.pkl")
within = pd.read_pickle("within_patient.pkl")


def get_values(patient_id: str) -> list:
    return raw_between[patient_id][raw_between.index != patient_id].values


def get_between_patient_scores() -> dict:
    results = dict()
    for patient_id in raw_between.index:
        results[patient_id] = get_values(patient_id)
    return results


between = get_between_patient_scores()


p = figure(plot_width=1500, plot_height=600)
# all_between_scores = np.concatenate(list(between.values()))

p.vbar(x=np.arange(len(between)), bottom=0, top=0, width=1, color="black")


show(p)
