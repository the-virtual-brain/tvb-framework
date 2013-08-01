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

var CONNECTIVITY_3D_CANVAS_ID = "GLcanvas_3D";

function initShaders_3D() {
	basicInitShaders("shader-3d-fs", "shader-3d-vs");
    
    shaderProgram.useLightingUniform = gl.getUniformLocation(shaderProgram, "uUseLighting");
    shaderProgram.ambientColorUniform = gl.getUniformLocation(shaderProgram, "uAmbientColor");
    shaderProgram.lightingDirectionUniform = gl.getUniformLocation(shaderProgram, "uLightingDirection");
    shaderProgram.directionalColorUniform = gl.getUniformLocation(shaderProgram, "uDirectionalColor");
    shaderProgram.alphaUniform = gl.getUniformLocation(shaderProgram, "uAlpha");
    shaderProgram.colorUniform = gl.getUniformLocation(shaderProgram, "uColor");
}

var NO_POSITIONS_3D;
var positionsBuffers_3D = [];

var colorsWeights;
var raysWeights;

function customMouseDown_3D(event) {
	GL_handleMouseDown(event, $("#" + CONNECTIVITY_3D_CANVAS_ID));
	//GFUNC_refreshOnContextChange();
	GFUNC_updateLeftSideVisualization();
}

function customMouseMove_3D(event) {
	if (GL_mouseDown == true) {
		GL_handleMouseMove(event);
		//GFUNC_refreshOnContextChange();		
		GFUNC_updateLeftSideVisualization();
	}
}

/**
 * Draw the light
 */
function addLight_3D() {
    gl.uniform1i(shaderProgram.useLightingUniform, true);
    gl.uniform3f(shaderProgram.ambientColorUniform, 0.3, 0.9, 0.7);

    var lightingDirection = Vector.create([0.85, 0.8, 0.75]);
    var adjustedLD = lightingDirection.toUnitVector().x(-1);
    var flatLD = adjustedLD.flatten();
    gl.uniform3f(shaderProgram.lightingDirectionUniform, flatLD[0], flatLD[1], flatLD[2]);
    gl.uniform3f(shaderProgram.directionalColorUniform, 0.7, 0.7, 0.7);
    gl.uniform1f(shaderProgram.alphaUniform, 1.0);
}

function drawScene_3D() {
    gl.viewport(0, 0, gl.viewportWidth, gl.viewportHeight);
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    perspective(45, gl.viewportWidth / gl.viewportHeight , 0.1, 2000.0);
    loadIdentity();
    addLight_3D();
    // Translate to get a good view.
    mvTranslate([0.0, 0.0, GL_zTranslation]);

    //draw the points
    mvPushMatrix();
    multMatrix(GL_currentRotationMatrix);
    //mvRotate(90, [0, 0, 1]);
    mvTranslate([GVAR_additionalXTranslationStep, GVAR_additionalYTranslationStep, 0])
    applyConnectivityNoseCorrection();
    displayPoints_3D();
    mvPopMatrix();
}

function bufferAtPoint_3D(point, radius) {
    var moonVertexPositionBuffer;
    var moonVertexNormalBuffer;
    var moonVertexIndexBuffer;

    var latitudeBands = 30;
    var longitudeBands = 30;

    var vertexPositionData = [];
    var normalData = [];
    for (var latNumber = 0; latNumber <= latitudeBands; latNumber++) {
        var theta = latNumber * Math.PI / latitudeBands;
        var sinTheta = Math.sin(theta);
        var cosTheta = Math.cos(theta);

        for (var longNumber = 0; longNumber <= longitudeBands; longNumber++) {
            var phi = longNumber * 2 * Math.PI / longitudeBands;
            var sinPhi = Math.sin(phi);
            var cosPhi = Math.cos(phi);

            var x = cosPhi * sinTheta;
            var y = cosTheta;
            var z = sinPhi * sinTheta;

            normalData.push(x);
            normalData.push(y);
            normalData.push(z);
            vertexPositionData.push(parseFloat(point[0]) + radius * x);
            vertexPositionData.push(parseFloat(point[1]) + radius * y);
            vertexPositionData.push(parseFloat(point[2]) + radius * z);
        }
    }

    var indexData = [];
    for (latNumber = 0; latNumber < latitudeBands; latNumber++) {
        for (longNumber = 0; longNumber < longitudeBands; longNumber++) {
            var first = (latNumber * (longitudeBands + 1)) + longNumber;
            var second = first + longitudeBands + 1;
            indexData.push(first);
            indexData.push(second);
            indexData.push(first + 1);

            indexData.push(second);
            indexData.push(second + 1);
            indexData.push(first + 1);
        }
    }

    moonVertexNormalBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, moonVertexNormalBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(normalData), gl.STATIC_DRAW);
    moonVertexNormalBuffer.itemSize = 3;
    moonVertexNormalBuffer.numItems = normalData.length / 3;

    moonVertexPositionBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, moonVertexPositionBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertexPositionData), gl.STATIC_DRAW);
    moonVertexPositionBuffer.itemSize = 3;
    moonVertexPositionBuffer.numItems = vertexPositionData.length / 3;

    moonVertexIndexBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, moonVertexIndexBuffer);
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint16Array(indexData), gl.STATIC_DRAW);
    moonVertexIndexBuffer.itemSize = 1;
    moonVertexIndexBuffer.numItems = indexData.length;

    return [moonVertexPositionBuffer, moonVertexNormalBuffer, moonVertexIndexBuffer];
}

