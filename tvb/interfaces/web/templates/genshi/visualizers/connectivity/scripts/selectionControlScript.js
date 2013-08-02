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
 * Variables and functions for simple not selection updates are defined below.
 */

function SEL_toggleNodeSelection(tableElement) {
	var selectedNode = parseInt(tableElement.id.replace('nodeSelection', ''));
	if (GFUNC_isNodeAddedToInterestArea(selectedNode)) {
		GFUNC_removeNodeFromInterestArea(selectedNode);
	} else {
		GFUNC_addNodeToInterestArea(selectedNode);
	}
	SEL_refreshSelectionTable();
	GFUNC_refreshOnContextChange();
}

function SEL_loadSelectionFromText() {
	var textAreaValue = document.getElementById('selection-text-area').value.replace('[', '').replace(']', '');
	var nodes = textAreaValue.split(',');
	var selectionOk = true;
	var errorTxt = 'Invalid node names:';
	for (var i = 0; i < nodes.length; i++) {
		if (GVAR_pointsLabels.indexOf(nodes[i]) == -1) {
			errorTxt = errorTxt + ' ' + nodes[i];
			selectionOk = false;
		}
	}
	if (selectionOk == false) {
		displayMessage(errorTxt, "errorMessage");
		return false;
	} else {
		displayMessage('Load succesfull.', "infoMessage");
		for (var i = 0; i < GVAR_pointsLabels.length; i++) {
			if (nodes.indexOf(GVAR_pointsLabels[i]) >= 0) {
				GFUNC_addNodeToInterestArea(i);
			} else {
				GFUNC_removeNodeFromInterestArea(i);
			}
		}
		SEL_refreshSelectionTable();
		GFUNC_refreshOnContextChange();
		refreshTableInterestArea();
	}
}

function SEL_refreshSelectionTable() {
	var selectionString = '[';
	for (var i = 0; i < GVAR_pointsLabels.length; i++) {
		if (GFUNC_isNodeAddedToInterestArea(i)) {
			selectionString = selectionString + GVAR_pointsLabels[i] + ',';
			$('#nodeSelection'+i).addClass('selected');
		} else {
			$('#nodeSelection'+i).removeClass('selected');
		}
	}
	if (selectionString.length > 2) 
		selectionString = selectionString.substring(0, selectionString.length-1) + ']'
	else selectionString = selectionString + ']'
	document.getElementById('selection-text-area').value = selectionString;
}

function SEL_populateAvailableSelections() {
    var connectivityGid = $("#connectivityGid").val();
	$.ajax({type: "POST",
			async: false, 
			url: '/flow/get_available_selections',
			data: {'con_selection': GVAR_baseSelection+'',
				   'con_labels': GVAR_pointsLabels+'',
                   'connectivity_gid': connectivityGid},
            success: function(r) {
                document.getElementById("selections-display-area").innerHTML = r;
            } ,
            error: function(r) {
                displayMessage("Error while retrieving available selections.", "errorMessage");
            }
        });
}

/**
 * This method should be called in order to init the selection component.
 * Make sure that before calling this method all the needed data
 * is loaded (specially the data related to the selected connectivity).
 */
function initConnectivitySelectionComponent() {
    $(document).ready(function () {
        $(function () {
            SEL_populateAvailableSelections();
            GFUNC_refreshWithNewSelection(document.getElementById('availableSelectionsList'));
        });
    });
}

/*
 * Variables and function for selecting and applying operations are defined below
 */

/*
 * The following constants define a operation done between nodes:
 * 1 - that are both in the interest area
 * 2 - that have the source in interest area and destination outside
 * 3 - that have the source outside interest area and destination inside
 */
SEL_INTER_OPERATION = 1;
SEL_EXIT_OPERATION = 2;
SEL_ENTER_OPERATION = 3;
SEL_OUTER_OPERATION = 4;

/*
 * Just dummy functions used for testing new 'selection operation' To be removed after.
 */

function divideSelectionBy(input, quantity) {
	output = input / quantity;
	return output;
}

function multiplySelectionWith(input, quantity) {
	output = input * quantity;
	return output;
}

function addToSelection(input, quantity) {
	output = input + quantity
	return output;
}

function decreaseSelection(input, quantity) {
	output = input - quantity;
	return output;
}

function setSelection(input, quantity) {
	output = quantity;
	return output;
}

OP_DICTIONARY ={ 1 : { 'name': 'Set(n)', 'operation': setSelection },
				 2 : { 'name': 'Add(n)', 'operation': addToSelection },
				 3 : { 'name': 'Decrease(n)', 'operation': decreaseSelection },
				 4 : { 'name': 'Multiply(n)', 'operation': multiplySelectionWith },
				 5 : { 'name': 'Divide(n)', 'operation': divideSelectionBy } }
				 
