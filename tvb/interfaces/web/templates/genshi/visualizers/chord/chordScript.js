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
 **/

/**
 * Created by vlad.farcas on 7/21/2017.
 *
 * Many thanks to Mike Bostock's bl.ock: https://bl.ocks.org/mbostock/7607999
 *
 * A first prototype of the connectivity chord viewer
 *
 */

var ChordData = {
    region_labels : [""],
    matrix: [],
}

function init_chord(url_base, labels) {

    var matrix = "weights";

    doAjaxCall({
        url: url_base,
        type: 'POST',
        async: true,
        success: function (data){
            ChordData.matrix = $.parseJSON(data);
        }
    });

    ChordData.region_labels = labels;

    var l = ChordData.region_labels.length;

    var middle_chord = d3.select("#middle-chord");

    init_data(ChordData, middle_chord);

    //add event listener to switch button
    $("#switch-1").on("click", function(e){

        let newmatrix = matrix === "weights" ? "tract_lengths" : "weights";

        doAjaxCall({
            url: url_base.replace(matrix, newmatrix),
            type: 'POST',
            async: true,
            success: function (data) {
                ChordData.matrix = $.parseJSON(data);
            }
        });

        matrix = newmatrix;

        middle_chord.selectAll("*").transition().duration(100).style("fill-opacity", "0");
        middle_chord.selectAll("*").remove();

        init_data(ChordData, middle_chord);

        middle_chord.selectAll("*").transition().duration(100).style("fill-opacity", "1");
    });
}