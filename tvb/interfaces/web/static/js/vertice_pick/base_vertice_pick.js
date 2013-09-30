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
 * Variables for displaying Time and computing Frames/Sec
 */
var BASE_PICK_doPick = false;
var near = 0.1;
var fov = 45;

var TRIANGLE_pickedIndex = -1;
var VERTEX_pickedIndex = -1;

// These are for the selection 'pins'
var navigatorX = 0.0, navigatorY = 0.0, navigatorZ = 0.0;
var navigatorXrot = 0.0, navigatorYrot = 0.0;

var drawingBrainVertices = [];
var drawingBrainNormals = [];
var drawingBrainIndexes = [];

var pickingBrainVertices = [];
var pickingBrainNormals = [];
var pickingBrainIndexes = [];

var noOfUnloadedBrainDisplayBuffers = 3;
var noOfUnloadedBrainPickingBuffers = 3;

var BASE_PICK_brainPickingBuffers = [];
var BASE_PICK_brainDisplayBuffers = [];
var BASE_PICK_navigatorBuffers = [];
/**
 * These buffers arrays will contain:
 * arr[i][0] Vertices buffer
 * arr[i][1] Normals buffer
 * arr[i][2] Triangles indices buffer
 * arr[i][3] Color buffer (same length as vertices /3 * 4)
 */ 
//Setting this to true allows to pick form the images as well as the classic
//color picking scheme. TODO: picking this way is not correct if any zoom is done.
var BASE_PICK_allowPickFrom2DImages = true;
//If we are in movie mode stop the custom redraw on all events since it will
//redraw automatically anyway.
var BASE_PICK_isMovieMode = false;
//A dictionary that hold information needed to draw the surface focal points
var surfaceFocalPoints= {};

var TRI = 3;

var gl;
var drawingMode;
GL_zoomSpeed = 0;

var BRAIN_CANVAS_ID = "GLcanvas";
var BASE_PICK_pinBuffers = [];
var BRAIN_CENTER = null;

function BASE_PICK_customInitGL(canvas) {
	window.onresize = function() {
        updateGLCanvasSize(BRAIN_CANVAS_ID);
	};
	initGL(canvas);
    drawingMode = gl.TRIANGLES;
}


function BASE_PICK_webGLStart(urlVerticesPickList, urlTrianglesPickList, urlNormalsPickList,
							  urlVerticesDisplayList, urlTrianglesDisplayList, urlNormalsDisplayList,
                              brain_center, callback) {
	BRAIN_CENTER = $.parseJSON(brain_center);
    var canvas = document.getElementById(BRAIN_CANVAS_ID);
    BASE_PICK_customInitGL(canvas);
    
    BASE_PICK_initShaders();
    initPickingBrainBuffers(urlVerticesPickList, urlTrianglesPickList, urlNormalsPickList, callback);
    initDrawingBrainBuffers(urlVerticesDisplayList, urlTrianglesDisplayList, urlNormalsDisplayList, callback);
    initBrainNavigatorBuffers();
    createStimulusPinBuffers();
    
    //Used for reset to default position by pressing space key
    GL_DEFAULT_Z_POS = 250;
    GL_zTranslation = GL_DEFAULT_Z_POS;

    gl.clearColor(0.0, 0.0, 0.0, 1.0);
    gl.clearDepth(1.0);
    gl.enable(gl.DEPTH_TEST);
    gl.depthFunc(gl.LEQUAL);
		
    // Enable keyboard and mouse interaction
    canvas.onkeydown = customKeyDown;
    canvas.onkeyup = customKeyUp;
    canvas.onmousedown = customMouseDown;
    canvas.onmouseup = customMouseUp;
    canvas.onmousemove = customMouseMove;
    canvas.onmouseout = handleMouseOut;
    
    isOneToOneMapping = true;

    //Custom handlers for each of the dimensions for different transforms need to be applied
    if (BASE_PICK_allowPickFrom2DImages == true) {
    	canvasX = document.getElementById('brain-x');
    	if (canvasX) canvasX.onmousedown = handleXLocale;
	    canvasY = document.getElementById('brain-y');
	    if (canvasY) canvasY.onmousedown = handleYLocale;
	    canvasZ = document.getElementById('brain-z');
	    if (canvasZ) canvasZ.onmousedown = handleZLocale;
    }
    
    drawScene();
}

//Need this to switch between drawing in normal mode and in 'picking' mode without re-initializing colors
var colorPickingBuffer = [];

/**
 * @param callback a string which should represents a valid js code.
 */
function executeCallback(callback) {
    if (callback == undefined || callback == null || callback.trim().length == 0) {
        return;
    }
    if (noOfUnloadedBrainPickingBuffers == 0 && noOfUnloadedBrainDisplayBuffers == 0) {
        eval(callback);
    }
}
/**
 * Initialize all required data needed for picking mechanism.
 */
function initPickingBrainBuffers(urlVerticesPickList, urlTrianglesPickList, urlNormalsPickList, callback) {
    displayMessage("Start loading picking data!", "infoMessage");
    initPickingBrainBuffersAsynchronous($.parseJSON(urlVerticesPickList), pickingBrainVertices, false, true, callback);
    initPickingBrainBuffersAsynchronous($.parseJSON(urlNormalsPickList), pickingBrainNormals, false, false, callback);
    initPickingBrainBuffersAsynchronous($.parseJSON(urlTrianglesPickList), pickingBrainIndexes, true, false, callback);
}


