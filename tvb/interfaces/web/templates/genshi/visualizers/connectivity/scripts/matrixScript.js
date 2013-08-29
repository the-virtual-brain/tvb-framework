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
 * This file handles the display and functionality of the 2d table view
 */
/*
 * Used to keep track of the start and end point for each quadrant.
 */
var startPointsX = [];
var endPointsX = [];
var startPointsY = [];
var endPointsY = [];

/*
 * Keep references to the last edited element, element color, and element class.
 * To be used for switching back to the original after an edit is performed.
 */
var lastEditedElement = null;
var lastElementColor = null;
var lastElementClass = null;

/**
 * Get the position of a element in the page. Used when finding out the position where the 
 * menu with information about a specific edge should be displayed.
 * 
 * @param elem - the element for which you want the absolute position in the page
 * 
 * @return a dictionary of the form {x: 'value of x offset', y: 'value of y offset'}
 */
function getMenuPosition(elem, contextMenuDiv){  
   
	var posX = 210;  // Default offset
	var posY = 15;  
	                
	while(elem != null){  
    	posX += elem.offsetLeft;  
	    posY += elem.offsetTop;  
	    elem = elem.offsetParent;  
	} 
	var $w = $("#scrollable-matrix-section");
	posY -= $w.scrollTop(); 
	if ($w[0].offsetTop > 0) {
		posY -= $w[0].offsetTop;
		posY -= ($("#main").scrollTop() - $w[0].offsetTop);
	}
	//posX -= $w.scrollLeft()
	
	var mh = 214; //$(contextMenuDiv).height();
	var mw = 200; //$(contextMenuDiv).width() 
	var ww = $("body").width() - 15;
	var wh = Math.max($(window).height(), $w.height());
	
	var maxRight = posX;
	if (maxRight > ww) { 
		posX -= (maxRight - ww); 
	}
	
	var dir = "down";
	if (posY + mh > wh) { 
		dir = "up"; 
	}
	if (dir == "up") { 
		posY -= (mh + 25); 
	}
	return {x : posX, y : posY };  
} 

/**
 * Method called on the click event of a table box that represents a certain node from the connectivity matrix
 *
 * @param table_elem the dom element which fired the click event
 */
function changeSingleCell(table_elem, i, j) {
	
	var inputDiv = document.getElementById('editNodeValues');
	if (!(GFUNC_isNodeAddedToInterestArea(i) && GFUNC_isNodeAddedToInterestArea(j))) {
		displayMessage("The node you selected is not in the current interest area!", "warningMessage");
	}
	if (inputDiv.style.display == 'none') {
		inputDiv.style.display = 'block';	
	} else {			
		lastEditedElement.className = lastElementClass;
	}
	lastEditedElement = table_elem;
	lastElementClass = table_elem.className;
	table_elem.className = "node edited";
	element_position = getMenuPosition(table_elem, inputDiv);
	inputDiv.style.position = 'fixed';
	inputDiv.style.left = element_position.x + 'px';
	inputDiv.style.top = element_position.y + 'px';
	
	var labelInfoSource = document.getElementById('selectedSourceNodeDetails');
	var labelInfoTarget = document.getElementById('selectedTargetNodeDetails');
	var descriptionText = GVAR_pointsLabels[i];
	if (labelInfoSource != null && labelInfoSource != undefined) {
		labelInfoSource.innerHTML = descriptionText;		
	}
	descriptionText = GVAR_pointsLabels[j];
	if (labelInfoTarget != null && labelInfoTarget != undefined) {
		labelInfoTarget.innerHTML = descriptionText;
	}
	
	var inputText = document.getElementById('weightsValue');
	inputText.value = GVAR_interestAreaVariables[GVAR_selectedAreaType]['values'][i][j];
	
	var hiddenNodeField = document.getElementById('currentlyEditedNode');
	hiddenNodeField.value = table_elem.id;
	MATRIX_colorTable();
}


/**
 * Method called when the 'Save' button from the context menu is pressed.
 * If a valid float is recieverm store the value in the weights matrix and if not
 * display an error message. Either way close the details context menu.
 */
