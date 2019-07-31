/**
 * TheVirtualBrain-Framework Package. This package holds all Data Management, and
 * Web-UI helpful to run brain-simulations. To use it, you also need do download
 * TheVirtualBrain-Scientific Package (for simulators). See content of the
 * documentation-folder for more details. See also http://www.thevirtualbrain.org
 *
 * (c) 2012-2017, Baycrest Centre for Geriatric Care ("Baycrest") and others
 *
 * This program is free software: you can redistribute it and/or modify it under the
 * terms of the GNU General Public License as published by the Free Software Foundation,
 * either version 3 of the License, or (at your option) any later version.
 * This program is distributed in the hope that it will be useful, but WITHOUT ANY
 * WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
 * PARTICULAR PURPOSE.  See the GNU General Public License for more details.
 * You should have received a copy of the GNU General Public License along with this
 * program.  If not, see <http://www.gnu.org/licenses/>.
 *
 **/

/* globals doAjaxCall, readDataPageURL, HLPR_readJSONfromFile */

// //it contains all the points that have to be/have been displayed (it contains all the points from the read file);
// //it is an array of arrays (each array contains the points for a certain line chart)
var AG_allPoints = [];
// it supplies the labels for x axis (time in milliseconds)
var AG_time = [];
//it is used for clearing timing events (the event that calls the drawGraph method after a specified time-interval)
var t = null;
//how many elements will be visible on the screen
//computed on the server
var AG_numberOfVisiblePoints = 0;
//all the points that are visible on the screen at a certain moment; the points are read from the <code>AG_allPoints</code> array
//and are translated with a value equal to [AG_translationStep * (AG_noOfLines - the index of the current line)]
//THE FORM of this matrix is: [ [[t1, a1], [t2, a2], ...], [[t1, b1], [t2, b2], ...], ..., [[t1, n1], [t2, n2], ...]]
// t1, t2, ... - represents time that is visible on the screen at a certain moment;
// a1, a2,... - represents the translated values
var AG_displayedPoints = [];
//All the times values that are displayed at a certain moment. To be used by the vertical time line.
var AG_displayedTimes = [];
//the last element that was displayed on the screen is located at this index; the index refers to <code>AG_allPoints</code> array
var AG_currentIndex = 0;
//this var should be set to the length of the <code>AG_allPoints</code> array
var AG_noOfLines = 0;
// the step used for translating the drawn line charts; we translate the drawn line charts because we don't want them to overlap
// the lines will be translated with <code>AG_translationStep * AG_computedStep</code>
var AG_translationStep = 1;
// a scaling factor for the displayed signal
var AG_scaling = 1;
// this var is computed on the server. It is used for line translation (<code>AG_translationStep * AG_computedStep</code>).
var AG_computedStep = 50;
//The normalization steps for each of the channels, in order to bring them centered near the channel bar
var AG_normalizationSteps = [];
//If the animation is paused using pause/start button
var AG_isStopped = true;
//If animation speed is set at a 0 value
var AG_isSpeedZero = false;
//the number of points that are shifted/unshift at a moment
var noOfShiftedPoints = 1;
// List of channels that will be submited on a change of the displayed channels
var AG_submitableSelectedChannels = [];
// contains the indexes of the channels that are displayed
var displayedChannels = [];
// a list of urls pointing to the files from where we should read the time
var timeSetUrls = [];
//a list containing the number of channel in each file specified in 'dataSetUrls' fields
var noOfChannelsPerSet = [];
// the number of points from the longest channel
var maxChannelLength = 0;
// the maximum number of data files from all the submited datatypes
var maxDataFileIndex = 0;
// represents the file index from the dataset that is displayed in the chart
var currentDataFileIndex = 0;
// contains the parsed data for the next file from the dataset
var nextData = [];
// contains the time for the next file from the dataset
var nextTimeData = [];
// <code>true</code> only if the next file from dataset was loaded into memory
var isNextDataLoaded = false;
// <code>true</code> only if the next time data was loaded into memory
var isNextTimeDataLoaded = false;
// <code>true</code> only if the the process of loading a file is started
var AG_isLoadStarted = false;
// this is the number of steps left before updating the next file
var threshold = 10;
// the amount of data that has passed
var totalPassedData = 0;
// the number of channels
var totalNumberOfChannels = 0;
// <code>true</code> only if any of the displayed channels contains NaN values
var nanValueFound = false;
//Channel prefix for each array of data
var channelPrefix = "Channel: ";
//
var totalTimeLength = 0;
//Default values for the x and y axis of the plot
//NOTE: do not remove from the axis AG_options 'labelWidth' and 'labelHeight' because
//this will slow down the animation
var lbl_x_width = 100;
var lbl_x_height = 30;
var zoom_range = [0.1, 20];