function initPickingBrainBuffersAsynchronous(urlList, resultBuffers, isIndex, isVertices, callback) {
    if (urlList.length == 0) {
        noOfUnloadedBrainPickingBuffers -= 1;
    	if (noOfUnloadedBrainPickingBuffers == 0) {
            __createPickingColorBuffers();
            displayMessage("Finish loading picking data!", "infoMessage");
            executeCallback(callback);
            drawScene();
    	}
        return;
    }
    $.get(urlList[0], function(data) {
        var dataList = eval(data);
        var buffer = HLPR_createWebGlBuffer(gl, dataList, isIndex, false);
        if (isVertices) {
            verticesPoints.push(dataList);
        }
        resultBuffers.push(buffer);
        urlList.splice(0, 1);
        return initPickingBrainBuffersAsynchronous(urlList, resultBuffers, isIndex, isVertices, callback);
    });
}


function __createPickingColorBuffers() {
    for (var i = 0; i < pickingBrainVertices.length; i++) {
        var fakeColorBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, fakeColorBuffer);
        var thisBufferColors = new Float32Array(pickingBrainVertices[i].numItems / 3 * 4);
        for (var j = 0; j < pickingBrainVertices[i].numItems / 3 * 4; j++) {
            thisBufferColors[j] = 0.5;
        }
        gl.bufferData(gl.ARRAY_BUFFER, thisBufferColors, gl.STATIC_DRAW);
        colorArrays.push(thisBufferColors);

        picking_triangles_number.push(pickingBrainIndexes[i].numItems);
        total_picking_triangles_number = total_picking_triangles_number + pickingBrainIndexes[i].numItems/3;

        BASE_PICK_brainPickingBuffers.push([pickingBrainVertices[i], pickingBrainNormals[i], pickingBrainIndexes[i], fakeColorBuffer]);
    }

    GL_initColorPickFrameBuffer();
    //The total number of required colors will be equal to the total triangle number
    GL_initColorPickingData(total_picking_triangles_number);

    //Create the color buffer array for the picking part where each triangles has a new color
    var pointsSoFar = 0;
    for (var j = 0; j < picking_triangles_number.length; j++) {
        //For each set of triangles(different file) create a new color buffers
        var newColorBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, newColorBuffer);
        var thisBufferColors = new Float32Array(picking_triangles_number[j] * 4);
        //Go trough all the triangles from this set and set the same color for 3 adjacend vertices representing a triangle
        for (var idx = 0; idx < picking_triangles_number[j]; idx++) {
            thisBufferColors[4 * idx] = GL_colorPickerInitColors[(idx + pointsSoFar - (idx + pointsSoFar) % 3) / 3][0];
            thisBufferColors[4 * idx + 1] = GL_colorPickerInitColors[(pointsSoFar + idx - (idx + pointsSoFar) % 3) / 3][1];
            thisBufferColors[4 * idx + 2] = GL_colorPickerInitColors[(pointsSoFar + idx - (idx + pointsSoFar) % 3) / 3][2];
            thisBufferColors[4 * idx + 3] = GL_colorPickerInitColors[(pointsSoFar + idx - (idx + pointsSoFar) % 3) / 3][3];
        }
        //Since the colorPickingArray is not split we need to keep track of the absolute index of the triangles
        //considering all the files that were processed before, this pointsSoFar keeps track of this
        pointsSoFar += picking_triangles_number[j];
        gl.bufferData(gl.ARRAY_BUFFER, thisBufferColors, gl.STATIC_DRAW);
        colorPickingBuffer.push(newColorBuffer);
    }

    for (var j = 0; j < picking_triangles_number.length; j++) {
        BASE_PICK_brainPickingBuffers[j][3] = colorPickingBuffer[j];
    }
}

/**
 * Initialize the buffers for the surface that should be displayed in non-pick mode.
 */
function initDrawingBrainBuffers(urlVerticesDisplayList, urlTrianglesDisplayList, urlNormalsDisplayList, callback) {
    displayMessage("Start loading surface data!", "infoMessage");
    initDrawingBrainBuffersAsynchronous($.parseJSON(urlVerticesDisplayList), drawingBrainVertices, false, callback);
    initDrawingBrainBuffersAsynchronous($.parseJSON(urlNormalsDisplayList), drawingBrainNormals, false, callback);
    initDrawingBrainBuffersAsynchronous($.parseJSON(urlTrianglesDisplayList), drawingBrainIndexes, true, callback);
}

function initDrawingBrainBuffersAsynchronous(urlList, resultBuffers, isIndex, callback) {
    if (urlList.length == 0) {
        noOfUnloadedBrainDisplayBuffers -= 1;
        if (noOfUnloadedBrainDisplayBuffers == 0) {
            __createColorBuffers();
            displayMessage("Finished loading surface data!", "infoMessage");
            executeCallback(callback);
            drawScene();
        }
        return;
    }
    $.get(urlList[0], function (data) {
        var dataList = eval(data);
        var buffer = HLPR_createWebGlBuffer(gl, dataList, isIndex, false);
        resultBuffers.push(buffer);
        urlList.splice(0, 1);
        return initDrawingBrainBuffersAsynchronous(urlList, resultBuffers, isIndex, callback);
    });
}

function __createColorBuffers() {
    for (var i = 0; i < drawingBrainVertices.length; i++) {
        var fakeColorBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, fakeColorBuffer);
        var thisBufferColors = new Float32Array(drawingBrainVertices[i].numItems / 3 * 4);
        for (var j = 0; j < drawingBrainVertices[i].numItems / 3 * 4; j++) {
            thisBufferColors[j] = 0.5;
        }
        gl.bufferData(gl.ARRAY_BUFFER, thisBufferColors, gl.STATIC_DRAW);
        BASE_PICK_brainDisplayBuffers.push([drawingBrainVertices[i], drawingBrainNormals[i], drawingBrainIndexes[i], fakeColorBuffer]);
    }
}

