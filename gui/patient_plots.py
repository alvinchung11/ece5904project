# Creating plots with patient date

import tkinter as tk
from tkinter import ttk

from patient_data import Patient

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from sksurv.linear_model import CoxPHSurvivalAnalysis
from sksurv.ensemble import RandomSurvivalForest

import joblib

def get_RSF_plot(master, feature_vector):
    frame = ttk.Frame(master)

    fig = Figure(figsize=(5, 4))
    plot_ax = fig.add_subplot()

    canvas = FigureCanvasTkAgg(fig, frame)
    canvas_widget = canvas.get_tk_widget()

    RSF_model : RandomSurvivalForest = joblib.load("../models/model_RSF.joblib")
    
    surv_func = RSF_model.predict_survival_function(feature_vector)

    canvas_widget.pack(fill="both", expand=True)
    
    plot_ax.set_title("Relapse-Free Probability Over Time")

    for fn in surv_func:
            plot_ax.step(fn.x, fn(fn.x), where="post")
    
    plot_ax.set_xlabel("Months")
    plot_ax.set_ylabel("Probability of No Relapse", size=12)
    plot_ax.set_xlim([0, 24])
    plot_ax.set_xticks(list(range(0, 25, 2)))
    plot_ax.grid(True)

    return frame

def get_CoxPH_plot(master, feature_vector):
    frame = ttk.Frame(master)

    fig = Figure(figsize=(5, 4))
    plot_ax = fig.add_subplot()

    canvas = FigureCanvasTkAgg(fig, frame)
    canvas_widget = canvas.get_tk_widget()

    CoxPH_model : CoxPHSurvivalAnalysis = joblib.load("../models/model_coxPH.joblib")
    
    surv_func = CoxPH_model.predict_survival_function(feature_vector)

    canvas_widget.pack(fill="both", expand=True)
    
    plot_ax.set_title("Relapse-Free Probability Over Time")

    for fn in surv_func:
            plot_ax.step(fn.x, fn(fn.x), where="post")
    
    plot_ax.set_xlabel("Months")
    plot_ax.set_ylabel("Probability of No Relapse", size=12)
    plot_ax.set_xlim([0, 24])
    plot_ax.set_xticks(list(range(0, 25, 2)))
    plot_ax.grid(True)

    return frame