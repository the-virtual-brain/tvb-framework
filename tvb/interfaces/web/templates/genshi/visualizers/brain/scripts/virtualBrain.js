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
 * WebGL methods "inheriting" from webGL_xx.js in static/js.
 */
var BRAIN_CANVAS_ID = "GLcanvas";
/**
 * Variables for displaying Time and computing Frames/Sec
 */
var lastTime = 0;
var currentTimeValue = 0;
var TICK_STEP = 50;
var TIME_STEP = 1;
var AG_isStopped = false;
var sliderSel = false;
var framestime = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,
                  50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50];
var near = 0.1;
var fov = 45;
var isPreview = false;

var pointPosition = 75.0;

var brainBuffers = [];
var brainLinesBuffers = [];
var shelfBuffers = [];
var measurePointsBuffers = [];
/**
 * This buffer arrays will contain:
 * arr[i][0] Vertices buffer
 * arr[i][1] Normals buffer
 * arr[i][2] Triangles indices buffer
 * arr[i][3] Color buffer (same length as vertices /3 * 4) in case of one-to-one mapping
 * arr[i][3] Alpha buffer Gradient values for the 2 closest measurement points
 * arr[i][4] Alpha Indices Buffer Indices of the 3 closest measurement points, in care of not one-to-one mapping
 */ 


var activitiesData = [], timeData = [], measurePoints = [], measurePointsLabels = [];

var pageSize = 0;
var urlBase = '';
var selectedMode = 0;
var selectedStateVar = 0;
var currentActivitiesFileLength = 0;
var nextActivitiesFileData = [];
var totalPassedActivitiesData = 0;
var shouldIncrementTime = true;
var currentAsyncCall = null;
var drawTriangleLines = false;
var drawBoundaries = false;
var boundaryVertexBuffers = [];
var boundaryNormalsBuffers = [];
var boundaryEdgesBuffers = [];

var MAX_TIME_STEP = 0;
var NO_OF_MEASURE_POINTS = 0;
var NEXT_PAGE_THREASHOLD = 100;

var displayMeasureNodes = false;

var activityMin = 0, activityMax = 0;
var isOneToOneMapping = false;
var isDoubleView = false;

var drawingMode;


function _webGLPortletPreview(baseDatatypeURL, urlVerticesList, urlTrianglesList, urlNormalsList,
                              urlAlphasList, urlAlphasIndicesList, minActivity, maxActivity, oneToOneMapping) {
	isPreview = true;
	GL_DEFAULT_Z_POS = 250;
	GL_zTranslation = GL_DEFAULT_Z_POS;
	pageSize = 1;
	urlBase = baseDatatypeURL;
    activitiesData = HLPR_readJSONfromFile(readDataPageURL(urlBase, 0, 1, selectedStateVar, selectedMode, TIME_STEP));
    if (oneToOneMapping == 'True') {
        isOneToOneMapping = true;
    }
    activityMin = parseFloat(minActivity);
    activityMax = parseFloat(maxActivity);
    var canvas = document.getElementById(BRAIN_CANVAS_ID);
    customInitGL(canvas);
    initShaders();
    if ($.parseJSON(urlVerticesList)) {
    	brainBuffers = initBuffers($.parseJSON(urlVerticesList), $.parseJSON(urlNormalsList), $.parseJSON(urlTrianglesList), 
    						   $.parseJSON(urlAlphasList), $.parseJSON(urlAlphasIndicesList), false);
    }
    LEG_generateLegendBuffers();
    
    gl.clearColor(0.0, 0.0, 0.0, 1.0);
    gl.clearDepth(1.0);
    gl.enable(gl.DEPTH_TEST);
    gl.depthFunc(gl.LEQUAL);
    // Enable keyboard and mouse interaction
    canvas.onkeydown = GL_handleKeyDown;
    canvas.onkeyup = GL_handleKeyUp;
    canvas.onmousedown = customMouseDown;
    document.onmouseup = NAV_customMouseUp;
    document.onmousemove = customMouseMove;
    setInterval(tick, TICK_STEP);
}

