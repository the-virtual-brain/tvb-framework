import importlib
import os
import uuid

from tvb.core.entities.file.simulator.h5_factory import config_h5_factory
from tvb.core.neotraits.h5 import H5File
from tvb.interfaces.neocom._h5loader import DirLoader


class SimulatorConfigurationH5(H5File):
    @staticmethod
    def get_full_class_name(class_entity):
        return class_entity.__module__ + '.' + class_entity.__name__

    def store_config_as_reference(self, config):
        gid = uuid.uuid4()

        config_path = DirLoader(os.path.dirname(self.path)).path_for_has_traits(type(config), gid)

        config_h5_class = config_h5_factory(type(config))

        with config_h5_class(config_path) as config_h5:
            config_h5.gid.store(gid)
            config_h5.store(config)
            config_h5.generic_attributes.type = self.get_full_class_name(type(config))

        return gid

    def load_from_reference(self, gid):
        dir_loader = DirLoader(os.path.dirname(self.path))
        config_filename = dir_loader.find_file_name(gid)
        config_path = os.path.join(dir_loader.base_dir, config_filename)

        config_h5 = H5File.from_file(config_path)

        config_type = config_h5.type.load()
        package, cls_name = config_type.rsplit('.', 1)
        module = importlib.import_module(package)
        config_class = getattr(module, cls_name)

        config_instance = config_class()
        config_h5.load_into(config_instance)
        config_h5.close()

        return config_instance