// the index of the cached file (the file that was loaded asynchronous)
var cachedFileIndex = 0;
//The displayed labels for the graph
var chanDisplayLabels = [];
// setup plot
var AG_options = {
    grid: {
        backgroundColor: 'white',
        hoverable: true,
        clickable: true
    },
    points: {
        show: false,
        radius: 0.001
    },
    zoom: {
        interactive: false
    },
    selection: {
        mode: "xy"
    },
    legend: {
        show: false
    }
};

var DEFAULT_MAX_CHANNELS = 10;
var plot = null;

var followingLine = [];
//The required position from which the following vertical time line will start moving with the array
//Expressed as a number from [0, 1], 0 - start from begining, 1 start only at end
var procentualLinePosition = 0.5;
//The actual position in the graph of the following vertical line. Start from -speed to account for the initial translation.
var currentLinePosition = 0;
//The number of points used to display the vertical line.
var numberOfPointsForVerticalLine = 1000;
var isDoubleView = false;

var AG_homeViewYValues = [];
var AG_homeViewXValues = {zoomRange: zoom_range, labelWidth: lbl_x_width, labelHeight: lbl_x_height};
//This will be set to true in the launch_viewer method called by burst small previews
var isSmallPreview = false;

var targetVerticalLinePosition;

// The base url for calling any methods on a given datatype
var baseDataURLS = [];
var nrOfPagesSet = [];
var dataPageSize = [];
var tsModes = [0, 0, 0];
var tsStates = [0, 0, 0];
var longestChannelIndex = 0;

// region selection component
var AG_regionSelector = null;
// State mode selector. Used as a global only in dual view
var AG_modeSelector = null;


// GID for the D3 viewer
var filterGid = null;

//timeseries viewer
var ts = null;

window.onresize = function () {
    resizeToFillParent();
};

/**
 * Animated graph entry point
 */
function AG_startAnimatedChart(ag_settings) {
    isSmallPreview = false;
    _AG_initGlobals(ag_settings);
    _AG_initPaginationState(ag_settings.number_of_visible_points);
    _AG_preStart();
    drawSliderForAnimationSpeed();
    _AG_init_selection(ag_settings.measurePointsSelectionGIDs);


}

function AG_startAnimatedChartPreview(ag_settings) {
    isSmallPreview = true;
    AG_isStopped = true;
    _AG_initGlobals(ag_settings);
    _AG_initPaginationState(ag_settings.number_of_visible_points);
    _AG_preStart();

    // Initialize AG_submitableSelectedChannels
    // warning: Assumes channel values are a range
    if (AG_submitableSelectedChannels.length === 0) {
        // Viewer breaks if this is empty. Fill the first few channels
        const defaultSelectionLength = Math.min(totalNumberOfChannels, DEFAULT_MAX_CHANNELS);
        for (let i = 0; i < defaultSelectionLength; i++) {
            AG_submitableSelectedChannels.push(i);
        }
    }

    refreshChannels();
}

function AG_rePaginate(number_of_visible_points) {
    _AG_initPaginationState(number_of_visible_points);
    $('#display-page-size').html('' + number_of_visible_points);
    refreshChannels();
    if (isDoubleView) {
        initActivityData();
    }
}

/**
 * Initialize global state. Part of the AG startup.
 * @private
 */