/**
 * When mouse is released check to see if the difference between when mouse was pressed
 * and mouse was released is higher than a threshold(now set to 5). If so the user either
 * rotated brain (when higher) or selected vertice (when lower).
 */
function customMouseUp(event) {
	GL_handleMouseUp(event);
	
	var canvasOffset = $("#" + BRAIN_CANVAS_ID).offset();
    var final_x_val = GL_lastMouseX + document.body.scrollLeft + document.documentElement.scrollLeft - Math.floor(canvasOffset.left);
    var final_y_val = GL_lastMouseY + document.body.scrollTop + document.documentElement.scrollTop - Math.floor(canvasOffset.top) + 1;
	
    if ((Math.abs(final_x_val - GL_mouseXRelToCanvas) > 5) || (Math.abs(final_y_val - GL_mouseYRelToCanvas) > 5)) {
    	if (BASE_PICK_isMovieMode == false) {
    		drawScene();
    	}
    } else {
    	BASE_PICK_doVerticePick();
    }
}

function customMouseDown(event) {
	GL_handleMouseDown(event, $("#" + BRAIN_CANVAS_ID));
}

function customKeyDown(event) {
	GL_handleKeyDown(event);
	drawScene();
}

function customKeyUp(event) {
	GL_handleKeyUp(event);
	drawScene();
}

/**
 * Also redraw the scene on mouse move to give a more 'fluent' look
 */
function customMouseMove(event) {
	GL_handleMouseMove(event);
	if (BASE_PICK_isMovieMode == false) {
		drawScene();
	}
}

function handleMouseOut(event) {
	document.getElementById(BRAIN_CANVAS_ID).blur();
}

function BASE_PICK_initShaders() {
	basicInitShaders("shader-fs", "shader-vs");

    shaderProgram.vertexColorAttribute = gl.getAttribLocation(shaderProgram, "aVertexColor");
    gl.enableVertexAttribArray(shaderProgram.vertexColorAttribute);

    shaderProgram.ambientColorUniform = gl.getUniformLocation(shaderProgram, "uAmbientColor");
    shaderProgram.lightingDirectionUniform = gl.getUniformLocation(shaderProgram, "uLightingDirection");
    shaderProgram.directionalColorUniform = gl.getUniformLocation(shaderProgram, "uDirectionalColor");
    shaderProgram.isPicking = gl.getUniformLocation(shaderProgram, "isPicking");
    shaderProgram.materialShininessUniform = gl.getUniformLocation(shaderProgram, "uMaterialShininess");
    shaderProgram.pointLightingLocationUniform = gl.getUniformLocation(shaderProgram, "uPointLightingLocation");
    shaderProgram.pointLightingSpecularColorUniform = gl.getUniformLocation(shaderProgram, "uPointLightingSpecularColor");
}

///////////////////////////////////////~~~~~~~~START MOUSE RELATED CODE~~~~~~~~~~~//////////////////////////////////
/**
 * Function should move brain navigator to a selected vertice using a color picking scheme
 */
