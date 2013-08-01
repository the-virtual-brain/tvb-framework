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

/**
 * Project Data Structure (Tree/Graph) functions are here.
 */
var GRAPH_TAB = "graphTab";
var TREE_TAB = "treeTab";

var lastSelectedNode = undefined;
var lastSelectedNodeType = undefined;
//we need this flag because we want to know when the user
// presses more times on the same graph node
var skipReload = false;


/**
 * Function selecting previously selected TAB between TREE / GRAPH, on pahe refresh.
 */
function displaySelectedTab() {
	
    var lastSelectedTab = $("#lastVisibleTab").val();
    if (lastSelectedTab == GRAPH_TAB) {
        showGraph();
    } else {
        showTree();
    }
}


//-----------------------------------------------------------------------
// 						TREE Section starts here
//-----------------------------------------------------------------------

function showTree() {
    $("#lastVisibleTab").val(TREE_TAB);
    
    $("#tree-related-li").show();
    $("#tree4").show();
    $("#levelTree_1").show();
    $("#levelTree_2").show();
    $("#label_levelTree_1").show();
    $("#label_levelTree_2").show();
    
    $("#graph-related-table").hide();
    $("#workflowCanvasDiv").hide();
    
    $("#" + TREE_TAB).addClass("active");
    $("#" + GRAPH_TAB).removeClass("active");
    select_tree_node();
    //$("#tree4").jstree('refresh');
}


/**
 * Selects into the tree view the last node that was selected into the graph view. If
 * into the graph view was selected an operation node then into the tree view will
 * be selected the project node.
 */
function select_tree_node() {
    if ($("#lastVisibleTab").val() == TREE_TAB) {
        $("#tree4").jstree("deselect_all");
        TVB_skipDisplayOverlay = true;
        if (lastSelectedNode != undefined && lastSelectedNodeType != undefined && lastSelectedNodeType == TVB_NODE_DATATYPE_TYPE) {
            $("#tree4").jstree("select_node", "#node_" + lastSelectedNode);
        } else {
            $("#tree4").jstree("select_node", "#projectID");
        }
        TVB_skipDisplayOverlay = false;
    }
}


/**
 * Used for updating the tree structure.
 *
 * @param projectId the id of the current project
 */
function updateTree(projectId, baseUrl, visibilityFilter) {
	
	if (!projectId) {
		projectId = $("#hiddenProjectId").val();
	}
	if (!baseUrl) {
		baseUrl = $("#hiddenBaseURL").val();
	}
	if (!visibilityFilter) {
    	visibilityFilter = _getSelectedVisibilityFilter();
    }
    var firstLevel = $("#levelTree_1").val();
    var secondLevel = $("#levelTree_2").val();
    var filterValue = $("#filterInput").val();

	var my_error_message = "The filters should not have the same value."
    if (firstLevel == secondLevel) {
        displayMessage(my_error_message, 'warningMessage');
        return;
    } 

    var url = "/project/readjsonstructure/" + projectId + "/" + visibilityFilter + "/" + firstLevel + "/" + secondLevel;
    if (filterValue.length > 2) {
        url += "/" + filterValue;
    }

    $("#tree4").jstree({//contextmenu: { "items" : createDefaultMenu, "select_node" : true },
		                "plugins": ["themes", "json_data", "ui", "crrm"], //, "contextmenu"
		                "themes": {
		                    "theme": "default",
		                    "dots": true,
		                    "icons": true,
		                    "url": baseUrl + "static/jquery/themes/default/style.css"
		                },
		                "json_data": {
		                    "ajax": { url: url,
		                        success: function (d) {
		                            return eval(d);
		                        }
		                    }}
		            });
    postInitializeTree(projectId);
    if (filterValue.length <= 2) {
        if (filterValue.length > 0) {
            displayMessage("You have to introduce at least tree letters in order to filter the data.", 'infoMessage');
        }
    } else {
        lastSelectedNode = undefined;
        lastSelectedNodeType = undefined;
    }
}

/**
 * Main function for specifying JSTree attributes.
 */
function postInitializeTree(projectId) {

	$("#tree4")
	.bind("select_node.jstree", function (event, data) {
          if ($("#lastVisibleTab").val() == GRAPH_TAB) {
              return;
          }
          lastSelectedNode = data.rslt.obj.attr("gid");
          if (lastSelectedNode != undefined && lastSelectedNode != null) {
              lastSelectedNodeType = TVB_NODE_DATATYPE_TYPE;
          } else {
              lastSelectedNode = undefined;
              lastSelectedNodeType = undefined;
          }
          skipReload = false;
          
          var backPage = 'data';
		  if ($("body")[0].id == "s-burst") {
				backPage = 'burst';
		  }
          displayNodeDetails(lastSelectedNode, TVB_NODE_DATATYPE_TYPE, backPage);
    })
    .bind("loaded.jstree", function () { select_tree_node(); });
}
//-----------------------------------------------------------------------
// 						TREE Section ends here
//-----------------------------------------------------------------------