function _AG_initGlobals(ag_settings) {
    isDoubleView = ag_settings.extended_view;
    // dataSetUrls = $.parseJSON(dataSetPaths);
    baseDataURLS = ag_settings.baseURLS;
    nrOfPagesSet = ag_settings.nrOfPages;
    dataPageSize = ag_settings.pageSize;
    chanDisplayLabels = ag_settings.channelLabels;
    noOfChannelsPerSet = ag_settings.channelsPerSet;
    timeSetUrls = ag_settings.timeSetPaths;
    maxChannelLength = parseInt(ag_settings.pageSize);
    AG_normalizationSteps = ag_settings.normalizedSteps;
    setMaxDataFileIndex(nrOfPagesSet);
    totalNumberOfChannels = ag_settings.noOfChannels;
    totalTimeLength = ag_settings.totalLength;
    nanValueFound = ag_settings.nan_value_found;
    AG_computedStep = ag_settings.translationStep;

}

/**
 * Initialize pagination. Part of AG startup.
 * @private
 */
function _AG_initPaginationState(number_of_visible_points) {
    AG_numberOfVisiblePoints = parseInt(number_of_visible_points);
    if (AG_numberOfVisiblePoints > maxChannelLength) {
        AG_numberOfVisiblePoints = maxChannelLength;
    }
    targetVerticalLinePosition = AG_numberOfVisiblePoints * procentualLinePosition;
}

/**
 * Misc common startup logic. Part of AG startup
 * @private
 */
function _AG_preStart() {
    // resizeToFillParent();
}

/**
 * Creates a selection component for each time series displayed by this eeg view
 * Part of AG startup
 * The order of the filterGids determines the order of the selectors
 * It must have the same ordering as all other timeseries arrays
 * @private
 */
function _AG_init_selection(filterGids) {
    let i;
    let selectors = [];

    filterGid = filterGids;

    /**
     * Returns the selected channel indices as interpreted by AG_submitableSelectedChannels
     * ( starting at 0 and ending at len(timeseries_0_channels) + ... + len(timeseries_final_channels) )
     */
    function getSelectedChannelsAsGlobalIndices() {
        let all_selected = [];
        let offset = 0;

        for (let i = 0; i < selectors.length; i++) {
            const selector = selectors[i];
            const selected_in_current = selector.val();

            for (let j = 0; j < selected_in_current.length; j++) {
                all_selected.push(offset + parseInt(selected_in_current[j], 10));
            }
            offset += selector._allValues.length;
        }
        return all_selected;
    }

    // init selectors
    let selectorId, selector;

    for (i = 0; i < filterGids.length; i++) {
        selectorId = "#channelSelector" + i;
        selector = TVBUI.regionSelector(selectorId, {filterGid: filterGids[i]});
        selector.change(function (current_selection) {
            AG_submitableSelectedChannels = getSelectedChannelsAsGlobalIndices();
            refreshChannels();
        });
        selectors.push(selector);
    }
    // the first selector is special. we select by default some channels in it and in case of a dual view
    // his selection is synchronized with the brain
    AG_regionSelector = selectors[0];

    // Initialize AG_submitableSelectedChannels
    AG_submitableSelectedChannels = getSelectedChannelsAsGlobalIndices();

    if (AG_submitableSelectedChannels.length === 0) {
        // Viewer breaks if this is empty. Fill the first few channels
        const defaultSelectionLength = Math.min(totalNumberOfChannels, DEFAULT_MAX_CHANNELS);
        // we take the values form the dom, a range(defaultSelectionLength) is not a valid selection if there are multiple time series
        AG_submitableSelectedChannels = AG_regionSelector._allValues.slice(0, defaultSelectionLength);
        AG_regionSelector.val(AG_submitableSelectedChannels);
    }

    // Init the mode selection components. Assumes that there are part of the selector dom
    let modeSelectors = [];
    for (i = 0; i < filterGids.length; i++) {
        selectorId = "#channelSelector" + i;
        selector = TVBUI.modeAndStateSelector(selectorId, i);
        selector.modeChanged(_AG_changeMode);
        selector.stateVariableChanged(_AG_changeStateVariable);
        modeSelectors.push(selector);
    }
    // The dual view needs to subscribe to this selector; so we save it like AG_regionSelector
    AG_modeSelector = modeSelectors[0];

    refreshChannels();
}

