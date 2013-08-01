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

//global variables needed for save/preview canvas operation
var C2I_shouldPreviewCanvas = false;
var C2I_shouldSaveCanvas = false;
var C2I_exportType, C2I_operationId;


/**
 * If you want ot preview a webGl canvas you have to set
 * the flag 'webGlCanvas' to true for that canvas.
 */
function previewCanvas(canvasId, exportType) {
    var canvas = document.getElementById(canvasId);
    var isWebGlCanvas = canvas.webGlCanvas;
    if (isWebGlCanvas != undefined && isWebGlCanvas) {
        C2I_shouldPreviewCanvas = true;
        C2I_exportType = exportType;
    } else {
        var strData = __exportCanvas(canvasId, exportType);
        window.open(strData, "_blank", "location=no,menubar=no,status=no,scrollbars=no,titlebar=no,toolbar=no");
    }
}


/**
 * If you want ot export webGl canvases you have to set
 * the flag 'webGlCanvas' to true for that canvases.
 */
function exportCanvases(exportType, operationId) {
    if ($("canvas, svg").length == 0) {
        displayMessage("Invalid action. Please report to your TVB technical contact.", "errorMessage");
        return;
    }
    $("canvas").each(function () {
        var canvasId = this.id;
        if (canvasId) {
            var isWebGlCanvas = this.webGlCanvas;
            if (isWebGlCanvas != undefined && isWebGlCanvas) {
                //we should treat in a different way the webGl canvases because of the webGl double buffering
                //by default, webGl will not save the depth and color buffers after each draw call.
                //Trying to call 'toDataURL' or 'readPixels' in this state will result in an array of zero’ed out data.
                C2I_shouldSaveCanvas = true;
                C2I_exportType = exportType;
                C2I_operationId = operationId;
            } else {
                __storeCanvas(canvasId, exportType, operationId)
            }
        }
    });
    $("svg").attr({ version: '1.1' , xmlns:"http://www.w3.org/2000/svg"});
    $("svg").each(function () {
        __storeSVG(this, exportType, operationId)
    });
}


/**
 * This method should be called in all visualizers which has a webGl
 * canvas and offer the export or preview functionality for that canvas.
 *
 * @param canvasId the id of the canvas
 */
function checkSavePreviewWebGlCanvas(canvasId) {
    if (C2I_shouldSaveCanvas) {
        __storeCanvas(canvasId, C2I_exportType, C2I_operationId);
        C2I_shouldSaveCanvas = false;
    } else if (C2I_shouldPreviewCanvas) {
        C2I_shouldPreviewCanvas = false;
        var strData = __exportCanvas(canvasId, C2I_exportType);
        window.open(strData, "_blank", "location=no,menubar=no,status=no,scrollbars=no,titlebar=no,toolbar=no");
    }
}


// sends the generated file to the client
function startDownload(strData, mimeType) {
    // Fake file type, to force the browser to start the download.
    var downloadMimeType = "image/octet-stream";
    document.location.href = strData.replace(mimeType, downloadMimeType);
}


/**
 *This method save the svg html. Before this it also adds the required css styles.
 */
function __storeSVG(svgElement, exportType, operationId) {
	// Wrap the svg element as to get the actual html and use that as the src for the image

	var wrap = document.createElement('div');
	wrap.appendChild(svgElement.cloneNode(true));
	var data = wrap.innerHTML;

    // get the styles for the svg
    $.get( "/static/style/tvbviz.css", function (stylesheet) {
                                                                         // strip all
        var re = new RegExp("[\\s\\n^]*\\/\\*(.|[\\r\\n])*?\\*\\/" +     // block style comments
                            "|([\\s\\n]*\\/\\/.*)" +                     // single line comments
                            "|(^\\s*[\\r\\n])", "gm");                   // empty lines

        var svgStyle = "<defs><style type='text/css'><![CDATA["
                     +  stylesheet.replace(re,"")
                     + "]]></style></defs>";

        // embed the styles in svg
        var startingTag = data.substr(0, data.indexOf(">") + 1);
        var restOfSvg = data.substr(data.indexOf(">") + 1, data.length + 1)
        var styleAddedData = startingTag + svgStyle + restOfSvg;


        // send it to server
        $.ajax({  type: "POST", url: '/project/figure/storeresultfigure/svg/' + operationId,
            data: {"export_data": styleAddedData},
            success: function(r) {
                displayMessage("Figure successfully saved!<br/> See Project section, Image archive sub-section.",
                               "infoMessage")
            } ,
            error: function(r) {
                displayMessage("Could not store preview image, sorry!", "warningMessage")
            }
        });

    } );
}

/**
 * This method should NOT be called from outside of this file in specially for webGl canvases.
 *
 * @param canvasId the id of the canvas
 * @param exportType this parameter may be "JPEG" or "PNG"
 */
function __exportCanvas(canvasId, exportType) {
    var oCanvas = document.getElementById(canvasId);
    var mimeType = "image/png";
    if (exportType == "JPEG") {
        mimeType = "image/jpeg";
    }
    return oCanvas.toDataURL(mimeType);
}


function __storeCanvas(canvasId, exportType, operationId) {
    var result = __exportCanvas(canvasId, exportType);
    $.ajax({  type: "POST", url: '/project/figure/storeresultfigure/jpg/' + operationId,
                data: {"export_data": result.replace('data:image/png;base64,', '')},
                success: function(r) {
                    displayMessage("Figure successfully saved!<br/> See Project section, Image archive sub-section.", "infoMessage")
                } ,
                error: function(r) {
                    displayMessage("Could not store preview image, sorry!", "warningMessage")
                }
            });
}