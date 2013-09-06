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

// ---------------------------------------------------------
//              GENERIC FUNCTIONS
// ---------------------------------------------------------

function displayMessage(msg, className) {
    // Change the content and style class for Message DIV.
    var messagesDiv = $("#messageDiv");
    messagesDiv.empty();
    messagesDiv.append(msg);
    if (className == 'errorMessage'){
    	className = 'msg-sticky msg-level-fatal';
    } else if (className =='warningMessage') {
    	className = 'msg-transient transient-medium msg-level-warn';
    } else {
    	className = 'msg-transient msg-level-info';
    }
    
    var messageDivParent = document.getElementById("messageDivParent");	
    if (messageDivParent) {
	    messageDivParent.className = className;
	    $(messageDivParent.parentNode).html($(messageDivParent.parentNode).html())
    } else {
    	messageDivParent = $("#generic-message");
    	messageDivParent.removeClass('no-message');
    	messageDivParent.className = className;
    }
}

function checkForIE() {
	var browserName=navigator.appName;
	var msg;
	if (browserName=="Microsoft Internet Explorer") {
	  	msg = "Internet Explorer is not supported. Please use Google Chrome, Mozilla Firefox or Apple Safari.";
	 	displayMessage("Internet Explorer is not supported. Please use Google Chrome, Mozilla Firefox or Apple Safari.", 'errorMessage')
	 }	
}

function get_URL_param(param) {
   var search = window.location.search.substring(1);
   var compareKeyValuePair = function(pair) {
      var key_value = pair.split('=');
      var decodedKey = decodeURIComponent(key_value[0]);
      var decodedValue = decodeURIComponent(key_value[1]);
      if(decodedKey == param) return decodedValue;
      return null;
   };

   var comparisonResult = null;

   if(search.indexOf('&') > -1) {
      var params = search.split('&');
      for(var i = 0; i < params.length; i++) {
         comparisonResult = compareKeyValuePair(params[i]);
         if(comparisonResult !== null) {
            break;
         }
      }
   } else {
      comparisonResult = compareKeyValuePair(search);
   }

   return comparisonResult;
}

// Functions for pagination
function changeDisplayPage(page, formId) {
    // Change hidden current_page and submit
    document.getElementById("currentPage").value = page;
    document.getElementById(formId).submit();
}

// Functions for TAB accessibility.
// This was a work-around for FF compatibility.
var pressedKey = 0;

function setUpKeyWatch(){
	$(document.documentElement).keydown(function (event) {
	  pressedKey = event.keyCode;
	  return true;
	});	
}
	
function redirectToHrefChild(redirectPage) {
   if (pressedKey == 13) {
   		var children = redirectPage.children;
	    for (var i=0; i < children.length; i++) {
				if (children[i].tagName == "A") {
					window.location = children[i].href;
					children[i].onclick();
					break;
				}
			}
	   } 
 }
 
function fireOnClick(redirectElem) {
	if (pressedKey == 13) {
		redirectElem.onclick();
	}
}

// ---------- Function on the top left call-out

function updateCallOutProject() {
	$.ajax({ async : false,
             type: 'GET',
             url: "/project/generate_call_out_control/",
             success: function(r) { $("#control_top_left").html(r); },
             error:   function(r) { if (r) displayMessage(r,'errorMessage'); }
            });
}



// ---------- Function on right call-out

function includeAdapterInterface(divId, projectId, algorithmId, back_page) {
    // Populate in divId, the interface of the adapter, specified by algorihmId.
    // The interface will be automatically populated with dataTypes from projectId     
    get_url = "/flow/getadapterinterface/"+ projectId+ "/" + algorithmId + '/' +back_page;
    $.ajax({ async : false,
             type: 'GET',
             url: get_url,
             success: function(r) { $("#"+ divId).html(r); },
             error:   function(r) { if (r) displayMessage(r,'errorMessage'); }
            });
}


/*
 * For a given input DIV id, gather all the inputs and selects entry
 * in a {name : value} dictionary.
 */