/**
 * Read speed from the dom
 * @param defaultSpeed default speed when there is no speed slider
 * @private
 */
function _AG_get_speed(defaultSpeed) {
    let speed = defaultSpeed;
    if (!isSmallPreview && !isDoubleView) {
        speed = $("#ctrl-input-speed").slider("value");
    }
    return speed;
}

function refreshChannels() {
    submitSelectedChannels(false);
}

function _AG_changeMode(tsIndex, val) {
    tsModes[tsIndex] = parseInt(val);
    refreshChannels();
}

function _AG_changeStateVariable(tsIndex, val) {
    tsStates[tsIndex] = parseInt(val);
    refreshChannels();
}

function _AG_getSelectedDataAndLongestChannelIndex(data) {
    let offset = 0;
    let selectedData = [];
    let channelLengths = [];

    for (let i = 0; i < data.length; i++) {
        const selectedChannels = getDisplayedChannels(data[i], offset);
        offset += data[i].length;
        if (selectedChannels.length > 0) {
            channelLengths.push(selectedChannels[0].length);
        } else {
            channelLengths.push(-1);
        }
        selectedData = selectedData.concat(selectedChannels);
    }
    const longestChannelIndex = channelLengths.indexOf(Math.max.apply(Math, channelLengths));
    return {selectedData: selectedData, longestChannelIndex: longestChannelIndex}
}

/*
 * Get required data for the channels in AG_submitableSelectedChannels. If none
 * exist then just use the previous 'displayedChannels' (or default in case of first run).
 */
function submitSelectedChannels(isEndOfData) {
    AG_currentIndex = AG_numberOfVisiblePoints;
    if (AG_submitableSelectedChannels.length === 0) {
        AG_submitableSelectedChannels = displayedChannels.slice();
    }

    if (!(isEndOfData && maxDataFileIndex === 0)) {
        AG_allPoints = [];
        displayedChannels = AG_submitableSelectedChannels.slice(0);
        generateChannelColors(displayedChannels.length);

        let results = [];
        for (let i = 0; i < nrOfPagesSet.length; i++) {
            const dataURL = readDataPageURL(baseDataURLS[i], 0, dataPageSize, tsStates[i], tsModes[i]);
            const data = HLPR_readJSONfromFile(dataURL);
            results.push(parseData(data, i));
        }
        const r = _AG_getSelectedDataAndLongestChannelIndex(results);
        AG_allPoints = AG_allPoints.concat(r.selectedData);
        longestChannelIndex = r.longestChannelIndex;

        // keep data only for the selected channels
        AG_noOfLines = AG_allPoints.length;
    }

    AG_displayedPoints = [];
    AG_displayedTimes = [];
    for (let ii = 0; ii < AG_noOfLines; ii++) {
        AG_displayedPoints.push([]);
    }

    if (!(isEndOfData && maxDataFileIndex === 0)) {
        //read time
        readTimeData(0, false);
        AG_time = nextTimeData.slice(0);
    }
    // reset data
    nextData = [];
    nextTimeData = [];
    AG_isLoadStarted = false;
    isNextDataLoaded = false;
    isNextTimeDataLoaded = false;
    currentDataFileIndex = 0;
    totalPassedData = 0;
    currentLinePosition = 0;
    if (nanValueFound) {
        displayMessage('The given data contains some NaN values. All the NaN values were replaced by zero.', 'warningMessage');
    }


    //create 2D plot
    //The shape we use for time series now only uses 1D
    var dataShape = [totalTimeLength, 1, AG_submitableSelectedChannels.length, 1];
    var selectedLabels = []
    for (let i = 0; i < AG_submitableSelectedChannels.length; i++) {
        selectedLabels.push([chanDisplayLabels[displayedChannels[i]]]);
    }
    //use d3 to create 2D plot
    ts = tv.plot.time_series();
    ts.baseURL(baseDataURLS[0]).preview(false).mode(0).state_var(0);
    ts.shape(dataShape).t0(AG_time[1] / 2).dt(AG_time[1]);
    ts.labels(selectedLabels);
    ts.channels(AG_submitableSelectedChannels);
    ts.viewer_type('dualbrain');


    resizeToFillParent(ts);
    $('#time-series-viewer').empty();
    ts(d3.select("#time-series-viewer"));
    tsView = ts;

    isnewDoubleView=true;


    // This is arbitrarily set to a value. To be consistent with tsview we rescale relative to this value
    _initial_magic_fcs_amp_scl = tsView.magic_fcs_amp_scl;

    $("#ctrl-input-scale").slider({
        value: 50, min: 0, max: 100,
        slide: function (event, target) {
            _updateScalingFromSlider(target.value);
        }
    });

}

