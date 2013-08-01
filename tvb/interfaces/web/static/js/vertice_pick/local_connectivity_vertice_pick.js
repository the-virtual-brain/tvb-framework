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

/*
 * ---------------------------------------===========================================--------------------------------------
 * WARNING: This script is just adding some functionality specific to the stimulus visualization on top of what is defined 
 * in /static/js/vertice_pick/base_vertice_pick.js. As such in all the cases when this script is used, you must first 
 * include base_vertice_pick.js. In case you need to ADD FUNCTIONS here, either make sure you don't "overwrite" something
 * necessary from base_vertice_pick.js, or just prefix your functions. (e.g. LCONN_PICK_${function_name}).
 * ---------------------------------------===========================================--------------------------------------
 */


function LCONN_PICK_changeColorBuffers(data_from_server) {
	/**
	 * Displays a gradient on the surface.
	 *
	 * @param data_from_server a json object which contains the data needed
	 * for drawing a gradient on the surface.
	 */
    data_from_server = $.parseJSON(data_from_server);

    var data = $.parseJSON(data_from_server['data']);
    var minValue = data_from_server['min_value'];
    var maxValue = data_from_server['max_value'];

    if (BASE_PICK_brainDisplayBuffers.length != data.length) {
        displayMessage("Could not draw the gradient view. Invalid data received from the server.", "errorMessage");
        return;
    }

    for (var i = 0; i < data.length; i++) {
        var fakeColorBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, fakeColorBuffer);
        var thisBufferColors = new Float32Array(data[i].length * 4);
        for (var j = 0; j < data[i].length ; j++) {
            var color = getGradientColor(data[i][j], minValue, maxValue);
            thisBufferColors[4*j] = color[0];
            thisBufferColors[4*j + 1] = color[1];
            thisBufferColors[4*j + 2] = color[2];
            thisBufferColors[4*j + 3] = 0.5;
        }
        gl.bufferData(gl.ARRAY_BUFFER, thisBufferColors, gl.STATIC_DRAW);
        BASE_PICK_brainDisplayBuffers[i][3] = fakeColorBuffer;
    }
    drawScene();
    displayMessage("Displaying Local Connectivity profile for selected focal point ..." )
}


function LCONN_PICK_drawDefaultColorBuffers() {
	/*
	 * In case something changed in the parameters or the loaded local_connectivity is
	 * set to None, just use this method to draw the 'default' surface with the gray coloring.
	 */
    if (noOfUnloadedBrainDisplayBuffers != 0) {
        displayMessage("The load operation for the surface data is not completed yet!", "infoMessage");
        return;
    }
	for (var i=0; i<BASE_PICK_brainDisplayBuffers.length; i++) {
		var fakeColorBuffer = gl.createBuffer();
	    gl.bindBuffer(gl.ARRAY_BUFFER, fakeColorBuffer);
	    var thisBufferColors = new Float32Array(BASE_PICK_brainDisplayBuffers[i][0].numItems/ 3 * 4);
	    for (var j = 0; j < BASE_PICK_brainDisplayBuffers[i][0].numItems / 3 * 4; j++) {
	    	thisBufferColors[j] = 0.5;
	    }
	    gl.bufferData(gl.ARRAY_BUFFER, thisBufferColors, gl.STATIC_DRAW);
	    BASE_PICK_brainDisplayBuffers[i][3] = fakeColorBuffer;
	}
    drawScene();
}