function BASE_PICK_doVerticePick() {
	//Drawing will be done to back buffer and all 'eye candy' is disabled to get pure color

    if (noOfUnloadedBrainPickingBuffers != 0 || noOfUnloadedBrainDisplayBuffers != 0) {
        displayMessage("The load operation for the surface data is not completed yet!", "infoMessage");
        return;
    }
    gl.bindFramebuffer(gl.FRAMEBUFFER, GL_colorPickerBuffer);
	gl.disable(gl.BLEND);
    gl.disable(gl.DITHER);
    gl.disable(gl.FOG);
    gl.disable(gl.LIGHTING);
    gl.disable(gl.TEXTURE_1D);
    gl.disable(gl.TEXTURE_2D);
	gl.viewport(0, 0, gl.viewportWidth, gl.viewportHeight);
	gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
	// View angle is 45, we want to see object from 0.1 up to 800 distance from viewer
	aspect = gl.viewportWidth / gl.viewportHeight;
	perspective(45, aspect , near, 800.0);
	loadIdentity();
	
	gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
	
	mvPushMatrix();
	mvTranslate([0.0, -5.0, -GL_zTranslation]);
    multMatrix(GL_currentRotationMatrix);
    mvRotate(180, [0, 0, 1]);
    
    //Draw the brain in picking mode
    BASE_PICK_doPick = true;
    
    //Swap normal display colors with picking colors and draw the 'colored' version to a back buffer
    BASE_PICK_drawBrain(BASE_PICK_brainPickingBuffers, noOfUnloadedBrainPickingBuffers);
    TRIANGLE_pickedIndex = GL_getPickedIndex();
    
    if (TRIANGLE_pickedIndex != GL_BACKGROUND) {
    /*
     * This should be 'fail-safe in case the clicked color is neither (0,0,0) nor in the picking dictionary. In this case just
     * start looking at adjacent pixels in pseudo-circular order until a proper one is found.
     */
	    var x_inc = 0;
	    var y_inc = 0;
	    var orig_x = GL_mouseXRelToCanvas;
	    var orig_y = GL_mouseYRelToCanvas;
	    
	    while (TRIANGLE_pickedIndex == GL_NOTFOUND && x_inc <= 20) {
	    	
			GL_mouseXRelToCanvas = orig_x + x_inc;
			GL_mouseYRelToCanvas = orig_y;
            TRIANGLE_pickedIndex = GL_getPickedIndex();
	    	if (TRIANGLE_pickedIndex != GL_NOTFOUND) { break; }
	    	
			GL_mouseXRelToCanvas = orig_x + x_inc;
			GL_mouseYRelToCanvas = orig_y + y_inc;
            TRIANGLE_pickedIndex = GL_getPickedIndex();
	    	if (TRIANGLE_pickedIndex != GL_NOTFOUND) { break; }
	    	
			GL_mouseXRelToCanvas = orig_x;
			GL_mouseYRelToCanvas = orig_y + y_inc;
            TRIANGLE_pickedIndex = GL_getPickedIndex();
	    	if (TRIANGLE_pickedIndex != GL_NOTFOUND) { break; }

			GL_mouseXRelToCanvas = orig_x - x_inc;
			GL_mouseYRelToCanvas = orig_y + y_inc;
            TRIANGLE_pickedIndex = GL_getPickedIndex();
	    	if (TRIANGLE_pickedIndex != GL_NOTFOUND) { break; }

			GL_mouseXRelToCanvas = orig_x - x_inc;
			GL_mouseYRelToCanvas = orig_y;
            TRIANGLE_pickedIndex = GL_getPickedIndex();
	    	if (TRIANGLE_pickedIndex != GL_NOTFOUND) { break; }

			GL_mouseXRelToCanvas = orig_x - x_inc;
			GL_mouseYRelToCanvas = orig_y - y_inc;
            TRIANGLE_pickedIndex = GL_getPickedIndex();
	    	if (TRIANGLE_pickedIndex != GL_NOTFOUND) { break; }

	    	GL_mouseXRelToCanvas = orig_x;
			GL_mouseYRelToCanvas = orig_y - y_inc;
            TRIANGLE_pickedIndex = GL_getPickedIndex();
	    	if (TRIANGLE_pickedIndex != GL_NOTFOUND) { break; }

	    	GL_mouseXRelToCanvas = orig_x + x_inc;
			GL_mouseYRelToCanvas = orig_y - y_inc;
            TRIANGLE_pickedIndex = GL_getPickedIndex();
	    	if (TRIANGLE_pickedIndex != GL_NOTFOUND) { break; }
	    
	    	x_inc += 1;
	    	y_inc += 1;
	    }
        BASE_PICK_moveBrainNavigator(false);
    }
    
    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
    
    //We found out pickedx inde now just draw again as normal
    mvPopMatrix();		 
	BASE_PICK_doPick = false;
	
	if (BASE_PICK_isMovieMode == false) {
		drawScene();
	}
}


/**
 * Moves the brain navigator to a certain position.
 */
function BASE_PICK_moveBrainNavigator(shouldRedrawScene) {
    if (TRIANGLE_pickedIndex != GL_NOTFOUND && TRIANGLE_pickedIndex != GL_BACKGROUND) {
        // If we managed to find an index find the triangle that corresponds to it from the list of splitted triangles
        // Then take the first vertice as new navigator coordinate. TODO: this could be replaced with some other metric
        // like the center of the triangle, or the vertice closest the the other two etc.

        var pickedIndex = TRIANGLE_pickedIndex;
        for (var j = 0; j < picking_triangles_number.length; j++) {
            if (pickedIndex < picking_triangles_number[j] / 3) {
                navigatorX = parseFloat(verticesPoints[j][9 * pickedIndex]);
                navigatorY = parseFloat(verticesPoints[j][9 * pickedIndex + 1]);
                navigatorZ = parseFloat(verticesPoints[j][9 * pickedIndex + 2]);
                break;
            } else {
                pickedIndex = pickedIndex - picking_triangles_number[j] / 3;
            }
        }
        VERTEX_pickedIndex = pickedIndex;
    }
    navigatorXrot = (360 - Math.atan2(navigatorY - BRAIN_CENTER[1], navigatorZ - BRAIN_CENTER[2]) * 180 / Math.PI) % 360;
    navigatorYrot = Math.atan2(navigatorX - BRAIN_CENTER[0], Math.sqrt((navigatorZ - BRAIN_CENTER[2]) * (navigatorZ - BRAIN_CENTER[2]) + (navigatorY - BRAIN_CENTER[1]) * (navigatorY - BRAIN_CENTER[1]))) * 180 / Math.PI;
    
    if (shouldRedrawScene) {
        drawScene();
    }
}


function BASE_PICK_removeFocalPoint(triangleIndex) {
	/*
	 * Remove the focal point given by triangle index.
	 */
	delete surfaceFocalPoints[triangleIndex];
	BASE_PICK_drawBrain(BASE_PICK_brainDisplayBuffers, noOfUnloadedBrainDisplayBuffers);
}


function BASE_PICK_clearFocalPoints() {
	surfaceFocalPoints = {};
	BASE_PICK_drawBrain(BASE_PICK_brainDisplayBuffers, noOfUnloadedBrainDisplayBuffers);
}


function BASE_PICK_addFocalPoint(triangleIndex) {
	/*
	 * Store all required information in order to draw this focal point.
	 */
	x_rot = (360 - Math.atan2(navigatorY - BRAIN_CENTER[1], navigatorZ - BRAIN_CENTER[2]) * 180 / Math.PI) % 360;
    y_rot = Math.atan2(navigatorX - BRAIN_CENTER[0], Math.sqrt((navigatorZ - BRAIN_CENTER[2]) * (navigatorZ - BRAIN_CENTER[2]) + (navigatorY - BRAIN_CENTER[1]) * (navigatorY - BRAIN_CENTER[1]))) * 180 / Math.PI;
    surfaceFocalPoints[triangleIndex] = {'xRotation' : x_rot, 'yRotation' : y_rot, 'position' : [navigatorX, navigatorY, navigatorZ]};
    BASE_PICK_drawBrain(BASE_PICK_brainDisplayBuffers, noOfUnloadedBrainDisplayBuffers);
}

