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
 * WARNING: This script is just adding some functionality specific to the model parameters on top of what is defined 
 * in /static/js/spatial/base_spatial.js. As such in all the cases when this script is used, you must first 
 * include base_spatial.js. In case you need to ADD FUNCTIONS here, either make sure you don't "overwrite" something
 * necessary from base_spatial.js, or just prefix your functions. (e.g. MP_SPATIAL_${function_name}).
 * ---------------------------------------===========================================--------------------------------------
 */


/**
 * Draws sliders for the parameters of a model.
 *
 * @param paramSlidersData will be a dictionary of form:
 * dict = {'$param_name': { 'min': $min, 'max': $max, 'default': $default, 'name': '$param_name'},
 *          ...,
 *          'all_param_names': [list_with_all_parameters_names]
 *          }
 */
function drawSlidersForModelParameters(paramSlidersData) {
    paramSlidersData = $.parseJSON(paramSlidersData);
    for (var i = 0; i < paramSlidersData['all_param_names'].length; i++) {
        var paramName = paramSlidersData['all_param_names'][i];
        var paramData = paramSlidersData[paramName];

        _drawSlider(paramName, paramData['min'], paramData['max'], paramData['step'], paramData['default']);
    }
}

function _drawSlider(name, minValue, maxValue, stepValue, defaultValue) {
    $("#" + name).slider({
        value: defaultValue,
        min: minValue,
        max: maxValue,
        step: stepValue
    });

    $("#value_" + name).text(defaultValue);

    $("#" + name).slider({
        change: function(event, ui) {
            if (GVAR_interestAreaNodeIndexes.length == 0) {
                displayMessage(NO_NODE_SELECTED_MSG, "errorMessage");
            } else {
	            var newValue = $('#' + name).slider("option", "value");
	            $("#value_" + name).text(newValue);
	            doAjaxCall({
	                async:false,
	                type:'GET',
	                url:'/spatial/modelparameters/regions/update_model_parameter_for_nodes/' + name + '/' + newValue + '/' + $.toJSON(GVAR_interestAreaNodeIndexes),
	                success:function (data) {
	                }
	            });
			}
        }
    });
}


/**
 * @param parentDivId the id of the div in which are drawn the model parameters sliders
 */
function resetParamSliders(parentDivId) {
    if (GVAR_interestAreaNodeIndexes.length > 0) {
        doAjaxCall({
            async:false,
            type:'GET',
            url:'/spatial/modelparameters/regions/reset_model_parameters_for_nodes/' + $.toJSON(GVAR_interestAreaNodeIndexes),
            success:function (data) {
                parentDiv = $("#" + parentDivId);
                parentDiv.empty();
                parentDiv.append(data);
            }
        });
    }
}

function loadModelForConnectivityNode(connectivityNodeIndex, paramSlidersDivId) {
    if (connectivityNodeIndex >= 0) {
        doAjaxCall({
            async:false,
            type:'GET',
            url:'/spatial/modelparameters/regions/load_model_for_connectivity_node/' + connectivityNodeIndex,
            success:function (data) {
                paramSlidersDiv = $("#" + paramSlidersDivId);
                paramSlidersDiv.empty();
                paramSlidersDiv.append(data);
            }
        });
    }
}


/**
 * This method will toggle the selected node.
 * If there remains only one selected node than this method
 * will also load the model, for the remaining selected node,
 * into the phase plane viewer.
 *
 * @param nodeIndex the index of the node that hast to be toggled.
 */
function toggleAndLoadModel(nodeIndex) {
    toggleSelection(nodeIndex);
    if (GFUNC_isNodeAddedToInterestArea(nodeIndex)) {
        if (GVAR_interestAreaNodeIndexes.length == 1) {
            loadModelForConnectivityNode(GVAR_interestAreaNodeIndexes[0], 'div_spatial_model_params');
        } else if (GVAR_interestAreaNodeIndexes.length > 1) {
            copyModel(GVAR_interestAreaNodeIndexes[0], [nodeIndex]);
        }
    }
}


function copyAndLoadModel() {
    if (GVAR_interestAreaNodeIndexes.length != 0) {
        copyModel(GVAR_interestAreaNodeIndexes[0], GVAR_interestAreaNodeIndexes.slice(1));
        loadModelForConnectivityNode(GVAR_interestAreaNodeIndexes[0], 'div_spatial_model_params');
    }
}


/**
 * Replace the model of the nodes 'to_nodes' with the model of the node 'from_node'.
 *
 * @param fromNode the index of the node from where will be copied the model
 * @param toNodes a list with the nodes indexes for which will be replaced the model
 */
function copyModel(fromNode, toNodes) {
    $.ajax({
        async:false,
        type:'POST',
        url:'/spatial/modelparameters/regions/copy_model/' + fromNode + '/' + $.toJSON(toNodes),
        success:function (data) {
        }
    });
}


