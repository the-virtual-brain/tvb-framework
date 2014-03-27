/**
 * TheVirtualBrain-Framework Package. This package holds all Data Management, and
 * Web-UI helpful to run brain-simulations. To use it, you also need do download
 * TheVirtualBrain-Scientific Package (for simulators). See content of the
 * documentation-folder for more details. See also http://www.thevirtualbrain.org
 *
 * (c) 2012-2013, Baycrest Centre for Geriatric Care ("Baycrest")
 *
 * This program is free software; you can redistribute it and/or modify it under
 * the terms of the GNU General Public License version 2 as published by the Free
 * Software Foundation. This program is distributed in the hope that it will be
 * useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
 * License for more details. You should have received a copy of the GNU General
 * Public License along with this program; if not, you can download it here
 * http://www.gnu.org/licenses/old-licenses/gpl-2.0
 *
 **/

var TS_SVG_selectedChannels = [];
// Store a list with all the channel labels so one can easily refresh between them on channel refresh
var allChannelLabels = [];

var MAX_INITIAL_CHANNELS = 20;

var tsView;

/**
 * Initializes selected channels
 * initializes global TS_SVG_selectedChannels
 */
function _initSelection(filterGid){
    // initialize selection component
    var regionSelector = TVBUI.regionSelector("#channelSelector", {filterGid: filterGid});
    var initialSelection = regionSelector.val()

    // If there is no selection take the first 20 channels or all
    if (initialSelection.length == 0){
        for(var i = 0; i < Math.min(MAX_INITIAL_CHANNELS, allChannelLabels.length); i++){
            TS_SVG_selectedChannels.push(i);
        }
        regionSelector.val(TS_SVG_selectedChannels);
    }else if (initialSelection.length > MAX_INITIAL_CHANNELS){
    // Take a default of maximum 20 channels at start to be displayed
        TS_SVG_selectedChannels = initialSelection.slice(0, MAX_INITIAL_CHANNELS);
        regionSelector.val(TS_SVG_selectedChannels);
    }else{
        // to not invoke val to keep the named selection in the dropdown
        TS_SVG_selectedChannels = initialSelection;
    }
    // we bind the event here after the previous val calls
    // do not want those to trigger the change event as tsView is not initialized yet
    regionSelector.change(function(value){
        TS_SVG_selectedChannels = [];
        for(var i=0; i < value.length; i++){
            TS_SVG_selectedChannels.push(parseInt(value[i], 10));
        }
        refreshChannels();
    });

    // compute labels for initial selection
    var selectedLabels = [];
    for(i = 0; i < TS_SVG_selectedChannels.length; i++){
        selectedLabels.push(allChannelLabels[TS_SVG_selectedChannels[i]]);
    }

    return selectedLabels;
}

/*
 * Do any required initializations in order to start the viewer.
 *
 * @param baseURL: the base URL from tvb in order to call datatype methods
 * @param isPreview: boolean that tell if we are in burst page preview mode or full viewer
 * @param dataShape: the shape of the input timeseries
 * @param t0: starting time
 * @param dt: time increment
 * @param channelLabels: a list with the labels for all the channels
 */
function initTimeseriesViewer(baseURL, isPreview, dataShape, t0, dt, channelLabels, filterGid) {

    // Store the list with all the labels since we need it on channel selection refresh
    allChannelLabels = channelLabels;

    // setup dimensions, div, svg elements and plotter
    var ts = tv.plot.time_series();

    var selectedLabels = _initSelection(filterGid);

    dataShape = $.parseJSON(dataShape);
    dataShape[2] = TS_SVG_selectedChannels.length;

    // configure data
    var displayElem = $('#time-series-viewer');
    ts.w(displayElem.width()).h(displayElem.height()).baseURL(baseURL).preview(isPreview).mode(0).state_var(0);
    ts.shape(dataShape).t0(t0).dt(dt);
    ts.labels(selectedLabels);
    ts.channels(TS_SVG_selectedChannels);
    // run
    ts(d3.select("#time-series-viewer"));
    tsView = ts;
}

/*
 * Get required data for the channels in TS_SVG_selectedChannels. If none
 * exist then just use the previous 'displayedChannels' (or default in case of first run).
 */
function refreshChannels() {

    var selectedLabels = [];
    var shape = tsView.shape();

    if (TS_SVG_selectedChannels.length == 0) {
        selectedLabels = allChannelLabels;
        shape[2] = allChannelLabels.length;
    } else {
        for (var i = 0; i < TS_SVG_selectedChannels.length; i++) {
            selectedLabels.push(allChannelLabels[TS_SVG_selectedChannels[i]]);
        }
        shape[2] = TS_SVG_selectedChannels.length
    }

    var new_ts = tv.plot.time_series();

    // configure data
    var displayElem = $('#time-series-viewer');
    new_ts.w(displayElem.width()).h(displayElem.height()).baseURL(tsView.baseURL()).preview(tsView.preview()).mode(tsView.mode()).state_var(tsView.state_var());
    new_ts.shape(shape).t0(tsView.t0()).dt(tsView.dt());
    new_ts.labels(selectedLabels);
    new_ts.channels(TS_SVG_selectedChannels);

    displayElem.empty();
    new_ts(d3.select("#time-series-viewer"));
    tsView = new_ts;
}

function changeMode() {
    tsView.mode($('#mode-select').val());
    refreshChannels();
}

function changeStateVar() {
    tsView.state_var($('#state-var-select').val());
    refreshChannels();
}
