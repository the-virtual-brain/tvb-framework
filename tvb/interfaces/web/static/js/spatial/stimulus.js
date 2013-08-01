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

/*
 * ---------------------------------------===========================================--------------------------------------
 * WARNING: This script is just adding some functionality specific to the stimulus on top of what is defined 
 * in /static/js/spatial/base_spatial.js. As such in all the cases when this script is used, you must first 
 * include base_spatial.js. In case you need to ADD FUNCTIONS here, either make sure you don't "overwrite" something
 * necessary from base_spatial.js, or just prefix your functions. (e.g. STIM_SPATIAL_${function_name}).
 * ---------------------------------------===========================================--------------------------------------
 */


/**
 * Saves the given weight for all the selected nodes.
 */
function saveWeightForSelectedNodes() {
    var newWeight = $("input[name='current_weight']").val();
    if (newWeight != null && newWeight.trim().length > 0 && !isNaN(newWeight)) {
        newWeight = parseFloat(newWeight);
        for (var i = 0; i < GVAR_interestAreaNodeIndexes.length; i++) {
            var nodeIndex = GVAR_interestAreaNodeIndexes[i];
            updatedRegionStimulusWeights[nodeIndex] = newWeight;
        }
        $("input[name='current_weight']").val("");
        GFUNC_removeAllMatrixFromInterestArea();
        refreshWeights();
        $.ajax({
        	async: false,
        	traditional: true,
        	type: 'POST',
        	data: {'scaling' : updatedRegionStimulusWeights},
        	url:'/spatial/stimulus/region/update_scaling',
        });
    }
}


/**
 * Resets all the weights to their default values.
 */
function resetRegionStimulusWeights() {
    updatedRegionStimulusWeights = originalRegionStimulusWeights.slice(0);
    refreshWeights();
    $.ajax({
        	async: false,
        	traditional: true,
        	type: 'POST',
        	data: {'scaling' : updatedRegionStimulusWeights},
        	url:'/spatial/stimulus/region/update_scaling',
        });
}


/**
 * Toggle the selection of the given node.
 *
 * @param nodeIndex the index of the selected node.
 */
function toggleNodeSelection(nodeIndex) {
    toggleSelection(nodeIndex);
    if (nodeIndex >= 0) {
        refreshWeights();
    }
}


/**
 * Method used for making initializations.
 */
function initConnectivityViewer(weights) {
        //The click event is bound on the div in which will be placed the connectivity canvas.
        //If I bind the event on the canvas and I'll change the connectivity which in turn
        // will change the canvas => on the new canvas the click event won't be bound
        $('#GLcanvas').unbind('click.toggleNodeSelection');
        $('#GLcanvas').bind('click.toggleNodeSelection', function (e) {
            if (e.target == document.getElementById("GLcanvas")) {
                toggleNodeSelection(CONN_pickedIndex);
            }
        });

        originalRegionStimulusWeights = weights;
        updatedRegionStimulusWeights = originalRegionStimulusWeights.slice(0);
        GVAR_interestAreaNodeIndexes = [];
        GVAR_connectivityNodesWithPositiveWeight = [];
        refreshWeights();
}


/*
 * NOTE: The method is called through eval. Do not remove it.
 *
 * Parse the entry for the focal points and load them into js to be later used.
 */
function initFocalPoints(focal_points) {
	for (var i = 0; i < focal_points.length; i++) {
		var focalPoint = parseInt(focal_points[i]);
		addedFocalPointsTriangles.push(focalPoint);
		addedSurfaceFocalPoints.push(focalPoint);
		TRIANGLE_pickedIndex = focalPoint;
		moveBrainNavigator(true);
		BASE_PICK_addFocalPoint(focalPoint);
	}
	drawSurfaceFocalPoints();
}



/**
 * Add a focal point for the currently selected surface.
 */
function addSurfaceFocalPoint() {
    if (TRIANGLE_pickedIndex < 0) {
        displayMessage(NO_VERTEX_SELECTED_MSG, "errorMessage");
    } else if (addedSurfaceFocalPoints.length >= 20) {
        displayMessage("The max number of focal points you are allowed to add is 20.", "errorMessage");
    } else {
        var valIndex = $.inArray(TRIANGLE_pickedIndex, addedFocalPointsTriangles);
        if (valIndex < 0) {
        	displayMessage("Adding focal point with number: "+ (addedSurfaceFocalPoints.length + 1)); //clear msg
            addedSurfaceFocalPoints.push(VERTEX_pickedIndex);
            addedFocalPointsTriangles.push(TRIANGLE_pickedIndex)
            drawSurfaceFocalPoints();
            BASE_PICK_addFocalPoint(TRIANGLE_pickedIndex);
        } else {
        	displayMessage("The focal point " + TRIANGLE_pickedIndex + " is already in the focal points list.", "warningMessage"); //clear msg
        }
    }
}