/**
 * Applies an equation for computing a model parameter.
 */
function applyEquationForParameter() {
    var paramName = $("#modelParameterSelect").val();
    var formInputs = $("#form_spatial_model_param_equations").serialize();
    var plotAxisInputs = $('#equationPlotAxisParams').serialize();
    var url = '/spatial/modelparameters/surface/apply_equation?param_name=' + paramName + ';' + plotAxisInputs;
    url += '&' + formInputs;
    $.ajax({
        async:false,
        type:'POST',
        url:url,
        success:function (data) {
            spatialModelParamsDiv = $("#div_spatial_model_params");
            spatialModelParamsDiv.empty();
            spatialModelParamsDiv.append(data);
            displayFocalPoints();
        }
    });
}


/**
 * Resets all the equations for all the model parameters.
 */
function resetAllEquations() {
    $.ajax({
        async:false,
        type:'POST',
        url:'/spatial/modelparameters/surface/reset_all_equations',
        success:function (data) {
            spatialModelParamsDiv = $("#div_spatial_model_params");
            spatialModelParamsDiv.empty();
            spatialModelParamsDiv.append(data);
        }
    });
}


/**
 * Removes the given vertexIndex from the list of focal points specified for the
 * equation used for computing the selected model parameter.
 */
function removeFocalPointForSurfaceModelParam(vertexIndex) {
    var paramName = $("select[name='model_param']").val();
    var url = '/spatial/modelparameters/surface/remove_focal_point?model_param=' + paramName;
        url += "&vertex_index=" + vertexIndex;
    $.ajax({
        async:false,
        type:'POST',
        url:url,
        success:function (data) {
            focalPointsDiv = $("#focalPointsDiv");
            focalPointsDiv.empty();
            focalPointsDiv.append(data);
        }
    });
}


/**
 * Adds the selected vertex to the list of focal points specified for the
 * equation used for computing the selected model parameter.
 */
function addFocalPointForSurfaceModelParam() {
    if (TRIANGLE_pickedIndex == undefined || TRIANGLE_pickedIndex < 0) {
        displayMessage(NO_VERTEX_SELECTED_MSG, "errorMessage");
        return;
    }
    var paramName = $("select[name='model_param']").val();
    var url = '/spatial/modelparameters/surface/apply_focal_point?model_param=' + paramName;
    url += "&triangle_index=" + TRIANGLE_pickedIndex;
	
    $.ajax({
        async:false,
        type:'POST',
        url:url,
        success:function (data) {
            focalPointsDiv = $("#focalPointsDiv");
            focalPointsDiv.empty();
            focalPointsDiv.append(data);
        }
    });
}


function redrawSurfaceFocalPoints(focalPointsJson) {
	/*
	 * Redraw the left side (3D surface view) of the focal points recieved in the json.
	 */
	BASE_PICK_clearFocalPoints();
	addedFocalPointsTriangles = []
	var focalPointsTriangles = $.parseJSON(focalPointsJson);
	for (var i = 0; i < focalPointsTriangles.length; i++) {
			TRIANGLE_pickedIndex = parseInt(focalPointsTriangles[i]);
			moveBrainNavigator(true);
			BASE_PICK_addFocalPoint(TRIANGLE_pickedIndex);
			addedFocalPointsTriangles.push(TRIANGLE_pickedIndex);
		}
}



/**
 * Displays all the selected focal points for the equation
 * used for computing selected model param.
 */
function displayFocalPoints() {
    var paramName = $("select[name='model_param']").val();
    var url = '/spatial/modelparameters/surface/get_focal_points?model_param=' + paramName;
    $.ajax({
        async:false,
        type:'POST',
        url:url,
        success:function (data) {
            focalPointsDiv = $("#focalPointsDiv");
            focalPointsDiv.empty();
            focalPointsDiv.append(data);
        }
    });
}


/**
 * Reset the equation for the currently selected model parameter.
 */
function resetEquationForParameter() {
    var selectedParam = $('select[name="model_param"]').val();
    if (selectedParam == undefined || selectedParam.length == 0) {
        return;
    }

    var url = '/spatial/modelparameters/surface/reset_equation_for_model_parameter';
    url += '?selected_param=' + selectedParam;
    $.ajax({
        async:false,
        type:'POST',
        url: url,
        success:function (data) {
            spatialModelParamsDiv = $("#div_spatial_model_params");
            spatialModelParamsDiv.empty();
            spatialModelParamsDiv.append(data);
        }
    });
}

function submitSurfaceParametersData(actionUrl){
	if (addedFocalPointsTriangles.length < 1) {
        displayMessage("You should define at least one focal point.", "errorMessage");
        return;
    }
    var parametersForm = document.getElementById("base_spatio_temporal_form");
    parametersForm.method = "POST";
    parametersForm.action = actionUrl;
    parametersForm.submit();	
}