function resizeToFillParent(ts) {
    var container, width, height;

    container = $('#eegSectionId').parent();
    width = container.width();

    //minus toolbar's height
    height = container.height() - 60;

    ts.w(width).h(height);

}

function _updateScalingFromSlider(value) {
    if (value == null) {
        value = $("#ctrl-input-scale").slider("value");
    }
    var expo_scale = (value - 50) / 50; // [1 .. -1]
    var scale = Math.pow(10, expo_scale * 4); // [1000..-1000]
    tsView.magic_fcs_amp_scl = _initial_magic_fcs_amp_scl * scale;
    tsView.render_focus();

    if (scale >= 1) {
        $("#display-scale").html("1 * " + scale.toFixed(2));
    } else {
        $("#display-scale").html("1 / " + (1 / scale).toFixed(2));
    }

}


var isEndOfData = false;
var AG_channelColorsDict = {};
var AG_reversedChannelColorsDict = {};

/*
 * Generate different colors for each channel.
 */
function generateChannelColors(nr_of_channels) {
    AG_channelColorsDict = {};
    AG_reversedChannelColorsDict = {};
    let step = parseInt(255 / nr_of_channels);
    for (let i = 0; i < nr_of_channels; i++) {
        const color = "rgb(" + 250 * (i % 2) + "," + (200 - i * step) + "," + 220 * ((i + 1) % 2) + ")";
        AG_channelColorsDict[color] = i;
        AG_reversedChannelColorsDict[i] = color;
    }
}

/**
 * Translate the given value.
 * We use this method to translate the values for the drawn line charts because we don't want them to overlap.
 *
 * @param value the value that should be translated.
 * @param index the number of <code>AG_translationSteps</code> that should be used for translating the given value.
 * @return {number}
 */
function AG_addTranslationStep(value, index) {
    return value * AG_scaling - AG_normalizationSteps[displayedChannels[index]] + AG_translationStep * AG_computedStep * index;
}

/*
 * Add all required data to AG_displayedPoints and AG_displayedTimes in order to center
 * around indexInPage, if some of the required data is on the previous page.
 */
function addFromPreviousPage(indexInPage, currentPage) {

    const previousPageUrl = readDataPageURL(baseDataURLS[0], (currentPage - 1) * dataPageSize, currentPage * dataPageSize, tsStates[0], tsModes[0]);
    let previousData = parseData(HLPR_readJSONfromFile(previousPageUrl), 0);
    previousData = getDisplayedChannels(previousData, 0).slice(0);
    const previousTimeData = HLPR_readJSONfromFile(timeSetUrls[0][currentPage - 1]);
    // Compute which slices we would need from the 'full' two-pages data.
    // We only need the difference so to center indexInPage at AG_numberOfVisiblePoints / 2
    let fromIdx, toIdx;
    fromIdx = previousData[0].length - (AG_numberOfVisiblePoints / 2 - indexInPage);  // This is from where we need to read from previous data
    AG_currentIndex = toIdx = AG_numberOfVisiblePoints - (AG_numberOfVisiblePoints / 2 - indexInPage); // This is where we need to add from the current page
    // Just generate displayed point and displayed times now
    for (let idx = 0; idx < previousData.length; idx++) {
        let idy;
        let oneLine = [];
        // Push data that is from previos slice
        for (idy = fromIdx; idy < previousData[0].length; idy++) {
            oneLine.push([previousTimeData[idy], AG_addTranslationStep(previousData[idx][idy], idx)]);
        }
        // Now that that is from our current slice
        for (idy = 0; idy < toIdx; idy++) {
            oneLine.push([AG_time[idy], AG_addTranslationStep(AG_allPoints[idx][idy], idx)]);
        }
        AG_displayedPoints.push(oneLine);
    }
    AG_displayedTimes = previousTimeData.slice(fromIdx).concat(AG_time.slice(0, toIdx));
    previousData = null;
}

