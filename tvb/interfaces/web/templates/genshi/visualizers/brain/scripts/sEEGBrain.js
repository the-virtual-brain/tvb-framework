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
displayMeasureNodes = true;


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


function bufferAtPoint(p, idx) {
	var result = HLPR_sphereBufferAtPoint(gl, p, 3);
    var bufferVertices= result[0];
    var bufferNormals = result[1];
    var bufferTriangles = result[2];
	var alphaAndColors = createColorBufferForSphere(false, idx, bufferVertices.numItems * 3);
	return [bufferVertices, bufferNormals, bufferTriangles, alphaAndColors[0], alphaAndColors[1]];
}

/**
 * Method used for creating a color buffer for a cube (measure point).
 *
 * @param isPicked If <code>true</code> then the color used will be
 * the one used for drawing the measure points for which the
 * corresponding eeg channels are selected.
 */
function createColorBufferForSphere(isPicked, nodeIdx, nrOfVertices) {
    var pointColor = [];
    var alphas = [];
    pointColor = [nodeIdx, 0, 0];
    var colors = [];
    for (var i = 0; i < nrOfVertices; i++) {
        colors = colors.concat(pointColor);
        if (isPicked) {
        	alphas = alphas.concat([1.0, 0.0]);
        } else {
        	alphas = alphas.concat([0.4, 0.0]);
        }
    }
    var alphaBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, alphaBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(alphas), gl.STATIC_DRAW);
    var cubeColorBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, cubeColorBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(colors), gl.STATIC_DRAW);
    return [alphaBuffer, cubeColorBuffer];
}

/**
 * In the extended view if a certain EEG channel was selected then we
 * have to draw the measure point corresponding to it with a different color.
 *
 * @param measurePointIndex the index of the measure point to which correspond the EEG channel
 * @param isPicked if <code>true</code> then the point will be drawn with the color corresponding
 * to the selected channels, otherwise with the default color
 */
function EX_changeColorBufferForMeasurePoint(measurePointIndex, isPicked) {
    var colorBufferIndex = measurePointsBuffers[measurePointIndex].length - 1;
    var alphaAndColors = createColorBufferForSphere(isPicked, measurePointIndex, measurePointsBuffers[measurePointIndex][0].numItems * 3);
    measurePointsBuffers[measurePointIndex][colorBufferIndex - 1] = alphaAndColors[0];
    measurePointsBuffers[measurePointIndex][colorBufferIndex] = alphaAndColors[1];
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
	        if (shouldIncrementTime) {
            	currentTimeValue = currentTimeValue + TIME_STEP;
           }
	        if (currentTimeValue > MAX_TIME_STEP) {
	        	// Next time value is no longer in activity data.
	            initActivityData();
	            if (isDoubleView) {
					loadEEGChartFromTimeStep(0);
				}
	        }
	    } else {
	    	updateColors(currentTimeValue);
	    }
        
	    if (!isPreview) {
	        drawBuffers(gl.TRIANGLES, measurePointsBuffers, false);
	    }
	    mvPushMatrix();
    	if (isDoubleView) {
    		mvTranslate([0, -5, -22]);
    	} else {
    		mvTranslate([0, -5, -10]);
    	}
    	mvRotate(180, [0, 0, 1]);
    	drawBuffers(drawingMode, shelfBuffers, true);
        mvPopMatrix();
        
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
    		gl.drawElements(gl.TRIANGLES, measurePointsBuffers[i][2].numItems, gl.UNSIGNED_SHORT, 0);
         }    
        var pickedIndex = GL_getPickedIndex();
		if (pickedIndex != undefined) {
            $("#channelChk_" + pickedIndex).attr('checked', !($("#channelChk_" + pickedIndex).attr('checked')));
            $("#channelChk_" + pickedIndex).trigger('change');
		}
	    mvPopMatrix();		 
		doPick = false;
        gl.bindFramebuffer(gl.FRAMEBUFFER, null);
	}
}
