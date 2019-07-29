from tvb.datatypes.graph import Covariance, CorrelationCoefficients, ConnectivityMeasure

from tvb.core.entities.file.datatypes.spectral_h5 import DataTypeMatrixH5
from tvb.core.neotraits.h5 import DataSet, Reference, Json


class CovarianceH5(DataTypeMatrixH5):

    def __init__(self, path):
        super(CovarianceH5, self).__init__(path)
        self.array_data = DataSet(Covariance.array_data, self, expand_dimension=2)
        self.source = Reference(Covariance.source, self)

    def write_data_slice(self, partial_result):
        """
        Append chunk.
        """
        self.array_data.append(partial_result, close_file=False)


class CorrelationCoefficientsH5(DataTypeMatrixH5):

    def __init__(self, path):
        super(CorrelationCoefficientsH5, self).__init__(path)
        self.array_data = DataSet(CorrelationCoefficients.array_data, self)
        self.source = Reference(CorrelationCoefficients.source, self)
        self.labels_ordering = Json(CorrelationCoefficients.labels_ordering, self)

    def get_correlation_data(self, selected_state, selected_mode):
        matrix_to_display = self.array_data[:, :, int(selected_state)-1, int(selected_mode)]
        return list(matrix_to_display.flat)


class ConnectivityMeasureH5(DataTypeMatrixH5):

    def __init__(self, path):
        super(ConnectivityMeasureH5, self).__init__(path)
        self.array_data = DataSet(ConnectivityMeasure.array_data, self)
        self.connectivity = Reference(ConnectivityMeasure.connectivity, self)

    def get_array_data(self):
        return self.array_data[:]