function getSubmitableData(inputDivId, allowDisabled) {
	
	var inputs = $("#" + inputDivId + " input");
	var submitableData = {}
	for (var i = 0; i < inputs.length; i++) {
		var thisInput = inputs[i];
		if (!allowDisabled && thisInput.disabled) {
			continue
		} 
		if (thisInput.type != 'button') {
			if (thisInput.type == 'checkbox') {
				submitableData[thisInput.name] = thisInput.checked;
			} else if (thisInput.type == 'radio') {
				if (thisInput.checked) {
					submitableData[thisInput.name] = thisInput.value;
				}
			} else {
				submitableData[thisInput.name] = thisInput.value;
			}	
		}
	}
	var selects = $("#" + inputDivId + " select");
	for (var i = 0; i < selects.length; i++) {
		var thisSelect = selects[i];
		if (!allowDisabled && thisSelect.disabled) {
			continue
		}
		if (thisSelect.multiple == true) {
			var selectedOptions = []
			for (var j=0; j < thisSelect.options.length; j++) {
				if (thisSelect.options[j].selected == true) {
					selectedOptions.push(thisSelect.options[j].value);
				}
			}
			submitableData[thisSelect.name] = selectedOptions;
		} else if (thisSelect.selectedIndex >= 0){
			submitableData[thisSelect.name] = thisSelect.options[thisSelect.selectedIndex].value;
		}
	}
	return submitableData;
}


/**
 * Generic function to maximize /minimize a column in Michael's columized framework.
 */
function toggleMaximizeColumn(link, maximizeColumnId) {
	
	if (link.text == "Maximize") {
		if (!$("div[id='main']").hasClass('is-maximized')) {
			$("div[id='main']")[0].className = $("div[id='main']")[0].className + " is-maximized";
			var maximizeColumn = $("#" + maximizeColumnId)[0]
			maximizeColumn.className = maximizeColumn.className + ' shows-maximized';
		}
		link.innerHTML = "Minimize";
		link.className = link.className.replace('action-zoom-in', 'action-zoom-out');
		
	} else {
		minimizeColumn(link, maximizeColumnId);
	}
}

function minimizeColumn(link, maximizeColumnId) {
	
	$("div[id='main']").each(function() {
		$(this).removeClass('is-maximized');
	});
	$("#" + maximizeColumnId).each(function() {
		$(this).removeClass('shows-maximized');
	});
	link.innerHTML = "Maximize";
	link.className = link.className.replace('action-zoom-out', 'action-zoom-in');
}



// ---------------END GENERIC ------------------------

// ---------------------------------------------------------
//              USER SECTION RELATED FUNCTIONS
// ---------------------------------------------------------


function changeMembersPage(projectId, pageNo, divId, editEnabled) {
    $(".projectmembers-pagetab-selected").attr("class", "projectmembers-pagetab");
    $("#tab-" + pageNo).attr("class", "projectmembers-pagetab projectmembers-pagetab-selected");
    if ($('span[class="user_on_page_'+ pageNo+'"]').length > 0) {
        $('span[class^="user_on_page_"]').hide(); 
        $('span[class="user_on_page_'+ pageNo+'"]').show(); 
    } else {
        my_url = '/project/getmemberspage/' + pageNo;
        if (projectId) {
            my_url = my_url + "/"+ projectId;
        }
        $.ajax({async: false, 
                type: 'GET',
                url:  my_url,
                success: function(r) {  $('span[class^="user_on_page_"]').hide(); 
                                        $("#" + divId).append(r);
                                        if (editEnabled) {  
                                            document.getElementById("visitedPages").value = document.getElementById("visitedPages").value + "," + pageNo;
                                        }
                                      },
                error: function(r) { if(r) displayMessage(r, 'errorMessage'); }});
    }
}


function show_hide(show_class, hide_class) {
	elems = $(show_class);
	for (var i=0; i< elems.length; i++) {
		elems[i].style.display = 'inline';
	}
	elems = $(hide_class);
	for (var i=0; i< elems.length; i++) {
		elems[i].style.display = 'none';
	}
}

/**
 * Function on the Settings page.
 */
