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
 * This file should hold variables and functions that should be shared between all the connectivity views.
 */

/**
 * Function called when Connectivity Page is loaded and ready for initialization.
 */
function GFUN_initializeConnectivityFull() {
        initConnectivitySelectionComponent();

        //Set the mouse listeners for the 3d visualizers: Top DIV, WebGL-edges (div & canvas), WebGL-3D (div & canvas).
        $('#monitorDiv').mousewheel(function(event, delta) { return _customMouseWheelEvent(delta); });
        $('#canvasDiv').mousewheel(function(event, delta) { return _customMouseWheelEvent(delta); });
        $('#GLcanvas').mousewheel(function(event, delta) { return _customMouseWheelEvent(delta); });
        $('#GLcanvas_3D').mousewheel(function(event, delta) { return _customMouseWheelEvent(delta); });
        $('#canvasDiv_3D').mousewheel(function(event, delta) { return _customMouseWheelEvent(delta); });
        $('#canvasDiv_PLOT').mousewheel(function(event, delta) { return _customMouseWheelEvent(delta); });

        //Draw any additional elements like color picking and hide all tabs but the default one
        ColSch_initColorSchemeParams(GVAR_interestAreaVariables[GVAR_selectedAreaType]['min_val'],
                                     GVAR_interestAreaVariables[GVAR_selectedAreaType]['max_val'], MATRIX_colorTable);
        drawSimpleColorPicker('nodeColorSelector');
        SEL_createOperationsTable();

        $('#leftSideDefaultSelectedTabId').click();   // enable only the first tab so others don't get exported
        $('#rightSideDefaultSelectedTabId').click();
}


function _customMouseWheelEvent(delta) {
    GL_handleMouseWeel(delta);
    GFUNC_updateLeftSideVisualization();
    return false; // prevent default
}

/*
 * -----------------------------------------------------------------------------------------------------
 * -------------The following part of the file contains variables and functions-------------------------
 * -------------related to the connectivity matrix weights and connectivity matrix----------------------
 * -----------------------------------------------------------------------------------------------------
 */
// Used to keep track of the displayed edges. If the value from a certain position (e.g. i, j) from this matrix is 1 than
// between the nodes i and j an edge is drawn in the corresponding 3D visualier 
var GVAR_connectivityMatrix = [];

function GFUNC_storeMinMax(minWeights, maxWeights, minTracts, maxTracts) {
	GVAR_interestAreaVariables[1]['min_val'] = parseFloat(minWeights);
    GVAR_interestAreaVariables[2]['min_val'] = parseFloat(minTracts);
    GVAR_interestAreaVariables[1]['max_val'] = parseFloat(maxWeights);
    GVAR_interestAreaVariables[2]['max_val'] = parseFloat(maxTracts);
}

/**
 * Populate the GVAR_connectivityMatrix with values equal to zero.
 *
 * @param lengthOfConnectivityMatrix the number of rows/columns that has to have the connectivityMatrix.
 */
function GFUNC_initConnectivityMatrix(lengthOfConnectivityMatrix) {//todo-io: check if we can do this init in other places
    for (var i = 0; i < lengthOfConnectivityMatrix; i++) {
        var row = [];
        for (var j = 0; j < lengthOfConnectivityMatrix; j++) {
            row.push(0);
        }
        GVAR_connectivityMatrix.push(row);
    }
}


function GFUNC_recomputeMinMaxW() {
	GVAR_interestAreaVariables[GVAR_selectedAreaType]['max_val'] = -1000000;
	GVAR_interestAreaVariables[GVAR_selectedAreaType]['min_val'] = 1000000;
	for (var i=0; i<GVAR_interestAreaVariables[GVAR_selectedAreaType]['values'].length;i++) {
		for (var j=0; j<GVAR_interestAreaVariables[GVAR_selectedAreaType]['values'][i].length; j++) {
			if (GVAR_interestAreaVariables[GVAR_selectedAreaType]['values'][i][j] < GVAR_interestAreaVariables[GVAR_selectedAreaType]['min_val']) {
				GVAR_interestAreaVariables[GVAR_selectedAreaType]['min_val'] = GVAR_interestAreaVariables[GVAR_selectedAreaType]['values'][i][j];
			}
			if (GVAR_interestAreaVariables[GVAR_selectedAreaType]['values'][i][j] > GVAR_interestAreaVariables[GVAR_selectedAreaType]['max_val']) {
				GVAR_interestAreaVariables[GVAR_selectedAreaType]['max_val'] = GVAR_interestAreaVariables[GVAR_selectedAreaType]['values'][i][j];
			}
		}
	}
}

