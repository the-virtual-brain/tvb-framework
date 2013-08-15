var CONNECTIVITY_SPACE_TIME_CANVAS_ID = "GLcanvas_SPACETIME";

var fullMatrixColors = null;		// Colors for the full connectivity matrix
var outlineVerticeBuffer = null;	// Vertices for the full matrix outline square
var outlineNormalsBuffer = null;	// Normals for the full matrix outline square
var outlineLinesBuffer = null;		// The line indices for thr full matrix outline square
var plotColorBuffers = [];			// A list of color buffers for the various space-time connectivity matrices
var verticesBuffer = [];			// A list of vertex buffers for the various space-time connectivity matrices
var normalsBuffer = [];				// A list of normal buffers for the various space-time connecitivty matrices
var indexBuffer = [];				// A list of triangles index buffers for the various space-time connectivity matrices
var linesIndexBuffer = [];			// A list of line index buffers for the various space-time connectivity matrices

var plotSize = 250;					// Default plot size of 250 pixels
var defaultZ = -2.0;				// Default plot Z position of -2.0
var doPick = false;					// No picking by default
var nrOfSteps = 6;					// Number of space-time plots we will draw in scene
var colorsForPicking = [];			// The colors which are used for the picking scheme

var plotTranslations = [];			// Keep track of the transation for each plot. 
var plotRotations = [];				// Keep track of the rotations for each plot
var zoomedInMatrix = -1;			// The matrix witch is currently zoomed in on
var clickedMatrix = -1;
var backupTranslations = [];
var backupRotations = [];
var animationStarted = false;
var alphaValueSpaceTime = 1.0;				// original alpha value for default plot		
var backupAlphaValue = alphaValueSpaceTime;	// backup used in animations
var minTractValue = -1;
var maxTractValue = -1;
var animationTimeout = 3;
var animationGranularity = 50;


function customMouseDown_SpaceTime(event) {
	if (!animationStarted) {
		if (clickedMatrix >= 0) {
			doZoomOutAnimation();
		} else {
			GL_handleMouseDown(event, '#' + CONNECTIVITY_SPACE_TIME_CANVAS_ID);
			doPick = true;
			drawSceneSpaceTime();
		}
	}
}

function nullEventHandler() {
	// Just do nothing for most events since we don't want zooming or other fancy stuff.
}

function initColorsForPicking() {
	colorsForPicking = [];
	for (var i=0; i <= nrOfSteps; i++) {
		// Go up to nrOfSteps since for 0 we will consider the full matrix as being clicked
		var r = parseInt(1.0 / (i + 1) * 255);
		var g = parseInt(i / nrOfSteps * 255);
		var b = 0.0;
		colorsForPicking.push([r / 255, g / 255, b / 255])
		var colorKey = r + '' + g + '0';
		GL_colorPickerMappingDict[colorKey] = i;
	}
	GL_initColorPickFrameBuffer();
}

/*
 * Custom shader initializations specific for the space-time connectivity plot
 */
function initShaders_SPACETIME() {
	basicInitShaders("shader-plot-fs", "shader-plot-vs");
    
    shaderProgram.drawLines = gl.getUniformLocation(shaderProgram, "uDrawLines");
    shaderProgram.alphaValue = gl.getUniformLocation(shaderProgram, "uAlpha");
    shaderProgram.lineColor = gl.getUniformLocation(shaderProgram, "uLineColor");
    shaderProgram.isPicking = gl.getUniformLocation(shaderProgram, "isPicking");
    shaderProgram.pickingColor = gl.getUniformLocation(shaderProgram, "pickingColor");
    
    shaderProgram.vertexColorAttribute = gl.getAttribLocation(shaderProgram, "aVertexColor");
    gl.enableVertexAttribArray(shaderProgram.vertexColorAttribute);
}


function connectivitySpaceTime_startGL() {
	//Do the required initializations for the connectivity space-time visualizer
    initShaders_SPACETIME();

    gl.clearDepth(1.0);
    gl.enable(gl.DEPTH_TEST);
    gl.depthFunc(gl.LEQUAL);

	drawSceneSpaceTime();
}


/*
 * Create the required buffers for the space-time plot.
 */
