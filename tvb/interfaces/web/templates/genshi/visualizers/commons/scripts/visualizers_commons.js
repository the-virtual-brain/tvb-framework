// -------------------------------------------------------------
//              Channel selector methods start from here
// -------------------------------------------------------------

function checkAll(entryArray, channelsArray) {
	/*
	 * Add all channels to the channelsArray list and make sure that 
	 * all of the checkbox are checked.
	 */
	divId = 'table_' + entryArray;
    $('div[id^="'+ divId + '"] input').each(function () {
        if (this.type == "checkbox") {
            var channelId = parseInt(this.id.split("channelChk_")[1]);
            var elemIdx = $.inArray(channelId, channelsArray);
		    if (elemIdx == -1) {
		        channelsArray.push(channelId);
		    }
		    $("#channelChk_" + channelId).attr('checked', true);
        }
    });
}

function clearAll(entryArray, channelsArray) {
	/*
	 * Remove all channels to the channelsArray list and make sure that 
	 * none of the checkbox are checked.
	 */
	divId = 'table_' + entryArray;
    $('div[id^="'+ divId + '"] input').each(function () {
        if (this.type == "checkbox") {
            var channelId = this.id.split("channelChk_")[1];
            var elemIdx = $.inArray(parseInt(channelId), channelsArray);
		    if (elemIdx != -1) {
		        channelsArray.splice(elemIdx, 1);
		    }
        }
        $("#channelChk_" + channelId).attr('checked', false);
    });
}

function updateChannelsList(domElem, channelsArray) {
	/*
	 * Update the channelsArray array whenever a checkbox is clicked.
	 */
    var channelId = parseInt(domElem.id.split("channelChk_")[1]);
    if (domElem.checked) {
        var elemIdx = $.inArray(channelId, channelsArray);
	    if (elemIdx == -1) {
	        channelsArray.push(channelId);
	    }
    } else {
        var elemIdx = $.inArray(channelId, channelsArray);
	    if (elemIdx != -1) {
	        channelsArray.splice(elemIdx, 1);
	    }
    }
}

// -------------------------------------------------------------
//              Channel selector methods end here
// -------------------------------------------------------------


// -------------------------------------------------------------
//              Datatype methods mappings start from here
// -------------------------------------------------------------

function readDataPageURL(baseDatatypeMethodURL, fromIdx, toIdx, stateVariable, mode, step) {
	if (stateVariable == undefined || stateVariable == null) {
		stateVariable = 0;
	}
	if (mode == undefined || stateVariable == null) {
		mode = 0;
	}
	if (step == undefined || step == null) {
		step = 1;
	}
	return baseDatatypeMethodURL + '/read_data_page/False?from_idx=' + fromIdx +";to_idx=" + toIdx + ";step=" + step + ";specific_slices=[null," + stateVariable + ",null," + mode +"]";
}

function readDataChannelURL(baseDatatypeMethodURL, fromIdx, toIdx, stateVariable, mode, step, channels) {
	var baseURL = readDataPageURL(baseDatatypeMethodURL, fromIdx, toIdx, stateVariable, mode, step);
	return baseURL.replace('read_data_page', 'read_channels_page') + ';channels_list=' + channels;
}
 
// -------------------------------------------------------------
//              Datatype methods mappings end here
// -------------------------------------------------------------