EDGES_TYPES = { 1 : 'In --> In',
				2 : 'In --> Out',
				3 : 'Out --> In',
				4 : 'Out --> Out' }
				

function SEL_createOperationsTable() {
	var operationsSelect = document.getElementById("con-op-operation");
	for (index in OP_DICTIONARY) {
		var option = new Option(OP_DICTIONARY[index]['name'], index);
		operationsSelect.options[operationsSelect.options.length] = option;
	}
	
	var edgesTypeSelect = document.getElementById("con-op-edges-type");
	for (index in EDGES_TYPES) {
		var option = new Option(EDGES_TYPES[index], index);
		edgesTypeSelect.options[edgesTypeSelect.options.length] = option;
	}
}

function getOperationArguments() {
	//TODO: if new functions will be needed with multiple arguments this should be edited
	return parseFloat(document.getElementById('con-op-arguments').value);
}

function doGroupOperation() {
	//Selected operation
	var operationsSelect = document.getElementById('con-op-operation');
	var selectedOp = parseInt(operationsSelect.options[operationsSelect.selectedIndex].value);
	selectedOp = OP_DICTIONARY[selectedOp]['operation']
	//Selected edges type
	var edgesSelect = document.getElementById('con-op-edges-type');
	var selectedEdgeType = parseInt(edgesSelect.options[edgesSelect.selectedIndex].value);
	//Arguments and results label
	var quantity = getOperationArguments(); 
	
	document.getElementById('con-op-arguments').value = '';
	if (isNaN(quantity)) {
		displayMessage("Operation failed. Be sure you provided the correct arguments.", "errorMessage");
		return false;
	}
	//TODO: if we want to add operation on tracts we should change the '1' with some passed value to indicate weight or tract
	try {
		for (var i=0; i<GVAR_interestAreaVariables[1]['values'].length;i++) {
			for (var j=0; j<GVAR_interestAreaVariables[1]['values'][i].length; j++) {
				switch(selectedEdgeType) {
				case 1: {
				  if (GFUNC_isNodeAddedToInterestArea(i) && GFUNC_isNodeAddedToInterestArea(j)) {
						GVAR_interestAreaVariables[1]['values'][i][j] = selectedOp(GVAR_interestAreaVariables[1]['values'][i][j], quantity)
					} break; }
				case 2: {
				  if (GFUNC_isNodeAddedToInterestArea(i) && !GFUNC_isNodeAddedToInterestArea(j)) {
						GVAR_interestAreaVariables[1]['values'][i][j] = selectedOp(GVAR_interestAreaVariables[1]['values'][i][j], quantity)
					} break; }
				case 3: {
				  if (!GFUNC_isNodeAddedToInterestArea(i) && GFUNC_isNodeAddedToInterestArea(j)) {
						GVAR_interestAreaVariables[1]['values'][i][j] = selectedOp(GVAR_interestAreaVariables[1]['values'][i][j], quantity)
					} break; }
				case 4: {
				  if (!GFUNC_isNodeAddedToInterestArea(i) && !GFUNC_isNodeAddedToInterestArea(j)) {
						GVAR_interestAreaVariables[1]['values'][i][j] = selectedOp(GVAR_interestAreaVariables[1]['values'][i][j], quantity)
					} break; }
				}
			}
		}
		GFUNC_recomputeMinMaxW();
		MATRIX_colorTable();
		var objToday = new Date(),
        weekday = new Array('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'),
        dayOfWeek = weekday[objToday.getDay()],
        domEnder = new Array( 'th', 'st', 'nd', 'rd', 'th', 'th', 'th', 'th', 'th', 'th' ),
        dayOfMonth = today + (objToday.getDate() < 10) ? '0' + objToday.getDate() + domEnder[objToday.getDate()] : objToday.getDate() + domEnder[parseFloat(("" + objToday.getDate()).substr(("" + objToday.getDate()).length - 1))],
        months = new Array('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'),
        curMonth = months[objToday.getMonth()],
        curYear = objToday.getFullYear(),
        curHour = objToday.getHours() > 12 ? objToday.getHours() - 12 : (objToday.getHours() < 10 ? "0" + objToday.getHours() : objToday.getHours()),
        curMinute = objToday.getMinutes() < 10 ? "0" + objToday.getMinutes() : objToday.getMinutes(),
        curSeconds = objToday.getSeconds() < 10 ? "0" + objToday.getSeconds() : objToday.getSeconds(),
        curMeridiem = objToday.getHours() > 12 ? "PM" : "AM";
		var today = curHour + ":" + curMinute + "." + curSeconds + curMeridiem + " " + dayOfWeek + " " + dayOfMonth + " of " + curMonth + ", " + curYear;
		displayMessage("Operation finished successfull at " + today + ".", "infoMessage");
	} catch(err) {
		displayMessage("Operation failed. Be sure you provided the correct arguments.", "errorMessage");
	}
}