function createConnectivityMatrix() {
	var nrElems = GVAR_interestAreaVariables[GVAR_selectedAreaType].values.length;
	// starting 'x' and 'y' axis values for the plot in order to center around (0, 0)
	var startX = - (plotSize / 2);	
	var startY = - (plotSize / 2);
	// The size of a matrix element
	var elementSize = plotSize / nrElems;
	// Create arrays from start for performance reasons 
	var vertices = new Float32Array(nrElems * nrElems * 4 * 3);
	var normals = [];
	var indices = new Uint16Array(nrElems * nrElems * 2 * 3);
	var linesIndices = new Uint16Array(nrElems * nrElems * 2 * 4);
	for (var i = 0; i < nrElems; i++) {
		for (var j = 0; j < nrElems; j++) {
			// For each separate element, compute the position of the 4 required vertices
			// depending on the position from the connectivity matrix
			var upperLeft = [startX + j * elementSize, startY + i * elementSize, defaultZ];
			var upperRight = [startX + (j + 1) * elementSize, startY + i * elementSize, defaultZ];
			var lowerLeft = [startX + j * elementSize, startY + (i + 1) * elementSize, defaultZ];
			var lowerRight = [startX + (j + 1) * elementSize, startY + (i + 1) * elementSize, defaultZ];
			// Since the vertice array is flatten, and there are 4 vertices per one element,
			// in order to fill the position in the vertice array we need to fill all 12 elements
			vertices[3 * 4 * (i * nrElems + j)] = upperLeft[0];
			vertices[3 * 4 * (i * nrElems + j) + 1] = upperLeft[1];
			vertices[3 * 4 * (i * nrElems + j) + 2] = upperLeft[2];
			vertices[3 * 4 * (i * nrElems + j) + 3] = upperRight[0];
			vertices[3 * 4 * (i * nrElems + j) + 4] = upperRight[1];
			vertices[3 * 4 * (i * nrElems + j) + 5] = upperRight[2];
			vertices[3 * 4 * (i * nrElems + j) + 6] = lowerLeft[0];
			vertices[3 * 4 * (i * nrElems + j) + 7] = lowerLeft[1];
			vertices[3 * 4 * (i * nrElems + j) + 8] = lowerLeft[2];
			vertices[3 * 4 * (i * nrElems + j) + 9] = lowerRight[0];
			vertices[3 * 4 * (i * nrElems + j) + 10] = lowerRight[1];
			vertices[3 * 4 * (i * nrElems + j) + 11] = lowerRight[2];
			// For the normals it's easier since we only need one normal for each vertex
			for (var k = 0; k < 4; k++) {
				normals.concat([0, 0, -1]);
			}
			// We have 2 triangles, which again are flatten so we need to fill 6 index elements
			indices[3 * 2 * (i * nrElems + j)] = 4 * (i * nrElems + j);
			indices[3 * 2 * (i * nrElems + j) + 1] = 4 * (i * nrElems + j) + 1;
			indices[3 * 2 * (i * nrElems + j) + 2] = 4 * (i * nrElems + j) + 2;
			indices[3 * 2 * (i * nrElems + j) + 3] = 4 * (i * nrElems + j) + 1;
			indices[3 * 2 * (i * nrElems + j) + 4] = 4 * (i * nrElems + j) + 2;
			indices[3 * 2 * (i * nrElems + j) + 5] = 4 * (i * nrElems + j) + 3;
			
			// For the lines we have 4 lines per element, flatten again, so 8 index elements to fill
			linesIndices[4 * 2 * (i * nrElems + j)] = 4 * (i * nrElems + j);
			linesIndices[4 * 2 * (i * nrElems + j) + 1] = 4 * (i * nrElems + j) + 1;
			linesIndices[4 * 2 * (i * nrElems + j) + 2] = 4 * (i * nrElems + j) + 1;
			linesIndices[4 * 2 * (i * nrElems + j) + 3] = 4 * (i * nrElems + j) + 3;
			linesIndices[4 * 2 * (i * nrElems + j) + 4] = 4 * (i * nrElems + j) + 2;
			linesIndices[4 * 2 * (i * nrElems + j) + 5] = 4 * (i * nrElems + j) + 3;
			linesIndices[4 * 2 * (i * nrElems + j) + 6] = 4 * (i * nrElems + j) + 2;
			linesIndices[4 * 2 * (i * nrElems + j) + 7] = 4 * (i * nrElems + j) + 0;
		}
	}
	// Now create all the required buffers having the computed data.
	normals = new Float32Array(normals);
	verticesBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, verticesBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);
    normalsBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, normalsBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, normals, gl.STATIC_DRAW);
    indexBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, indexBuffer);
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, indices, gl.STATIC_DRAW);
    indexBuffer.numItems = indices.length;
    linesIndexBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, linesIndexBuffer);
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, linesIndices, gl.STATIC_DRAW);
    linesIndexBuffer.numItems = linesIndices.length;
    createOutlineSquare(startX, startY, elementSize, nrElems);
}