function _webGLStart(baseDatatypeURL, onePageSize, urlTimeList, urlVerticesList, urlLinesList, urlTrianglesList, urlNormalsList, urlMeasurePoints, noOfMeasurePoints,
                     urlAlphasList, urlAlphasIndicesList, minActivity, maxActivity, oneToOneMapping, doubleView, shelfObject, urlMeasurePointsLabels, boundaryURL) {
	isPreview = false;
    isDoubleView = doubleView;
    GL_DEFAULT_Z_POS = 250;
    if (isDoubleView) {
    	GL_currentRotationMatrix = createRotationMatrix(270, [1, 0, 0]).x(createRotationMatrix(270, [0, 0, 1]));
    	GL_DEFAULT_Z_POS = 300;
    	$("#displayFaceChkId").trigger('click');
    }
    GL_zTranslation = GL_DEFAULT_Z_POS;
    
    if (noOfMeasurePoints > 0) {
	    measurePoints = HLPR_readJSONfromFile(urlMeasurePoints);
        measurePointsLabels = HLPR_readJSONfromFile(urlMeasurePointsLabels);
	    NO_OF_MEASURE_POINTS = measurePoints.length;
	} else if (noOfMeasurePoints < 0) {
		measurePoints = $.parseJSON(urlMeasurePoints);
		measurePointsLabels = HLPR_readJSONfromFile(urlMeasurePointsLabels);
	    NO_OF_MEASURE_POINTS = measurePoints.length;
	} else {
		NO_OF_MEASURE_POINTS = 0;
		measurePoints = [];
		measurePointsLabels = [];
	}
    
    var timeUrls = $.parseJSON(urlTimeList);
    for (var i = 0; i < timeUrls.length; i++) {
    	timeData = timeData.concat(HLPR_readJSONfromFile(timeUrls[i]));
    }
    
	pageSize = onePageSize;
	urlBase = baseDatatypeURL;
	initActivityData();

    if (oneToOneMapping == 'True') {
        isOneToOneMapping = true;
    }
    activityMin = parseFloat(minActivity);
    activityMax = parseFloat(maxActivity);
    
    var canvas = document.getElementById(BRAIN_CANVAS_ID);
    customInitGL(canvas);
    GL_initColorPickFrameBuffer();
    initShaders();
    NAV_initBrainNavigatorBuffers();

    LEG_initMinMax(activityMin, activityMax);

    if ($.parseJSON(urlVerticesList)) {
	    brainBuffers = initBuffers($.parseJSON(urlVerticesList), $.parseJSON(urlNormalsList), $.parseJSON(urlTrianglesList), 
	    						   $.parseJSON(urlAlphasList), $.parseJSON(urlAlphasIndicesList), isDoubleView);
    		}
    brainLinesBuffers = HLPR_getDataBuffers(gl, $.parseJSON(urlLinesList), isDoubleView, true);
    LEG_generateLegendBuffers();
    initRegionBoundaries(boundaryURL);
    
    if (shelfObject) {
    	shelfObject = $.parseJSON(shelfObject);
    	shelfBuffers = initBuffers(shelfObject[0], shelfObject[1], shelfObject[2], false, false, true);
    }
    // Initialize the buffers for the measure points
    for (var i = 0; i < NO_OF_MEASURE_POINTS; i++) {
        measurePointsBuffers[i] = bufferAtPoint(measurePoints[i], i);
    }

    gl.clearColor(0.0, 0.0, 0.0, 1.0);
    gl.clearDepth(1.0);
    gl.enable(gl.DEPTH_TEST);
    gl.depthFunc(gl.LEQUAL);
    // Enable keyboard and mouse interaction
    canvas.onkeydown = GL_handleKeyDown;
    canvas.onkeyup = GL_handleKeyUp;
    canvas.onmousedown = customMouseDown;
    document.onmouseup = NAV_customMouseUp;
    document.onmousemove = customMouseMove; 
    
    if (!isPreview) {
	    if (timeData.length > 0) {
	        MAX_TIME_STEP = timeData.length - 1;
	        $("#sliderStep").slider({min:1, max: 50, step: 1,
	            stop: function(ev, ui) {
	            	var newStep = $("#sliderStep").slider("option", "value");
	                setTimeStep(newStep);
	                refreshCurrentDataSlice();
	                sliderSel = false;
	            },
	            slide: function(event, ui) {
	            	sliderSel = true;
	            }
	            });
	        // Initialize slider for timeLine
	        $("#slider").slider({ min:0, max: MAX_TIME_STEP,
	            slide: function(event, ui) {
	                sliderSel = true;
	                currentTimeValue = $("#slider").slider("option", "value");
	            },
	            stop: function(event, ui) {
	                sliderSel = false;
	                loadFromTimeStep($("#slider").slider("option", "value"));
	            } });
	    } else {
	        $("#fieldSetForSliderSpeed").hide();
	    }
	    document.getElementById("Infobox").innerHTML = "";
	}
	if (!isDoubleView) {
		canvasX = document.getElementById('brain-x');
    	if (canvasX) canvasX.onmousedown = handleXLocale;
	    canvasY = document.getElementById('brain-y');
	    if (canvasY) canvasY.onmousedown = handleYLocale;
	    canvasZ = document.getElementById('brain-z');
	    if (canvasZ) canvasZ.onmousedown = handleZLocale;
	}

    //validate activitiesData and specify the re-draw function.
    if(isOneToOneMapping){
        if(3 * activitiesData[0].length === brainBuffers[0][0].numItems ){            
            setInterval(tick, TICK_STEP);
        } else{
            displayMessage("The number of activity points should equal the number of surface vertices", "errorMessage");
        }
    } else {
        if (NO_OF_MEASURE_POINTS === activitiesData[0].length){
            setInterval(tick, TICK_STEP);
        } else{
            displayMessage("The number of activity points should equal the number of regions", "errorMessage");
        }
    }
}

////////////////////////////////////////// GL Initializations //////////////////////////////////////////

function customInitGL(canvas) {
	window.onresize = function() {
		updateGLCanvasSize(BRAIN_CANVAS_ID);
	};
	initGL(canvas);
    canvas.redrawFunctionRef = drawScene;            // interface-like function used in HiRes image exporting
    drawingMode = gl.TRIANGLES;
    gl.newCanvasWidth = canvas.clientWidth;
    gl.newCanvasHeight = canvas.clientHeight;
}

