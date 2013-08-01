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
#   Frontiers in Neuroinformatics (in press)
#
#

"""
This module implements a class for executing arbitray MATLAB code

Conversion between Python types and MATLAB types is handled and dependent
on scipy.io's loadmat and savemat function.

.. moduleauthor:: Marmaduke Woodman <Marmaduke@tvb.invalid>
.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>
"""

import os
import time
import random
import tempfile
from scipy.io import loadmat, savemat
from tvb.basic.config.settings import TVBSettings as cfg
from tvb.core.utils import MATLAB, OCTAVE, matlab_cmd
from tvb.core.adapters.abcadapter import ABCAsynchronous



class MatlabAnalyzer(ABCAsynchronous):
    """
    MatlabAnalyzer is an adapter for calling arbitrary MATLAB code with
    arbitrary data.

    Specific analyzers should derive from this class and implement the
    interface and launch methods inherited from Asynchronous Adapter.
    """

    matlab_paths = []


    def __init__(self):
        ABCAsynchronous.__init__(self)
        self.mlab_exe = cfg.MATLAB_EXECUTABLE
        self.hex = hex(random.randint(0, 2 ** 32))
        self.script_name = "script%s" % self.hex
        self.script_fname = self.script_name + '.m'
        self.wkspc_name = "wkspc%s" % self.hex
        self.wkspc_fname = self.wkspc_name + '.mat'
        self.done_name = "done%s" % self.hex
        self.done_fname = self.done_name + '.mat'
        self.log_fname = "log%s" % self.hex


    def _matlab_pre(self):
        """
        Called to obtain the pre operation code for MATLAB. Current, we
        1. add paths to the MATLAB path
        2. enter a try clause
        """
        paths = "".join(["addpath('" + p + "');\n" for p in self.matlab_paths])
        return paths + "\ntry\n"


    def _matlab_post(self):
        """
        Called to obtain the post operation code for MATLAB. Currently, we
        1. catch exception if one was raised
        2. set the hexstamp variable in MATLAB
        3. save all working files
        """
        catch = "\ncatch e\nexception%s = e\nend\n" % self.hex
        save_clause = ""
        if MATLAB in self.mlab_exe:
            save_clause = "hexstamp = '%s'\nsave %s -V7\nsave %s -V7 hexstamp\nquit"
        if OCTAVE in self.mlab_exe:
            save_clause = "hexstamp = '%s'\nsave %s.mat -V7\nsave %s.mat -V7 hexstamp\nquit"
        return catch + save_clause % (self.hex, self.wkspc_name, self.done_name)


    def launch(self, code, data=None, wd=None, cleanup=True):
        """
        Analyzers that derive from this adapter and use MATLAB should
        override this method.
        """
        return self.matlab(code, data, cleanup)


    def cleanup(self):
        """
        Make sure Matlab is closed after execution.
        """
        time.sleep(0.5)  # wait for MATLAB to close
        for file_ref in [self.script_fname, self.wkspc_fname,
                         self.done_fname, self.log_fname]:
            try:
                os.remove(file_ref)
            except Exception:
                pass


    def add_to_path(self, path_to_add):
        """
        Add a path to the list of paths that will be added to the path
        in the MATLAB session
        """
        self.matlab_paths.append(path_to_add)


    def matlab(self, code, data=None, work_dir=None, cleanup=True):
        """
        method matlab takes as arguments:

            code: MATLAB code in a string
            data: a dict of data that scipy.io.savemat knows how to deal with
            work_dir: working directory to be used by MATLAB
            cleanup: set to False to keep files

        and returns a tuple:

            [0] string of code exec'd by MATLAB
            [1] string of log produced by MATLAB
            [2] dict of data from MATLAB's workspace
        """
        wdir = tempfile.tempdir or os.getcwd()
        os.chdir(wdir)
        os.chdir(work_dir or os.getcwd())

        pre, post = self._matlab_pre(), self._matlab_post()
        code = ("\nsuccess%s = 0\n" + code + "\nsuccess%s = 1\n") % (self.hex, self.hex)

        if data:
            pre += "\nload %s\n" % self.wkspc_name
            savemat(self.wkspc_fname, data, format="5")
        with open(self.script_fname, 'w') as file_data:
            file_data.write(pre + code + post)

        os.system(matlab_cmd(self.mlab_exe, self.script_name, self.log_fname))
        while not os.path.exists(self.done_fname):
            time.sleep(0.1)

        with open(self.log_fname, 'r') as file_data:
            logtext = file_data.read()
        retdata = loadmat(self.wkspc_fname, squeeze_me=True)

        if cleanup:
            self.cleanup()
        return pre + code + post, logtext, retdata


    @classmethod
    def scrape_mfile(filename):
        """
        MatlabAnalyzer.scrape_mfile takes an absolute filename (i.e. 
        no expansion is done), analyzes the file and returns a dictionary
        of information about the corresponding MATLAB function: 

            ret{'docs' : docstring of the MATLAB function 

                'args' : list of argument names to the MATLAB function or 
                         None if the function takes no arguments

                'rets' : list of function's results' names or None if the 
                         function produces no results
        """

        # helper functions to clean strings
        re_keep = lambda m, r: m.group()[:re.match(r, m.group()).end()]
        re_del = lambda m, r: m.group()[re.match(r, m.group()).end():]

        with open(filename) as fd:
            src = fd.read()

        # grab the docstring first
        docs = re.search('(^%.*\n)+', src, re.MULTILINE).group()

        # grab the function signature
        sig = re.match('.*function.*', src)

        # if we don't have one return None
        if not sig:
            return None

        # get the text
        sig = sig.group()

        # remove 'function' from string
        fn = re.match('\s*function\s*', src)
        sig1 = sig[fn.end():]

        # get outputs, either 'A=foo' or '[A,B] = foo'
        lhs = re.match('\w+\s*=|\[.+\]\s*=', sig1)
        outs = re_keep(lhs, '\w+|\[.+\]')[1:-1].split() if lhs else None
        sig2 = sig1[lhs.end():]

        # get function name
        rhs = re.match('\s*\w+', sig2)
        fname = re_del(rhs, '\s*')
        sig3 = sig2[rhs.end():]

        # get arguments if they exist
        rhs = re.match('.*\(.+\)', sig3)
        ins = rhs.group()[1:-1].split(',') if rhs else None

        return {'args': ins, 'rets': outs, 'docs': docs}



   