/*
 * Compute the required vertex and idex for the square outline of the full connectivity matrix
 */
function createOutlineSquare(startX, startY, elementSize, nrElems) {
	var outlineVertices = [startX, startY, defaultZ,
    					   startX + nrElems * elementSize, startY, defaultZ,
    					   startX, startY + nrElems * elementSize, defaultZ,
    					   startX + nrElems * elementSize, startY + nrElems * elementSize, defaultZ];
    var outlineNormals = [0, 0, -1, 0, 0, -1, 0, 0, -1, 0, 0, -1];
    var outlineLines = [0, 1, 0, 2, 1, 3, 2, 3];
    outlineVerticeBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, outlineVerticeBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(outlineVertices), gl.STATIC_DRAW);
    outlineNormalsBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, outlineNormalsBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(outlineNormals), gl.STATIC_DRAW);
    outlineLinesBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, outlineLinesBuffer);
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint16Array(outlineLines), gl.STATIC_DRAW);
    outlineLinesBuffer.numItems = outlineLines.length;
}


/*
 * Generate a color buffer which represents the state of the weights for 
 * a given 'interval' centered around a given tract value
 * 
 * @param tractValue: the center of the interval
 * @param intervalLength: the length of the interval
 * 
 * @returns: a color buffer, where for the connections that fall in the defined interval,
 * 			 a gradient color is assigned based on the weights strenght, and for the 
 * 			 rest the color black is used.
 */
function generateColors(tractValue, intervalLength) {
	var matrixWeightsValues = GVAR_interestAreaVariables[1].values;
	var matrixTractsValues = GVAR_interestAreaVariables[2].values;
	var minWeightsValue = GVAR_interestAreaVariables[1].min_val;
	var maxWeightsValue = GVAR_interestAreaVariables[1].max_val;
	var nrElems = matrixWeightsValues.length;
	var colors = new Float32Array(nrElems * nrElems * 3 * 4);
	for (var i = 0; i < nrElems; i++) {
		for (var j = 0; j < nrElems; j++) {
			for (var k = 0; k < 4; k++) {
				// For each element generate 4 identical colors coresponding to the 4 vertices used for the element
				var delayValue = matrixTractsValues[i][nrElems - j - 1] / conductionSpeed;
				if (delayValue >= (tractValue - intervalLength / 2) && delayValue <= (tractValue + intervalLength / 2)) {
					var color = getGradientColor(matrixWeightsValues[i][nrElems - j - 1], minWeightsValue, maxWeightsValue);
					for (var colorIdx = 0; colorIdx < 3; colorIdx++) {
						colors[3 * 4 * (i * nrElems + j) + k * 3 + colorIdx] = color[colorIdx];
					}
				} else {
					colors[3 * 4 * (i * nrElems + j) + k * 3] = 0;
					colors[3 * 4 * (i * nrElems + j) + k * 3 + 1] = 0;
					colors[3 * 4 * (i * nrElems + j) + k * 3 + 2] = 0;
				}
			}
		}
	}
	var buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, colors, gl.STATIC_DRAW);
    return buffer;
}


/*
 * Update the header with informations about matrices.
 */ 
function updateSpaceTimeHeader() {
	var minTract = $('#fromTractValue').val();
	if (minTract == "") {
		minTract = minTractValue;
	} else {
		minTract = parseFloat(minTract);
	}
	
	var maxTract = $('#toTractValue').val();
	if (maxTract == "") {
		maxTract = maxTractValue;
	} else {
		maxTract = parseFloat(maxTract);
	}
	
	if (minTract < GVAR_interestAreaVariables[2].min_val) minTract = GVAR_interestAreaVariables[2].min_val;
	if (maxTract < 0) maxTract = maxTractValue;
	if (maxTract > GVAR_interestAreaVariables[2].max_val) maxTract = GVAR_interestAreaVariables[2].max_val;
	if (minTract > maxTract) {
		var swapAux = minTract;
		minTract = maxTract;
		maxTract = swapAux;
	}
	minTractValue = minTract;
	maxTractValue = maxTract;
	$('#fromTractValue').val(minTractValue.toFixed(2));
	$('#toTractValue').val(maxTractValue.toFixed(2));
	initColorBuffers();
	if (clickedMatrix >= 0) {
		doZoomOutAnimation();
	} else {
		drawSceneSpaceTime();
	}
}