function initShaders() {
    basicInitShaders("shader-fs", "shader-vs");

    if (isOneToOneMapping) {
        shaderProgram.vertexColorAttribute = gl.getAttribLocation(shaderProgram, "aVertexColor");
        gl.enableVertexAttribArray(shaderProgram.vertexColorAttribute);
    } else {
        shaderProgram.vertexAlphaAttribute = gl.getAttribLocation(shaderProgram, "alpha");
        gl.enableVertexAttribArray(shaderProgram.vertexAlphaAttribute);
        shaderProgram.vertexColorIndicesAttribute = gl.getAttribLocation(shaderProgram, "alphaIndices");
        gl.enableVertexAttribArray(shaderProgram.vertexColorIndicesAttribute);

        shaderProgram.colorsUniform = [];
        for (var i = 0; i <= NO_OF_MEASURE_POINTS + 1 + legendGranularity; i++) {
            shaderProgram.colorsUniform[i] = gl.getUniformLocation(shaderProgram, "uVertexColors[" + i + "]");
        }
    }

    shaderProgram.useBlending = gl.getUniformLocation(shaderProgram, "uUseBlending");
    shaderProgram.linesColor = gl.getUniformLocation(shaderProgram, "uLinesColor");
    shaderProgram.drawLines = gl.getUniformLocation(shaderProgram, "uDrawLines");
    shaderProgram.vertexLineColor = gl.getUniformLocation(shaderProgram, "uUseVertexLineColor");
    
    shaderProgram.ambientColorUniform = gl.getUniformLocation(shaderProgram, "uAmbientColor");
    shaderProgram.lightingDirectionUniform = gl.getUniformLocation(shaderProgram, "uLightingDirection");
    shaderProgram.directionalColorUniform = gl.getUniformLocation(shaderProgram, "uDirectionalColor");
    shaderProgram.isPicking = gl.getUniformLocation(shaderProgram, "isPicking");
    shaderProgram.pickingColor = gl.getUniformLocation(shaderProgram, "pickingColor");
    
    shaderProgram.materialShininessUniform = gl.getUniformLocation(shaderProgram, "uMaterialShininess");
    shaderProgram.pointLightingLocationUniform = gl.getUniformLocation(shaderProgram, "uPointLightingLocation");
    shaderProgram.pointLightingSpecularColorUniform = gl.getUniformLocation(shaderProgram, "uPointLightingSpecularColor");
}

///////////////////////////////////////~~~~~~~~START MOUSE RELATED CODE~~~~~~~~~~~//////////////////////////////////

var doPick = false;

function customMouseDown(event) {
	GL_handleMouseDown(event, $("#" + BRAIN_CANVAS_ID));
    NAV_inTimeRefresh = false
    if (displayMeasureNodes && isDoubleView) {
    	doPick = true;
    }
}

function customMouseMove(event) {
    if (!GL_mouseDown) {
        return;
    }
    var newX = event.clientX;
    var newY = event.clientY;
    var deltaX = newX - GL_lastMouseX;
    var deltaY = newY - GL_lastMouseY;
    if (NAV_isMouseControlOverBrain) {
	    var newRotationMatrix = createRotationMatrix(deltaX / 10, [0, 1, 0]);
	    newRotationMatrix = newRotationMatrix.x(createRotationMatrix(deltaY / 10, [1, 0, 0]));
        GL_currentRotationMatrix = newRotationMatrix.x(GL_currentRotationMatrix);
    } else {
        NAV_navigatorX = NAV_navigatorX - deltaX * 250 / 800;
        NAV_navigatorY = NAV_navigatorY + deltaY * 250 / 800;
    }
    GL_lastMouseX = newX;
    GL_lastMouseY = newY;
}

/////////////////////////////////////////~~~~~~~~END MOUSE RELATED CODE~~~~~~~~~~~//////////////////////////////////


////////////////////////////////////////~~~~~~~~~ WEB GL RELATED RENDERING ~~~~~~~/////////////////////////////////
/**
 * Update colors for all Positions on the brain.
 */
    
function updateColors(currentTimeValue) {
    var currentTimeInFrame = Math.floor((currentTimeValue - totalPassedActivitiesData) / TIME_STEP);
    if (isOneToOneMapping) {
        for (i = 0; i < brainBuffers.length; i++) {
        	// Reset color buffers at each step.
        	brainBuffers[i][3] = null;
            var upperBorder = brainBuffers[i][0].numItems / 3;
            var colors = new Float32Array(upperBorder * 4);
            var offset_start = i * 40000;

            getGradientColorArray(activitiesData[currentTimeInFrame].slice(offset_start, offset_start + upperBorder),
                                  activityMin, activityMax, colors);
            brainBuffers[i][3] = gl.createBuffer();
            gl.bindBuffer(gl.ARRAY_BUFFER, brainBuffers[i][3]);
            gl.bufferData(gl.ARRAY_BUFFER, colors, gl.STATIC_DRAW);
            colors = null;
        }
    } else {
        for (var i = 0; i < NO_OF_MEASURE_POINTS; i++) {
        	var rgb = getGradientColor(activitiesData[currentTimeInFrame][i], activityMin, activityMax)
            gl.uniform4f(shaderProgram.colorsUniform[i], rgb[0], rgb[1], rgb[2], 1);
        }
        // default color for a measure point
        gl.uniform4f(shaderProgram.colorsUniform[NO_OF_MEASURE_POINTS], 0.34, 0.95, 0.37, 1.0);
        // color used for a picked measure point
        gl.uniform4f(shaderProgram.colorsUniform[NO_OF_MEASURE_POINTS + 1], 0.99, 0.99, 0.0, 1.0);
    }
    if (shouldLoadNextActivitiesFile()) {
        loadNextActivitiesFile();
    }
    if (shouldChangeCurrentActivitiesFile()) {
        changeCurrentActivitiesFile();
    }
}

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

