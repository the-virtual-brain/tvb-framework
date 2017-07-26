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
 * Many thanks to Mike Bostock's bl.ock: https://gist.github.com/mbostock/4062006 and https://bl.ocks.org/mbostock/6452972
 *
 * A first prototype of the connectivity chord viewer
 *
 */

var toggleParameters = true;

var data = {
    region_labels : [""],
    weights : [],
    tract_lengths : [],
    data_counts : [],
    beta : 10, //weights parameter
    alpha: 0.001 //tract_length parameter
}

function set_region_labels(l){
    data.region_labels = l;
}

function set_weights(w){
    data.weights = w;
}

function set_tract_lenghts(t){
    data.tract_lengths = t;
}

function float_array_to_hex(f){
    return "#" + (f[0] * 255).toString(16) + "" + (f[1] * 255).toString(16) + "" + (f[2] * 255).toString(16);
}

function init_chord(){
    var l = data.region_labels.length;
    var colorScheme = ColSch_initColorSchemeGUI(0, l, function () {
        var diagram = d3.select(".diagram-svg").selectAll("*");
        diagram.transition().duration(100).style("fill-opacity", "0");
        diagram.remove();
        init_data();
    });
    init_data();
    //add event listener to switch button
    $(".switch-input").on("click", function(e){
        var diagram = d3.select(".diagram-svg").selectAll("*");
        diagram.transition().duration(100).style("fill-opacity", "0");
        diagram.remove();
        toggleParameters = !toggleParameters;
        init_data();
        diagram.transition().duration(100).style("fill-opacity", "1");
    });
    function init_data(){
        for(var i = 0; i < l; i++){
            var counts_line = [];
            for(var j = 0; j < l; j++){
                var w = 0;
                if (toggleParameters) {//We have chosen the weigths parameter
                     w = data.weights[i * l + j] * data.beta;
                }
                else{//We have chosen the tract length parameter
                     w = data.tract_lengths[i * l + j] * data.alpha;
                }
                counts_line[j] = w;
            }
            data.data_counts[i] = counts_line;
        }
        var diagram = d3.select(".diagram-svg"),
        width = +diagram.attr("width"),
        height = +diagram.attr("height"),
        outerRadius = Math.min(width, height) * 0.5 - 40,
        innerRadius = outerRadius - 30;

        var chord = d3.chord()
            .padAngle(0.05)
            .sortSubgroups(d3.descending);
        var arc = d3.arc()
            .innerRadius(innerRadius)
            .outerRadius(outerRadius);
        var ribbon = d3.ribbon()
            .radius(innerRadius);

        var g = diagram.append("g")
            .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")")
            .datum(chord(data.data_counts));

        var group = g.append("g")
            .attr("class", "groups")
            .selectAll("g")
            .data(function(chords) { return chords.groups; })
            .enter().append("g");

        group.append("path")
            .style("fill", function(d) { return float_array_to_hex(ColSch_getColor(d.index)); })
            .style("stroke", function(d) { return d3.rgb(float_array_to_hex(ColSch_getColor(d.index))).darker(); })
            .attr("d", arc)
            .attr("id", function(d, i){return "group-" + i;})
            .on("mouseover", fade(.01))
            .on("mouseout", fade(1));

        var groupTick = group.selectAll(".group-tick")
          .data(function(d) { return groupTicks(d, 1e3); })
          .enter().append("g")
            .attr("class", "group-tick")
            .attr("transform", function(d) { return "rotate(" + (d.angle * 180 / Math.PI - 90) + ") translate(" + outerRadius + ",0)"; });

        groupTick.append("line")
            .attr("x2", 6);

        //NOTE: in case we want different order/group of region centers, take care of this
        var i = -1;

        groupTick
          .filter(function(d) { return d.value % 5e3 === 0; })
          .append("text")
            .attr("x", 8)
            .attr("dy", ".35em")
            .attr("transform", function(d) { return d.angle > Math.PI ? "rotate(180) translate(-16)" : null; })
            .style("text-anchor", function(d) { return d.angle > Math.PI ? "end" : null; })
            .text(function(d){i++; return data.region_labels[i];});

        g.append("g")
            .attr("class", "ribbons")
          .selectAll("path")
          .data(function(chords) { return chords; })
          .enter().append("path")
            .attr("d", ribbon)
            .style("fill", function(d) { return float_array_to_hex(ColSch_getColor(d.source.index)); })
            .style("stroke", function(d) { return d3.rgb(float_array_to_hex(ColSch_getColor(d.source.index))).darker(); })

        // Returns an array of tick angles and values for a given group and step.
        function groupTicks(d, step) {
          var k = (d.endAngle - d.startAngle) / d.value;
          return d3.range(0, d.value, step).map(function(value) {
            return {value: value, angle: value * k + d.startAngle};
          });
        }

        function fade(opacity) {
            return function(d, i) {
            diagram.selectAll("g.ribbons path")
                .filter(function(d) { return d.source.index != i && d.target.index != i; })
                .transition()
                .duration(100)
                .style("stroke-opacity", opacity)
                .style("fill-opacity", opacity);
            };
        }
    }
}