function GFUNC_initTractsAndWeights(fileWeights, fileTracts) {
	GVAR_interestAreaVariables[1]['values'] = HLPR_readJSONfromFile(fileWeights);
	GVAR_interestAreaVariables[2]['values'] = HLPR_readJSONfromFile(fileTracts);
}


/*
 * --------------------------------------------------------------------------------------------------------
 * -----------------------The next part handles the context menu update -----------------------------------
 * --------------------------------------------------------------------------------------------------------
 */
function GFUNC_updateContextMenu(selectedNodeIndex, selectedNodeLabel, isAnyComingInLinesChecked, isAnyComingOutLinesChecked) {
	/*
	 * When clicking on a new node from the connectivity 3D visualization, create a specific context menu depending on
	 * conditions like (was a node selected, is the node part of interest area, are the lines already drawn)
	 */
    if (selectedNodeIndex == -1) {
        $('#nodeNameId').text("Please select a node...");
        $("#addNodeToInterestAreaItemId").hide();
        $("#stimulusItemId").hide();
        $("#removeNodeFromInterestAreaItemId").hide();
        $("#drawComingOutLinesForSelectedNodeItemId").hide();
        $("#removeComingOutLinesForSelectedNodeItemId").hide();
        $("#drawComingInLinesForSelectedNodeItemId").hide();
        $("#removeComingInLinesForSelectedNodeItemId").hide();
        $("#setCurrentColorForNodeItemId").hide();
    } else {
        $('#nodeNameId').text("Node: " + selectedNodeLabel);
        $('#selectedNodeIndex').val(selectedNodeIndex);

        $("#stimulusItemId").show();

        if (GFUNC_isNodeAddedToInterestArea(selectedNodeIndex)) {
            $("#addNodeToInterestAreaItemId").hide();
            $("#removeNodeFromInterestAreaItemId").show();
        } else {
            $("#addNodeToInterestAreaItemId").show();
            $("#removeNodeFromInterestAreaItemId").hide();
        }

        if (isAnyComingOutLinesChecked) {
            $("#removeComingOutLinesForSelectedNodeItemId").show();
            $("#drawComingOutLinesForSelectedNodeItemId").hide();
        } else {
            $("#removeComingOutLinesForSelectedNodeItemId").hide();
            $("#drawComingOutLinesForSelectedNodeItemId").show();
        }
        if (isAnyComingInLinesChecked) {
            $("#removeComingInLinesForSelectedNodeItemId").show();
            $("#drawComingInLinesForSelectedNodeItemId").hide();
        } else {
            $("#removeComingInLinesForSelectedNodeItemId").hide();
            $("#drawComingInLinesForSelectedNodeItemId").show();
        }

        $("#setCurrentColorForNodeItemId").show();
    }
}

/**
 * jQuery's contextMenu plugin behaves differently on different browsers so here we patch it to
 * make it work; replaced <code>x=e.pageX, y=e.pageY</code> with <code>x=e.clientX, y=e.clientY</code>
 */
function patchContextMenu() {
    $.contextMenu.show = function(t,e) {
        var cmenu=this, x=e.clientX, y=e.clientY;
        cmenu.target = t; // Preserve the object that triggered this context menu so menu item click methods can see it
        if (cmenu.beforeShow()!==false) {
            // If the menu content is a function, call it to populate the menu each time it is displayed
            if (cmenu.menuFunction) {
                if (cmenu.menu) { $(cmenu.menu).remove(); }
                cmenu.menu = cmenu.createMenu(cmenu.menuFunction(cmenu,t),cmenu);
                cmenu.menu.css({display:'none'});
                $(cmenu.appendTo).append(cmenu.menu);
            }
            var $c = cmenu.menu;
            x+=cmenu.offsetX; y+=cmenu.offsetY;
            var pos = cmenu.getPosition(x,y,cmenu,e); // Extracted to method for extensibility
            cmenu.showShadow(pos.x,pos.y,e);
            // Resize the iframe if needed
            if (cmenu.useIframe) {
                $c.find('iframe').css({width:$c.width()+cmenu.shadowOffsetX+cmenu.shadowWidthAdjust,height:$c.height()+cmenu.shadowOffsetY+cmenu.shadowHeightAdjust});
            }
            $c.css( {top:pos.y+"px", left:pos.x+"px", position:"fixed",zIndex:9999} )[cmenu.showTransition](cmenu.showSpeed,((cmenu.showCallback)?function(){cmenu.showCallback.call(cmenu);}:null));
            cmenu.shown=true;
            $(document).one('click',null,function(){cmenu.hide()}); // Handle a single click to the document to hide the menu
        }
    }
}