function toggleMeasureNodes() {
    displayMeasureNodes = ! displayMeasureNodes;
    if (displayMeasureNodes && isDoubleView) {
        $("input[type=checkbox][id^='channelChk_']").each(function (i) {
            if (this.checked) {
                var index = this.id.split("channelChk_")[1];
                EX_changeColorBufferForMeasurePoint(index, true);
            }
        });
    }
}


var isFaceToDisplay = false;
function switchFaceObject() {
	isFaceToDisplay = !isFaceToDisplay;
}

/**
 * Draw model with filled Triangles of isolated Points (Vertices).
 */
function wireFrame() {
    if (drawingMode == gl.POINTS) {
        drawingMode = gl.TRIANGLES;
        $("#ctrl-action-points").html("Points");
    } else {
        drawingMode = gl.POINTS;
        $("#ctrl-action-points").html("Smooth");
    }
}


/**
 * Movie interaction
 */
function pauseMovie() {
    AG_isStopped = !AG_isStopped;
    var pauseButton = $("#ctrl-action-pause");
    if (AG_isStopped) {
        pauseButton.html("Play");
        pauseButton.attr("class", "action action-controller-launch");
    } else {
        pauseButton.html("Pause");
        pauseButton.attr("class", "action action-controller-pause");
    }
}

function setTimeStep(newStep) {
    TIME_STEP = newStep;
    if (TIME_STEP == 0) {
        TIME_STEP = 1;
    }
}

function resetSpeedSlider() {
	if (!isPreview) {
		setTimeStep(1);
    	$("#sliderStep").slider("option", "value", 1);
    	refreshCurrentDataSlice();
	}
}


function toggleDrawTriangleLines() {
	drawTriangleLines = !drawTriangleLines;
}

function toggleDrawBoundaries() {
	drawBoundaries = !drawBoundaries;
}

/**
 * Creates a list of webGl buffers.
 *
 * @param dataList a list of lists. Each list will contain the data needed for creating a gl buffer.
 */
function createWebGlBuffers(dataList) {
    var result = [];
    for (var i = 0; i < dataList.length; i++) {
        var buffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(dataList[i]), gl.STATIC_DRAW);
        buffer.numItems = dataList[i].length;
        result.push(buffer);
    }

    return result;
}

/**
 * Read data from the specified urls.
 *
 * @param data_url_list a list of urls from where   it should read the data
 * @param staticFiles <code>true</code> if the urls points to some static files
 */
function readFloatData(data_url_list, staticFiles) {
    var result = [];
    for (var i = 0; i < data_url_list.length; i++) {
        var data_json = HLPR_readJSONfromFile(data_url_list[i], staticFiles);
        if (staticFiles) {
            for (var j = 0; j < data_json.length; j++) {
                data_json[j] = parseFloat(data_json[j]);
            }
        }
        result.push(data_json);
        data_json = null;
    }
    return result;
}

/**
 * Computes the data for alpha and alphasIndices.
 *
 * @param vertices a list which contains lists of vertices. E.g.: [[slice_1_vertices],...,[slice_n_vertices]]
 * @param measurePoints a list which contains all the measure points. E.g.: [[x0,y0,z0],[x1,y1,z1],...]
 */
function computeAlphas(vertices, measurePoints) {
    var alphas = [];
    var alphasIndices = [];
    for (var i = 0; i < vertices.length; i++) {
        var currentAlphas = [];
        var currentAlphasIndices = [];
        for (var j = 0; j < vertices[i].length/3; j++) {
            var currentVertex = [vertices[i][j * 3], vertices[i][j * 3 + 1], vertices[i][j * 3 + 2]];
            var closestPosition = _findClosestPosition(currentVertex, measurePoints);
            currentAlphas.push(1);
            currentAlphas.push(0);
            currentAlphasIndices.push(closestPosition);
            currentAlphasIndices.push(0);
            currentAlphasIndices.push(0);
        }
        alphas.push(currentAlphas);
        alphasIndices.push(currentAlphasIndices);
    }
    return [alphas, alphasIndices];
}


/**
 * Method used for creating a color buffer for a cube (measure point).
 *
 * @param isPicked If <code>true</code> then the color used will be
 * the one used for drawing the measure points for which the
 * corresponding eeg channels are selected.
 */
function createColorBufferForCube(isPicked) {
    var pointColor = [];
    if (isOneToOneMapping) {
        pointColor = [0.34, 0.95, 0.37, 1.0];
        if (isPicked) {
            pointColor = [0.99, 0.99, 0.0, 1.0];
        }
    } else {
        pointColor = [NO_OF_MEASURE_POINTS, 0, 0];
        if (isPicked) {
            pointColor = [NO_OF_MEASURE_POINTS + 1, 0, 0];
        }
    }
    var colors = [];
    for (var i = 0; i < 24; i++) {
        colors = colors.concat(pointColor);
    }
    var cubeColorBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, cubeColorBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(colors), gl.STATIC_DRAW);
    return cubeColorBuffer;
}


