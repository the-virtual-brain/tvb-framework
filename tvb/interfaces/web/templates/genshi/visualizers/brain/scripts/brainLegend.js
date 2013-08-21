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

////////////////////////////////////~~~~~~~~~~~~START LEGEND RELATED CODE~~~~~~~~~~~~~~~~///////////////////////////
var legendXMin = 80;
var legendXMax = 83;
var legendYMin = -63;
var legendYMax = 63;
var legendZ = -150;
var legendGranularity = 127;
var legend_activity_values = [];

///// We draw legend with WebGL, so for the legend object we need buffers.
var LEG_legendBuffers = [];

///// Clowny face means the colors on Brain are completely spread over the colors area.
var LEG_clownyFace = false;

var legendMin = 0;
var legendMax = 1;

function LEG_initMinMax(minVal, maxVal) {
	legendMin = minVal;
	legendMax = maxVal;
}

function LEG_setClownyFace() {
    LEG_clownyFace = !LEG_clownyFace;
    LEG_updateLegendColors();
}


function LEG_updateLegendXMinAndXMax() {
    //800/600 = 1.33
    legendXMin = (gl.viewportWidth/gl.viewportHeight) * 78/1.33;
    legendXMax = (gl.viewportWidth/gl.viewportHeight) * 78/1.33 + 3;
}

function LEG_updateLegendVerticesBuffers() {
    LEG_updateLegendXMinAndXMax();

    var vertices = [];
    var inc = (legendYMax - legendYMin) / legendGranularity;
    for (var i = legendYMin; i <= legendYMax; i = i + inc) {
        vertices = vertices.concat([legendXMax, i, legendZ]);
        vertices = vertices.concat([legendXMin, i, legendZ]);
    }

    LEG_legendBuffers[0] = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, LEG_legendBuffers[0]);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices), gl.STATIC_DRAW);
    LEG_legendBuffers[0].itemSize = 3;
    LEG_legendBuffers[0].numItems = vertices.length / 3;
}

function LEG_generateLegendBuffers() {
    LEG_updateLegendXMinAndXMax();

	var vertices = [];
	var normals = [];
	var indices = [];

	var inc = (legendYMax - legendYMin) / legendGranularity;
	var activityDiff = legendMax - legendMin;
    legend_activity_values = [];        // empty the set, or the gradient will get higher on subsequent calls
	for (var i=legendYMin; i<=legendYMax; i=i+inc) {
		vertices = vertices.concat([legendXMax, i, legendZ]);
		vertices = vertices.concat([legendXMin, i, legendZ]);
		normals = normals.concat([0, 0, 1, 0, 0, 1]);
		var activityValue = legendMin + activityDiff * ((i - legendYMin) / (legendYMax - legendYMin));
		legend_activity_values = legend_activity_values.concat([activityValue, activityValue]);
	}
	for (var i=0; i<vertices.length/3 - 2; i++) {
		indices = indices.concat([i, i+1, i+2]);
	}
	LEG_legendBuffers[0] = gl.createBuffer();
	gl.bindBuffer(gl.ARRAY_BUFFER, LEG_legendBuffers[0]);
	gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices), gl.STATIC_DRAW);
	LEG_legendBuffers[0].itemSize = 3;
	LEG_legendBuffers[0].numItems = vertices.length / 3;
	
	LEG_legendBuffers[1] = gl.createBuffer();
	gl.bindBuffer(gl.ARRAY_BUFFER, LEG_legendBuffers[1]);
	gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(normals), gl.STATIC_DRAW);
	LEG_legendBuffers[1].itemSize = 3;
	LEG_legendBuffers[1].numItems = normals.length / 3;
	
	LEG_legendBuffers[2] = gl.createBuffer();
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, LEG_legendBuffers[2]);
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint16Array(indices), gl.STATIC_DRAW);
    LEG_legendBuffers[2].itemSize = 1;
    LEG_legendBuffers[2].numItems = indices.length;
    
    if (isOneToOneMapping) {
    	var colors = []
        for (var i=0; i < LEG_legendBuffers[0].numItems* 4; i++) {
        	colors = colors.concat(0, 0, 1, 1.0);
        }
    	LEG_legendBuffers[3] = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, LEG_legendBuffers[3]);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(colors), gl.STATIC_DRAW);
        
    } else {
    	var alphas = [];
    	var alphasIndices = [];
    	for (var i=0; i<legend_activity_values.length/2; i++) {
    		alphas = alphas.concat([1.0, 0.0, 1.0, 0.0]);
    		alphasIndices = alphasIndices.concat([i + NO_OF_MEASURE_POINTS + 2, 1, 1, i + NO_OF_MEASURE_POINTS + 2, 1, 1])
    	}
    	
    	LEG_legendBuffers[3] = gl.createBuffer();
	    gl.bindBuffer(gl.ARRAY_BUFFER, LEG_legendBuffers[3]);
	    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(alphas), gl.STATIC_DRAW);
	    
	    LEG_legendBuffers[4] = gl.createBuffer();
	    gl.bindBuffer(gl.ARRAY_BUFFER, LEG_legendBuffers[4]);
	    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(alphasIndices), gl.STATIC_DRAW);    
	}	
    LEG_updateLegendColors()
}