function saveNodeDetails() {
	var inputText = document.getElementById('weightsValue');
	var newValue = parseFloat($.trim(inputText.value));
	if (isNaN(newValue)) {
		displayMessage('The value you entered is not a valid float. Original value is kept.', 'warningMessage');
    	var hiddenNodeField = document.getElementById('currentlyEditedNode');
		var tableNodeID = hiddenNodeField.value;
    	table_element = document.getElementById(tableNodeID);
		table_element.className = lastElementClass;
	} else {	
		//displayMessage('')
		var hiddenNodeField = document.getElementById('currentlyEditedNode');
		var tableNodeID = hiddenNodeField.value;
		var indexes = tableNodeID.split("td_" + GVAR_interestAreaVariables[GVAR_selectedAreaType]['prefix'] + '_')[1].split("_");
		table_element = document.getElementById(tableNodeID);
		table_element.className = lastElementClass;
		if (newValue > GVAR_interestAreaVariables[GVAR_selectedAreaType]['max_val']) {
			GVAR_interestAreaVariables[GVAR_selectedAreaType]['max_val'] = newValue;
			CONN_initLinesHistorgram();
		}
		if (newValue < 0) {
			newValue = 0;
		}
		if (newValue < GVAR_interestAreaVariables[GVAR_selectedAreaType]['min_val']) {
			GVAR_interestAreaVariables[GVAR_selectedAreaType]['min_val'] = newValue;
			CONN_initLinesHistorgram();
		}
		if (GVAR_interestAreaVariables[GVAR_selectedAreaType]['values'][indexes[0]][indexes[1]] == GVAR_interestAreaVariables[GVAR_selectedAreaType]['max_val']) {
			GVAR_interestAreaVariables[GVAR_selectedAreaType]['values'][indexes[0]][indexes[1]] = newValue;
			GVAR_interestAreaVariables[GVAR_selectedAreaType]['max_val'] = 0;
			for (var i=0; i<GVAR_interestAreaVariables[GVAR_selectedAreaType]['values'].length; i++) {
				for (var j=0; j<GVAR_interestAreaVariables[GVAR_selectedAreaType]['values'].length; j++) {
					if (GVAR_interestAreaVariables[GVAR_selectedAreaType]['values'][i][j] > GVAR_interestAreaVariables[GVAR_selectedAreaType]['max_val']) { GVAR_interestAreaVariables[GVAR_selectedAreaType]['max_val'] = GVAR_interestAreaVariables[GVAR_selectedAreaType]['values'][i][j];}
				}
			}
			CONN_initLinesHistorgram();
		}
		else {
			if (GVAR_interestAreaVariables[GVAR_selectedAreaType]['values'][indexes[0]][indexes[1]] == 0 && newValue > 0) {
				CONN_comingInLinesIndices[indexes[1]].push(parseInt(indexes[0]));
				CONN_comingOutLinesIndices[indexes[0]].push(parseInt(indexes[1]));
			} 
			if (GVAR_interestAreaVariables[GVAR_selectedAreaType]['values'][indexes[0]][indexes[1]] > 0 && newValue == 0) {
				HLPR_removeByElement(CONN_comingInLinesIndices[indexes[1]], parseInt(indexes[0]));
				HLPR_removeByElement(CONN_comingOutLinesIndices[indexes[0]], parseInt(indexes[1]));
			}			
			GVAR_interestAreaVariables[GVAR_selectedAreaType]['values'][indexes[0]][indexes[1]] = newValue;
			CONN_lineWidthsBins[indexes[0]][indexes[1]] = CONN_getLineWidthValue(newValue);
		}	
	}
	var inputDiv = document.getElementById('editNodeValues');
	inputDiv.style.display = 'none';	
	lastElementClass = null;
	lastEditedElement = null;
	lastElementColor = null;
	
	MATRIX_colorTable();
	GFUNC_refreshOnContextChange();
}


/**
 * Hide the details context menu that pops up aside a edited element. This
 * method is called when pressing the 'Cancel' button or when clicking outside the table/canvas.
 */
function hideNodeDetails() {
	var inputDiv = document.getElementById('editNodeValues');
	var hiddenNodeField = document.getElementById('currentlyEditedNode');
	var tableNodeID = hiddenNodeField.value;
	if (tableNodeID != undefined && tableNodeID != null && tableNodeID != "") {
		inputDiv.style.display = 'none';
		if (lastEditedElement != undefined && lastEditedElement != null) {
			lastEditedElement.className = lastElementClass;
			lastEditedElement.style.backgroundColor = lastElementColor;			
		}
		hiddenNodeField.value = null;
		lastElementClass = null;
		lastEditedElement = null;	
		lastElementColor = null;
		MATRIX_colorTable();
	}
}

/**
 * Method used to toggle between show/hide in-going lines. Used from the details context menu 
 * aside a edited element.
 * 
 * @param index - specified which of the two nodes is the one for which to make the toggle,
 * 				  0 = source node, 1 = destination node
 */
