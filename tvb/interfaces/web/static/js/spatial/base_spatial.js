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

//needed for allowing the user to rotate the brain
var lastSelected_TRIANGLE_pickedIndex = -5;
// the default weights values for a region stimulus; needed for reset action
var originalRegionStimulusWeights = [];
// the updated weights values for a region stimulus
var updatedRegionStimulusWeights = [];
// this array will contain all the focal points selected by the user
var addedSurfaceFocalPoints = [];
// this array will contain all the triangles for the defined focal points
var addedFocalPointsTriangles = [];

var NO_VERTEX_SELECTED_MSG = "You have no vertex selected.";
var NO_NODE_SELECTED_MSG = "You have no node selected.";


/**
 * Display the index for the selected vertex.
 */
function displayIndexForThePickedVertex() {
    if (TRIANGLE_pickedIndex == undefined || TRIANGLE_pickedIndex < 0) {
        displayMessage("No triangle is selected.", "warningMessage");
    } else {
        displayMessage("The index of the selected triangle is " + TRIANGLE_pickedIndex, "infoMessage");
    }
}


/**
 * Display the name for the selected connectivity node.
 */
function displayNameForPickedNode() {
    if (CONN_pickedIndex == undefined || CONN_pickedIndex < 0) {
        displayMessage("No node is currently selected selected.", "warningMessage");
    } else {
        displayMessage("The selected node is " + GVAR_pointsLabels[CONN_pickedIndex], "infoMessage");
    }
}


/**
 * Submits all the region stimulus data to the server for creating a new Stimulus instance.
 *
 * @param actionUrl the url at which will be submitted the data.
 * @param nextStep
 * @param checkScaling
 */
function submitRegionStimulusData(actionUrl, nextStep, checkScaling) {
	if (checkScaling == true) {
		var scalingSet = false;
		for (var i=0; i<updatedRegionStimulusWeights.length; i++) {
			if (updatedRegionStimulusWeights[i] != 0) {
				scalingSet = true;
			}
		}
		if (scalingSet == false) {
			displayMessage("You should set scaling that is not 0 for at least some nodes.", "warningMessage");
        	return;
		}
	}
	submitPageData(actionUrl, {'next_step' : nextStep})
}

/*
 * Gather the data from all the forms in the page and submit them to actionUrl.
 * 
 * @param actionUrl: the url to which data will be submitted
 * @param baseData:
 */
function submitPageData(actionUrl, baseData) {
	var dataDictionary = baseData;
	var pageForms = $('form');
	for (var i=0; i<pageForms.length; i++) {
		pageForms[i].id = "form_id_" + i;
		var formData = getSubmitableData(pageForms[i].id, false);
		for (key in formData) {
			dataDictionary[key] = formData[key];
		}
	}
		
    var parametersForm = document.createElement("form");
    parametersForm.method = "POST";
    parametersForm.action = actionUrl;
    document.body.appendChild(parametersForm);
    
    for (key in dataDictionary) {
	        var input = document.createElement('INPUT');
	        input.type = 'hidden';
	        input.name = key;
	        input.value = dataDictionary[key];
	        parametersForm.appendChild(input);
	    }
    
    parametersForm.submit();
}


/**
 * Collects the data needed for creating a SurfaceStimulus and submit it to the server.
 *
 * @param actionUrl the url at which will be submitted the data.
 * @param nextStep
 * @param includeFocalPoints
 */
function submitSurfaceStimulusData(actionUrl, nextStep, includeFocalPoints) {
    if (includeFocalPoints == true && addedSurfaceFocalPoints.length < 1) {
        displayMessage("You should define at least one focal point.", "errorMessage");
        return;
    }
    var baseDict = {'next_step' : nextStep}
	if (includeFocalPoints == true) {
		baseDict['defined_focal_points'] = JSON.stringify(addedFocalPointsTriangles);
	}
    submitPageData(actionUrl, baseDict)
}

