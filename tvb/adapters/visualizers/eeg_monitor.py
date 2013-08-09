# -*- coding: utf-8 -*-
#
#
# TheVirtualBrain-Framework Package. This package holds all Data Management, and 
# Web-UI helpful to run brain-simulations. To use it, you also need do download
# TheVirtualBrain-Scientific Package (for simulators). See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2013, Baycrest Centre for Geriatric Care ("Baycrest")
#
# This program is free software; you can redistribute it and/or modify it under 
# the terms of the GNU General Public License version 2 as published by the Free
# Software Foundation. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details. You should have received a copy of the GNU General 
# Public License along with this program; if not, you can download it here
# http://www.gnu.org/licenses/old-licenses/gpl-2.0
#
#
#   CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#
"""
.. moduleauthor:: Ionel Ortelecan <ionel.ortelecan@codemart.ro>
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: Bogdan Neacsa <bogdan.neacsa@codemart.ro>
"""
import json
import numpy
from tvb.core.adapters.abcdisplayer import ABCDisplayer
from tvb.datatypes.time_series import TimeSeriesEEG
from tvb.core.adapters.exceptions import LaunchException



class EegMonitor(ABCDisplayer):
    """
    This viewer takes as inputs at least one ArrayWrapper and at most 3 
    ArrayWrappers, and returns the needed parameters for a 2D representation 
    of the values from these arrays, in EEG form. So far arrays of at most 3
    dimensions are supported.
    """
    has_nan = False
    _ui_name = "EEG lines Visualizer"
    _ui_subsection = "eeg"

    page_size = 4000
    preview_page_size = 250
    current_page = 0


    def get_input_tree(self):
        """ Accept as input Array of any size"""
        return [{'name': 'input_data', 'label': 'Input Data', 'required': True,
                 'type': TimeSeriesEEG, 'description': 'Time series to display.'},
                {'name': 'data_2', 'label': 'Input Data 2',
                 'type': TimeSeriesEEG, 'description': 'Time series to display.'},
                {'name': 'data_3', 'label': 'Input Data 3',
                 'type': TimeSeriesEEG, 'description': 'Time series to display.'}]


    def get_required_memory_size(self, time_series):
        """
        Return the required memory to run this algorithm.
        """
        return -1


    def compute_parameters(self, input_data, data_2=None, data_3=None, is_preview=False, selected_dimensions=[0, 2]):
        """
        Start the JS visualizer, similar to EEG-lab

        :param input_data: Time series to display
        :type input_data: `TimeSeriesEEG`
        :param data_2: additional input data
        :param data_3: additional input data

        :returns: the needed parameters for a 2D representation
        :rtype: dict

        :raises LaunchException: when at least two input data parameters are provided and they sample periods differ
        """
        #Convert Original ArrayWrappers into a 2D list.
        original_timeseries = [input_data]
        multiple_input = False

        error_sample = "The input TimeSeries have different sample periods. You cannot view them in the same time !"
        if data_2 is not None and data_2.gid != input_data.gid and is_preview is False:
            if data_2.sample_period != input_data.sample_period:
                raise LaunchException(error_sample)
            original_timeseries.append(data_2)
            multiple_input = True

        if (data_3 is not None and data_3.gid != input_data.gid
                and (data_2 is None or data_2.gid != data_3.gid) and is_preview is False):
            if data_3.sample_period != input_data.sample_period:
                raise LaunchException(error_sample)
            original_timeseries.append(data_3)
            multiple_input = True

        self.selected_dimensions = selected_dimensions
        # Compute distance between channels
        step, translations, channels_per_set = self.compute_required_info(original_timeseries)

        base_urls, page_size, total_pages, time_set_urls = self._get_data_set_urls(original_timeseries, is_preview)
        # Hardcoded now 1st dimension is time
        if is_preview is False:
            max_chunck_length = max([timeseries.read_data_shape()[0] for timeseries in original_timeseries])
        else:
            max_chunck_length = min(self.preview_page_size, original_timeseries[0].read_data_shape()[0])
        no_of_channels, labels, total_time_length, graph_labels, modes, state_vars = self._pre_process(
            original_timeseries, multiple_input)
        if is_preview:
            total_time_length = max_chunck_length
        # compute how many elements will be visible on the screen
        points_visible = 500
        points_visible = min([max_chunck_length, points_visible])
        parameters = dict(title=self._get_sub_title(original_timeseries),
                          labelsForCheckBoxes=labels,
                          tsModes=modes,
                          tsStateVars=state_vars,
                          graphLabels=json.dumps(graph_labels),
                          noOfChannels=no_of_channels,
                          translationStep=step,
                          normalizedSteps=json.dumps(translations),
                          nan_value_found=self.has_nan,
                          baseURLS=json.dumps(base_urls),
                          pageSize=page_size,
                          nrOfPages=json.dumps(total_pages),
                          timeSetPaths=json.dumps(time_set_urls),
                          channelsPerSet=json.dumps(channels_per_set),
                          total_length=total_time_length,
                          longestChannelLength=max_chunck_length,
                          number_of_visible_points=points_visible,
                          label_x=self._get_label_x(original_timeseries[0]),
                          extended_view=False,
                          entities=original_timeseries,
                          page_size=min(self.page_size, max_chunck_length))
        return parameters


    def generate_preview(self, input_data, data_2=None, data_3=None, figure_size=None):
        params = self.compute_parameters(input_data, data_2, data_3, is_preview=True)
        pages = dict(channelsPage=None)
        return self.build_display_result("eeg/preview", params, pages)


    def launch(self, input_data, data_2=None, data_3=None):
        """
        Compute visualizer's page
        """
        params = self.compute_parameters(input_data, data_2, data_3)
        pages = dict(controlPage="eeg/controls", channelsPage="commons/channel_selector.html")
        return self.build_display_result("eeg/view", params, pages=pages)


    def _pre_process(self, timeseries_list, multiple_inputs):
        """From input, Compute no of lines and labels."""
        no_of_lines = 0
        labels = {}
        modes = {}
        state_vars = {}
        graph_labels = []
        max_length = 0
        for timeseries in timeseries_list:
            current_length, no_of_lines = self._count_channels(timeseries, no_of_lines, labels, modes, state_vars,
                                                               graph_labels, multiple_inputs)
            if current_length > max_length:
                max_length = current_length
        return no_of_lines, labels, max_length, graph_labels, modes, state_vars


    def _count_channels(self, timeseries, starting_index, labels, modes, state_vars, graph_labels, mult_inp):
        """
        For a input array and the labels dictionary, add new entries starting
         with channels from 'starting index'.
        """
        shape = timeseries.read_data_shape()
        channels = []
        for j in range(shape[self.selected_dimensions[1]]):
            if len(timeseries.sensors.labels) > 0:
                this_label = "[" + str(timeseries.sensors.labels[j]) + "]"
            else:
                this_label = "[channel:" + str(j) + "]"
            if mult_inp:
                this_label = str(timeseries.id) + '.' + this_label
            graph_labels.append(this_label)
            channels.append((this_label, starting_index + j))
        ts_name = timeseries.display_name + " [id:" + str(timeseries.id) + "]"
        labels[ts_name] = channels
        state_vars[ts_name] = timeseries.labels_dimensions.get(timeseries.labels_ordering[1], [])

        modes[ts_name] = range(shape[3])
        return shape[0], starting_index + shape[self.selected_dimensions[1]]


    @staticmethod
    def _replace_nan_values(input_data):
        """ Replace NAN values with a given values"""
        is_any_value_nan = False
        if not numpy.isfinite(input_data).all():
            for idx in xrange(len(input_data)):
                input_data[idx] = numpy.nan_to_num(input_data[idx])
            is_any_value_nan = True
        return is_any_value_nan


    def compute_required_info(self, list_of_timeseries):
        """Compute average difference between Max and Min."""
        step = []
        translations = []
        channels_per_set = []
        for timeseries in list_of_timeseries:
            data_shape = timeseries.read_data_shape()
            resulting_shape = []
            for idx, shape in enumerate(data_shape):
                if idx in self.selected_dimensions:
                    resulting_shape.append(shape)

            page_chunk_data = timeseries.read_data_page(self.current_page * self.page_size,
                                                        (self.current_page + 1) * self.page_size)
            channels_per_set.append(int(resulting_shape[1]))

            for idx in range(resulting_shape[1]):
                self.has_nan = self.has_nan or self._replace_nan_values(page_chunk_data[:, idx])
                array_max = numpy.max(page_chunk_data[:, idx])
                array_min = numpy.min(page_chunk_data[:, idx])
                translations.append((array_max + array_min) / 2)
                if array_max == array_min:
                    array_max += 1
                step.append(abs(array_max - array_min))

        return max(step), translations, channels_per_set


    @staticmethod
    def _get_sub_title(datatype_list):
        """ Compute sub-title for current page"""
        sub_title = ""
        for array_w in datatype_list:
            if len(sub_title.strip()) > 0:
                sub_title = sub_title + "_" + array_w.display_name
            else:
                sub_title = array_w.display_name
        return sub_title


    @staticmethod
    def _get_label_x(original_timeseries):
        """
        Compute the label displayed on the x axis
        """
        return "Time(" + original_timeseries.sample_period_unit + ")"


    def _get_data_set_urls(self, list_of_timeseries, is_preview=False):
        """
        Returns a list of lists. Each list contains the urls to the files
        containing the data for a certain array wrapper.
        """
        base_urls = []
        time_set_urls = []
        total_pages_set = []
        if is_preview is False:
            page_size = self.page_size
            for timeseries in list_of_timeseries:
                overall_shape = timeseries.read_data_shape()
                total_pages = overall_shape[0] / self.page_size
                if overall_shape[0] % self.page_size > 0:
                    total_pages += 1
                timeline_urls = []
                for i in range(total_pages):
                    current_max_size = min((i + 1) * self.page_size, overall_shape[0]) - i * self.page_size
                    params = "current_page=" + str(i) + ";page_size=" + str(self.page_size) + \
                             ";max_size=" + str(current_max_size)
                    timeline_urls.append(self.paths2url(timeseries, 'read_time_page', parameter=params))
                base_urls.append(ABCDisplayer.VISUALIZERS_URL_PREFIX + timeseries.gid)
                time_set_urls.append(timeline_urls)
                total_pages_set.append(total_pages)
        else:
            base_urls.append(ABCDisplayer.VISUALIZERS_URL_PREFIX + list_of_timeseries[0].gid)
            total_pages_set.append(1)
            page_size = self.preview_page_size
            params = "current_page=0;page_size=" + str(self.preview_page_size) + ";max_size=" + \
                     str(min(self.preview_page_size, list_of_timeseries[0].read_data_shape()[0]))
            time_set_urls.append([self.paths2url(list_of_timeseries[0], 'read_time_page', parameter=params)])
        return base_urls, page_size, total_pages_set, time_set_urls

    