function displayPoints_3D() {
    for (var i = 0; i < NO_POSITIONS_3D; i++) {
        mvPushMatrix();

		var color = getGradientColor(colorsWeights[i], parseFloat($('#colorMinId').val()), parseFloat($('#colorMaxId').val()));
        gl.uniform3f(shaderProgram.colorUniform, color[0], color[1], color[2]);
        //gl.uniform3f(shaderProgram.colorUniform, 1.0, 1.0, 1.0)

        gl.bindBuffer(gl.ARRAY_BUFFER, positionsBuffers_3D[i][0]);
        gl.vertexAttribPointer(shaderProgram.vertexPositionAttribute, positionsBuffers_3D[i][0].itemSize, gl.FLOAT, false, 0, 0);

        gl.bindBuffer(gl.ARRAY_BUFFER, positionsBuffers_3D[i][1]);
        gl.vertexAttribPointer(shaderProgram.vertexNormalAttribute, positionsBuffers_3D[i][1].itemSize, gl.FLOAT, false, 0, 0);

        gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, positionsBuffers_3D[i][2]);
        setMatrixUniforms();
        gl.drawElements(gl.TRIANGLES, positionsBuffers_3D[i][2].numItems, gl.UNSIGNED_SHORT, 0);
        mvPopMatrix();
    }
}

function applyConnectivityNoseCorrection() {
    if (connectivity_nose_correction != undefined && connectivity_nose_correction != null &&
            connectivity_nose_correction.length == 3) {
        mvRotate(parseInt(connectivity_nose_correction[0]), [1, 0, 0]);
        mvRotate(parseInt(connectivity_nose_correction[1]), [0, 1, 0]);
        mvRotate(parseInt(connectivity_nose_correction[2]), [0, 0, 1]);
    }
}

function computeRay(rayWeight, minWeight, maxWeight) {
    var minRay = 1;
    var maxRay = 4;
	if (minWeight != maxWeight) {
		return minRay + [(rayWeight - minWeight) / (maxWeight - minWeight)] * (maxRay - minRay);
	}	
    else{
  		return minRay + (maxRay - minRay) / 2;  	
    }
}

function saveRequiredInputs_3D(filePositions, rays, colors, conn_nose_correction) {
	/*
	 * Initialize all the actual data needed by the connectivity 3D visualizer. This should be called
	 * only once.
	 */
	//Store nose correction
	connectivity_nose_correction = $.parseJSON(conn_nose_correction);
	
	//Read the positions, and create the required buffers
	GVAR_initPointsAndLabels(filePositions);
	
    NO_POSITIONS_3D = GVAR_positionsPoints.length;

    raysWeights = $.parseJSON(rays);
    colorsWeights = $.parseJSON(colors);

    // Initialize the buffers for drawing the points
    for (i = 0; i < NO_POSITIONS_3D; i++) {
    	ray_value = computeRay(raysWeights[i], parseFloat($('#rayMinId').val()), parseFloat($('#rayMaxId').val()));
        positionsBuffers_3D[i] = bufferAtPoint_3D(GVAR_positionsPoints[i], ray_value);
    }	
}

function conectivity3D_initCanvas() {
	var canvas = document.getElementById(CONNECTIVITY_3D_CANVAS_ID);
    //needed for the export/save canvas operation
    canvas.webGlCanvas = true;
    initGL(canvas);
    
    // Enable keyboard and mouse interaction
    canvas.onkeydown = GL_handleKeyDown;
    canvas.onkeyup = GL_handleKeyUp;
    canvas.onmousedown = customMouseDown_3D;
    document.onmouseup = GL_handleMouseUp;
    document.onmousemove = customMouseMove_3D;
}

function connectivity3D_startGL() {
	//Do the required initializations for the connectivity 3D visualizer
    initShaders_3D();

    //connectivity_nose_correction = $.parseJSON(conn_nose_correction);
    gl.clearColor(0.0, 0.0, 0.0, 1.0);
    gl.clearDepth(1.0);
    gl.enable(gl.DEPTH_TEST);
    gl.depthFunc(gl.LEQUAL);

	drawScene_3D();
}

function prepareConnectivity3D(filePositions, rays, colors, conn_nose_correction) {			
	conectivity3D_initCanvas();
	saveRequiredInputs_3D(filePositions, rays, colors, conn_nose_correction);
}

function start_connectivity_3D(filePositions, rays, colors, conn_nose_correction) {
	conectivity3D_initCanvas();
    saveRequiredInputs_3D(filePositions, rays, colors, conn_nose_correction);
    connectivity3D_startGL();
}