/////////////////////////////////////////~~~~~~~~END MOUSE RELATED CODE~~~~~~~~~~~//////////////////////////////////

function createStimulusPinBuffers() {
	BASE_PICK_pinBuffers[0] = gl.createBuffer();
	gl.bindBuffer(gl.ARRAY_BUFFER, BASE_PICK_pinBuffers[0]);
	var vertices = [-1, 0.5, 5,
					-0.5, 1, 5,
					0.5, 1, 5,
					1, 0.5, 5,
					1, -0.5, 5,
					0.5, -1, 5,
					-0.5, -1, 5,
					-1, -0.5, 5,
					0, 0, 0,
					-0.2, -0.2, 5,
					-0.2, 0.2, 5,
					0.2, -0.2, 5,
					0.2, 0.2, 5,
					-0.2, -0.2, 12,
					-0.2, 0.2, 12,
					0.2, -0.2, 12,
					0.2, 0.2, 12];
	gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices), gl.STATIC_DRAW);
    BASE_PICK_pinBuffers[0].itemSize = 3;
    BASE_PICK_pinBuffers[0].numItems = 17;
    
    BASE_PICK_pinBuffers[1] = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, BASE_PICK_pinBuffers[1]);
    var vertexNormals = [ 
				        0.0,  0.0,  1.0,
				        0.0,  0.0,  1.0,
				        0.0,  0.0,  1.0,
				        0.0,  0.0,  1.0,
				        0.0,  0.0,  1.0,
				        0.0,  0.0,  1.0,
				        0.0,  0.0,  1.0,
				        0.0,  0.0,  1.0,
				        0.0,  0.0,  1.0,
				        0.0,  0.0,  1.0,
				        0.0,  0.0,  1.0,
				        0.0,  0.0,  1.0,
				        0.0,  0.0,  1.0,
				        0.0,  0.0,  1.0,
				        0.0,  0.0,  1.0,
				        0.0,  0.0,  1.0,
				        0.0,  0.0,  1.0
				    ];
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertexNormals), gl.STATIC_DRAW);
    BASE_PICK_pinBuffers[1].itemSize = 3;
    BASE_PICK_pinBuffers[1].numItems = 17;
    
    BASE_PICK_pinBuffers[2] = gl.createBuffer();
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, BASE_PICK_pinBuffers[2]);
    var cubeVertexIndices = [   0, 1, 5,      1, 2, 5,    
						        2, 3, 5,      3, 4, 5,
						        6, 7, 5,      0, 7, 5,
						        0, 1, 8,      1, 2, 8,
						        2, 3, 8,      3, 4, 8,
						        4, 5, 8,      5, 6, 8,
						        6, 7, 7,      9, 10, 11,      
						        10, 11, 12,   13, 14, 15,
						        14, 15, 16, 
						        9, 10, 13,      10, 13, 14,	  
						        10, 12, 14,      12, 14, 16,
						        11, 12, 16,      11, 15, 16,
						        9, 11, 13,      11, 13, 15     
						    ];
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint16Array(cubeVertexIndices), gl.STATIC_DRAW);
    BASE_PICK_pinBuffers[2].itemSize = 1;
    BASE_PICK_pinBuffers[2].numItems = 75;
    
	same_color = [];
    for (var i=0; i<BASE_PICK_pinBuffers[0].numItems* 4; i++) {
    	same_color = same_color.concat(1.0, 0.6, 0.0, 1.0);
    }
    BASE_PICK_pinBuffers[3] = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, BASE_PICK_pinBuffers[3]);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(same_color), gl.STATIC_DRAW);
}

////////////////////////////////////~~~~~~~~START BRAIN NAVIGATOR RELATED CODE~~~~~~~~~~~///////////////////////////