function bufferAtPoint(p) {
	var result = HLPR_bufferAtPoint(gl, p);
    var bufferVertices= result[0];
    var bufferNormals = result[1];
    var bufferTriangles = result[2];
    var alphas = [];
    for (var i = 0; i < 24; i++) {
        alphas = alphas.concat([1.0, 0.0]);
    }

    if (isOneToOneMapping) {
    	return [bufferVertices, bufferNormals, bufferTriangles, createColorBufferForCube(false)];
    } else {
    	var alphaBuffer = gl.createBuffer();
	    gl.bindBuffer(gl.ARRAY_BUFFER, alphaBuffer);
	    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(alphas), gl.STATIC_DRAW);
    	return [bufferVertices, bufferNormals, bufferTriangles, alphaBuffer, createColorBufferForCube(false)];
    }
}


function initBuffers(urlVertices, urlNormals, urlTriangles, urlAlphas, urlAlphasIndices, staticFiles) {
    var verticesData = readFloatData(urlVertices, staticFiles);
    var vertices = createWebGlBuffers(verticesData);
    var normals = HLPR_getDataBuffers(gl, urlNormals, staticFiles);
    var indexes = HLPR_getDataBuffers(gl, urlTriangles, staticFiles, true);
    
    var alphas = normals;  // Fake buffers, copy of the normals, in case of transparency, we only need dummy ones.
    var alphasIndices = normals;
    if (!isOneToOneMapping && urlAlphas && urlAlphasIndices && urlAlphas.length) {
        alphas = HLPR_getDataBuffers(gl, urlAlphas);
        alphasIndices = HLPR_getDataBuffers(gl, urlAlphasIndices);
    } else if (isDoubleView) {
        //if is double view than we use the static surface 'eeg_skin_surface' and we have to compute the alphas and alphasIndices;
        var alphasData = computeAlphas(verticesData, measurePoints);
        alphas = createWebGlBuffers(alphasData[0]);
        alphasIndices = createWebGlBuffers(alphasData[1]);
    }
    var result = [];
    for (var i=0; i< vertices.length; i++) {
    	if (isOneToOneMapping) {
    		var fakeColorBuffer = gl.createBuffer();
		    gl.bindBuffer(gl.ARRAY_BUFFER, fakeColorBuffer);
		    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices[i].numItems * 4), gl.STATIC_DRAW);
    		result.push([vertices[i], normals[i], indexes[i], fakeColorBuffer]);
    	} else {
    		result.push([vertices[i], normals[i], indexes[i], alphas[i], alphasIndices[i]]);
    	}
    }
    return result;
}


function initRegionBoundaries(boundariesURL) {
	if (boundariesURL) {
		$.ajax({
	        url: boundariesURL,
	        async: true,
	        success: function(data) {
	        	data = $.parseJSON(data);
	        	var boundaryVertices = data[0];
			    var boundaryEdges = data[1];
			    var boundaryNormals = data[2];
			    for (var i = 0; i < boundaryVertices.length; i++) {
			    	boundaryVertexBuffers.push(HLPR_createWebGlBuffer(gl, boundaryVertices[i], false, false));
			    	boundaryNormalsBuffers.push(HLPR_createWebGlBuffer(gl, boundaryNormals[i], false, false));
			    	boundaryEdgesBuffers.push(HLPR_createWebGlBuffer(gl, boundaryEdges[i], true, false));
			    }
	        }
	    });
	}
}


function drawBuffers(drawMode, buffersSets, useBlending) {
	if (useBlending) {
		gl.uniform1i(shaderProgram.useBlending, true);
    	gl.blendFunc(gl.SRC_ALPHA, gl.ONE);
    	gl.enable(gl.BLEND);
    	// Add gray color for semi-transparent object.
    	gl.uniform3f(shaderProgram.ambientColorUniform, 0.2, 0.2, 0.2);
	    var lightingDirection = Vector.create([-0.25, -0.25, -1]);
	    var adjustedLD = lightingDirection.toUnitVector().x(-1);
	    var flatLD = adjustedLD.flatten();
	    gl.uniform3f(shaderProgram.lightingDirectionUniform, flatLD[0], flatLD[1], flatLD[2]);
	    gl.uniform3f(shaderProgram.directionalColorUniform, 0.8, 0.8, 0.8);
	}
    for (var i = 0; i < buffersSets.length; i++) {
        gl.bindBuffer(gl.ARRAY_BUFFER, buffersSets[i][0]);
        gl.vertexAttribPointer(shaderProgram.vertexPositionAttribute, 3, gl.FLOAT, false, 0, 0);
        gl.bindBuffer(gl.ARRAY_BUFFER, buffersSets[i][1]);
        gl.vertexAttribPointer(shaderProgram.vertexNormalAttribute, 3, gl.FLOAT, false, 0, 0);
        if (isOneToOneMapping) {
            gl.bindBuffer(gl.ARRAY_BUFFER, buffersSets[i][3]);
            gl.vertexAttribPointer(shaderProgram.vertexColorAttribute, 4, gl.FLOAT, false, 0, 0);
        } else {
            gl.bindBuffer(gl.ARRAY_BUFFER, buffersSets[i][3]);
            gl.vertexAttribPointer(shaderProgram.vertexAlphaAttribute, 2, gl.FLOAT, false, 0, 0);
            gl.bindBuffer(gl.ARRAY_BUFFER, buffersSets[i][4]);
            gl.vertexAttribPointer(shaderProgram.vertexColorIndicesAttribute, 3, gl.FLOAT, false, 0, 0);
        }
        gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, buffersSets[i][2]);
        setMatrixUniforms();
        gl.drawElements(drawMode, buffersSets[i][2].numItems, gl.UNSIGNED_SHORT, 0);
    }
    if (useBlending) {
    	gl.depthFunc(gl.LEQUAL);
    	gl.disable(gl.BLEND);
    	gl.uniform1i(shaderProgram.useBlending, false);
    }
}