/*
 * Add all required data to AG_displayedPoints and AG_displayedTimes in order to center
 * around indexInPage, if some of the required data is on the next page.
 */
function addFromNextPage(indexInPage, currentPage) {

    const followingPageUrl = readDataPageURL(baseDataURLS[0], (currentPage + 1) * dataPageSize, (currentPage + 2) * dataPageSize, tsStates[0], tsModes[0]);
    let followingData = parseData(HLPR_readJSONfromFile(followingPageUrl), 0);
    followingData = getDisplayedChannels(followingData, 0).slice(0);
    const followingTimeData = HLPR_readJSONfromFile(timeSetUrls[0][currentPage + 1]);
    let fromIdx, toIdx;
    fromIdx = indexInPage - (AG_numberOfVisiblePoints / 2);	// We need to read starting from here from the current page
    AG_currentIndex = toIdx = fromIdx + AG_numberOfVisiblePoints - AG_allPoints[0].length;	// We need to read up to here from next page
    for (let idx = 0; idx < AG_allPoints.length; idx++) {
        let idy;
        const oneLine = [];
        // Push data that is from this slice
        for (idy = fromIdx; idy < AG_allPoints[0].length; idy++) {
            oneLine.push([AG_time[idy], AG_addTranslationStep(AG_allPoints[idx][idy], idx)]);
        }
        // Now that that is from next slice
        for (idy = 0; idy < toIdx; idy++) {
            oneLine.push([followingTimeData[idy], AG_addTranslationStep(followingData[idx][idy], idx)]);
        }
        AG_displayedPoints.push(oneLine);
    }
    AG_displayedTimes = AG_time.slice(fromIdx).concat(followingTimeData.slice(0, toIdx));
    // Since next page is already loaded, that becomes the current page
    AG_allPoints = followingData;
    AG_time = followingTimeData;
    totalPassedData = (currentPage + 1) * dataPageSize;
    currentDataFileIndex = currentPage + 1;
    isNextDataLoaded = true;
    isNextTimeDataLoaded = true;
}

/*
 * Just re-populate whole displayedPoints and displayedTimes given a start and end index.
 */
function prepareDisplayData(fromIdx, toIdx, pointsArray, timeArray) {

    for (let idx = 0; idx < pointsArray.length; idx++) {
        let oneLine = [];
        for (let idy = fromIdx; idy < toIdx; idy++) {
            oneLine.push([timeArray[idy], AG_addTranslationStep(pointsArray[idx][idy], idx)]);
        }
        AG_displayedPoints.push(oneLine);
    }
    AG_displayedTimes = timeArray.slice(fromIdx, toIdx)
}

/*
 * Read the next data file asyncronously. Also get the corresponding time data file.
 */
function loadNextDataFile() {
    AG_isLoadStarted = true;
    const nx_idx = getNextDataFileIndex();
    cachedFileIndex = nx_idx;
    AG_readFileDataAsynchronous(nrOfPagesSet, noOfChannelsPerSet, nx_idx, maxChannelLength, 0);
    readTimeData(nx_idx, true);
}