function validateDb(db_url, tvb_storage){
	var db_url = document.getElementById(db_url).value;
	var storage = document.getElementById(tvb_storage).value;
	$.ajax({ async : false,
        type: 'POST',
        url: "/settings/check_db_url",
        data: { URL_VALUE: db_url , TVB_STORAGE : storage},
        success: function(r) {  
        						r = $.parseJSON(r);
        						if (r['status'] == 'ok') {				
        							displayMessage(r['message'], "infoMessage");
        						} else {
        							displayMessage(r['message'], "errorMessage");
        						}		
        					  },
		error: function(r) { 
			displayMessage("Some error occured during method call.",'errorMessage'); 
			}
      });
}

function validateMatlabPath(matlab_path){
	var matlab_path = document.getElementById(matlab_path).value;
	$.ajax({ async : false,
        type: 'GET',
        url: "/settings/validate_matlab_path",
        data: { MATLAB_EXECUTABLE: matlab_path},
        success: function(r) {  
        						r = $.parseJSON(r);
        						if (r['status'] == 'ok') {				
        							displayMessage(r['message'], "infoMessage");
        						} else {
        							displayMessage(r['message'], "errorMessage");
        						}		
        					  },
		error: function(r) { 
			displayMessage("Some error occured during method call.",'errorMessage'); 
			}
      });
}

function changeDBValue(selectComponent) {
	var component = eval(selectComponent);
	var selectedValue = $(component).val();
    correspondingValue = component.options[component.selectedIndex].attributes.correspondingVal.nodeValue;
    correspondingTextField = document.getElementById('URL_VALUE');
    correspondingTextField.value = correspondingValue;
    if (selectedValue == 'sqlite') {
    	correspondingTextField.setAttribute('readonly', 'readonly');	
    } else {
    	correspondingTextField.removeAttribute('readonly'); 	
    }
}


// ------------------END USER-----------------------------


// ---------------------------------------------------------
//              GENERIC PROJECT FUNCTIONS
// ---------------------------------------------------------

function viewProject(projectId, formId) {
    document.getElementById(formId).action = "/project/editone/"+ projectId;
    document.getElementById(formId).submit();
}

function selectProject(projectId, formId) {
    // Change hidden project_id and submit
    document.getElementById("hidden_project_id").value = projectId;
    document.getElementById(formId).submit();
}

function exportProject(projectId) {
	window.location = "/project/downloadproject/?project_id=" + projectId
}

// ---------------END PROJECT ------------------------


// -----------------------------------------------------------------------
//		 		OVERLAY DATATYPE/OPERATIONS 
//------------------------------------------------------------------------

// Set to true when we want to avoid display of overlay (e.g. when switching TAB on Data Structure page).
var TVB_skipDisplayOverlay = false;
var TVB_NODE_OPERATION_TYPE = "operation";
var TVB_NODE_OPERATION_GROUP_TYPE = "operationGroup";
var TVB_NODE_DATATYPE_TYPE = "datatype";
/**
 * Displays the overlay with details for a node(operation or dataType group/single).
 *
 * @param entity_gid an operation or dataType GID
 * @param entityType the type of the entity: operation or dataType
 * @param backPage is a string, saying where the visualizers that can be launched from the overlay should point their BACK button.
 */
function displayNodeDetails(entity_gid, entityType, backPage, excludeTabs) {
	closeOverlay(); // If there was overlay opened, just close it
    if (entity_gid == undefined || entity_gid == "firstOperation" || entity_gid == "fakeRootNode" || TVB_skipDisplayOverlay) {
        return;
    }
    var url = '';
	if (entityType == TVB_NODE_OPERATION_TYPE) {
		url = '/project/get_operation_details/' + entity_gid + "/0";
	} else if (entityType == TVB_NODE_OPERATION_GROUP_TYPE) {
		url = '/project/get_operation_details/' + entity_gid + "/1";
	} else {
		url = '/project/get_datatype_details/' + entity_gid;
	}

    if (backPage == undefined || backPage == '') {
        backPage = get_URL_param('back_page');
    }
	if (backPage) {
		url = url + "/" + backPage;
	}
	if (excludeTabs) {
		url = url + "?exclude_tabs=" + excludeTabs
	}
    showOverlay(url, true);
}


/**
 * Close overlay and refrech backPage.
 */	
