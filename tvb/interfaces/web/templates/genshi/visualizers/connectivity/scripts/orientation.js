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
 * This file contains code for drawing orientation: ears and nose.
 */

// represents an array that contains the buffers needed for drawing the nose and the ears
var ORIENTATION_Buffers;


function ORIENTATION_draw_nose_and_ears() {
	 //draw the nose
    mvPushMatrix();
    gl.uniform1i(shaderProgram.colorIndex, YELLOW_COLOR_INDEX);
    
    mvTranslate([0.0, -20.0, -55.0]);
    mvRotate(180, [1, 0, 0]);
    multMatrix(GL_currentRotationMatrix);
    drawPyramid(ORIENTATION_Buffers[1], ORIENTATION_Buffers[2], ORIENTATION_Buffers[0]);
    mvPopMatrix();

    //draw the left ear
    mvPushMatrix();
    gl.uniform1i(shaderProgram.colorIndex, BLUE_COLOR_INDEX);
    mvTranslate([-17.0, 0.0, -55.0]);
    multMatrix(GL_currentRotationMatrix);
    drawPyramid(ORIENTATION_Buffers[3], ORIENTATION_Buffers[4], ORIENTATION_Buffers[0]);
    mvPopMatrix();

    //draw the right ear
    mvPushMatrix();
    gl.uniform1i(shaderProgram.colorIndex, RED_COLOR_INDEX);
    mvTranslate([17.0, 0.0, -55.0]);
    multMatrix(GL_currentRotationMatrix);
    drawPyramid(ORIENTATION_Buffers[5], ORIENTATION_Buffers[6], ORIENTATION_Buffers[0]);
    mvPopMatrix();
}


function drawPyramid(vertexPositionBuffer, vertexPositionBufferForBottomOfPyramid, normals) {
    gl.bindBuffer(gl.ARRAY_BUFFER, vertexPositionBuffer);
    gl.vertexAttribPointer(shaderProgram.vertexPositionAttribute, vertexPositionBuffer.itemSize, gl.FLOAT, false, 0, 0);
    gl.bindBuffer(gl.ARRAY_BUFFER, normals);
    gl.vertexAttribPointer(shaderProgram.vertexNormalAttribute, normals.itemSize, gl.FLOAT, false, 0, 0);
    setMatrixUniforms();
    gl.drawArrays(gl.TRIANGLES, 0, vertexPositionBuffer.numItems);
    //draw the bottom of the pyramid
    drawSquare(vertexPositionBufferForBottomOfPyramid)
}


function drawSquare(vertexPositionBuffer) {
    gl.uniform1i(shaderProgram.colorIndex, GREEN_COLOR_INDEX);
    gl.bindBuffer(gl.ARRAY_BUFFER, vertexPositionBuffer);
    gl.vertexAttribPointer(shaderProgram.vertexPositionAttribute, vertexPositionBuffer.itemSize, gl.FLOAT, false, 0, 0);
    setMatrixUniforms(shaderProgram);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, vertexPositionBuffer.numItems);
}

/**
 * Returns an array of buffers that are used for drawing the nose and the ears.
 *
 * idx0 - buffer which contains the normals used for drawing the nose and the ears
 * idx1 - buffer which contains the points needed for drawing the NOSE
 * idx2 - buffer which contains the points needed for drawing the bottom of the nose
 * idx3 - buffer which contains the points needed for drawing the LEFT EAR
 * idx4 - buffer which contains the points needed for drawing the bottom of the left ear
 * idx5 - buffer which contains the points needed for drawing the RIGHT EAR
 * idx6 - buffer which contains the points needed for drawing the bottom of the right ear
 */