/*
 * Functions that initialize the points and labels data and variables to hold these are
 * defined below.
 */
// contains the points read from the file 'position.txt' file (the points for the connectivity matrix);
// each element of this array represents an array of 3 elements (the X, Y, Z coordinates of the point).
var GVAR_positionsPoints;
// contains the labels for the points from the connectivity matrix.
var GVAR_pointsLabels = [];
// The intereset area under which this connectivity was saved.
var GVAR_baseSelection = '';

function GVAR_initPointsAndLabels(filePositions) {
	var pointsAndLabels = HLPR_readPointsAndLabels(filePositions);
    GVAR_positionsPoints = pointsAndLabels[0];
    GVAR_pointsLabels = pointsAndLabels[1];
    GVAR_additionalXTranslationStep = -pointsAndLabels[2];
    GVAR_additionalYTranslationStep = -pointsAndLabels[3];
}

/*
 * ----------------------------------------------------------------------------------------------------------
 * ----- Code which allows a user to draw with a different color all the nodes with a positive weight -------
 * ----------------------------------------------------------------------------------------------------------
 */
var GVAR_connectivityNodesWithPositiveWeight = [];

function GFUNC_removeNodeFromNodesWithPositiveWeight(selectedNodeIndex) {
    if (GFUNC_isIndexInNodesWithPositiveWeight(selectedNodeIndex)) {
        var elemIdx = $.inArray(selectedNodeIndex, GVAR_connectivityNodesWithPositiveWeight);
        GVAR_connectivityNodesWithPositiveWeight.splice(elemIdx, 1);
    }
}

function GFUNC_addNodeToNodesWithPositiveWeight(selectedNodeIndex) {
    if (!GFUNC_isIndexInNodesWithPositiveWeight(selectedNodeIndex)) {
        GVAR_connectivityNodesWithPositiveWeight.push(selectedNodeIndex);
    }
}

function GFUNC_isIndexInNodesWithPositiveWeight(nodeIndex) {
    var elemIdx = $.inArray(nodeIndex, GVAR_connectivityNodesWithPositiveWeight);
    return elemIdx != -1;
}

/*
 * ------------------------------------------------------------------------------------------------
 * ----- Method related to handling the interest area of nodes are in the following section -------
 * ------------------------------------------------------------------------------------------------
 */
var GVAR_interestAreaNodeIndexes = [];

function GFUNC_removeNodeFromInterestArea(selectedNodeIndex) {
    if (GFUNC_isNodeAddedToInterestArea(selectedNodeIndex)) {
          var elemIdx = $.inArray(selectedNodeIndex, GVAR_interestAreaNodeIndexes);
        GVAR_interestAreaNodeIndexes.splice(elemIdx,1);
    }
}

function GFUNC_addNodeToInterestArea(selectedNodeIndex) {
    if (!GFUNC_isNodeAddedToInterestArea(selectedNodeIndex)) {
        GVAR_interestAreaNodeIndexes.push(selectedNodeIndex);
    }
}

function GFUNC_isNodeAddedToInterestArea(nodeIndex) {
    var elemIdx = $.inArray(nodeIndex, GVAR_interestAreaNodeIndexes);
    return elemIdx != -1;
}

/*
 * ------------------------------------------------------------------------------------------------
 * ------ Global functions related to selection handling, like saving loading etc. ----------------
 * ------------------------------------------------------------------------------------------------
 */
