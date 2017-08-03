import json
import numpy
from tvb.adapters.visualizers.matrix_viewer import MappedArrayVisualizer
from tvb.datatypes.graph import CorrelationCoefficients


class PearsonChord(MappedArrayVisualizer):
    """
    Viewer for Pearson CorrelationCoefficients.
    Very similar to the CrossCorrelationVisualizer - this one done with Matplotlib
    """
    _ui_name = "Pearson Chord View"
    _ui_subsection = "correlation_pearson"

    def get_input_tree(self):
        """ Inform caller of the data we need as input """

        return [{"name": "datatype",
                 "type": CorrelationCoefficients,
                 "label": "Pearson Correlation to be displayed in a hierarchical edge bundle",
                 "required": True}]

    def get_required_memory_size(self, datatype):
        """Return required memory."""

        input_size = datatype.read_data_shape()
        return numpy.prod(input_size) * 8.0

    def launch(self, datatype):
        """Construct data for visualization and launch it."""

        matrix_shape = datatype.array_data.shape[0:2]
        parent_ts = datatype.source
        parent_ts = self.load_entity_by_gid(parent_ts.gid)
        labels = parent_ts.get_space_labels()
        state_list = datatype.source.labels_dimensions.get(datatype.source.labels_ordering[1], [])
        mode_list = range(datatype.source._length_4d)
        if not labels:
            labels = None
        # TODO use default Pearson correlation values (-1, 1) for min and max)
        pars = dict(matrix_labels=json.dumps(labels),
                    matrix_shape=json.dumps(matrix_shape),
                    viewer_title='Pearson Edge Bundle',
                    url_base=MappedArrayVisualizer.paths2url(datatype, "get_correlation_data", flatten="True", parameter=""),
                    state_variable=state_list[0],
                    mode=mode_list[0],
                    state_list=json.dumps(state_list),
                    mode_list=json.dumps(mode_list))

        return self.build_display_result("pearson_edge_bundle/view", pars)