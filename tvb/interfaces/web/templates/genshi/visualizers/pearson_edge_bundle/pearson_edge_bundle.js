/**
 * TheVirtualBrain-Framework Package. This package holds all Data Management, and
 * Web-UI helpful to run brain-simulations. To use it, you also need do download
 * TheVirtualBrain-Scientific Package (for simulators). See content of the
 * documentation-folder for more details. See also http://www.thevirtualbrain.org
 *
 * (c) 2012-2017, Baycrest Centre for Geriatric Care ("Baycrest") and others
 *
 * This program is free software: you can redistribute it and/or modify it under the
 * terms of the GNU General Public License as published by the Free Software Foundation,
 * either version 3 of the License, or (at your option) any later version.
 * This program is distributed in the hope that it will be useful, but WITHOUT ANY
 * WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
 * PARTICULAR PURPOSE.  See the GNU General Public License for more details.
 * You should have received a copy of the GNU General Public License along with this
 * program.  If not, see <http://www.gnu.org/licenses/>.
 *
 *   CITATION:
 * When using The Virtual Brain for scientific publications, please cite it as follows:
 *
 *   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
 *   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
 *       The Virtual Brain: a simulator of primate brain network dynamics.
 *   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
 *
 * .. moduleauthor:: Vlad Farcas <vlad.farcas@codemart.ro>
 **/


var ChordData = {
    region_labels : [""],
    matrix : [],
    svg_d3 : null,
    url_base : "",
    mode : "",
    mode_list : "",
    state: "",
    state_list : "",
    thresh: -1,
}

function ajaxify(){

    ChordData.svg_d3.selectAll("*").transition().duration(100).style("fill-opacity", "0");
    ChordData.svg_d3.selectAll("*").remove();
    ChordData.svg_d3.selectAll("*").transition().duration(100).style("fill-opacity", "1");

    ChordData.thresh = parseFloat($('#slider').attr("value"));

    doAjaxCall({
        url: ChordData.url_base + "selected_state=" + "0" + ";selected_mode=" + ChordData.mode,
        type: 'POST',
        async: true,
        success: function (data){
            ChordData.matrix = $.parseJSON(data);
            init_data(ChordData, function(d){
                return d >= ChordData.thresh ;
            });
        }
    });

}

function init_chord(url_base, labels, shape, state, mode, state_list, mode_list) {

    ChordData.region_labels = labels;
    ChordData.state = state;
    ChordData.mode = mode;
    ChordData.state_list = state_list;
    ChordData.mode_list = mode_list;

    var l = ChordData.region_labels.length;

    ChordData.svg_d3 = d3.select("#middle-chord");

    ChordData.url_base = url_base;

    ajaxify();

}

//slider for threshold
function showVal(newVal){
    $("#slider").attr("value", newVal);
    $("#valBox").html(newVal);
    $("#slider-value").html(newVal);
}