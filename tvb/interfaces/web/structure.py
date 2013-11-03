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
.. moduleauthor:: lia.domide <lia.domide@codemart.ro>
"""



class WebStructure(object):

    ### TVB sections. Will appear as footer entries.
    SECTION_USER = "user"
    SECTION_PROJECT = "project"
    SECTION_BURST = "burst"
    SECTION_ANALYZE = "analyze"
    SECTION_STIMULUS = "stimulus"
    SECTION_CONNECTIVITY = "connectivity"

    ### Subsections for USER section
    SUB_SECTION_LOGIN = "login"
    SUB_SECTION_ACCOUNT = "account"

    ### Subsections for PROJECT section.
    SUB_SECTION_PROJECT_MENU = "project"
    SUB_SECTION_OPERATIONS = "operations"
    SUB_SECTION_DATA_STRUCTURE = "data"
    SUB_SECTION_LIST_PROJECTS = "list"
    SUB_SECTION_PROPERTIES_PROJECT = "properties"
    SUB_SECTION_FIGURES = "figures"
    SUB_SECTION_PIPELINE = "pipeline"

    ### Subsections for BURST section.
    SUB_SECTION_BURST = "burst"
    SUB_SECTION_MODEL_REGIONS = "regionmodel"
    SUB_SECTION_MODEL_SURFACE = "surfacemodel"
    SUB_SECTION_NOISE_CONFIGURATION = "noiseconfig"

    ### Subsections for ANALYZE section.
    ### These subsections can extends, and depend on existing analyzers in the system.
    SUB_SECTION_ANALYZE_MENU = "analyze"
    SUB_SECTION_ANALYZE_1 = "crosscorr"
    SUB_SECTION_ANALYZE_2 = "ccpearson"
    SUB_SECTION_ANALYZE_3 = "coherence"
    SUB_SECTION_ANALYZE_4 = "complexcoherence"
    SUB_SECTION_ANALYZE_5 = "covariance"
    SUB_SECTION_ANALYZE_6 = "components"
    SUB_SECTION_ANALYZE_7 = "fourier"
    SUB_SECTION_ANALYZE_8 = "ica"
    SUB_SECTION_ANALYZE_9 = "timeseries"
    SUB_SECTION_ANALYZE_10 = "wavelet"
    SUB_SECTION_ANALYZE_11 = "bct"
    SUB_SECTION_ANALYZE_12 = "bctcentrality"
    SUB_SECTION_ANALYZE_13 = "bctclustering"
    SUB_SECTION_ANALYZE_14 = "bctdegree"
    SUB_SECTION_ANALYZE_15 = "bctdensity"
    SUB_SECTION_ANALYZE_16 = "bctdistance"

    ### Subsections for STIMULUS section.
    SUB_SECTION_STIMULUS_MENU = "stimulus"
    SUB_SECTION_STIMULUS_SURFACE = "regionstim"
    SUB_SECTION_STIMULUS_REGION = "surfacestim"

    ### Subsections for CONNECTIVITY section
    SUB_SECTION_CONNECTIVITY_MENU = "step"
    SUB_SECTION_CONNECTIVITY = "connectivity"
    SUB_SECTION_LOCAL_CONNECTIVITY = "local"

    ### Subsections used under BURST and PROJECT sections.
    ### These subsections can extend, and depend on existing visualizers in the system.
    SUB_SECTION_VIEW_0 = "view_connectivity"
    SUB_SECTION_VIEW_1 = "view_brain"
    SUB_SECTION_VIEW_2 = "view_brain_eeg"
    SUB_SECTION_VIEW_3 = "view_brain_seeg"
    SUB_SECTION_VIEW_4 = "view_covariance"
    SUB_SECTION_VIEW_5 = "view_coherence"
    SUB_SECTION_VIEW_6 = "view_complex_coherence"
    SUB_SECTION_VIEW_7 = "view_correlation"
    SUB_SECTION_VIEW_8 = "view_correlation_pearson"
    SUB_SECTION_VIEW_9 = "view_eeg"
    SUB_SECTION_VIEW_10 = "view_fourier"
    SUB_SECTION_VIEW_11 = "view_histogram"
    SUB_SECTION_VIEW_12 = "view_ica"
    SUB_SECTION_VIEW_13 = "view_pca"
    SUB_SECTION_VIEW_14 = "view_pse"
    SUB_SECTION_VIEW_15 = "view_pse_iso"
    SUB_SECTION_VIEW_16 = "view_timeseries"
    SUB_SECTION_VIEW_17 = "view_topography"
    SUB_SECTION_VIEW_18 = "view_wavelet"


    ### Texts to appear in HTML page headers as section-title.
    WEB_SECTION_TITLES = {

        SECTION_USER: "User",
        SECTION_PROJECT: "Project",
        SECTION_BURST: "Simulator",
        SECTION_ANALYZE: "Analyze",
        SECTION_STIMULUS: "Stimulus",
        SECTION_CONNECTIVITY: 'Connectivity'}


    ### Texts to appear in HTML page headers as subsection-title.
    ### Attribute _ui_name in visualizer will be used as page-subtitle.
    WEB_SUBSECTION_TITLES = {

        SUB_SECTION_LOGIN: "Login",
        SUB_SECTION_ACCOUNT: "Register",

        SUB_SECTION_PROJECT_MENU: "",
        SUB_SECTION_OPERATIONS: "Operations",
        SUB_SECTION_DATA_STRUCTURE: "Data Structure",
        SUB_SECTION_LIST_PROJECTS: "List",
        SUB_SECTION_PROPERTIES_PROJECT: "Properties",
        SUB_SECTION_FIGURES: "Image Archive",
        SUB_SECTION_PIPELINE: "DTI Pipeline",

        SUB_SECTION_BURST: "",
        SUB_SECTION_MODEL_REGIONS: "Region Model Parameters",
        SUB_SECTION_MODEL_SURFACE: "Surface Model Parameters",
        SUB_SECTION_NOISE_CONFIGURATION: "Noise dispersion configuration",

        SUB_SECTION_ANALYZE_MENU: "",
        SUB_SECTION_ANALYZE_1: "Cross Correlation",
        SUB_SECTION_ANALYZE_2: "Correlation Coefficients",
        SUB_SECTION_ANALYZE_3: "Coherence",
        SUB_SECTION_ANALYZE_4: "Complex Coherence",
        SUB_SECTION_ANALYZE_5: "Covariance",
        SUB_SECTION_ANALYZE_6: "Principal Components",
        SUB_SECTION_ANALYZE_7: "Fourier",
        SUB_SECTION_ANALYZE_8: "ICA",
        SUB_SECTION_ANALYZE_9: "TimeSeries",
        SUB_SECTION_ANALYZE_10: "Wavelet",
        SUB_SECTION_ANALYZE_11: "BCT",
        SUB_SECTION_ANALYZE_12: "BCT Centrality",
        SUB_SECTION_ANALYZE_13: "BCT Clustering",
        SUB_SECTION_ANALYZE_14: "BCT Degree",
        SUB_SECTION_ANALYZE_15: "BCT Density",
        SUB_SECTION_ANALYZE_16: "BCT Distance",

        SUB_SECTION_STIMULUS_MENU: "",
        SUB_SECTION_STIMULUS_SURFACE: "Region",
        SUB_SECTION_STIMULUS_REGION: "Surface",

        SUB_SECTION_CONNECTIVITY_MENU: "",
        SUB_SECTION_CONNECTIVITY: "Large Scale",
        SUB_SECTION_LOCAL_CONNECTIVITY: "Local",

        SUB_SECTION_VIEW_0: "Connectivity Viewer",
        SUB_SECTION_VIEW_1: "Brain Viewer",
        SUB_SECTION_VIEW_2: "EEG Viewer",
        SUB_SECTION_VIEW_3: "SEEG Viewer",
        SUB_SECTION_VIEW_4: "Covariance Viewer",
        SUB_SECTION_VIEW_5: "Coherence Viewer",
        SUB_SECTION_VIEW_6: "Complex Coherence Viewer",
        SUB_SECTION_VIEW_7: "Cross Correlation Viewer",
        SUB_SECTION_VIEW_8: "Pearson Correlation Coefficients Viewer",
        SUB_SECTION_VIEW_9: "EEG Viewer",
        SUB_SECTION_VIEW_10: "Fourier Viewer",
        SUB_SECTION_VIEW_11: "Histogram Viewer",
        SUB_SECTION_VIEW_12: "ICA Viewer",
        SUB_SECTION_VIEW_13: "PCA Viewer",
        SUB_SECTION_VIEW_14: "Discrete PSE Viewer",
        SUB_SECTION_VIEW_15: "Isocline PSE Viewer",
        SUB_SECTION_VIEW_16: "TimeSeries Viewer",
        SUB_SECTION_VIEW_17: "Topography Viewer",
        SUB_SECTION_VIEW_18: "Wavelet Viewer"
    }


    ### ID of the HTML generated paragraph, to jump to it directly, in the online help overlay.
    VISUALIZERS_ONLINE_HELP_SHORTCUTS = {

        ## Connectivity subsection link will not be needed, as we will have a full section in the help for this.
        ## SUB_SECTION_VIEW_0: "connectivity-visualizer**",
        SUB_SECTION_VIEW_1: "brain-activity-visualizer",
        SUB_SECTION_VIEW_2: "dual-brain-eeg-visualizer",
        SUB_SECTION_VIEW_3: "dual-brain-seeg-visualizer",
        SUB_SECTION_VIEW_4: "covariance-visualizer",
        SUB_SECTION_VIEW_5: "cross-coherence-visualizer",
        SUB_SECTION_VIEW_6: "complex-coherence-visualizer",
        SUB_SECTION_VIEW_7: "cross-correlation-visualizer",
        SUB_SECTION_VIEW_8: "pearson-coefficients-visualizer",
        SUB_SECTION_VIEW_9: "eeg-time-series-visualizer",
        SUB_SECTION_VIEW_10: "fourier-spectrum-visualizer",
        SUB_SECTION_VIEW_11: "connectivity-measure-visualizer",
        SUB_SECTION_VIEW_12: "independent-component-visualizer",
        SUB_SECTION_VIEW_13: "principal-component-visualizer",
        SUB_SECTION_VIEW_14: "discrete-pse-visualizer",
        SUB_SECTION_VIEW_15: "isocline-pse-visualizer",
        SUB_SECTION_VIEW_16: "time-series-visualizer-svg-d3",
        SUB_SECTION_VIEW_17: "topographic-visualizer",
        SUB_SECTION_VIEW_18: "wavelet-spectrogram-visualizer"
    }


    ### ID of the HTML generated paragraph, to jump to it directly, in the online help overlay.
    ANALYZERS_ONLINE_HELP_SHORTCUTS = {

        SUB_SECTION_ANALYZE_1: "cross-correlation-of-nodes",
        SUB_SECTION_ANALYZE_2: "pearson-correlation-coefficient",
        SUB_SECTION_ANALYZE_3: "cross-coherence-of-nodes",
        SUB_SECTION_ANALYZE_4: "complex-coherence-of-nodes",
        SUB_SECTION_ANALYZE_5: "temporal-covariance-of-nodes",
        SUB_SECTION_ANALYZE_6: "principal-component-analysis-pca",
        SUB_SECTION_ANALYZE_7: "fourier-spectral-analysis",
        SUB_SECTION_ANALYZE_8: "independent-component-analysis-ica",
        SUB_SECTION_ANALYZE_9: "timeseries-metrics",
        SUB_SECTION_ANALYZE_10: "continuous-wavelet-transform-cwt",
        SUB_SECTION_ANALYZE_11: "brain-connectivity-toolbox-analyzers",
        SUB_SECTION_ANALYZE_12: "brain-connectivity-toolbox-analyzers",
        SUB_SECTION_ANALYZE_13: "brain-connectivity-toolbox-analyzers",
        SUB_SECTION_ANALYZE_14: "brain-connectivity-toolbox-analyzers",
        SUB_SECTION_ANALYZE_15: "brain-connectivity-toolbox-analyzers",
        SUB_SECTION_ANALYZE_16: "brain-connectivity-toolbox-analyzers",
    }
    
    
    