function GFUNC_doSelectionSave() {
	var selectionName = document.getElementById("currentSelectionName").value;
	var names = [];
	var conSelections_select = document.getElementById('availableSelectionsList');
	for (var i = 1; i < conSelections_select.options.length; i++) {
		names.push(conSelections_select.options[i].text);
	}
	if (selectionName.length > 0) {
		$.ajax({  	type: "POST", 
				url: '/flow/store_connectivity_selection/' + selectionName,
                data: {"selection": GVAR_interestAreaNodeIndexes+'',
                	   "labels": GVAR_pointsLabels+'',
                	   "select_names": names+''},
                success: function(r) {
                	var response = $.parseJSON(r);
                	if (response[0] == true) {
                		SEL_populateAvailableSelections();
	                    displayMessage(response[1], "infoMessage");
	                    var selectionDropdown = document.getElementById('availableSelectionsList');
	                    for (var i = 0; i < selectionDropdown.options.length; i++) {
	                    	if (selectionDropdown.options[i].text == selectionName) {
	                    		selectionDropdown.selectedIndex = i;
	                    		break;
	                    	}
	                    }
                	} else {
                		displayMessage(response[1], "errorMessage");
                	}
                    
                } ,
                error: function(r) {
                    displayMessage("Selection was not saved properly.", "errorMessage");
                }
            });		
	} else {
		displayMessage("Selection name must not be empty.", "errorMessage");
	}
}

function GFUNC_refreshWithNewSelection(selectComp) {
	var selectedOption = selectComp.options[selectComp.selectedIndex];
	var selectionNodes = selectedOption.value.replace('{', '').replace('}', '').split(',');
	for (var i = 0; i < NO_POSITIONS; i++) {
        GFUNC_removeNodeFromInterestArea(i);
	}
	for (var i = 0; i < selectionNodes.length; i++) {
		var idx = GVAR_pointsLabels.indexOf(selectionNodes[i]);
		if (idx >= 0) {
			GFUNC_addNodeToInterestArea(idx);				
		}
	}
	if (selectComp.selectedIndex == 0) {
		//TODO: this could be done differently in case the 'New selection' value is not at first index
		//However in current generation of select component this will always be the case
		document.getElementById('currentSelectionName').value = '';
	} else {
		document.getElementById('currentSelectionName').value = selectedOption.text;		
	}
	refreshTableInterestArea();
	GFUNC_refreshOnContextChange();
	SEL_refreshSelectionTable();
}

/*
 * Methods to add/remove the entire connectivity matrix to the interest area.
 */
function GFUNC_addAllMatrixToInterestArea() {
	for (var i = 0; i < NO_POSITIONS; i++) {
		if (!GFUNC_isNodeAddedToInterestArea(i)) {
	        GFUNC_addNodeToInterestArea(i);
	    }			
	}
	refreshTableInterestArea();
	GFUNC_refreshOnContextChange();
	SEL_refreshSelectionTable();
}

function GFUNC_removeAllMatrixFromInterestArea() {
	for (var i = 0; i < NO_POSITIONS; i++) {
		if (GFUNC_isNodeAddedToInterestArea(i)) {
	        GFUNC_removeNodeFromInterestArea(i);
	    }			
	}
	refreshTableInterestArea();
	GFUNC_refreshOnContextChange();
	SEL_refreshSelectionTable();
}
/*
 * --------------------------------------------------------------------------------------------------
 * -------------Only functions related to changing the tabs are below this point.--------------------
 * --------------------------------------------------------------------------------------------------
 */

/*
 * -------------------------------Right side tab functions below------------------------------------
 */
var GVAR_selectedAreaType = 1;

// contains the data for the two possible visualization tables (weights and tracts)

var GVAR_interestAreaVariables = {
	1 : {'prefix': 'w', 'values':[], 
		 'min_val':0, 
		 'max_val':0,
		 'legend_div_id': 'weights-legend'},
	2 : {'prefix': 't', 'values':[], 
		 'min_val':0, 
		 'max_val':0,
		 'legend_div_id': 'tracts-legend'}
}

function hideRightSideTabs(selectedHref) {
	$(".matrix-switcher li").each(function (listItem){
		$(this).removeClass('active');
	});
	selectedHref.parentElement.className = 'active';
	$(".matrix-viewer").each(function (divElem) {
		$(this).hide();
	});
}

function showWeightsTable() {
	$("#div-matrix-weights").show();
	GVAR_selectedAreaType = 1;
	refreshTableInterestArea();
	MATRIX_colorTable();
}

function showTractsTable() {
	$("#div-matrix-tracts").show();
	GVAR_selectedAreaType = 2;
	refreshTableInterestArea();
	MATRIX_colorTable();
}