/**
 * Generate the data from the currently configured stimulus.
 */
function startStimulusVisualization() {

    if (addedSurfaceFocalPoints.length < 1) {
        displayMessage("You should define at least one focal point.", "errorMessage");
        return;
    }
    LEG_generateLegendBuffers();
    $.ajax({
        async:false,
        type:'GET',
        url:'/spatial/stimulus/surface/view_stimulus?focal_points=' + JSON.stringify(addedFocalPointsTriangles),
        success:function (data) {
            data = $.parseJSON(data);
            if (data['status'] == 'ok') {
                STIM_PICK_setVisualizedData(data);
                $('.action-stop')[0].className = $('.action-stop')[0].className.replace('action-idle', '');
                $('.action-run')[0].className = $('.action-run')[0].className + " action-idle";
            } else {
                displayMessage(data['errorMsg'], "errorMessage");
            }

        },
        error: function(x, e) {
            if (x.status == 500) {
                displayMessage("An error occured probably due to invalid parameters.", "errorMessage");
            }
        }
    });
}

function stopStimulusVisualization() {
	STIM_PICK_stopDataVisualization();
	$('.action-run')[0].className = $('.action-run')[0].className.replace('action-idle', '');
	$('.action-stop')[0].className = $('.action-stop')[0].className + " action-idle";
    LEG_legendBuffers = [];
}


/**
 * Displays with a different color all the nodes that have a weight grater than 0.
 */
function refreshWeights() {
    $("input[name='weight']").val($.toJSON(updatedRegionStimulusWeights));
    for (var i = 0; i < updatedRegionStimulusWeights.length; i++) {
        $("#nodeScale" + i).text(updatedRegionStimulusWeights[i]);
        if (updatedRegionStimulusWeights[i] > 0) {
            GFUNC_addNodeToNodesWithPositiveWeight(i);
            document.getElementById("nodeScale" + i).className = "node-scale node-scale-selected"
        } else {
            GFUNC_removeNodeFromNodesWithPositiveWeight(i);
            document.getElementById("nodeScale" + i).className = "node-scale"
        }
    }
    displayNumberOfSelections();
}


/**
 * Displays the number of selected nodes.
 */
function displayNumberOfSelections() {
    if (GVAR_interestAreaNodeIndexes.length > 0) {
        $("#selectionMsg").text("You have " + GVAR_interestAreaNodeIndexes.length + " node(s) selected.");
    } else {
        $("#selectionMsg").text("You have no node selected.");
    }
}


/**
 * Method used for selecting/unselecting a connectivity node. This method will
 * also select/unselect the node from the 'hemispheres' component.
 *
 * @param nodeIndex the index of the node that hast to be toggled.
 */
function toggleSelection(nodeIndex) {
    if (nodeIndex >= 0) {
        if (GFUNC_isNodeAddedToInterestArea(nodeIndex)) {
            GFUNC_removeNodeFromInterestArea(nodeIndex);
            $("#nodeSelection" + nodeIndex).removeClass('selected');
        } else {
            GFUNC_addNodeToInterestArea(nodeIndex);
            $("#nodeSelection" + nodeIndex).addClass('selected');
        }
    }
}


function centerNavigatorOnFocalPoint(focalPointTriangle) {
	/*
	 * Move the brain navigator on this focal point.
	 */
	TRIANGLE_pickedIndex = parseInt(focalPointTriangle);
	moveBrainNavigator(true);
}


/**
 * Displays all the focal points that were selected by the user.
 */