function closeAndRefreshNodeDetailsOverlay(returnCode, backPage) {
	
	closeOverlay();
	if (returnCode == 0) {
		
		if (backPage == 'operations') {
			document.getElementById('operationsForm').submit();
			
		} else if (backPage == 'data') {
			if ($("#lastVisibleTab").val() == GRAPH_TAB) {
		    	update_workflow_graph('workflowCanvasDiv', lastSelectedNode, lastSelectedNodeType);
		  	} else {
		    	updateTree();
		   }
		    
		} else if (backPage == 'burst') {
			$("#tab-burst-tree")[0].onclick();
		}
	}
}


/**
 * Used from DataType(Group) overlay to store changes in meta-data.
 */
function overlaySubmitMetadata(datatypeGID, formToSubmitId, backPage) {
	
	var submitableData = getSubmitableData(formToSubmitId, false);
	$.ajax({ async : false,
             type: 'POST',
             url: "/project/updatemetadata",
             data: submitableData,
             success: function(r) {
			                if (r) {
			                    displayMessage(r, 'errorMessage');
			                } else {
			                    displayMessage("Data succesfully stored!");
			                    closeAndRefreshNodeDetailsOverlay(0, backPage);
			                }
             },
             error:   function(r) {
                			displayMessage(r, 'errorMessage');
             }
     });
}


/**
 * Used from DataType(Group) overlay to remove current entity.
 */
function overlayRemoveEntity(projectId, dataGid, backPage) {
    $.ajax({ async : false,
             type: 'POST',
             url: "/project/noderemove/" + projectId + "/" + dataGid,
             success: function(r) {
			                if (r) {
			                    displayMessage(r, 'errorMessage');
			                } else {
			                    displayMessage("Node succesfully removed!");
			                    lastSelectedNode = undefined;
    							lastSelectedNodeType = undefined;
			                    closeAndRefreshNodeDetailsOverlay(0, backPage);
			                }
             },
             error:   function(r) {
                displayMessage(r, 'errorMessage');
             }
     });
}


/**
 * Take an operation Identifier and reload previously selected input parameters for it.
 * Used from Operation-Overlay and View All Operations button/each row. 
 */
function reloadOperation(operationId, formId) {
    document.getElementById(formId).action = "/flow/reloadoperation/"+ operationId;
    document.getElementById(formId).submit();
}


/**
 * Take an operation Identifier which was started from a burst, and redirect to the 
 * burst page with that given burst as the selected one.
 */
function reloadBurstOperation(operationId, isGroup, formId) {
	document.getElementById(formId).action = "/flow/reload_burst_operation/" + operationId + '/' + isGroup;
	document.getElementById(formId).submit();
}


/**
 * To be called from Operation/DataType overlay window to switch current entity's visibility.
 */
function overlayMarkVisibility(entityGID, entityType, toBeVisible, backPage) {
	var returnCode = _markEntityVisibility(entityGID, entityType, toBeVisible);
	closeAndRefreshNodeDetailsOverlay(returnCode, backPage);
}


/**
 * Used from view-operations and overlay-dataType /operation as well.
 */
function _markEntityVisibility(entityGID, entityType, toBeVisible) {
	var returnCode = 0;
	$.ajax({ async: false, 
			 type: 'POST',
			 url: "/project/set_visibility/" + entityType+"/"+ entityGID+"/"+ toBeVisible,
			 success: function(r) {
			 	displayMessage("Visibility was changed.");
			 },
			 error: function(r) {
			 	displayMessage("Error when trying to change visibility! Check logs...", "errorMessage");
			 	returnCode = 1;
			 }
	});
	return returnCode;
}


// ---------------END OVERLAY DATATYPE/OPERATIONS ------------------------

// ---------------------------------------------------------
//              OPERATIONS FUNCTIONS
// ---------------------------------------------------------

/**
 * Sets the visibility for an operation, from specifically the View Operation page. 
 * This will also trigger operation reload.
 *
 * @param operationGID an operation/operationGroup GID
 * @param isGroup True if OperationGroup entity
 * @param toBeRelevant <code>True</code> if the operation is to be set relevant, otherwise <code>False</code>.
 */
function setOperationRelevant(operationGID, isGroup, toBeRelevant, submitFormId) {
	entityType = "operation";
	if (isGroup) {
		entityType = "operationGroup"
	}
	var returnCode = _markEntityVisibility(operationGID, entityType, toBeRelevant);
	if (returnCode == 0){
		document.getElementById(submitFormId).submit();
	}
}