function initColorBuffers() {
	initColorsForPicking();
    plotColorBuffers = [];
	var stepValue = (maxTractValue - minTractValue) / nrOfSteps;
	plotColorBuffers.push(generateColors((maxTractValue + minTractValue) / 2, maxTractValue - minTractValue));
	// In order to avoid floating number approximations which keep the loop for one more iteration just approximate by
	// substracting 0.1
	for (var tractValue = minTractValue + stepValue / 2; tractValue < parseInt(maxTractValue) - 0.1; tractValue = tractValue + stepValue) {
		plotColorBuffers.push(generateColors(tractValue, stepValue));
	} 
}

/*
 * Initialize the space time connectivity plot.
 */
function conectivitySpaceTime_initCanvas() {
	var canvas = document.getElementById(CONNECTIVITY_SPACE_TIME_CANVAS_ID);
    initGL(canvas);
    gl.clearColor(0.0, 0.0, 0.0, 1.0);
    plotSize = parseInt(canvas.clientWidth / 3);	// Compute the size of one connectivity plot depending on the canvas width
    createConnectivityMatrix();
    canvas.onkeydown = nullEventHandler;
    canvas.onkeyup = nullEventHandler;
    canvas.onmousedown = customMouseDown_SpaceTime;
    document.onmouseup = nullEventHandler;
    document.onmousemove = nullEventHandler;
    
    plotTranslations = [];
    plotRotations = [];
    plotTranslations.push([-parseInt(canvas.clientWidth / 4), 0, 0]);	//The translation for the left-most full connectivity matrix
    plotRotations.push([90, [0, 1, 0]]);
    for (var i = 0; i < nrOfSteps; i++) {
    	plotTranslations.push([-parseInt(canvas.clientWidth / 8) + parseInt(canvas.clientWidth / 2.2 / nrOfSteps) * i, 0.0, 0.0]); // Values tested that display nicely for 6 plots at least
    	plotRotations.push([80 - i * nrOfSteps, [0, 1, 0]]);
    }
    
    if (minTractValue < 0) {
    	minTractValue = GVAR_interestAreaVariables[2].min_val / conductionSpeed;
    }
	if (maxTractValue < 0) {
		maxTractValue = GVAR_interestAreaVariables[2].max_val / conductionSpeed;
	}
	
    updateSpaceTimeHeader();
    clickedMatrix = -1;
    
    document.getElementById("leg_min_tract").innerHTML = "Min tract length : " + GVAR_interestAreaVariables[2].min_val + ' mm';
    document.getElementById("leg_max_tract").innerHTML = "Max tract length : " + GVAR_interestAreaVariables[2].max_val + ' mm';
    document.getElementById("leg_min_weights").innerHTML = "Min weight : " + GVAR_interestAreaVariables[1].min_val;
    document.getElementById("leg_max_weights").innerHTML = "Max weight : " + GVAR_interestAreaVariables[1].max_val;
}


/*
 * Draw the full matrix, with the outline square.
 */