function changeCurrentDataFile() {
    if (!isNextDataLoaded || !isNextTimeDataLoaded) {
        return;
    }

    if (cachedFileIndex !== getNextDataFileIndex()) {
        AG_isLoadStarted = false;
        isNextDataLoaded = false;
        isNextTimeDataLoaded = false;
        nextData = [];
        nextTimeData = [];
        return;
    }

    const speed = _AG_get_speed(100);
    const longestChannelLength = AG_allPoints[longestChannelIndex].length;

    if (speed > 0) {
        totalPassedData = totalPassedData + longestChannelLength;
        if (longestChannelLength < AG_currentIndex) {
            AG_currentIndex = -(longestChannelLength - AG_currentIndex);
        } else {
            AG_currentIndex = 0;
        }
    } else if (speed < 0) {
        totalPassedData = totalPassedData - longestChannelLength;
        if (totalPassedData < 0) {
            totalPassedData = 0;
        }
    } else {
        return;
    }

    AG_allPoints = nextData.slice(0);
    nextData = [];
    AG_time = nextTimeData.slice(0);
    nextTimeData = [];
    currentDataFileIndex = getNextDataFileIndex();
    AG_isLoadStarted = false;
    isNextDataLoaded = false;
    isNextTimeDataLoaded = false;

    if (speed < 0) {
        AG_currentIndex = longestChannelLength + AG_currentIndex;
    }
}

function shouldLoadNextDataFile() {
    if (!AG_isLoadStarted && maxDataFileIndex > 0) {
        const nextFileIndex = getNextDataFileIndex();
        const speed = _AG_get_speed(1); // Assume left to right pass of data
        if (currentDataFileIndex !== nextFileIndex) {
            if ((speed > 0) && (maxChannelLength - AG_currentIndex < threshold * AG_numberOfVisiblePoints)) {
                return true;
            }
            if ((speed < 0) && (AG_currentIndex - AG_numberOfVisiblePoints < threshold * AG_numberOfVisiblePoints)) {
                return true;
            }
        }
    }
    return false;
}

/*
 * In case of multiple arrays find out which has the most data files that need
 * to be loaded.
 */
function setMaxDataFileIndex(nrOfPagesPerArray) {
    let max_ln = 0;
    for (let i = 0; i < nrOfPagesPerArray.length; i++) {
        if (nrOfPagesPerArray[i] > max_ln) {
            max_ln = nrOfPagesPerArray[i];
        }
    }
    maxDataFileIndex = max_ln - 1;
}

/*
 * Return the index of the next data file that should be loaded.
 */
function getNextDataFileIndex() {
    let nextIndex;
    const speed = _AG_get_speed(100);
    if (speed > 0) {
        nextIndex = currentDataFileIndex + 1;
        if (nextIndex >= maxDataFileIndex) {
            return maxDataFileIndex;
        }
    } else {
        nextIndex = currentDataFileIndex - 1;
        if (nextIndex <= 0) {
            return 0;
        }
    }
    return nextIndex;
}

function AG_readFileDataAsynchronous(nrOfPages, noOfChannelsPerSet, currentFileIndex, maxChannelLength, dataSetIndex) {
    if (dataSetIndex >= nrOfPages.length) {
        isNextDataLoaded = true;
        // keep data only for the selected channels
        const r = _AG_getSelectedDataAndLongestChannelIndex(nextData);
        longestChannelIndex = r.longestChannelIndex;
        nextData = r.selectedData; //todo: occasional shape mismatch 3d <- 2d
        return;
    }
    if (nrOfPages[dataSetIndex] - 1 < currentFileIndex && AG_isLoadStarted) {
        // todo: assumed that this is computing a padding for smaller signals. check if this is really the purpose of this
        let j;
        let padding = [];
        let oneChannel = [];
        for (j = 0; j < maxChannelLength; j++) {
            oneChannel.push(0);
        }
        for (j = 0; j < noOfChannelsPerSet[dataSetIndex]; j++) {
            padding.push(oneChannel);
        }
        nextData.push(padding);

        AG_readFileDataAsynchronous(nrOfPages, noOfChannelsPerSet, currentFileIndex, maxChannelLength, dataSetIndex + 1);
    } else {
        doAjaxCall({
            url: readDataPageURL(baseDataURLS[dataSetIndex], currentFileIndex * dataPageSize, (currentFileIndex + 1) * dataPageSize, tsStates[dataSetIndex], tsModes[dataSetIndex]),
            success: function (data) {
                if (AG_isLoadStarted) {
                    data = $.parseJSON(data);
                    const result = parseData(data, dataSetIndex);
                    nextData.push(result);

                    AG_readFileDataAsynchronous(nrOfPages, noOfChannelsPerSet, currentFileIndex, maxChannelLength, dataSetIndex + 1);
                }
            }
        });
    }
}