function _stopOperationsOrBurst(operationId, isGroup, isBurst, removeAfter) {

    var urlBase = "/flow/stop_operation/";
    if (isBurst) {
        urlBase = "/flow/stop_burst_operation/";
    }
    urlBase += operationId + '/' + isGroup ;
    if (removeAfter) {
        urlBase += '/True';
    }

    $.ajax({async: false,
            type: 'POST',
            url: urlBase,
            success: function(r) {  if (r.toLowerCase() == 'true') {
                                        displayMessage("The operation was successfully removed.", "infoMessage")
                                    } else {
                                        displayMessage("Could not remove operation.",'warningMessage');
                                    }},
            error: function(r) { displayMessage("Some error occurred while removing operation.",'errorMessage'); }
    });
}


function stopOperation(operationId, isGroup) {
    // Take an operation Identifier and reload previously selected input parameters for it.
    _stopOperationsOrBurst(operationId, isGroup, false, false);
}

function stopBurstOperation(operationId, isGroup) {
    // Take an operation Identifier and reload previously selected input parameters for it.
    _stopOperationsOrBurst(operationId, isGroup, true, false);
}


function deleteOperation(operationId, isGroup) {
	// Delete a operation that was not part of a Burst
	_stopOperationsOrBurst(operationId, isGroup, false, true);
}


function deleteBurstOperation(operationId, isGroup) {
	// Delete a operation that was part of a burst launch
    _stopOperationsOrBurst(operationId, isGroup, true, true);
}


function resetOperationFilters(submitFormId) {
	//Reset all the filters set for the operation page.
	var input = document.createElement("INPUT");
	input.type = "hidden";
	input.name = "reset_filters";
	input.value = "true";
	form = document.getElementById(submitFormId);
	form.appendChild(input);
	form.submit()
}

function applyOperationFilter(filterName, submitFormId) {
	// Make sure pagination is reset otherwise it might happen for he new filter the given page does not exist.
	document.getElementById("currentPage").value = 1;
	document.getElementById('filtername').value = filterName;
	document.getElementById(submitFormId).submit();
}

/*
 * Refresh the operation page is no overlay is currently displayed.
 */
function refreshOperations() {

	if (document.getElementById("overlay") == null) {
		document.getElementById('operationsForm').submit();
	} else {
		setTimeout(refreshOperations, 30000);
	}
}


// ----------------END OPERATIONS----------------------------

// ---------------------------------------------------------
//              PIPELINE RELATED FUNCTIONS
// ---------------------------------------------------------

function importerSelectRadio(prefixRadio, selectedType) {
	$(".labelSelected").each(function () {
		var new_class = this.className.replace('labelSelected', '').trim();
		if (new_class.indexOf(prefixRadio) >=0) {
			this.className = new_class;
		}
	});
	$(".img" + selectedType).attr("class", $(".img" + selectedType).attr("class") + ' labelSelected');
	$("#"+ prefixRadio + selectedType).attr("checked", 'true');
}
// ------------------END PIPELINE-----------------------------


// ---------------------------------------------------------
//              OVERLAY RELATED FUNCTIONS
// ---------------------------------------------------------
/**
 * Opens the overlay dialog and fill in
 *
 * @param url URL to be called in order to get overlay code
 */
KEY_UP_EVENT = "keyup"
function showOverlay(url, allowClose, message_data) {

    $.ajax({
        async:false,
        type:'GET',
        url: url,
        dataType:'html',
        cache:true,
        data: message_data,
        success:function (htmlResult) {
            var bodyElem = $('body');
            bodyElem.addClass("overlay");
            if (allowClose == true) {
            	bodyElem.bind(KEY_UP_EVENT, closeOverlayOnEsc);            	
            }
            var parentDiv = $("#main");
            if (parentDiv.length == 0) { parentDiv = $('body') }
            parentDiv.prepend(htmlResult);
            MathJax.Hub.Queue(["Typeset", MathJax.Hub, "overlay"]);
        },
        error:function (r) {
            if (r) {
            	displayMessage(r, 'errorMessage');
            } 
        }
    });
}