function drawSurfaceFocalPoints() {
	var focalPointsContainer = $('.focal-points');
    focalPointsContainer.empty();
    var dummyDiv = document.createElement('DIV');
    for (var i = 0; i < addedFocalPointsTriangles.length; i++) {
        dummyDiv.innerHTML = '<li> <a href="#" onclick="centerNavigatorOnFocalPoint(' + addedFocalPointsTriangles[i] + ')">Focal point ' + addedFocalPointsTriangles[i] + '</a>' +
            '<a href="#" onclick="removeFocalPoint(' + i + ')" title="Delete focal point: ' + addedFocalPointsTriangles[i] + '" class="action action-delete">Delete</a>' +
            '</li>';
	    var focalPointElement = dummyDiv.firstChild;
	    focalPointsContainer.append(focalPointElement);
    }
}


/**
 * Removes a focal point.
 *
 * @param focalPointIndex the index of the focal point that has to be removed.
 */
function removeFocalPoint(focalPointIndex) {
	var focalIndex = addedFocalPointsTriangles[focalPointIndex];
	BASE_PICK_removeFocalPoint(focalIndex);
	addedFocalPointsTriangles.splice(focalPointIndex, 1);
    addedSurfaceFocalPoints.splice(focalPointIndex, 1);
    drawSurfaceFocalPoints();
}

/*
 * Remove all the defined focal points
 */
function deleteAllFocalPoint() {
	for (var i = addedFocalPointsTriangles.length - 1; i >= 0; i--) {
		removeFocalPoint(i);
	}
}


/**
 * Collects the data defined for the local connectivity and submit it to the server.
 *
 * @param actionURL the url at which will be submitted the data
 * @param formId
 */
function submitLocalConnectivityData(actionURL, formId) {
    var parametersForm = document.getElementById(formId);
    parametersForm.method = "POST";
    parametersForm.action = actionURL;
    parametersForm.submit();
}


/**
 * Used for plotting equations.
 *
 * @param containerId the id of the container in which should be displayed the equations plot
 * @param url the url where should be made the call to obtain the html which contains the equations plot
 * @param formDataId the id of the form which contains the data for the equations
 * @param fieldsPrefixes a list with the prefixes of the fields at which the equation is sensible. If any
 * field that starts with one of this prefixes is changed than the equation chart will be redrawn.
 * @param axisDataId
 */
function plotEquations(containerId, url, formDataId, fieldsPrefixes, axisDataId) {
    _plotEquations(containerId, url, formDataId, axisDataId);
    _applyEvents(containerId, url, formDataId, axisDataId, fieldsPrefixes);
}


/**
 * Private function.
 *
 * Updates the equations chart.
 */
function _plotEquations(containerId, url, formDataId, axisDataId) {
    var formInputs = $("#" + formDataId).serialize();
    var axisData = $('#' + axisDataId).serialize();
    $.ajax({
        async:false,
        type:'GET',
        url:url + "?" + formInputs + ';' + axisData,
        success:function (data) {
        	var containerElement = $("#" + containerId);
            containerElement.empty();
            containerElement.append(data);
        }
    });
}


/**
 * Private function.
 *
 * Applies change events on fields that starts with <code>fieldsPrefixes</code> to updated
 * the plotted equations. The fields should be on a form with id <code>formDataId</code>.
 */
function _applyEvents(containerId, url, formDataId, axisDataId, fieldsPrefixes) {
    for (var i = 0; i < fieldsPrefixes.length; i++) {
        $('select[name^="' + fieldsPrefixes[i] + '"]').change(function () {
            _plotEquations(containerId, url, formDataId, axisDataId);
        });
        $('input[name^="' + fieldsPrefixes[i] + '"]').change(function () {
            _plotEquations(containerId, url, formDataId, axisDataId);
        });
    }
}


/**
 * Loads the interface found at the given url.
 */
function load_entity() {
    var selectedEntityGid = $("select[name='existentEntitiesSelect']").val();
    var myForm;

    if (selectedEntityGid == undefined || selectedEntityGid == "None" || selectedEntityGid.trim().length == 0) {
		myForm = document.getElementById("reset-to-default");
    } else {
		myForm = document.getElementById("load-existing-entity");
		$("#entity-gid").val(selectedEntityGid);
    }
    myForm.submit();
}