// --------------------------------------------------------------------------------------
// ---------------------------- NOISE SPECIFIC SETTINGS ---------------------------------
// --------------------------------------------------------------------------------------


function updateNoiseParameters(rootDivID) {
	var noiseValues = {};
	var displayedValue = '['
	var inputs = $('#' + rootDivID).find("input[id^='noisevalue']").each(
		function() {
			var nodeIdx = this.getAttribute('id').split('__')[1];
			noiseValues[parseInt(nodeIdx)] = $(this).val();
			displayedValue += $(this).val() + ' '
		}
	)
	displayedValue = displayedValue.slice(0, -1);
	displayedValue += ']';
	var submitData = {'selectedNodes' : $.toJSON(GVAR_interestAreaNodeIndexes),
					  'noiseValues' : $.toJSON(noiseValues)}
					  
	$.ajax({  	type: "POST", 
    			async: true,
				url: '/spatial/noiseconfiguration/update_noise_configuration',
				data: submitData, 
				traditional: true,
                success: function(r) {
                	var nodesLength = GVAR_interestAreaNodeIndexes.length;
				    for (var i = 0; i < nodesLength; i++) {
				        $("#nodeScale" + GVAR_interestAreaNodeIndexes[i]).text(displayedValue);
				        document.getElementById("nodeScale" + GVAR_interestAreaNodeIndexes[i]).className = "node-scale node-scale-selected"
				    }
				    GFUNC_removeAllMatrixFromInterestArea();
                } ,
            });
}

/*
 * Load the default values for the table-like connectivity node selection display.
 */
function loadDefaultNoiseValues() {
	$.ajax({  	type: "POST", 
    			async: true,
				url: '/spatial/noiseconfiguration/load_initial_values',
				traditional: true,
                success: function(r) {
                	var nodesData = $.parseJSON(r);
				    for (var i = 0; i < nodesData[0].length; i++) {
				    	var displayedValue = '[';
				    	for (var j = 0; j < nodesData.length; j++) {
				    		displayedValue += nodesData[j][i] + ' ';
				    	}
				    	displayedValue = displayedValue.slice(0, -1);
						displayedValue += ']';
				        $("#nodeScale" + i).text(displayedValue);
				    }
				    GFUNC_removeAllMatrixFromInterestArea();
                } ,
            });
}

function toggleAndLoadNoise(nodeIndex) {
    toggleSelection(nodeIndex);
    if (GFUNC_isNodeAddedToInterestArea(nodeIndex)) {
        if (GVAR_interestAreaNodeIndexes.length == 1) {
            loadNoiseValuesForConnectivityNode(GVAR_interestAreaNodeIndexes[0]);
        } else if (GVAR_interestAreaNodeIndexes.length > 1) {
            copyNoiseConfig(GVAR_interestAreaNodeIndexes[0], [nodeIndex]);
        }
    }
}


function copyAndLoadNoiseConfig() {
    if (GVAR_interestAreaNodeIndexes.length != 0) {
        copyNoiseConfig(GVAR_interestAreaNodeIndexes[0], GVAR_interestAreaNodeIndexes.slice(1));
        loadNoiseValuesForConnectivityNode(GVAR_interestAreaNodeIndexes[0]);
    }
}


function loadNoiseValuesForConnectivityNode(connectivityNodeIndex) {
    if (connectivityNodeIndex >= 0) {
        doAjaxCall({
            async:false,
            type:'GET',
            url:'/spatial/noiseconfiguration/load_noise_values_for_connectivity_node/' + connectivityNodeIndex,
            success:function (data) {
            	var parsedData = $.parseJSON(data);
            	for (var key in parsedData) {
            		$('#noisevalue__' + key).val(parsedData[key]);
            	}
            }
        });
    }
}



/**
 * Replace the model of the nodes 'to_nodes' with the model of the node 'from_node'.
 *
 * @param fromNode the index of the node from where will be copied the model
 * @param toNodes a list with the nodes indexes for which will be replaced the model
 */
function copyNoiseConfig(fromNode, toNodes) {
    $.ajax({
        async:false,
        type:'POST',
        url:'/spatial/noiseconfiguration/copy_configuration/' + fromNode + '/' + $.toJSON(toNodes),
        success:function (data) { }
    });
}


/**
 * Simplest drawScene
 */
function drawScene() {

	if (GL_zoomSpeed != 0) {
        GL_zTranslation -= GL_zoomSpeed * GL_zTranslation;
        GL_zoomSpeed = 0;
    }
    BASE_PICK_drawBrain(BASE_PICK_brainDisplayBuffers, noOfUnloadedBrainDisplayBuffers);
}