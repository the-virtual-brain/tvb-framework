var startColorRGB = [192, 192, 192];
var endColorRGB = [255, 0, 0];
var nodeColorRGB = [255, 255, 255];

/**
 * @param startColorComponentId id of the container in which will be drawn the color picker for the start color
 * @param endColorComponentId id of the container in which will be drawn the color picker for the end color
 */
function drawSimpleColorPicker(divId, refreshFunction) {
    $('#' + divId).ColorPicker({
        color: '#ffffff',
        onShow: function (colpkr) {
            $(colpkr).fadeIn(500);
            return false;
        },
        onHide: function (colpkr) {
            $(colpkr).fadeOut(500);
            return false;
        },
        onChange: function (hsb, hex, rgb) {
            $('#' + divId + ' div').css('backgroundColor', '#' + hex);
            nodeColorRGB = [parseInt(rgb.r), parseInt(rgb.g), parseInt(rgb.b)];
            if (refreshFunction) {
                 refreshFunction();
            }
        }
    });	
    $('#' + divId + ' div').css('backgroundColor', '#ffffff');
}


function getNewNodeColor() {
	return nodeColorRGB;
}


function drawColorPickerComponent(startColorComponentId, endColorComponentId, refreshFunction) {
	start_color_css = 'rgb(' + startColorRGB[0] + ',' + startColorRGB[1] + ',' + startColorRGB[2] + ')'
	end_color_css = 'rgb(' + endColorRGB[0] + ',' + endColorRGB[1] + ',' + endColorRGB[2] + ')'
    $('#' + startColorComponentId).ColorPicker({
        color: start_color_css,
        onShow: function (colpkr) {
            $(colpkr).fadeIn(500);
            return false;
        },
        onHide: function (colpkr) {
            $(colpkr).fadeOut(500);
            return false;
        },
        onChange: function (hsb, hex, rgb) {
            $('#' + startColorComponentId + ' div').css('backgroundColor', '#' + hex);
            startColorRGB = [parseInt(rgb.r), parseInt(rgb.g), parseInt(rgb.b)];
            if (refreshFunction) {
                 refreshFunction();
            }
        }
    });

    $('#' + endColorComponentId).ColorPicker({
        color: end_color_css,
        onShow: function (colpkr) {
            $(colpkr).fadeIn(500);
            return false;
        },
        onHide: function (colpkr) {
            $(colpkr).fadeOut(500);
            return false;
        },
        onChange: function (hsb, hex, rgb) {
            $('#' + endColorComponentId + ' div').css('backgroundColor', '#' + hex);
            endColorRGB = [parseInt(rgb.r), parseInt(rgb.g), parseInt(rgb.b)];
            if (refreshFunction) {
                refreshFunction();
            }
        }
    });

    $('#' + startColorComponentId + ' div').css('backgroundColor', start_color_css);
    $('#' + endColorComponentId + ' div').css('backgroundColor', end_color_css);
}


/**
 * You must have a color picker component into the page in order to work this method.
 *
 * The following condition should be true: <code> min <= pointValue <= max </code>
 */
function getGradientColor(pointValue, min, max) {
    if (min == max) {
        return [normalizeColor(startColorRGB[0]), normalizeColor(startColorRGB[1]), normalizeColor(startColorRGB[2])];
    }

    var r = normalizeColor(startColorRGB[0]) + [(pointValue - min) / (max - min)] * (normalizeColor(endColorRGB[0]) - normalizeColor(startColorRGB[0]));
    var g = normalizeColor(startColorRGB[1]) + [(pointValue - min) / (max - min)] * (normalizeColor(endColorRGB[1]) - normalizeColor(startColorRGB[1]));
    var b = normalizeColor(startColorRGB[2]) + [(pointValue - min) / (max - min)] * (normalizeColor(endColorRGB[2]) - normalizeColor(startColorRGB[2]));

    return [normalizeValue(r), normalizeValue(g), normalizeValue(b)];
}

function getGradientColorString(pointValue, min, max) {
    rgb_values = getGradientColor(pointValue, min, max);
    return "rgb("+Math.round(rgb_values[0]*255)+","+ Math.round(rgb_values[1]*255)+","+ Math.round(rgb_values[2]*255)+")";
}

function getStartColor() {
	return startColorRGB;
}

function getEndColor() {
	return endColorRGB;
}

function normalizeColor(color) {
    return color / 255.0;
}

function normalizeValue(value) {
    if (value > 1) {
        return 1;
    } else if (value < 0) {
        return 0;
    }

    return value;
}