//-----------------------------------------------------------------------
// 						GRAPH Section starts here
//-----------------------------------------------------------------------

function showGraph() {
    $("#lastVisibleTab").val(GRAPH_TAB);
    
    $("#tree-related-li").hide();
    $("#tree4").hide();
    $("#levelTree_1").hide();
    $("#levelTree_2").hide();
    $("#label_levelTree_1").hide();
    $("#label_levelTree_2").hide();
    
    $("#graph-related-table").show();
    $("#workflowCanvasDiv").show();
    
    $("#" + TREE_TAB).removeClass("active");
    $("#" + GRAPH_TAB).addClass("active");
    update_workflow_graph('workflowCanvasDiv', lastSelectedNode, lastSelectedNodeType);
}


function update_workflow_graph(containerDivId, nodeGid, nodeType) {
    if (nodeGid == undefined || nodeType == undefined) {
        nodeGid = "firstOperation";
        nodeType = TVB_NODE_OPERATION_TYPE;
    }
    if (nodeGid == lastSelectedNode && skipReload) {
        return;
    }
    lastSelectedNode = nodeGid;
    lastSelectedNodeType = nodeType;
    var visibilityFilter = _getSelectedVisibilityFilter();
    $.ajax({    async : false,
                type: 'GET',
                url: '/project/create_json/' + nodeGid + "/" + nodeType + "/" + visibilityFilter,
                success: function(data) {
                    $("#" + containerDivId).empty();
                    var json = $.parseJSON(data);
                    _draw_graph(containerDivId, json);
                }
            });

}

/**
 * Main function for specifying JIT Graph attributes.
 */
function _draw_graph(containerDivId, json) {
    // init ForceDirected
    var fd = new $jit.ForceDirected({
                //id of the visualization container
                injectInto: containerDivId,
                //Enable zooming and panning with scrolling and DnD
                Navigation: {
                    enable: true,
                    //Enable panning events only if we're dragging the empty canvas (and not a node).
                    panning: 'avoid nodes',
                    zooming: 10
                },
                // Change node and edge styles such as color and width.
                // These properties are also set per node with dollar prefixed data-properties in the JSON structure.
                Node: {
                    overridable: true
                },
                Edge: {
                    overridable: true,
                    type: 'arrow',
                    color: '#23A4FF',
                    lineWidth: 0.4
                },
                Tips: {
                    enable: true,
                    type: 'Native',
                    onShow: function(tip, node) {
                        if (node.id != "fakeRootNode") {
                            tip.innerHTML = "<div class=\"tip-title\">" +
		                                            node.name +
		                                    "</div></br>" +
		                                    "<div class=\"tip-text\">" +
		                                            "<b>Id:</b> " + node.data.entity_id + "</br>" +
		                                            "<b>Type:</b> " + node.data.dataType + "</br>" +
		                                            "<b>Display Name:</b> " + node.data.subtitle + "</br>" +
		                                    "</div>";
                            }
                    }
                },
                // Add node events
                Events: { 	enable: true,
		                    type: 'Native',
		                    //Change cursor style when hovering a node
		                    onMouseEnter: function(node, eventInfo, e) {
		                        fd.canvas.getElement().style.cursor = 'move';
		                    },
		                    onMouseLeave: function(node, eventInfo, e) {
		                        fd.canvas.getElement().style.cursor = '';
		                    },
		                    //Update node positions when dragged
		                    onDragMove: function(node, eventInfo, e) {
		                        var pos = eventInfo.getPos();
		                        node.pos.setc(pos.x, pos.y);
		                        fd.plot();
		                    },
		                    //Implement the same handler for touchscreens
		                    onTouchMove: function(node, eventInfo, e) {
		                        //stop default touchmove event
		                        $jit.util.event.stop(e);
		                        this.onDragMove(node, eventInfo, e);
		                    }
                },
                // This method is only triggered
                // on label creation and only for DOM labels (not native canvas ones).
                onCreateLabel: function(domElement, node) {
                    var nameContainer = document.createElement('span');
                    var style = nameContainer.style;

                    //1 character is drawn on 3 points
                    var nodeName = node.name;
                    if (node.data.$dim < 30) {
                        nodeName = nodeName.substr(0, 3) + "...";
                    } else {
                        if (nodeName.length * 3 > node.data.$dim) {
                            nodeName = nodeName.substr(0, (node.data.$dim / 3) - 3);
                            nodeName += "...";
                        }
                    }

                    if (node.id == "fakeRootNode") {
                        node.setData('alpha', 0);
                        node.eachAdjacency(function(adj) {
                            adj.setData('alpha', 0);
                        });
                        return;
                    }
                    nameContainer.className = 'name';
                    nameContainer.innerHTML = nodeName;
                    domElement.appendChild(nameContainer);

                    style.fontSize = "1.0em";
                    style.color = "#ddd";
                    if (node.id == lastSelectedNode) {
                        node.setData('color', "#ff0000");
                    };

                    nameContainer.onclick = function() {
                        //skipReload = true;
                        //displayNodeDetails(node.id, node.data.dataType, 'data');
                        update_workflow_graph(containerDivId, node.id, node.data.dataType);
                    };
                },
                // Change node styles when DOM labels are placed or moved.
                onPlaceLabel: function(domElement, node) {
				                    var style = domElement.style;
				                    var left = parseInt(style.left);
				                    var top = parseInt(style.top);
				                    var w = domElement.offsetWidth;
				                    style.left = (left - w / 2) + 'px';
				                    style.top = (top - 5) + 'px';
				                    style.display = '';
                				}
            });
    // load JSON data.
    fd.loadJSON(json);
    // compute positions incrementally and animate.
    fd.computeIncremental({ property: 'end',
			                onComplete: function() {
							                    fd.animate({
							                                modes: ['linear'],
							                                transition: $jit.Trans.Elastic.easeOut,
							                                duration: 1500
							                            });
			                					}
			            	});
}