/*
 * Data is received from the HLPR_parseJSON as a 500/74 array. We need to transform it
 * into an 74/500 one and in the transformation also replace all NaN values.
 */
function parseData(dataArray, dataSetIndex) {

    let result = [];
    for (let i = 0; i < noOfChannelsPerSet[dataSetIndex]; i++) {
        result.push([]);
    }
    for (let j = 0; j < dataArray.length; j++) {
        for (let k = 0; k < noOfChannelsPerSet[dataSetIndex]; k++) {
            let arrElem = dataArray[j][k];
            if (arrElem === 'NaN') {
                nanValueFound = true;
                arrElem = 0;
            }
            result[k].push(arrElem);
        }
    }
    return result;
}

/**
 *
 * @param fileIndex
 * @param asyncRead <code>true</code> only if the file should be read asynchronous
 */
function readTimeData(fileIndex, asyncRead) {
    if (timeSetUrls[longestChannelIndex].length <= fileIndex) {
        nextTimeData = [];
        for (let i = 0; i < maxChannelLength; i++) {
            nextTimeData.push(totalPassedData + i);
        }
        isNextTimeDataLoaded = true;
    } else {
        if (asyncRead) {
            doAjaxCall({
                url: timeSetUrls[longestChannelIndex][fileIndex],
                success: function (data) {
                    nextTimeData = $.parseJSON(data);
                    isNextTimeDataLoaded = true;
                }
            });
        } else {
            nextTimeData = HLPR_readJSONfromFile(timeSetUrls[longestChannelIndex][fileIndex]);
            isNextTimeDataLoaded = true;
        }
    }
}

function getArrayFromDataFile(dataFile) {
    let fileData = dataFile.replace(/\n/g, " ").replace(/\t/g, " ");
    let arrayData = $.trim(fileData).split(" ");
    for (let i = 0; i < arrayData.length; i++) {
        arrayData[i] = parseFloat(arrayData[i]);
    }
    return arrayData;
}

function getDisplayedChannels(listOfAllChannels, offset) {
    let selectedData = [];
    for (let i = 0; i < displayedChannels.length; i++) {
        if (listOfAllChannels[displayedChannels[i] - offset] !== undefined) {
            selectedData.push(listOfAllChannels[displayedChannels[i] - offset].slice(0));
        }
    }
    return selectedData;
}

//------------------------------------------------START SPEED RELATED CODE--------------------------------------------------------

function drawSliderForAnimationSpeed() {
    $("#ctrl-input-speed").slider({
        orientation: 'horizontal',
        value: 3,
        min: -50,
        max: 50,
        change: function (event, ui) {
            updateSpeedFactor();
        }
    });
}

function updateSpeedFactor() {
    var speed = $("#ctrl-input-speed").slider("option", "value");
    $('#display-speed').html('' + speed);
    AG_isSpeedZero = (speed == 0);
}

//------------------------------------------------END SPEED RELATED CODE--------------------------------------------------------
//------------------------------------------------START TIME SERIES TIME SELECTION RELATED CODE--------------------------------------------------------

function intervalSet() {
    var start = $('#SetIntervalStart').val();
    var end = $('#SetIntervalEnd').val();
    if (start>=0 && start < end) {
        tsView.timeselection_interval_set(start, end);
    }
}