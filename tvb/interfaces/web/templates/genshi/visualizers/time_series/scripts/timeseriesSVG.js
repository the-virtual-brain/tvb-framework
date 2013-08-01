var TS_SVG_selectedChannels = [];
// Store a list with all the channel labels so one can easily refresh between them on channel refresh
var allChannelLabels = [];

var tsView;

function initTimeseriesViewer(baseURL, isPreview, dataShape, t0, dt, channelLabels) {
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
    // Store the list with all the labels since we need it on channel selection refresh
    allChannelLabels = channelLabels;

    // setup dimensions, div, svg elements and plotter
    ts = tv.plot.time_series();

    // configure data
    ts.w($('#time-series-viewer').width()).h($('#time-series-viewer').height()).baseURL(baseURL).preview(isPreview).mode(0).state_var(0);

    ts.shape($.parseJSON(dataShape)).t0(t0).dt(dt);

    // using single quotes because labels is list like ["a", "b", ...]
    ts.labels(allChannelLabels);

    // passing empty list of channels will return data for all the channels
    ts.channels([]);
    // run
    ts(d3.select("#time-series-viewer"));
    tsView = ts;
}

function refreshChannels() {
    /*
     * Get required data for the channels in TS_SVG_selectedChannels. If none
     * exist then just use the previous 'displayedChannels' (or default in case of first run).
     */
    var selectedLabels = [];
    var shape = ts.shape();

    if (TS_SVG_selectedChannels.length == 0) {
        selectedLabels = allChannelLabels;
        shape[2] = allChannelLabels.length;
    } else {
        for (var i = 0; i < TS_SVG_selectedChannels.length; i++) {
            selectedLabels.push(allChannelLabels[TS_SVG_selectedChannels[i]]);
        }

        shape[2] = TS_SVG_selectedChannels.length
    }

    new_ts = tv.plot.time_series()

    // configure data
    new_ts.w($('#time-series-viewer').width()).h($('#time-series-viewer').height()).baseURL(ts.baseURL()).preview(ts.preview()).mode(ts.mode()).state_var(ts.state_var())

    new_ts.shape(shape).t0(ts.t0()).dt(ts.dt())

    // using single quotes because labels is list like ["a", "b", ...]
    new_ts.labels(selectedLabels)

    new_ts.channels(TS_SVG_selectedChannels)

    // run
    $('#time-series-viewer').empty()
    new_ts(d3.select("#time-series-viewer"))
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