function LEG_setUniform(idx, activity, start_color, diff_color) {
	/**
	 * Set the uniform color corresponding to activity at index IDX
	 * having the start color and the color difference.
	 */
	if (LEG_clownyFace) {
		var r = start_color[0] + activity * diff_color[0];
        var g = start_color[1] + (activity*100 - Math.round(activity *100)) * diff_color[1];
        var b = start_color[2] + (activity*10000 - Math.round(activity *10000)) * diff_color[2];
        
	} else {
	    var r = start_color[0] + activity * diff_color[0];
	    var g = start_color[1] + activity * diff_color[1];
	    var b = start_color[2] + activity * diff_color[2];	
	}
    gl.uniform4f(shaderProgram.colorsUniform[idx], r, g, b, 1);	
}


function LEG_updateLegendColors() {
	/**
	 * Refresh color buffer for legend.
	 * **/
	var colorDiff = legendMax - legendMin;
    if (colorDiff == 0) {
    	colorDiff = 1;
    }
    var nStartColors = [normalizeColor(startColorRGB[0]), 
                        normalizeColor(startColorRGB[1]),
                        normalizeColor(startColorRGB[2])];
    var nDiffColors = [normalizeColor(endColorRGB[0]) - nStartColors[0],
                       normalizeColor(endColorRGB[1]) - nStartColors[1],
                       normalizeColor(endColorRGB[2]) - nStartColors[2]];	
                       
    if (isOneToOneMapping) {
    	upperBorder = legend_activity_values.length / 2
    	var colors = new Float32Array(upperBorder * 8);
    	for (var j = 0; j < upperBorder; j++) {
            var diff_activity = (parseFloat(legend_activity_values[j*2]) -legendMin) / colorDiff;
            var sub_f32s = colors.subarray(j * 8, (j + 1) * 8);
            if (LEG_clownyFace) {
                sub_f32s[0] = nStartColors[0] + diff_activity * nDiffColors[0];
                sub_f32s[1] = nStartColors[1] + (diff_activity*1000 - Math.round(diff_activity *1000))  * nDiffColors[1];
                sub_f32s[2] = nStartColors[2] + (diff_activity*1000000 - Math.round(diff_activity *1000000))  * nDiffColors[2];
                sub_f32s[3] = 1;
                for (k=0; k<4; k++) {
                	sub_f32s[4 + k] = sub_f32s[k]
                } 
                         	
            } else {
                sub_f32s[0] = nStartColors[0] + diff_activity * nDiffColors[0];
                sub_f32s[1] = nStartColors[1] + diff_activity * nDiffColors[1];
                sub_f32s[2] = nStartColors[2] + diff_activity * nDiffColors[2];
                sub_f32s[3] = 1;
                for (k=0; k<4; k++) {
                	sub_f32s[4 + k] = sub_f32s[k]
                }
            }
            LEG_legendBuffers[3] = gl.createBuffer();
            gl.bindBuffer(gl.ARRAY_BUFFER, LEG_legendBuffers[3]);
            gl.bufferData(gl.ARRAY_BUFFER, colors, gl.STATIC_DRAW);
        }
        
    } else {
        for (var i = 0; i < legend_activity_values.length/2; i++) {
        	var diff_activity = (parseFloat(legend_activity_values[i*2]) - legendMin) /colorDiff;
        	LEG_setUniform(i + NO_OF_MEASURE_POINTS + 2, diff_activity, nStartColors, nDiffColors);
        }    	
    }
}
/////////////////////////////////////////~~~~~~~~END LEGEND RELATED CODE~~~~~~~~~~~//////////////////////////////////