function toggleIngoingLines(index) {
	var hiddenNodeField = document.getElementById('currentlyEditedNode');
	var indexes = hiddenNodeField.value.split("td_" + GVAR_interestAreaVariables[GVAR_selectedAreaType]['prefix'] + '_')[1].split("_");
	start_hemisphere_idx = null
	for (var i=0; i<startPointsY.length - 1; i++) {
		if (indexes[index] >= startPointsY[i] && indexes[index] <= startPointsY[i + 1]){
			start_hemisphere_idx = startPointsY[i];
		}
	}
	if (start_hemisphere_idx == null) {
		start_hemisphere_idx = startPointsY[startPointsY.length - 1];
	}
	end_hemisphere_idx = null
	for (var i=0; i<endPointsY.length - 1; i++) {
		if (indexes[index] >= endPointsY[i] && indexes[index] <= endPointsY[i + 1]){
			end_hemisphere_idx = endPointsY[i + 1];
		}
	}
	if (end_hemisphere_idx == null) {
		end_hemisphere_idx = endPointsY[endPointsY.length - 1];
	}	
	
	for (var i=0; i<NO_POSITIONS; i++) {
		if (GVAR_interestAreaVariables[GVAR_selectedAreaType]['values'][i][indexes[index]] > 0) {
            if (GVAR_connectivityMatrix[i][indexes[index]] == 1) {
            	GVAR_connectivityMatrix[i][indexes[index]] = 0;
            } else {
            	GVAR_connectivityMatrix[i][indexes[index]] = 1;
            }
        }
       else {
       		GVAR_connectivityMatrix[i][indexes[index]] = 0;
       }     
      }
    GFUNC_updateLeftSideVisualization();
}

/**
 * Method used to toggle between show/hide outgoing lines. Used from the details context menu 
 * aside a edited element.
 * 
 * @param index - specified which of the two nodes is the one for which to make the toggle,
 * 				  0 = source node, 1 = destination node
 */
function toggleOutgoingLines(index) {
	var hiddenNodeField = document.getElementById('currentlyEditedNode');
	var indexes = hiddenNodeField.value.split("td_" + GVAR_interestAreaVariables[GVAR_selectedAreaType]['prefix'] + '_')[1].split("_");
	start_hemisphere_idx = null
	for (var i=0; i<startPointsX.length - 1; i++) {
		if (indexes[index] >= startPointsX[i] && indexes[index] <= startPointsX[i + 1]){
			start_hemisphere_idx = startPointsX[i];
		}
	}
	if (start_hemisphere_idx == null) {
		start_hemisphere_idx = startPointsX[startPointsX.length - 1];
	}
	end_hemisphere_idx = null
	for (var i=0; i<endPointsX.length - 1; i++) {
		if (indexes[index] >= endPointsX[i] && indexes[index] <= endPointsX[i + 1]){
			end_hemisphere_idx = endPointsX[i + 1];
		}
	}
	if (end_hemisphere_idx == null) {
		end_hemisphere_idx = endPointsX[endPointsX.length - 1];
	}	
	
	for (var i=0; i<NO_POSITIONS; i++) {
			if (GVAR_interestAreaVariables[GVAR_selectedAreaType]['values'][indexes[index]][i] > 0 ) {
	            if (GVAR_connectivityMatrix[indexes[index]][i] == 1) {
	            	GVAR_connectivityMatrix[indexes[index]][i] = 0;
	            } else {
	            	GVAR_connectivityMatrix[indexes[index]][i] = 1;
	            }
            }
            else {
            	GVAR_connectivityMatrix[indexes[index]][i] = 0;
            }
        }	
    GFUNC_updateLeftSideVisualization();
}

/**
 * Method used to cut ingoing lines. Used from the details context menu 
 * aside a edited element.
 * 
 * @param index - specified which of the two nodes is the one for which to make the cut,
 * 				  0 = source node, 1 = destination node
 */