function drawFullMatrix(doPick, idx) {
	mvPushMatrix();
	
	// Translate and rotate to get a good view 
	mvTranslate(plotTranslations[idx]);
    mvRotate(plotRotations[idx][0], plotRotations[idx][1]);
    mvRotate(180, [0, 0, 1]);
	
	// Draw the actual matrix.
	gl.bindBuffer(gl.ARRAY_BUFFER, verticesBuffer);
    gl.vertexAttribPointer(shaderProgram.vertexPositionAttribute, TRI, gl.FLOAT, false, 0, 0);
	gl.bindBuffer(gl.ARRAY_BUFFER, normalsBuffer);
    gl.vertexAttribPointer(shaderProgram.vertexNormalAttribute, TRI, gl.FLOAT, false, 0, 0);
	setMatrixUniforms();
	
	if (doPick) {
		var currentPickColor = colorsForPicking[idx];
		gl.uniform3f(shaderProgram.pickingColor, currentPickColor[0], currentPickColor[1], currentPickColor[2]);
	} else {
		gl.bindBuffer(gl.ARRAY_BUFFER, plotColorBuffers[idx]);
	    gl.vertexAttribPointer(shaderProgram.vertexColorAttribute, 3, gl.FLOAT, false, 0, 0);
	    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, indexBuffer);
		gl.drawElements(gl.TRIANGLES, indexBuffer.numItems, gl.UNSIGNED_SHORT, 0);
	    gl.uniform3f(shaderProgram.lineColor, 0.1, 0.1, 0.2);
		gl.uniform1i(shaderProgram.drawLines, true);
		gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, linesIndexBuffer);
		gl.drawElements(gl.LINES, linesIndexBuffer.numItems, gl.UNSIGNED_SHORT, 0);
		gl.uniform1i(shaderProgram.drawLines, false);
		
		// Now draw the square outline
		if (idx == clickedMatrix) {
			gl.uniform3f(shaderProgram.lineColor, 0.2, 0.2, 0.8);
	    	gl.lineWidth(3.0);
		} else {
			gl.uniform3f(shaderProgram.lineColor, 0.3, 0.3, 0.3);
			gl.lineWidth(2.0);
		}
	    gl.bindBuffer(gl.ARRAY_BUFFER, outlineVerticeBuffer);
	    gl.vertexAttribPointer(shaderProgram.vertexPositionAttribute, TRI, gl.FLOAT, false, 0, 0);
		gl.bindBuffer(gl.ARRAY_BUFFER, outlineNormalsBuffer);
	    gl.vertexAttribPointer(shaderProgram.vertexNormalAttribute, TRI, gl.FLOAT, false, 0, 0);
	    gl.uniform1i(shaderProgram.drawLines, true);
		gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, outlineLinesBuffer);
		gl.drawElements(gl.LINES, outlineLinesBuffer.numItems, gl.UNSIGNED_SHORT, 0);
		gl.lineWidth(2.0);
		gl.uniform1i(shaderProgram.drawLines, false);
	}
	gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, indexBuffer);
	gl.drawElements(gl.TRIANGLES, indexBuffer.numItems, gl.UNSIGNED_SHORT, 0);
	
    mvPopMatrix();
}


function computeAnimationTranslations(startPoint, endPoint, startRotation, endRotation, startAlpha, endAlpha, animationSteps) {
	var translationAnimation = [];
	var rotationAnimation = [];
	var alphas = [];
	// y-axis component does not vary so we only handle x and z linearly
	var x_inc = (endPoint[0] - startPoint[0]) / animationSteps;
	var z_inc = (endPoint[2] - startPoint[2]) / animationSteps;
	// also we do rotations just along y-axis so angle of rotation is all we need to change
	var rot_inc = (endRotation[0] - startRotation[0]) / animationSteps;
	// for alpha alos vary linearly
	var alpha_inc = (endAlpha - startAlpha) / animationSteps;
	for (var i = 1; i <= animationSteps; i++) {
		translationAnimation.push([startPoint[0] + i * x_inc, startPoint[1], startPoint[2] + i * z_inc]);
		rotationAnimation.push([startRotation[0] + i * rot_inc, startRotation[1]]);
		alphas.push(startAlpha + alpha_inc * i);
	}
	return {'translations' : translationAnimation, 'rotations' : rotationAnimation, 'alphas' : alphas};
}


function animationStep(step, animationSteps, animations, zoomIn) {
	for (var j = 0; j < animations.length; j++) {
		plotTranslations[j] = animations[j]['translations'][step];
		plotRotations[j] = animations[j]['rotations'][step];
		alphaValueSpaceTime = animations[j]['alphas'][step];
	}
	drawSceneSpaceTime();
	if (step + 1 < animationSteps) {
		setTimeout(function() { animationStep(step + 1, animationSteps, animations, zoomIn); }, animationTimeout);
	} else {
		var matrixSelected = document.getElementById('selectedMatrixValue');
		if (zoomIn) {
			zoomedInMatrix = clickedMatrix;
			var stepValue = (maxTractValue - minTractValue) / nrOfSteps;
			if (zoomedInMatrix != 0) {
				var fromTractVal = (minTractValue + stepValue * (zoomedInMatrix - 1)).toFixed(2)
				var toTractVal = (minTractValue + stepValue * zoomedInMatrix).toFixed(2)
				matrixSelected.innerHTML = '[' + fromTractVal + '..' + toTractVal + ']';
			} else {
				matrixSelected.innerHTML = 'Full matrix';
			}
		} else {
			plotTranslations = backupTranslations;
			plotRotations = backupRotations;
			alphaValueSpaceTime = backupAlphaValue;
			clickedMatrix = -1;
			zoomedInMatrix = -1;
			matrixSelected.innerHTML = 'None';
		}
		drawSceneSpaceTime();
		animationStarted = false;
	}
}