function initBrainNavigatorBuffers() {
    BASE_PICK_navigatorBuffers[0] = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, BASE_PICK_navigatorBuffers[0]);
	var vertices = [-0.2, -0.2, 0,
					-0.2, 0.2, 0,
					0.2, -0.2, 0,
					0.2, 0.2, 0,
					-0.2, -0.2, 12,
					-0.2, 0.2, 12,
					0.2, -0.2, 12,
					0.2, 0.2, 12,
					-1, 0.5, 12,
					-0.5, 1, 12,
					0.5, 1, 12,
					1, 0.5, 12,
					1, -0.5, 12,
					0.5, -1, 12,
					-0.5, -1, 12,
					-1, -0.5, 12];
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices), gl.STATIC_DRAW);
    BASE_PICK_navigatorBuffers[0].itemSize = 3;
    BASE_PICK_navigatorBuffers[0].numItems = 16;

    BASE_PICK_navigatorBuffers[1] = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, BASE_PICK_navigatorBuffers[1]);
    var vertexNormals = [ 
				        0.0,  0.0,  1.0,
				        0.0,  0.0,  1.0,
				        0.0,  0.0,  1.0,
				        0.0,  0.0,  1.0,
				        0.0, 0.0,  1.0,
				        0.0, 0.0,  1.0,
				        0.0, 0.0,  1.0,
				        0.0, 0.0,  1.0,
				        0.0, 0.0,  1.0,
				        0.0, 0.0,  1.0,
				        0.0, 0.0,  1.0,
				        0.0, 0.0,  1.0,
				        0.0, 0.0,  1.0,
				        0.0, 0.0,  1.0,
				        0.0, 0.0,  1.0,
				        0.0, 0.0,  1.0
				    ];
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertexNormals), gl.STATIC_DRAW);
    BASE_PICK_navigatorBuffers[1].itemSize = 3;
    BASE_PICK_navigatorBuffers[1].numItems = 12;

    BASE_PICK_navigatorBuffers[2] = gl.createBuffer();
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, BASE_PICK_navigatorBuffers[2]);
    var cubeVertexIndices = [   0, 1, 2,      1, 2, 3,    // z plane - far
						        4, 5, 6,      5, 6, 7,    // z plane - near - small
						        8, 9, 13,     9, 10, 13,  // z plane - near - big
						        10, 11, 13,   11, 12, 13,
						        14, 15, 13,   8, 15, 13,
						        0, 1, 4,      1, 4, 5,	  // 'walls'
						        1, 3, 5,      3, 5, 7,
						        2, 3, 7,      2, 6, 7,
						        0, 2, 4,      2, 4, 6
						    ];
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint16Array(cubeVertexIndices), gl.STATIC_DRAW);
    BASE_PICK_navigatorBuffers[2].itemSize = 1;
    BASE_PICK_navigatorBuffers[2].numItems = 54;
	same_color = [];
    for (var i=0; i<BASE_PICK_navigatorBuffers[0].numItems* 4; i++) {
    	same_color = same_color.concat(0.0, 0.0, 1.0, 1.0);
    }
    BASE_PICK_navigatorBuffers[3] = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, BASE_PICK_navigatorBuffers[3]);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(same_color), gl.STATIC_DRAW);
}

////////////////////////////////////~~~~~~~~END BRAIN NAVIGATOR RELATED CODE~~~~~~~~~~~/////////////////////////////

/**
 * Draw the light
 */
function addLight() {
    gl.uniform3f(shaderProgram.ambientColorUniform, 0.8, 0.8, 0.7);
    var lightingDirection = Vector.create([0.85, 0.8, 0.75]);
    var adjustedLD = lightingDirection.toUnitVector().x(-1);
    var flatLD = adjustedLD.flatten();
    gl.uniform3f(shaderProgram.lightingDirectionUniform, flatLD[0], flatLD[1], flatLD[2]);
    gl.uniform3f(shaderProgram.directionalColorUniform, 0.7, 0.7, 0.7);
    gl.uniform3f(shaderProgram.pointLightingLocationUniform, 0, -10, -400);
    gl.uniform3f(shaderProgram.pointLightingSpecularColorUniform, 0.8, 0.8, 0.8);
    gl.uniform1f(shaderProgram.materialShininessUniform, 30.0);
}

/**
 * Create webgl buffers from the specified files
 *
 * @param dataList the list of JS data
 * @return a list in which will be added the buffers created based on the data from the specified files
 */

//This was used when selecting vertice from navigator panels, to change the color of the area
//that is closest to that point. In this version it's not used but the function that does
//it is still here and will keep until finally deciding on final solution.
var colorArrays = [];
//Keep the vertices data for it will be needed later for the actual coordinates
//of the selected point and for computing the closest vertices when using '2d-type-selection'
var verticesPoints = [];

var picking_triangles_number = [];
var total_picking_triangles_number = 0;


function drawBuffers(drawMode, buffersSets, isSurface) {
    for (var i = 0; i < buffersSets.length; i++) {
        gl.bindBuffer(gl.ARRAY_BUFFER, buffersSets[i][0]);
        gl.vertexAttribPointer(shaderProgram.vertexPositionAttribute, TRI, gl.FLOAT, false, 0, 0);
        gl.bindBuffer(gl.ARRAY_BUFFER, buffersSets[i][1]);
        gl.vertexAttribPointer(shaderProgram.vertexNormalAttribute, TRI, gl.FLOAT, false, 0, 0);
    	gl.bindBuffer(gl.ARRAY_BUFFER, buffersSets[i][3]);
        gl.vertexAttribPointer(shaderProgram.vertexColorAttribute, 4, gl.FLOAT, false, 0, 0);
    	gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, buffersSets[i][2]);	
        setMatrixUniforms();
        gl.drawElements(drawMode, buffersSets[i][2].numItems, gl.UNSIGNED_SHORT, 0);
    }
}

/**
 * Draw from buffers.
 */