function drawRegionBoundaries() {
	if (boundaryVertexBuffers && boundaryEdgesBuffers) {
		gl.uniform1i(shaderProgram.drawLines, true);
		gl.uniform3f(shaderProgram.linesColor, 0.7, 0.7, 0.1);
	    gl.lineWidth(3.0);
	    for (var i=0; i < boundaryVertexBuffers.length; i++) {
	    	gl.bindBuffer(gl.ARRAY_BUFFER, boundaryVertexBuffers[i]);
	        gl.vertexAttribPointer(shaderProgram.vertexPositionAttribute, 3, gl.FLOAT, false, 0, 0);
	        gl.bindBuffer(gl.ARRAY_BUFFER, boundaryNormalsBuffers[i]);
	        gl.vertexAttribPointer(shaderProgram.vertexNormalAttribute, 3, gl.FLOAT, false, 0, 0);
	    	gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, boundaryEdgesBuffers[i]);
	        setMatrixUniforms();
	        gl.drawElements(gl.LINES, boundaryEdgesBuffers[i].numItems, gl.UNSIGNED_SHORT, 0);
	    }
	    gl.uniform1i(shaderProgram.drawLines, false);
	} else {
		displayMessage('Boundaries data not yet loaded. Dispaly will refresh automatically when load is finished.', 'infoMessage')		
	}
}


function drawBrainLines(linesBuffers, brainObjBuffers) {
	gl.uniform1i(shaderProgram.drawLines, true);
    gl.uniform3f(shaderProgram.linesColor, 0.3, 0.1, 0.3);
    gl.lineWidth(1.0);
    for (var i=0; i < linesBuffers.length; i++) {
    	gl.bindBuffer(gl.ARRAY_BUFFER, brainObjBuffers[i][0]);
        gl.vertexAttribPointer(shaderProgram.vertexPositionAttribute, 3, gl.FLOAT, false, 0, 0);
        gl.bindBuffer(gl.ARRAY_BUFFER, brainObjBuffers[i][1]);
        gl.vertexAttribPointer(shaderProgram.vertexNormalAttribute, 3, gl.FLOAT, false, 0, 0);
    	gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, linesBuffers[i]);
        setMatrixUniforms();
        gl.drawElements(gl.LINES, linesBuffers[i].numItems, gl.UNSIGNED_SHORT, 0);
    }
    gl.uniform1i(shaderProgram.drawLines, false);
}

/**
 * Actual scene drawing step.
 */
function tick() {
	if (!sliderSel) drawScene();
    if (isDoubleView && !AG_isStopped && !sliderSel) {
    	drawGraph(true, TIME_STEP);
    }
}

/**
 * Draw from buffers.
 */