function showSelectionTable() {
	$("#matrix-hemispheres-selection-id").show();
	SEL_refreshSelectionTable();
}

/*
 * ------------------------------Left side tab functions below------------------------------------
 */
var CONNECTIVITY_TAB = 1;
var CONNECTIVITY_2D_TAB = 2;
var CONNECTIVITY_3D_TAB = 3;
var CONNECTIVITY_SPACE_TIME_TAB = 4;
var SELECTED_TAB = CONNECTIVITY_TAB;

function GFUNC_updateLeftSideVisualization() {
	if (SELECTED_TAB == CONNECTIVITY_TAB) {
		 drawScene();
	 }
	 if (SELECTED_TAB == CONNECTIVITY_2D_TAB) {
		 C2D_displaySelectedPoints();
	 }
	 if (SELECTED_TAB == CONNECTIVITY_3D_TAB) {
		 drawScene_3D();
	 }
	 if (SELECTED_TAB == CONNECTIVITY_SPACE_TIME_TAB) {
		 drawSceneSpaceTime();
	 }
}

function GFUNC_refreshOnContextChange() {
	 GFUNC_updateLeftSideVisualization();
	 var selection_button = $("#save-selection-button");
	 selection_button.unbind('click');
	 selection_button.bind('click', function(event) {GFUNC_doSelectionSave()});
	 selection_button.removeClass('action-idle');
}

function hideLeftSideTabs(selectedHref) {
	$(".view-switcher li").each(function (listItem) {
		$(this).removeClass('active');
	});
	selectedHref.parentElement.className = 'active';
	$(".monitor-container").each(function (divMonitor) {
		$(this).hide();
        $(this).find('canvas').each(function () {
            if (this.drawForImageExport)            // remove redrawing method such that only current view is exported
                this.drawForImageExport = null;
        });
	});
}

function startConnectivity() {
	$("#monitor-3Dedges-id").show()
        			.find('#GLcanvas')[0].redrawFunctionRef = drawScene;         // interface-like function used in HiRes image exporting
	connectivity_initCanvas();
	connectivity_startGL(false);
	SELECTED_TAB = CONNECTIVITY_TAB;
    $(window).resize(function() {               // resize is called continuously during a resize event
        clearTimeout(this.timeoutForResizing);  // this will only call the function when resizing is done
        this.timeoutForResizing = setTimeout(startConnectivity, 250);
    });
}

function start2DConnectivity(idx) {
	$("#monitor-2D-id").show().find('canvas').each(function() {
        // interface-like methods needed for exporting HiRes images
        this.drawForImageExport = __resizeCanvasBeforeExport;
        this.afterImageExport   = __restoreCanvasAfterExport;
    });
	if (idx == 0) {
		C2D_selectedView = 'left';
		C2D_shouldRefreshNodes = true;
	}
	if (idx == 1) {
		C2D_selectedView = 'both';
		C2D_shouldRefreshNodes = true;
	} 
	if (idx == 2) {
		C2D_selectedView = 'right';
		C2D_shouldRefreshNodes = true;
	}
	C2D_displaySelectedPoints();
	SELECTED_TAB = CONNECTIVITY_2D_TAB;
}

function start3DConnectivity() {
	$("#monitor-3D-id").show()
        .find('#GLcanvas_3D')[0].redrawFunctionRef = drawScene_3D;   // interface-like function used in HiRes image exporting
	connectivity3D_initCanvas();
	connectivity3D_startGL();
	SELECTED_TAB = CONNECTIVITY_3D_TAB;
    $(window).resize(function() {               // resize is called continuously during a resize event
        clearTimeout(this.timeoutForResizing);  // this will only call the function when resizing is done
        this.timeoutForResizing = setTimeout(start3DConnectivity, 250);
    });
}

function startMPLH5ConnectivityView() {
	$("#monitor-mplh5").show();
    initMPLH5CanvasForExportAsImage(mplh5_figureNo)
}

function startSpaceTimeConnectivity() {
	$("#monitor-plot-id").show()
        .find('#GLcanvas_SPACETIME')[0].redrawFunctionRef = drawSceneSpaceTime;   // interface-like function used in HiRes image exporting
	conectivitySpaceTime_initCanvas();
	connectivitySpaceTime_startGL();
	SELECTED_TAB = CONNECTIVITY_SPACE_TIME_TAB;
}