function cutIngoingLines(index) {
	var hiddenNodeField = document.getElementById('currentlyEditedNode');
	var indexes = hiddenNodeField.value.split("td_" + GVAR_interestAreaVariables[GVAR_selectedAreaType]['prefix'] + '_')[1].split("_");
	start_hemisphere_idx = null
	for (var i=0; i<startPointsY.length - 1; i++) {
		if (indexes[index] >= startPointsY[i] && indexes[index] <= startPointsY[i + 1]){
			start_hemisphere_idx = startPointsY[i];
		}
	}
	if (start_hemisphere_idx == null) {
		start_hemisphere_idx = startPointsY[startPointsY.length - 1];
	}
	end_hemisphere_idx = null
	for (var i=0; i<endPointsY.length - 1; i++) {
		if (indexes[index] >= endPointsY[i] && indexes[index] <= endPointsY[i + 1]){
			end_hemisphere_idx = endPointsY[i + 1];
		}
	}
	if (end_hemisphere_idx == null) {
		end_hemisphere_idx = endPointsY[endPointsY.length - 1];
	}	
	
	for (var i=0; i<NO_POSITIONS; i++) {
        	GVAR_connectivityMatrix[i][indexes[index]] = 0;
        }
    for (var i=0; i<NO_POSITIONS; i++) {
    	if (GVAR_interestAreaVariables[GVAR_selectedAreaType]['values'][i][indexes[index]] > 0){
    		HLPR_removeByElement(CONN_comingInLinesIndices[indexes[index]], parseInt(i));
			HLPR_removeByElement(CONN_comingOutLinesIndices[i], parseInt(indexes[index]));
    	}
    	GVAR_interestAreaVariables[GVAR_selectedAreaType]['values'][i][indexes[index]] = 0;
    }
    MATRIX_colorTable();
	GFUNC_refreshOnContextChange();
}

/**
 * Method used to cut outgoing lines. Used from the details context menu 
 * aside a edited element.
 * 
 * @param index - specified which of the two nodes is the one for which to make the cut,
 * 				  0 = source node, 1 = destination node
 */
function cutOutgoingLines(index) {
	var hiddenNodeField = document.getElementById('currentlyEditedNode');
	var indexes = hiddenNodeField.value.split("td_" + GVAR_interestAreaVariables[GVAR_selectedAreaType]['prefix'] + '_')[1].split("_");
	start_hemisphere_idx = null
	for (var i=0; i<startPointsX.length - 1; i++) {
		if (indexes[index] >= startPointsX[i] && indexes[index] <= startPointsX[i + 1]){
			start_hemisphere_idx = startPointsX[i];
		}
	}
	if (start_hemisphere_idx == null) {
		start_hemisphere_idx = startPointsX[startPointsX.length - 1];
	}
	end_hemisphere_idx = null
	for (var i=0; i<endPointsX.length - 1; i++) {
		if (indexes[index] >= endPointsX[i] && indexes[index] <= endPointsX[i + 1]){
			end_hemisphere_idx = endPointsX[i + 1];
		}
	}
	if (end_hemisphere_idx == null) {
		end_hemisphere_idx = endPointsX[endPointsX.length - 1];
	}	
	
	for (var i=0; i<NO_POSITIONS; i++) {
		if (GVAR_interestAreaVariables[GVAR_selectedAreaType]['values'][indexes[index]][i] > 0){
    		HLPR_removeByElement(CONN_comingInLinesIndices[i], parseInt(indexes[index]));
			HLPR_removeByElement(CONN_comingOutLinesIndices[indexes[index]], parseInt(i));
    	}
        GVAR_connectivityMatrix[indexes[index]][i] = 0;
    	GVAR_interestAreaVariables[GVAR_selectedAreaType]['values'][indexes[index]][i] = 0;
    }	
    MATRIX_colorTable();
	GFUNC_refreshOnContextChange();
}



function refreshTableInterestArea() {
    if ($('#div-matrix-tracts').length > 0) {
        for (var i = 0; i < NO_POSITIONS; i++) {
            updateNodeInterest(i);
        }
    }
}

/**
 * For a given node index update the style of the table correspondingly.
 */
function updateNodeInterest(nodeIdx) {
	var isInInterest = GFUNC_isNodeAddedToInterestArea(nodeIdx);
	var upperSideButtons = $("th[id^='upper_change_" + nodeIdx + "_']");
	var leftSideButtons = $("td[id^='left_change_" + nodeIdx + "_']");    
    
    for (var k = 0; k < upperSideButtons.length; k++) {
	    if (isInInterest == true) {
    		upperSideButtons[k].className = 'selected';
    	} else {
    		upperSideButtons[k].className = '';
    	}	
    }
    
    for (var k = 0; k < leftSideButtons.length; k++) {
	    if (isInInterest == true) {
    		leftSideButtons[k].className = 'identifier selected';
    	} else {
    		leftSideButtons[k].className = 'identifier';
    	}	
    }    
    
    for (var i=0; i<NO_POSITIONS; i++){	
    	horiz_table_data_id = 'td_' + GVAR_interestAreaVariables[GVAR_selectedAreaType]['prefix'] + '_' + nodeIdx + '_' + i;
    	vertical_table_data_id = 'td_' + GVAR_interestAreaVariables[GVAR_selectedAreaType]['prefix'] + '_' + i + '_' + nodeIdx;
    	horiz_table_element = document.getElementById(horiz_table_data_id);
    	vertical_table_element = document.getElementById(vertical_table_data_id);
	    if (isInInterest && GFUNC_isNodeAddedToInterestArea(i)) {
	       	vertical_table_element.className = 'node selected';
	    	horiz_table_element.className = 'node selected'; 		
    	}
    	else {
			vertical_table_element.className = 'node';
		    horiz_table_element.className = 'node';     		
    	}	
    }
}