function drawScene() {
    // COMPUTE FR/SEC
	if (!doPick) {
		gl.uniform1f(shaderProgram.isPicking, 0);
		gl.uniform3f(shaderProgram.pickingColor, 1, 1, 1);
		if (!isPreview) {
		    var timeNow = new Date().getTime();
		    if (lastTime != 0) {
		        var elapsed = timeNow - lastTime;
		        framestime.shift();
		        framestime.push(elapsed);
		
		        if (GL_zoomSpeed != 0 && NAV_isMouseControlOverBrain) {
		            GL_zTranslation -= GL_zoomSpeed * elapsed;
		            GL_zoomSpeed = 0;
		        } else if (GL_zoomSpeed != 0) {
		            NAV_navigatorZ = NAV_navigatorZ + GL_zoomSpeed * 4;
		            GL_zoomSpeed = 0;
		        }
		    }
		    lastTime = timeNow;
		    document.getElementById("TimeStep").innerHTML = elapsed;
		    if (timeData.length > 0) {
		        document.getElementById("TimeNow").innerHTML = (timeData[currentTimeValue] * 10 / 10).toString().substring(0.4);
		    }
		    var medianTime = Math.floor(1000 / ((eval(framestime.join("+"))) / framestime.length));
		    document.getElementById("FramesPerSecond").innerHTML = medianTime;
		    document.getElementById("slider-value").innerHTML = TIME_STEP;
		    if (sliderSel == false && !isPreview) {
		        $("#slider").slider("option", "value", currentTimeValue);
		    }
		}
	    // END COMPUTE FR/SEC
	    gl.viewport(0, 0, gl.viewportWidth, gl.viewportHeight);
	    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
	    // View angle is 45, we want to see object from 0.1 up to 800 distance from viewer
	    perspective(45, gl.viewportWidth / gl.viewportHeight, near, 800.0);
	    loadIdentity();
	    addLight();
		drawBuffers(gl.TRIANGLES, [LEG_legendBuffers], false);
	    
	    // Translate to get a good view.
	    mvTranslate([0.0, -5.0, -GL_zTranslation]);
	    multMatrix(GL_currentRotationMatrix);
	    mvRotate(180, [0, 0, 1]);
		
		// If we are in the middle of waiting for the next data file just
		// stop and wait since we might have an index that is 'out' of this data slice
		if (AG_isStopped == false) {
	        updateColors(currentTimeValue);
	        if (shouldIncrementTime && !isPreview) {
            	currentTimeValue = currentTimeValue + TIME_STEP;
           }
	        if (currentTimeValue > MAX_TIME_STEP && !isPreview) {
	        	// Next time value is no longer in activity data.
	            initActivityData();
	            if (isDoubleView) {
					loadEEGChartFromTimeStep(0);
				}
	        }
	    } else {
	    	updateColors(currentTimeValue);
	    }
	    drawBuffers(drawingMode, brainBuffers, false);
	    if (drawingMode == gl.POINTS) {
	    	gl.uniform1i(shaderProgram.vertexLineColor, true);
	    }
	    if (drawBoundaries) {
	    	drawRegionBoundaries();
	    }
	    if (drawTriangleLines) {
	    	drawBrainLines(brainLinesBuffers, brainBuffers);
	    }
        gl.uniform1i(shaderProgram.vertexLineColor, false);
        
	    if (!isPreview) {
	    	if (displayMeasureNodes) {
		        drawBuffers(gl.TRIANGLES, measurePointsBuffers, false);
		    } 
		    if (!isDoubleView) {
		    	NAV_draw_navigator();
		    }
		    if (isFaceToDisplay) {
		        mvPushMatrix();
		    	if (isDoubleView) {
		    		mvTranslate([0, -5, -22]);
		    	} else {
		    		mvTranslate([0, -5, -10]);
		    	}
		    	mvRotate(180, [0, 0, 1]);
		    	drawBuffers(gl.TRIANGLES, shelfBuffers, true);
		        mvPopMatrix();
		    }
	    }
	} else {
		gl.bindFramebuffer(gl.FRAMEBUFFER, GL_colorPickerBuffer);
   		gl.disable(gl.BLEND);
        gl.disable(gl.DITHER);
        gl.disable(gl.FOG);
        gl.disable(gl.LIGHTING);
        gl.disable(gl.TEXTURE_1D);
        gl.disable(gl.TEXTURE_2D);
        gl.disable(gl.TEXTURE_3D);
   		gl.uniform1f(shaderProgram.isPicking, 1);	
   		gl.viewport(0, 0, gl.viewportWidth, gl.viewportHeight);
    	gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    	// View angle is 45, we want to see object from 0.1 up to 800 distance from viewer
    	aspect = gl.viewportWidth / gl.viewportHeight;
    	perspective(45, aspect , near, 800.0);
    	loadIdentity();
    	
   	    if (GL_colorPickerInitColors.length == 0) {
   			GL_initColorPickingData(NO_OF_MEASURE_POINTS);
   		}	 
   		     
    	gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    	
		mvPushMatrix();
		mvTranslate([0.0, -5.0, -GL_zTranslation]);
	    multMatrix(GL_currentRotationMatrix);
	    mvRotate(180, [0, 0, 1]);
	    
	    for (var i = 0; i < NO_OF_MEASURE_POINTS; i++){
	    	gl.uniform3f(shaderProgram.pickingColor, GL_colorPickerInitColors[i][0], 
	    											 GL_colorPickerInitColors[i][1], 
	    											 GL_colorPickerInitColors[i][2]);
            gl.bindBuffer(gl.ARRAY_BUFFER, measurePointsBuffers[i][0]);
	        gl.vertexAttribPointer(shaderProgram.vertexPositionAttribute, 3, gl.FLOAT, false, 0, 0);
			gl.bindBuffer(gl.ARRAY_BUFFER, measurePointsBuffers[i][1]);
	        gl.vertexAttribPointer(shaderProgram.vertexNormalAttribute, 3, gl.FLOAT, false, 0, 0);
	        
	        gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, measurePointsBuffers[i][2]);
	        setMatrixUniforms();
    		gl.drawElements(gl.TRIANGLES, 36, gl.UNSIGNED_SHORT, 0);
         }    
        var pickedIndex = GL_getPickedIndex();
		if (pickedIndex != undefined) {
            var pickedChannel = $("#channelChk_" + pickedIndex);
            pickedChannel.attr('checked', !(pickedChannel.attr('checked')));
            pickedChannel.trigger('change');
		}
	    mvPopMatrix();		 
		doPick = false;
        gl.bindFramebuffer(gl.FRAMEBUFFER, null);
	}
}

////////////////////////////////////////~~~~~~~~~ END WEB GL RELATED RENDERING ~~~~~~~/////////////////////////////////


/////////////////////////////////////// ~~~~~~~~~~ DATA RELATED METHOD ~~~~~~~~~~~~~ //////////////////////////////////

/**
 * Change the currently selected state variable. Get the newly selected value, reset the currentTimeValue to start
 * and read the first page of the new mode/state var combination.
 */
function changeStateVariable() {
	selectedStateVar = $('#state-variable-select').val();
    $("#slider").slider("option", "value", currentTimeValue);
	initActivityData();
}