function BASE_PICK_drawBrain(brainBuffers, noOfUnloadedBuffers) {
    if (noOfUnloadedBuffers != 0) {
        displayMessage("The load operation for the surface data is not completed yet!", "infoMessage");
        return;
    }
	
    if (BASE_PICK_doPick == false) {
    	gl.enable(gl.BLEND);
	    gl.enable(gl.DITHER);
	    gl.enable(gl.FOG);
	    gl.enable(gl.LIGHTING);
	    gl.enable(gl.TEXTURE_1D);
	    gl.enable(gl.TEXTURE_2D);
    	addLight();
    	gl.uniform1f(shaderProgram.isPicking, 0);
    } else {
		gl.disable(gl.BLEND);
	    gl.disable(gl.DITHER);
	    gl.disable(gl.FOG);
	    gl.disable(gl.LIGHTING);
	    gl.disable(gl.TEXTURE_1D);
	    gl.disable(gl.TEXTURE_2D);
    	gl.uniform1f(shaderProgram.isPicking, 1);
    }
		
	gl.viewport(0, 0, gl.viewportWidth, gl.viewportHeight);
	gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
	// View angle is 45, we want to see object from 0.1 up to 800 distance from viewer
	aspect = gl.viewportWidth / gl.viewportHeight;
	perspective(45, aspect , near, 800.0);
	loadIdentity();
    
    // Translate to get a good view.
    mvTranslate([0.0, -5.0, -GL_zTranslation]);
    multMatrix(GL_currentRotationMatrix);
    mvRotate(180, [0, 0, 1]);

    drawBuffers(drawingMode, brainBuffers);

	if (BASE_PICK_isMovieMode == false) {
		mvPushMatrix();
		mvTranslate([navigatorX, navigatorY, navigatorZ]);
		mvRotate(navigatorXrot, [1, 0, 0]);
		mvRotate(navigatorYrot, [0, 1, 0]);
	    drawBuffers(gl.TRIANGLES, [BASE_PICK_navigatorBuffers]);
	    mvPopMatrix();
	}
	
    for (var key in surfaceFocalPoints) {
    	var focalPointPosition = surfaceFocalPoints[key]['position'];
    	mvPushMatrix();
    	mvTranslate(focalPointPosition);
    	mvRotate(surfaceFocalPoints[key]['xRotation'], [1, 0, 0]);
    	mvRotate(surfaceFocalPoints[key]['yRotation'], [0, 1, 0]);
    	drawBuffers(gl.TRIANGLES, [BASE_PICK_pinBuffers]);
    	mvPopMatrix();
    }
}

// ------------------------------------- START CODE FOR PICKING FROM 2D NAVIGATOR PICKS ----------------------------
/**
 * Find the intersection between a point given by mouseX and mouseY coordinates and a plane
 * given by an axis represented by type (0=x, 1=y, 2=z)
 */
function findPlaneIntersect(mouseX, mouseY, mvPickMatrix, near, aspect, fov, type) {

  	var centered_x, centered_y, unit_x, unit_y, near_height, near_width, i, j;
    
	centered_y = gl.viewportHeight - mouseY - gl.viewportHeight/2.0;
	centered_x = mouseX - gl.viewportWidth/2.0;
	unit_x = centered_x/(gl.viewportWidth/2.0);
	unit_y = centered_y/(gl.viewportHeight/2.0);    
	near_height = near * Math.tan( fov * Math.PI / 360.0 );
	near_width = near_height*aspect;
	var ray = Vector.create([ unit_x*near_width, unit_y*near_height, -1.0*near, 0 ]);
	var ray_start_point = Vector.create([ 0.0, 0.0, 0.0, 1.0 ]);
	
	//mvPickMatrix = translateMatrix(currentPoint, mvPickMatrix);
	var R = mvPickMatrix.minor(1,1,3,3);
	var Rt = R.transpose();	
	var tc = mvPickMatrix.col(4);	
	var t = Vector.create([ tc.e(1), tc.e(2), tc.e(3) ]);	
	var tp = Rt.x(t);
	var mvPickMatrixInv = Matrix.I(4);
	for (i=0; i < 3; i++) {
		for (j=0; j < 3; j++) {
			mvPickMatrixInv.elements[i][j] = Rt.elements[i][j];
		}	
		mvPickMatrixInv.elements[i][3] = -1.0 * tp.elements[i];
	}		
	var rayp = mvPickMatrixInv.x(ray);
	var ray_start_pointp = mvPickMatrixInv.x(ray_start_point);
	var anchor = Vector.create([ ray_start_pointp.e(1), ray_start_pointp.e(2), ray_start_pointp.e(3) ]);
	var direction = Vector.create([ rayp.e(1), rayp.e(2), rayp.e(3) ]);
	
    // Perform intersection test between ray l and world geometry (cube)
    // Line and Plane objects are taken from sylvester.js library
	var l = Line.create(anchor, direction.toUnitVector());
	// Geometry in this case is a front plane of cube at z = 1;
	anchor = Vector.create([ 0, 0, 0 ]);    // Vertex of the cube
	var normal = Vector.create([0, 0, 0 ]);  // Normal of front face of cube
	normal.elements[type] = 1;
    return getIntersection(anchor, normal, l); 
}

function getIntersection(anchor, normal, l) {	
	var p = Plane.create(anchor, normal);   // Plane 
	// Check if line l and plane p intersect
	var rval = false;
	if (l.intersects(p)) {
		var intersectionPt = l.intersectionWith(p);
		return intersectionPt.elements;
	}
	return null;
}

/**
 * The handlers for the 3 navigator windows. For each of them the steps are:
 * 1. Get mouse position
 * 2. Check if click was done on the IMG element or in the rest of the div(ignore the later)
 * 3. Apply the basic transformations that were done in generating the navigator IMG
 * 4. Find intersection with specific plane and move navigator there
 */
function handleXLocale(event) {
	// Get the mouse position relative to the canvas element.
    var GL_mouseXRelToCanvasImg = 0;
    var GL_mouseYRelToCanvasImg = 0;
    if (event.offsetX || event.offsetX == 0) { // Opera and Chrome
        GL_mouseXRelToCanvasImg = event.offsetX;
        GL_mouseYRelToCanvasImg = event.offsetY;
    } else if (event.layerX || event.layerY == 0) { // Firefox
       GL_mouseXRelToCanvasImg = event.layerX;
       GL_mouseYRelToCanvasImg = event.layerY;
    }
    if ((event.originalTarget != undefined && event.originalTarget.nodeName == 'IMG') || (
    	event.srcElement != undefined && event.srcElement.nodeName == 'IMG')) {
        GL_mouseXRelToCanvas = (GL_mouseXRelToCanvasImg * $('#GLcanvas').width()) / 250.0;
        GL_mouseYRelToCanvas = (GL_mouseYRelToCanvasImg * $('#GLcanvas').height()) / 172.0;

    	perspective(45, gl.viewportWidth / gl.viewportHeight, near, 800.0);
        loadIdentity();
        addLight();
        
        // Translate to get a good view.
        mvTranslate([0.0, -5.0, -GL_DEFAULT_Z_POS]);
    	//multMatrix(GL_currentRotationMatrix);
        mvRotate(180, [0, 0, 1]);
        
    	sectionViewRotationMatrix = createRotationMatrix(90, [0, 1, 0]).x(createRotationMatrix(270, [1, 0, 0]));
    	multMatrix(sectionViewRotationMatrix);
    	var result = findPlaneIntersect(GL_mouseXRelToCanvas, GL_mouseYRelToCanvas, GL_mvMatrix, near, gl.viewportWidth / gl.viewportHeight, fov, 0);
    	NAV_navigatorY = result[1];
    	NAV_navigatorZ = -result[2];
		_redrawSectionView = true;
		NAV_draw_navigator();    	
    }
}

