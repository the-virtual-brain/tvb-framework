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

////////////////////////////////////~~~~~~~~START BRAIN NAVIGATOR RELATED CODE~~~~~~~~~~~///////////////////////////

var NAV_navigatorX = 0.0, NAV_navigatorY = 0.0, NAV_navigatorZ = 0.0;
// As we draw the 3D navigator as WebGL object, we need buffers for it.
var NAV_navigatorBuffers = [];
/// No brain rotation happens, but the brain-navigator is working.
var NAV_isMouseControlOverBrain = true;
/// When brain Navigator is manipulated and this check is True, projections on X, Y, Z are refreshed at each redraw.
var NAV_inTimeRefresh = false;
var _inTimeRefreshCheckbox;
/// Flag to mark that sections are to be redrawn.
var _redrawSectionView = true;


function NAV_initBrainNavigatorBuffers() {
    NAV_navigatorBuffers[0] = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, NAV_navigatorBuffers[0]);
    var vertices = [ // z plane
			        -pointPosition, -pointPosition,  0.0,
			        pointPosition, -pointPosition,  0.0,
			        pointPosition,  pointPosition,  0.0,
			        -pointPosition,  pointPosition,  0.0,
			        // y plane
			        -pointPosition, 0.0, -pointPosition,
			        pointPosition, 0.0, -pointPosition,
			        pointPosition, 0.0,  pointPosition,
			        -pointPosition, 0.0,  pointPosition,
			        // x plane
			        0.0, -pointPosition, -pointPosition,
			        0.0,  pointPosition, -pointPosition,
			        0.0,  pointPosition,  pointPosition,
			        0.0, -pointPosition,  pointPosition
			    ];
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices), gl.STATIC_DRAW);
    NAV_navigatorBuffers[0].itemSize = 3;
    NAV_navigatorBuffers[0].numItems = 8;

    NAV_navigatorBuffers[1] = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, NAV_navigatorBuffers[1]);
    var vertexNormals = [ // z plane
				        0.0,  0.0,  1.0,
				        0.0,  0.0,  1.0,
				        0.0,  0.0,  1.0,
				        0.0,  0.0,  1.0,
				        // y plane
				        0.0, -1.0,  0.0,
				        0.0, -1.0,  0.0,
				        0.0, -1.0,  0.0,
				        0.0, -1.0,  0.0,
				        // x plane
				        1.0,  0.0,  0.0,
				        1.0,  0.0,  0.0,
				        1.0,  0.0,  0.0,
				        1.0,  0.0,  0.0
				    ];
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertexNormals), gl.STATIC_DRAW);
    NAV_navigatorBuffers[1].itemSize = 3;
    NAV_navigatorBuffers[1].numItems = 12;

    NAV_navigatorBuffers[2] = gl.createBuffer();
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, NAV_navigatorBuffers[2]);
    var cubeVertexIndices = [   0, 1, 2,      0, 2, 3,    // z plane
						        4, 5, 6,      4, 6, 7,    // y plane
						        8, 9, 10,     8, 10, 11  // x plane
						    ];
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint16Array(cubeVertexIndices), gl.STATIC_DRAW);
    NAV_navigatorBuffers[2].itemSize = 1;
    NAV_navigatorBuffers[2].numItems = 18;
    // Fake buffers, these won't be used, they only need to be passed
    if (isOneToOneMapping) {
    	same_color = [];
        for (var i=0; i<NAV_navigatorBuffers[0].numItems* 4; i++) {
        	same_color = same_color.concat(0.34, 0.95, 0.37, 1.0);
        }
        NAV_navigatorBuffers[3] = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, NAV_navigatorBuffers[3]);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(same_color), gl.STATIC_DRAW);
    } else {
	    NAV_navigatorBuffers[3] = NAV_navigatorBuffers[1];
	    NAV_navigatorBuffers[4] = NAV_navigatorBuffers[1];
	}
}

function NAV_setInTimeRefresh(checkbox) {
	_inTimeRefreshCheckbox = checkbox;
	if (checkbox.checked) {
		NAV_inTimeRefresh = true;
	} else {
		NAV_inTimeRefresh = false;
	}
}

function NAV_customMouseUp(event) {
    GL_handleMouseUp(event);
	if (_inTimeRefreshCheckbox && _inTimeRefreshCheckbox.checked) {
	    NAV_inTimeRefresh = true;
	} else {
		NAV_inTimeRefresh = false;
	}
}