/**
 * Closes Overlay dialog.
 *
 */
function closeOverlay() {
	var bodyElem = $('body');
    bodyElem.removeClass("overlay");
    bodyElem.unbind(KEY_UP_EVENT, closeOverlayOnEsc);
   	$("#overlay").remove();
}

/**
 * Event listener attached to <body> to handle ESC key pressed
 * @param evt keyboard event
 */
function closeOverlayOnEsc(evt) {
    var evt = (evt) ? evt : ((event) ? event : null);
	
	// handle ESC key code
	if (evt.keyCode == 27) {
		closeOverlay();
		// Force page reload, otherwise the div#main with position absolute will be wrongly displayed
		// The wrong display happens only when iFrame with anchors are present in the Help Inline Doc.
		window.location.href=window.location.href
	}
}

/**
 * Select a given tab from overlay
 *
 * @param tabId identifier of the tab to be selected
 */
function selectOverlayTab(tabId) {
	var css_class = "active";
	
    $("li[id^='overlayTab_']").each(function() {
        $(this).removeClass(css_class);
    });

    $("section[id^='overlayTabContent_']").each(function () {
        $(this).removeClass(css_class);
    });

    $("#overlayTab_" + tabId).addClass(css_class);
    $("#overlayTabContent_" + tabId).addClass(css_class);
}

/**
 * This function activate progress bar and blocks any user
 * action.
 */
function showOverlayProgress() {
	var overlayElem = $("#overlay");
	if (overlayElem != null) {
		overlayElem.addClass("overlay-blocker");
		var bodyElem = $('body');
		bodyElem.unbind(KEY_UP_EVENT, closeOverlayOnEsc);
	}
	
	return false;	
}

// ---------------------------------------------------------
// Here are specific functions for each overlay to be opened
// ---------------------------------------------------------

// We use this counter to allow multiple Ajax calls in the 
// same time. This way we ensure only the first one opens 
// overlay and last one closes it.
BLOCKER_OVERLAY_COUNTER = 0;
BLOCKER_OVERLAY_TIMEOUT = null;

function showBlockerOverlay(timeout, overlay_data) {
	timeout = checkArg(timeout, 60 * 1000);
	overlay_data = checkArg(overlay_data, {"message_data" : "Your request is being processed right now. Please wait a moment..."})
	BLOCKER_OVERLAY_COUNTER++;
	if (BLOCKER_OVERLAY_COUNTER == 1) {
		showOverlay("/showBlockerOverlay", false, overlay_data);
		
		// Ensure that overlay will close in 1 min 
		BLOCKER_OVERLAY_TIMEOUT = setTimeout(forceCloseBlockerOverlay, timeout);
	}
}

function showQuestionOverlay(question, yesCallback, noCallback) {
	/*
	 * Dispaly a question overlay with yes / no answers. The params yesCallback / noCallback
	 * are javascript code that will be evaluated when pressing the corresponding choice buttons.
	 */
	var undefined;
	if (yesCallback == undefined) {
		yesCallback = 'closeOverlay()';
	}
	if (noCallback == undefined) {
		noCallback = 'closeOverlay()';
	}
	var url = "/project/show_confirmation_overlay";
	var data = {'yes_action' : yesCallback, 'no_action' : noCallback}
	if (question != undefined) {
		data['question'] = question;
	}
	showOverlay(url, true, data);
}

function forceCloseBlockerOverlay() {
	displayMessage('It took too much time to process this request. Please reload page.', 'errorMessage');
	closeBlockerOverlay();
}

function closeBlockerOverlay() {
	BLOCKER_OVERLAY_COUNTER--;
	if (BLOCKER_OVERLAY_COUNTER <= 0) {
		if (BLOCKER_OVERLAY_TIMEOUT != null) {
			clearTimeout(BLOCKER_OVERLAY_TIMEOUT);
			BLOCKER_OVERLAY_TIMEOUT = null;
		}
		closeOverlay();
		
		BLOCKER_OVERLAY_COUNTER = 0;	
	}
}

/**
 * Function which opens online-help into overlay
 * 
 * @param {Object} section
 * @param {Object} subsection
 */