/**
 * Change the currently selected mode. Get the newly selected value, reset the currentTimeValue to start
 * and read the first page of the new mode/state var combination.
 */
function changeMode() {
	selectedMode = $('#mode-select').val();
	$("#slider").slider("option", "value", currentTimeValue);
	initActivityData();
}

/**
 * Just read the first slice of activity data and set the time step to 0.
 */
function initActivityData() {
	currentTimeValue = 0;
    //read the first file
    var initUrl = getUrlForPageFromIndex(0);
    activitiesData = HLPR_readJSONfromFile(initUrl);
    if (activitiesData != undefined) {
        currentActivitiesFileLength = activitiesData.length * TIME_STEP;
        totalPassedActivitiesData = 0;
    }
}

/**
 * Load the brainviewer from this given time step.
 */
function loadFromTimeStep(step) {
	showBlockerOverlay(50000);
	if (step % TIME_STEP != 0) {
		step = step - step % TIME_STEP + TIME_STEP; // Set time to be multiple of step
	}
	var nextUrl = getUrlForPageFromIndex(step);
	currentAsyncCall = null;
	readFileData(nextUrl, false);
	currentTimeValue = step;
	activitiesData = null;
    activitiesData = nextActivitiesFileData.slice(0);
    nextActivitiesFileData = null;
    currentActivitiesFileLength = activitiesData.length * TIME_STEP;
	totalPassedActivitiesData = currentTimeValue;
	// Also sync eeg monitor if in double view
	if (isDoubleView) {
		loadEEGChartFromTimeStep(step);
	}
	closeBlockerOverlay();
}

/**
 * Refresh the current data with the new time step.
 */
function refreshCurrentDataSlice() {
	if (currentTimeValue % TIME_STEP != 0) {
		currentTimeValue = currentTimeValue - currentTimeValue % TIME_STEP + TIME_STEP; // Set time to be multiple of step
	}
	loadFromTimeStep(currentTimeValue);
}

/**
 * Generate the url that reads one page of data starting from @param index
 */
function getUrlForPageFromIndex(index) {
	var fromIdx = index;
	if (fromIdx > MAX_TIME_STEP) fromIdx = 0;
	var toIdx = fromIdx + pageSize * TIME_STEP;
	return readDataPageURL(urlBase, fromIdx, toIdx, selectedStateVar, selectedMode, TIME_STEP)
}

/**
 * If we are at the last NEXT_PAGE_THRESHOLD points of data we should start loading the next data file
 * to get an animation as smooth as possible.
 */
function shouldLoadNextActivitiesFile() {

    if (!isPreview && (currentAsyncCall == null) && ((currentTimeValue - totalPassedActivitiesData + NEXT_PAGE_THREASHOLD * TIME_STEP) >= currentActivitiesFileLength)) {
        if (nextActivitiesFileData == null || nextActivitiesFileData.length == 0) {
            return true;
        }
    }
    return false;
}

/**
 * Start a new async call that should load required data for the next activity slice.
 */
function loadNextActivitiesFile() {
	var nextFileIndex = totalPassedActivitiesData + currentActivitiesFileLength;
	var nextUrl = getUrlForPageFromIndex(nextFileIndex);
    var asyncCallId = new Date().getTime();
    currentAsyncCall = asyncCallId;
    readFileData(nextUrl, true, asyncCallId);
}

/**
 * If the next time value is bigger that the length of the current activity loaded data
 * that means it's time to switch to the next activity data slice.
 */
function shouldChangeCurrentActivitiesFile() {
    return ((currentTimeValue + TIME_STEP - totalPassedActivitiesData) >= currentActivitiesFileLength)
}

/**
 * We've reached the end of the current activity chunk. Time to switch to
 * the next one.
 */
function changeCurrentActivitiesFile() {
    if ((nextActivitiesFileData == null || nextActivitiesFileData == undefined || nextActivitiesFileData.length == 0)) {
    	// Async data call was not finished, stop incrementing call and wait for data.
        shouldIncrementTime = false;
        return;
    }
    activitiesData = null;
    activitiesData = nextActivitiesFileData.slice(0);
    nextActivitiesFileData = null;
    totalPassedActivitiesData = totalPassedActivitiesData + currentActivitiesFileLength;
    currentActivitiesFileLength = activitiesData.length * TIME_STEP;
    currentAsyncCall = null;
    if (activitiesData != undefined && activitiesData.length > 0) {
        shouldIncrementTime = true;
    }
    if (totalPassedActivitiesData >= MAX_TIME_STEP) {
        totalPassedActivitiesData = 0;
    }
}


function readFileData(fileUrl, async, callIdentifier) {
	nextActivitiesFileData = null;
	// Keep a call identifier so we don't "intersect" async calls when two
	// async calls are started before the first one finishes.
	var self = this;
	self.callIdentifier = callIdentifier;
    $.ajax({
        url: fileUrl,
        async: async,
        success: function(data) {
        	if ((self.callIdentifier == currentAsyncCall) || !async) {
        		nextActivitiesFileData = eval(data);
            	data = null;
        	}
        }
    });
}


/////////////////////////////////////// ~~~~~~~~~~ END DATA RELATED METHOD ~~~~~~~~~~~~~ //////////////////////////////////