/**
 * Method called when clicking on a node index from the top column. Change the entire column
 * associated with that index
 *
 * @param domElem the dom element which fired the click event
 */  
function changeEntireColumn(domElem) {
	var index = domElem.id.split("upper_change_")[1];
	index = parseInt(index.split('_')[0]);
	if (GFUNC_isNodeAddedToInterestArea(index)) {
		GFUNC_removeNodeFromInterestArea(index);
	} else {
		GFUNC_addNodeToInterestArea(index);	
	}
	updateNodeInterest(index);
	SEL_refreshSelectionTable(); 
    GFUNC_refreshOnContextChange();
}


/**
 * Method called when clicking on a node label from the left column. Change the entire row
 * associated with that index
 *
 * @param domElem the dom element which fired the click event
 */  
function changeEntireRow(domElem) {
	var index = domElem.id.split("left_change_")[1];
	index = parseInt(index.split('_')[0]);
	if (GFUNC_isNodeAddedToInterestArea(index)) {
		GFUNC_removeNodeFromInterestArea(index);
	} else {
		GFUNC_addNodeToInterestArea(index);
	}
	updateNodeInterest(index);
	SEL_refreshSelectionTable(); 
    GFUNC_refreshOnContextChange();
}


/**
 * Helper methods that store information used when the colorTable method is called
 */

function TBL_storeHemisphereDetails(newStartPointsX, newEndPointsX, newStartPointsY, newEndPointsY) {
	startPointsX = eval(newStartPointsX);
	endPointsX = eval(newEndPointsX);
	startPointsY = eval(newStartPointsY);
	endPointsY = eval(newEndPointsY);
}

/**
 * Function to update the legend colors; the gradient will be created only after the table was drawn
 * so it will have the same size as the table matrix
 * @private
 */
function _updateLegendColors(){
	var div_id = GVAR_interestAreaVariables[GVAR_selectedAreaType]['legend_div_id'];
	var legendDiv = document.getElementById(div_id);

	var height = Math.max($("#div-matrix-weights")[0].clientHeight, $("#div-matrix-tracts")[0].clientHeight);
    ColSch_updateLegendColors(legendDiv, height);

    ColSch_updateLegendLabels('#table-' + div_id, GVAR_interestAreaVariables[GVAR_selectedAreaType]['min_val'],
                              GVAR_interestAreaVariables[GVAR_selectedAreaType]['max_val'], height)
}


/**
 * Method that colors the entire table.
 */
function MATRIX_colorTable() {
    var prefix_id = GVAR_interestAreaVariables[GVAR_selectedAreaType]['prefix'];
    var dataValues = GVAR_interestAreaVariables[GVAR_selectedAreaType]['values'];
    var minValue = GVAR_interestAreaVariables[GVAR_selectedAreaType]['min_val'];
    var maxValue = GVAR_interestAreaVariables[GVAR_selectedAreaType]['max_val'];

    for (var hemisphereIdx=0; hemisphereIdx<startPointsX.length; hemisphereIdx++)
	{
		var startX = startPointsX[hemisphereIdx];
		var endX = endPointsX[hemisphereIdx];
		var startY = startPointsY[hemisphereIdx];
		var endY = endPointsY[hemisphereIdx];

		for (var i=startX; i<endX; i++)
			for (var j=startY; j<endY; j++) {
				var tableDataID = 'td_' + prefix_id + '_' + i + '_' + j;
				var tableElement = document.getElementById(tableDataID);
				if (dataValues)
                    tableElement.style.backgroundColor = getGradientColorString(dataValues[i][j], minValue, maxValue);
			}
	}
	_updateLegendColors();
}

function saveChanges() {
    // clone the weights matrix
    $("#newWeightsId").val($.toJSON(GVAR_interestAreaVariables[1]['values']));
    $("#newTractsId").val($.toJSON(GVAR_interestAreaVariables[2]['values']));
    $("#interestAreaNodeIndexesId").val($.toJSON(GVAR_interestAreaNodeIndexes));
    $("#experimentFormId").submit();
}