function ORIENTATION_initOrientationBuffers() {
    var noseVertexPositionBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, noseVertexPositionBuffer);
    var vertices = [
        // Front face
        0.0,  1.0,  0.0,
        -1.0, -1.0,  1.0,
        1.0, -1.0,  1.0,

        // Right face
        0.0,  1.0,  0.0,
        1.0, -1.0,  1.0,
        1.0, -1.0, -1.0,

        // Back face
        0.0,  1.0,  0.0,
        1.0, -1.0, -1.0,
        -1.0, -1.0, -1.0,

        // Left face
        0.0,  1.0,  0.0,
        -1.0, -1.0, -1.0,
        -1.0, -1.0,  1.0
    ];
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices), gl.STATIC_DRAW);
    noseVertexPositionBuffer.itemSize = 3;
    noseVertexPositionBuffer.numItems = 12;

    var leftEarVertexPositionBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, leftEarVertexPositionBuffer);
    vertices = [
        // Front face
        -2.0, 0.0, 0.0,
        1.0, 1.0,  1.0,
        1.0, -1.0,  1.0,

        // Right face
        1.0,  -1.0,  1.0,
        1.0, -1.0,  -1.0,
        -2.0, 0.0, 0.0,

        // Back face
        1.0,  -1.0,  -1.0,
        1.0, 1.0, -1.0,
        -2.0, 0.0, 0.0,

        // Left face
        1.0,  1.0,  -1.0,
        1.0, 1.0, 1.0,
        -2.0, 0.0,  0.0
    ];
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices), gl.STATIC_DRAW);
    leftEarVertexPositionBuffer.itemSize = 3;
    leftEarVertexPositionBuffer.numItems = 12;

    var rightEarVertexPositionBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, rightEarVertexPositionBuffer);
    vertices = [
        // Front face
        -1.0, 1.0, 1.0,
        -1.0, -1.0,  1.0,
        2.0, 0.0,  0.0,

        // Right face
        -1.0,  -1.0,  1.0,
        2.0, 0.0,  0.0,
        -1.0, -1.0, -1.0,

        // Back face
        -1.0,  -1.0,  -1.0,
        -1.0, 1.0, -1.0,
        2.0, 0.0, 0.0,

        // Left face
        -1.0,  1.0,  1.0,
        -1.0, 1.0, -1.0,
        2.0, 0.0,  0.0
    ];
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices), gl.STATIC_DRAW);
    rightEarVertexPositionBuffer.itemSize = 3;
    rightEarVertexPositionBuffer.numItems = 12;

    var earNormals = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, earNormals);
    normals = [     1.0,  0.0,  1.0,  // Front
        1.0,  0.0,  1.0,
        1.0,  0.0,  1.0,
        1.0,  -1.0, 0.0,  // Right
        1.0,  -1.0, 0.0,
        1.0,  -1.0, 0.0,
        0.0,  1.0,  -1.0,  // Right
        0.0,  1.0,  -1.0,
        0.0,  1.0,  -1.0,
        1.0,  1.0,  0.0,  // Left
        1.0,  1.0,  0.0,
        1.0,  1.0,  0.0];
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(normals), gl.STATIC_DRAW);
    earNormals.itemSize = 3;
    earNormals.numItems = 12;

    var leftEarBottom = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, leftEarBottom);
    vertices = [
        1.0,  1.0,  1.0,
        1.0,  1.0,  -1.0,
        1.0, -1.0,  1.0,
        1.0, -1.0,  -1.0
    ];
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices), gl.STATIC_DRAW);
    leftEarBottom.itemSize = 3;
    leftEarBottom.numItems = 4;

    var rightEarBottom = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, rightEarBottom);
    vertices = [
        -1.0,  1.0,  1.0,
        -1.0,  1.0,  -1.0,
        -1.0, -1.0,  1.0,
        -1.0, -1.0,  -1.0
    ];
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices), gl.STATIC_DRAW);
    rightEarBottom.itemSize = 3;
    rightEarBottom.numItems = 4;

    var noseBottom = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, noseBottom);
    vertices = [
        1.0, -1.0,  1.0,
        -1.0,  -1.0,  1.0,
        1.0, -1.0, -1.0,
        -1.0, -1.0,  -1.0
    ];
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices), gl.STATIC_DRAW);
    noseBottom.itemSize = 3;
    noseBottom.numItems = 4;

    ORIENTATION_Buffers = [earNormals, noseVertexPositionBuffer, noseBottom, 
    					   leftEarVertexPositionBuffer, leftEarBottom, 
    					   rightEarVertexPositionBuffer, rightEarBottom];
}
