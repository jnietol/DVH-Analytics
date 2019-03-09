#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import wx
from models.datatable import DataTable
from models.dvh import calc_eud, calc_tcp
import wx.lib.mixins.listctrl as listmix
from copy import deepcopy


class EditableListCtrl(wx.ListCtrl, listmix.TextEditMixin):
    ''' TextEditMixin allows any column to be edited. '''

    # ----------------------------------------------------------------------
    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        """Constructor"""
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.TextEditMixin.__init__(self)


class RadBioFrame:
    def __init__(self, parent, dvh, *args, **kwds):

        self.parent = parent
        self.dvh = dvh

        self.table_published_values = wx.ListCtrl(self.parent, wx.ID_ANY,
                                                  style=wx.BORDER_SUNKEN | wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        self.text_input_eud_a = wx.TextCtrl(self.parent, wx.ID_ANY, "")
        self.text_input_gamma_50 = wx.TextCtrl(self.parent, wx.ID_ANY, "")
        self.text_input_td_50 = wx.TextCtrl(self.parent, wx.ID_ANY, "")
        self.button_apply_parameters = wx.Button(self.parent, wx.ID_ANY, "Apply Parameters")
        self.table_rad_bio = EditableListCtrl(self.parent, ID= wx.ID_ANY, style=wx.BORDER_SUNKEN | wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        self.columns = ['MRN', 'ROI Name', 'a', u'\u03b3_50', 'TD or TCD', 'EUD', 'NTCP or TCP', 'PTV Overlap',
                        'ROI Type', 'Rx Dose', 'Total Fxs', 'Fx Dose']
        self.width = [100, 175, 50, 50, 80, 80, 80, 100, 100, 100, 100, 100]
        self.data_table_rad_bio = DataTable(self.table_rad_bio, columns=self.columns, widths=self.width)

        # Adding wx.RadioBox prior to data table_rad_bio causes display glitch
        # self.radio_box_apply = wx.RadioBox(self.parent, wx.ID_ANY, "Apply to:", choices=["All", "Selected"],
        #                                    majorDimension=1, style=wx.RA_SPECIFY_ROWS)

        self.__set_properties()
        self.__do_layout()

        parent.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_parameter_select, self.table_published_values)
        parent.Bind(wx.EVT_BUTTON, self.apply_parameters, id=self.button_apply_parameters.GetId())

        self.disable_buttons()

    def __set_properties(self):
        self.table_published_values.AppendColumn("Structure", format=wx.LIST_FORMAT_LEFT, width=150)
        self.table_published_values.AppendColumn("Endpoint", format=wx.LIST_FORMAT_LEFT, width=300)
        self.table_published_values.AppendColumn("a", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.table_published_values.AppendColumn(u"\u03b3_50", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.table_published_values.AppendColumn("TD_50", format=wx.LIST_FORMAT_LEFT, width=-1)
        # self.radio_box_apply.SetSelection(0)

        for i, col in enumerate(self.columns):
            self.table_rad_bio.AppendColumn(col, format=wx.LIST_FORMAT_LEFT, width=self.width[i])

        self.published_data = [['Brain', 'Necrosis', 5, 3, 60],
                               ['Brainstem', 'Necrosis', 7, 3, 65],
                               ['Optic Chasm', 'Blindness', 25, 3, 65],
                               ['Colon', 'Obstruction/Perforation', 6, 4, 55],
                               ['Ear (mid/ext)', 'Acute serous otitus', 31, 3, 40],
                               ['Ear (mid/ext)', 'Chronic serous otitus', 31, 4, 65],
                               ['Esophagus', 'Perforation', 19, 4, 68],
                               ['Heart', 'Pericarditus', 3, 3, 50],
                               ['Kidney', 'Nephritis', 1, 3, 28],
                               ['Lens', 'Cataract', 3, 1, 18],
                               ['Liver', 'Liver Failure', 3, 3, 40],
                               ['Lung', 'Pneumontis', 1, 2, 24.5],
                               ['Optic Nerve', 'Blindness', 25, 3, 65],
                               ['Retina', 'Blindness', 15, 2, 65]]

        for row in self.published_data:
            index = self.table_published_values.InsertItem(50000, str(row[0]))
            for i in [1, 2, 3, 4]:
                self.table_published_values.SetItem(index, i, str(row[i]))

    def __do_layout(self):
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_parameters = wx.BoxSizer(wx.VERTICAL)
        sizer_parameters_input = wx.StaticBoxSizer(wx.StaticBox(self.parent, wx.ID_ANY, ""), wx.HORIZONTAL)
        sizer_button = wx.BoxSizer(wx.VERTICAL)
        sizer_td_50 = wx.BoxSizer(wx.VERTICAL)
        sizer_gamma_50 = wx.BoxSizer(wx.VERTICAL)
        sizer_eud = wx.BoxSizer(wx.VERTICAL)
        sizer_published_values = wx.BoxSizer(wx.VERTICAL)
        label_published_values = wx.StaticText(self.parent, wx.ID_ANY,
                                               "Published EUD Parameters from Emami et. al. for 1.8-2.0Gy "
                                               "fractions (Click to apply)")
        label_published_values.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                               wx.FONTWEIGHT_BOLD, 0, ""))
        sizer_published_values.Add(label_published_values, 0, wx.ALL, 5)
        sizer_published_values.Add(self.table_published_values, 1, wx.ALL, 10)
        sizer_published_values.SetMinSize((500, 335))
        sizer_main.Add(sizer_published_values, 1, wx.ALL | wx.EXPAND, 10)
        label_parameters = wx.StaticText(self.parent, wx.ID_ANY, "Parameters:")
        label_parameters.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        sizer_parameters.Add(label_parameters, 0, 0, 0)
        label_eud = wx.StaticText(self.parent, wx.ID_ANY, "EUD a-value:")
        sizer_eud.Add(label_eud, 0, 0, 0)
        sizer_eud.Add(self.text_input_eud_a, 0, wx.ALL | wx.EXPAND, 5)
        sizer_parameters_input.Add(sizer_eud, 1, wx.EXPAND, 0)
        label_gamma_50 = wx.StaticText(self.parent, wx.ID_ANY, u"\u03b3_50:")
        sizer_gamma_50.Add(label_gamma_50, 0, 0, 0)
        sizer_gamma_50.Add(self.text_input_gamma_50, 0, wx.ALL | wx.EXPAND, 5)
        sizer_parameters_input.Add(sizer_gamma_50, 1, wx.EXPAND, 0)
        label_td_50 = wx.StaticText(self.parent, wx.ID_ANY, "TD_50 or TCD_50:")
        sizer_td_50.Add(label_td_50, 0, 0, 0)
        sizer_td_50.Add(self.text_input_td_50, 0, wx.ALL | wx.EXPAND, 5)
        sizer_parameters_input.Add(sizer_td_50, 1, wx.EXPAND, 0)
        sizer_button.Add(self.button_apply_parameters, 1, wx.ALL | wx.EXPAND, 15)
        sizer_parameters_input.Add(sizer_button, 1, wx.EXPAND, 0)
        # sizer_parameters_input.Add(self.radio_box_apply, 0, wx.EXPAND, 0)
        sizer_parameters.Add(sizer_parameters_input, 1, wx.ALL | wx.EXPAND, 5)
        sizer_main.Add(sizer_parameters, 0, wx.ALL | wx.EXPAND, 10)
        sizer_main.Add(self.table_rad_bio, 1, wx.ALL | wx.EXPAND, 10)
        self.layout = sizer_main

    def enable_buttons(self):
        self.button_apply_parameters.Enable()

    def disable_buttons(self):
        self.button_apply_parameters.Disable()

    def enable_initial_buttons(self):
        self.button_apply_parameters.Enable()

    def on_parameter_select(self, evt):
        index = self.table_published_values.GetFirstSelected()

        self.text_input_eud_a.SetValue(str(self.published_data[index][2]))
        self.text_input_gamma_50.SetValue(str(self.published_data[index][3]))
        self.text_input_td_50.SetValue(str(self.published_data[index][4]))

    def update_dvh_data(self, dvh):
        self.dvh = dvh
        data = {'MRN': self.dvh.mrn,
                'ROI Name': self.dvh.roi_name,
                'a': [''] * self.dvh.count,
                u'\u03b3_50': [''] * self.dvh.count,
                'TD or TCD': [''] * self.dvh.count,
                'EUD': [''] * self.dvh.count,
                'NTCP or TCP': [''] * self.dvh.count,
                'PTV Overlap': self.dvh.ptv_overlap,
                'ROI Type': self.dvh.roi_type,
                'Rx Dose': self.dvh.rx_dose,
                'Total Fxs': self.dvh.get_plan_values('fxs'),
                'Fx Dose': self.dvh.get_rx_values('fx_dose')}
        self.data_table_rad_bio.set_data(data, self.columns)

    def apply_parameters(self, evt):
        selected_indices = get_selected_items(self.table_rad_bio)
        if not selected_indices:
            selected_indices = range(self.data_table_rad_bio.row_count)
        for i in selected_indices:
            current_row = self.data_table_rad_bio.get_row(i)
            new_row = deepcopy(current_row)
            new_row[2] = self.text_input_eud_a.GetValue()
            new_row[3] = self.text_input_gamma_50.GetValue()
            new_row[4] = self.text_input_td_50.GetValue()
            new_row[5] = round(calc_eud(self.dvh.dvh[:, i], float(new_row[2])), 2)
            new_row[6] = round(calc_tcp(float(new_row[3]), float(new_row[4]), float(new_row[5])), 3)
            self.data_table_rad_bio.edit_row(new_row, i)


def get_selected_items(list_control):
    selection = []

    index_current = -1
    while True:
        index_next = list_control.GetNextItem(index_current, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        if index_next == -1:
            return selection

        selection.append(index_next)
        index_current = index_next