function handleYLocale(event) {
	// Get the mouse position relative to the canvas element.
    var GL_mouseXRelToCanvasImg = 0;
    var GL_mouseYRelToCanvasImg = 0;
    if (event.offsetX || event.offsetX == 0) { // Opera and Chrome
        GL_mouseXRelToCanvasImg = event.offsetX;
        GL_mouseYRelToCanvasImg = event.offsetY;
    } else if (event.layerX || event.layerY == 0) { // Firefox
        GL_mouseXRelToCanvasImg = event.layerX;
        GL_mouseYRelToCanvasImg = event.layerY;
    }
    if ((event.originalTarget != undefined && event.originalTarget.nodeName == 'IMG') || (
    	event.srcElement != undefined && event.srcElement.nodeName == 'IMG')) {
        GL_mouseXRelToCanvas = (GL_mouseXRelToCanvasImg * $('#GLcanvas').width()) / 250.0;
        GL_mouseYRelToCanvas = (GL_mouseYRelToCanvasImg * $('#GLcanvas').height()) / 172.0;

    	perspective(45, gl.viewportWidth / gl.viewportHeight, near, 800.0);
        loadIdentity();
        addLight();
        
        // Translate to get a good view.
		mvTranslate([0.0, -5.0, -GL_DEFAULT_Z_POS]);
    	//multMatrix(GL_currentRotationMatrix);
    	mvRotate(180, [0, 0, 1]);    	
    	
    	sectionViewRotationMatrix = createRotationMatrix(90, [1, 0, 0]).x(createRotationMatrix(180, [1, 0, 0]));
    	multMatrix(sectionViewRotationMatrix);
    	var result = findPlaneIntersect(GL_mouseXRelToCanvas, GL_mouseYRelToCanvas, GL_mvMatrix, near, gl.viewportWidth / gl.viewportHeight, fov, 1);
    	NAV_navigatorX = result[0];
    	NAV_navigatorZ = -result[2];
		_redrawSectionView = true;
		NAV_draw_navigator();     	
    }
}

function handleZLocale(event) {
	// Get the mouse position relative to the canvas element.
    var GL_mouseXRelToCanvasImg = 0;
    var GL_mouseYRelToCanvasImg = 0;
    if (event.offsetX || event.offsetX == 0) { // Opera and Chrome
        GL_mouseXRelToCanvasImg = event.offsetX;
        GL_mouseYRelToCanvasImg = event.offsetY;
    } else if (event.layerX || event.layerY == 0) { // Firefox
        GL_mouseXRelToCanvasImg = event.layerX;
        GL_mouseYRelToCanvasImg = event.layerY;
    }
    if ((event.originalTarget != undefined && event.originalTarget.nodeName == 'IMG') || (
    	event.srcElement != undefined && event.srcElement.nodeName == 'IMG')) {
        GL_mouseXRelToCanvas = (GL_mouseXRelToCanvasImg * $('#GLcanvas').width()) / 250.0;
        GL_mouseYRelToCanvas = (GL_mouseYRelToCanvasImg * $('#GLcanvas').height()) / 172.0;
    	
    	perspective(45, gl.viewportWidth / gl.viewportHeight, near, 800.0);
        loadIdentity();
        addLight();
        
        // Translate to get a good view.
		mvTranslate([0.0, -5.0, -GL_DEFAULT_Z_POS]);
    	//multMatrix(GL_currentRotationMatrix);
    	mvRotate(180, [0, 0, 1]);
    	
    	sectionViewRotationMatrix = createRotationMatrix(180, [0, 1, 0]).x(Matrix.I(4));
    	multMatrix(sectionViewRotationMatrix);
    	var result = findPlaneIntersect(GL_mouseXRelToCanvas, GL_mouseYRelToCanvas, GL_mvMatrix, near, gl.viewportWidth / gl.viewportHeight, fov, 2);
    	NAV_navigatorX = -result[0];
    	NAV_navigatorY = result[1];
		_redrawSectionView = true;
		NAV_draw_navigator();     	
    }
}

function BASE_PICK_handleMouseWeel(event) {
	GL_handleMouseWeel(event);
	if (BASE_PICK_isMovieMode == false) {
		drawScene();
	}
}

/**
 * Init the legend labels, from minValue to maxValue
 *
 * @param maxValue Maximum value for the gradient end
 * @param minValue Minimum value for the gradient start
 */
function BASE_PICK_initLegendInfo(maxValue, minValue) {

	var brainLegendDiv = document.getElementById('brainLegendDiv');
    ColSch_updateLegendLabels(brainLegendDiv, minValue, maxValue, "100%")
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
