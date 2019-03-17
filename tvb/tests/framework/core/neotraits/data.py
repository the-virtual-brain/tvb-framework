from tvb.basic.neotraits._attr import Dim
from tvb.basic.neotraits.api import HasTraits, Attr, NArray, Int, trait_property, cached_trait_property
from tvb.basic.neotraits.ex import TraitValueError



class BazDataType(HasTraits):
    miu = NArray()
    scalar_str = Attr(str, required=False)


class FooDatatype(HasTraits):
    array_float = NArray()
    array_int = NArray(dtype=int, shape=(Dim.any, Dim.any))
    scalar_int = Attr(int)
    abaz = Attr(field_type=BazDataType)
    some_transient = NArray(shape=(Dim.any, Dim.any, Dim.any ), required=False)


class BarDatatype(FooDatatype):
    array_str = NArray(dtype='S32', shape=(Dim.any,))


class PropsDataType(HasTraits):
    n_node = Int()

    def __init__(self, **kwargs):
        super(PropsDataType, self).__init__(**kwargs)
        self._weights = None

    @trait_property(NArray(shape=(Dim.any, Dim.any)))
    def weights(self):
        return self._weights

    @weights.setter
    def weights(self, val):
        if val.shape != (self.n_node, self.n_node):
            raise TraitValueError
        self._weights = val

    @trait_property(Attr(bool))
    def is_directed(self):
        isit = (self.weights == self.weights.T).all()
        # The strict typing is fighting against python conventions
        # numpy.bool_ is not bool ...
        return bool(isit)

    @cached_trait_property(NArray())
    def once(self):
        return self.weights * 22.44