//-----------------------------------------------------------------------
// 						GRAPH Section ends here
//-----------------------------------------------------------------------


//-----------------------------------------------------------------------
// 					More GENERIC functions from here
//-----------------------------------------------------------------------

function createLink(dataId, projectId, isGroup) {
	$.ajax({ async : false,
		     type: 'GET',
		     url: "/project/createlink/" + dataId +"/" + projectId + "/" + isGroup,
		     success: function(r) {if(r) displayMessage(r,'warningMessage'); },
		     error:   function(r) {if(r) displayMessage(r,'warningMessage'); }
	      });
}

function removeLink(dataId, projectId, isGroup) {
	$.ajax({ async : false,
		     type: 'GET',
		     url: "/project/removelink/" + dataId +"/" + projectId + "/" + isGroup,
		     success: function(r) {if(r) displayMessage(r,'warningMessage'); },
		     error:   function(r) {if(r) displayMessage(r,'warningMessage'); }
	      });
}

function updateLinkableProjects(datatype_id, isGroup, entity_gid) {
    $.ajax({
                async : false,
                type: 'GET',
                url: "/project/get_linkable_projects/" + datatype_id + "/" + isGroup + "/" + entity_gid,
                success: function(data) {
                	var linkedDiv = $("#linkable_projects_div_" + entity_gid);
                    linkedDiv.empty();
                    linkedDiv.append(data);
                }
            });
}

/**
 * Launch from DataType overlay an analysis or a visualize algorithm.
 */
function doLaunch(visualizer_url, param_name, data_gid, param_algo, algo_ident, back_page_link) {
	
	var myForm = document.createElement("form");
	myForm.method="POST" ;
	myForm.action = visualizer_url + "?back_page="+back_page_link;
	var myInput = document.createElement("input");
	myInput.setAttribute("name", param_name);
	myInput.setAttribute("value", data_gid);
	myForm.appendChild(myInput);
	if (param_algo != ''){
		var myInput = document.createElement("input");
		myInput.setAttribute("name", param_algo);
		myInput.setAttribute("value", algo_ident);
		myForm.appendChild(myInput);
	}
	document.body.appendChild(myForm);
	myForm.submit();
	document.body.removeChild(myForm);
}

/**
 * Launch from DataType overlay an analysis or a visualize algorithm.
 */
function doGroupLaunch(visualizer_url, param_name, param_algo, algo_ident) {
	
	var myForm = document.createElement("form");
	myForm.method="POST" ;
	myForm.action = visualizer_url;
	var myInput = document.createElement("input");
	myInput.setAttribute("name", 'range_param_name');
	myInput.setAttribute("value", param_name);
	myForm.appendChild(myInput);
	if (param_algo != ''){
		var myInput = document.createElement("input");
		myInput.setAttribute("name", param_algo);
		myInput.setAttribute("value", algo_ident);
		myForm.appendChild(myInput);
	}
	document.body.appendChild(myForm);
	myForm.submit();
	document.body.removeChild(myForm);
}


/**
 * Called when the visibility filter is changed.
 *
 * @param projectId a project id.
 */
function changedVisibilityFilter(projectId, baseUrl, filterElemId) {
	
	// Activate visibility filter
	$("#visibilityFiltersId > li[class='active']").each(function () {
        $(this).removeClass('active');
    });
    //do NOT use jquery ($("#" + filterElemId)) to select the element because its id may contain spaces
    document.getElementById(filterElemId).classList.add('active');
    
    lastSelectedNode = undefined;
    lastSelectedNodeType = undefined;
    update_workflow_graph('workflowCanvasDiv', lastSelectedNode, lastSelectedNodeType);
    updateTree(projectId, baseUrl);
}

function _getSelectedVisibilityFilter() {
    var selectedFilter = "";
    $("#visibilityFiltersId > li[class='active']").each(function() {
        selectedFilter = this.id;
    });
    return selectedFilter;
}