function showHelpOverlay(section, subsection) {
	var url = "/help/showOnlineHelp"
	if (section != null) {
		url += "/" + section
	}
	if (subsection != null) {
		url += "/" + subsection
	}
	
	showOverlay(url, true);
}


/**
 * Function that opens a loading overlay until the file storage update is done.
 */
function upgradeFileStorage() {
	doAjaxCall({	
					overlay_timeout: 60 * 1000 * 60 * 4, //Timeout of 4 hours
					overlay_data: {'message_data': "Due to upgrade from pytables to h5py we need to update all your stored data. Please be patient and don't close TVB during the process."},
	                type:'GET',
	                url:'/user/upgrade_file_storage',
	                success:function (data) {
	                	var result = $.parseJSON(data);
	                	var message = result['message'];
	                	var status = result['status'];
	                	if (message.length > 0) {
	                		if (status == true) {
	                			displayMessage(message, "infoMessage");
	                		} else {
	                			displayMessage(message, "errorMessage");
	                		}
 	                	}
            			closeBlockerOverlay();
	               },
	               error:function (r) {
            			closeBlockerOverlay();
            			displayMessage("An unexpected error occured during update.", 'errorMessage');
	        		}
	            });
}



/**
 * Displays the dialog which allows the user to upload certain data.
 *
 * @param projectId the selected project
 */
function showDataUploadOverlay(projectId) {
	showOverlay("/project/get_data_uploader_overlay/" + projectId, true);
}

/**
 * Displays the dialog which allows the user to upload a project.
 *
 * @param projectId the selected project
 */
function showProjectUploadOverlay() {
	showOverlay("/project/get_project_uploader_overlay", true);
}


// -------------END OVERLAY--------------------------------


// ---------------------------------------------------------
//              RESULT FIGURE RELATED FUNCTIONS
// ---------------------------------------------------------

/**
 * Displays the zoomed image.
 */
function zoomInFigure(figure_id) {
	showOverlay("/project/figure/displayzoomedimage/" + figure_id, true);
}


function displayFiguresForSession(selected_session) {
    var actionUrl = "/project/figure/displayresultfigures/" + selected_session;
    var myForm = document.createElement("form");
    myForm.method = "POST";
    myForm.action = actionUrl;
    document.body.appendChild(myForm);
    myForm.submit();
    document.body.removeChild(myForm);
}

// --------------END RESULT FIGURE------------------------------


// -------------------------------------------------------------
//              AJAX Calls
// -------------------------------------------------------------

/**
 * Execute an AJAX call using jQuery with some parameters from given dictionary.
 * 
 * - {String} url URL to call
 * - {String} type request TYPE (POST, GET). Default = POST
 * - {bool} async Specify if the call should be done Sync 
 * 		or Async. Default = true (asynchronous) 
 * - {function} success Function to be called for success
 * - {function} error Function to be called for error
 * - {bool} showBlockerOverlay if True will show blocker overlay until request is done. Default = true
 */

function doAjaxCall(params) {
	params.type = checkArg(params.type, 'POST');
	params.async = checkArg(params.async, true);
	params.showBlockerOverlay = checkArg(params.showBlockerOverlay, true);
	
	if(showBlockerOverlay) {
		// should execute async, otherwise overlay is not shown
		params.async = true;
		showBlockerOverlay(params.overlay_timeout, params.overlay_data);
	}

	successFunc = function(result) {
		if( typeof params.success != 'undefined') {
			params.success(result);
		}
		if(showBlockerOverlay) {
			closeBlockerOverlay();
		}
	};

	errorFunc = function(result) {
		if(showBlockerOverlay) {
			closeBlockerOverlay();
		}
		if( typeof params.error != 'undefined') {
			params.error(result);
		} else {
			if(result) {
				displayMessage(result, 'errorMessage');
			} else {
				displayMessage("Error encountered on server.", 'errorMessage');
			}
		}
	};

	// Do AJAX call
	$.ajax({
		url : params.url,
		type : params.type,
		async : params.async,
		success : successFunc,
		error : errorFunc,
		data : params.data,
		cache : params.cache
	});
}

function checkArg(arg, def) {
	return ( typeof arg == 'undefined' ? def : arg);
}

// -------------End AJAX Calls----------------------------------