////////////////////////////////////~~~~~~~~END BRAIN NAVIGATOR RELATED CODE~~~~~~~~~~~/////////////////////////////

function NAV_draw_navigator() {
	mvTranslate([NAV_navigatorX, NAV_navigatorY, NAV_navigatorZ]);
	if (_redrawSectionView || NAV_inTimeRefresh) {
        drawSectionView('x', false);
        drawSectionView('y', false);
        drawSectionView('z', false);
        _redrawSectionView = false;
    }
	drawBuffers(gl.TRIANGLES, [NAV_navigatorBuffers], true);
}

////////////////////////////////////~~~~~~~~START BRAIN SECTION VIEW RELATED CODE~~~~~~~~~~~///////////////////////////

function drawSectionView(axis, first) {
    var sectionViewRotationMatrix = Matrix.I(4);
    var sectionValue;
    if (axis != undefined) {
        if (axis == 'x') {
            sectionViewRotationMatrix = createRotationMatrix(90, [0, 1, 0]).x(createRotationMatrix(270, [1, 0, 0]));
            sectionValue = NAV_navigatorX;
        }
        if (axis == 'y') {
            sectionViewRotationMatrix = createRotationMatrix(90, [1, 0, 0]).x(createRotationMatrix(180, [1, 0, 0]));
            sectionValue = NAV_navigatorY;
        }
        if (axis == 'z') {
            sectionViewRotationMatrix = createRotationMatrix(180, [0, 1, 0]).x(Matrix.I(4));
            sectionValue = NAV_navigatorZ;
        }
    }
    gl.viewport(0, 0, gl.viewportWidth, gl.viewportHeight);
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

    perspective(fov, gl.viewportWidth / gl.viewportHeight, 250 + sectionValue - 1, 250 + sectionValue);
    loadIdentity();
    mvTranslate([0.0, -5.0, -250.0]);
    mvPushMatrix();
    multMatrix(sectionViewRotationMatrix);
    drawBuffers(gl.TRIANGLES, brainBuffers, false);
    mvPopMatrix();
    displaySection(BRAIN_CANVAS_ID, 'brain-' + axis, axis, first);

    var brainAreaLabel = NAV_getAreaLabel([NAV_navigatorX, NAV_navigatorY, NAV_navigatorZ], measurePoints, measurePointsLabels);
    $(".brainArea").text("Brain area: " + brainAreaLabel);
    //gl.bindFramebuffer(gl.FRAMEBUFFER, null);
}

////////////////////////////////////~~~~~~~~END BRAIN SECTION VIEW RELATED CODE~~~~~~~~~~~/////////////////////////////

/**
 * Used for calculating the distance between two points
 */
function _distance(point1, point2) {
    return Math.sqrt((point1[0] - point2[0]) * (point1[0] - point2[0]) + (point1[1] - point2[1]) * (point1[1] - point2[1]) + (point1[2] - point2[2]) * (point1[2] - point2[2]));
}

/**
 * @param point a point of form [x, y, z]
 * @param positions represents a list of points
 */
function _findClosestPosition(point, positions) {
    if (positions == undefined || positions.length == 0) {
        displayMessage("Invalid position parameters passed...", "warningMessage");
    }
    var minDistance = _distance(point, positions[0]);
    var closestPosition = 0;
    for (var pp = 0; pp < positions.length; pp++) {
        var dist = _distance(point, positions[pp]);
        if (dist <= minDistance) {
            minDistance = dist;
            closestPosition = pp;
        }
    }
    return closestPosition;
}

/**
 * @param point a point ([x, y, z]) for which we want to find its area label
 * @param measurePoints an array which contains the measure points
 * @param measurePointsLabels an array which contains the labels for the measure points
 */
function NAV_getAreaLabel(point, measurePoints, measurePointsLabels) {
    var undefinedAreaStr = "Area undefined";
    if (measurePointsLabels == undefined || measurePointsLabels.length == 0) {
        return undefinedAreaStr;
    }
    var closestPosition = _findClosestPosition(point, measurePoints);
    if (measurePointsLabels.length > closestPosition) {
        return measurePointsLabels[closestPosition];
    }
    return undefinedAreaStr;
}