function doZoomInAnimation() {
	animationStarted = true;
	var targetForwardPosition = [0.0, 0.0, 200];
	var targetForwardRotation = [360, [0, 1, 0]];
	backupTranslations = plotTranslations.slice(0);
	backupRotations  = plotRotations.slice(0);
	backupAlphaValue = alphaValueSpaceTime;
	var animations = [];
	for (var i = 0; i < plotTranslations.length; i++) {
		if (i == clickedMatrix) {
			animations.push(computeAnimationTranslations(plotTranslations[i], targetForwardPosition,
														 plotRotations[i], targetForwardRotation, 
														 alphaValueSpaceTime, 1, animationGranularity));
		} else {
			var targetTranslation = [plotTranslations[i][0], plotTranslations[i][1], -200];
			animations.push(computeAnimationTranslations(plotTranslations[i], targetTranslation,
														 plotRotations[i], plotRotations[i], 
														 alphaValueSpaceTime, 1, animationGranularity));
		}
	}
	animationStep(0, animationGranularity, animations, true);
}


function doZoomOutAnimation() {
	animationStarted = true;
	var animations = [];
	for (var i = 0; i < plotTranslations.length; i++) {
		animations.push(computeAnimationTranslations(plotTranslations[i], backupTranslations[i],
													 plotRotations[i], backupRotations[i],
													 alphaValue, backupAlphaValue, animationGranularity));	
	}
	animationStep(0, animationGranularity, animations, false);
}


/*
 * Draw the entire space plot matrices.
 */
function drawSceneSpaceTime() {
	if (!doPick) {
		gl.uniform1f(shaderProgram.alphaValue, alphaValueSpaceTime);
		gl.uniform1f(shaderProgram.isPicking, 0);
		gl.uniform3f(shaderProgram.pickingColor, 1, 1, 1);
		gl.viewport(0, 0, gl.viewportWidth, gl.viewportHeight);
	    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
	    perspective(45, gl.viewportWidth / gl.viewportHeight , 0.1, 2000.0);
	    loadIdentity();
	    // Translate to get a good view.
	    mvTranslate([0.0, 0.0, -600]);
	    
		for (var i = 0; i < plotColorBuffers.length; i++) {
			drawFullMatrix(false, i);
		}
		
	    //gl.disable(gl.BLEND);
	    //gl.enable(gl.DEPTH_TEST);
	} else {
		gl.bindFramebuffer(gl.FRAMEBUFFER, GL_colorPickerBuffer);
   		gl.disable(gl.BLEND) 
        gl.disable(gl.DITHER)
        gl.disable(gl.FOG) 
        gl.disable(gl.LIGHTING) 
        gl.disable(gl.TEXTURE_1D) 
        gl.disable(gl.TEXTURE_2D) 
        gl.disable(gl.TEXTURE_3D) 
   		gl.uniform1f(shaderProgram.isPicking, 1);	
   		gl.viewport(0, 0, gl.viewportWidth, gl.viewportHeight);
    	gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    	// View angle is 45, we want to see object from 0.1 up to 800 distance from viewer
    	aspect = gl.viewportWidth / gl.viewportHeight;
    	perspective(45, aspect , near, 800.0);
    	loadIdentity();
    	// Translate to get a good view.
	    mvTranslate([0.0, 0.0, -600]);
	    
		for (var i = 0; i < plotColorBuffers.length; i++) {
			drawFullMatrix(true, i);
		}
		clickedMatrix = GL_getPickedIndex();
        gl.bindFramebuffer(gl.FRAMEBUFFER, null);
        doPick = false;
		if (clickedMatrix >= 0) {
			doZoomInAnimation();
		}
	}
    
}

