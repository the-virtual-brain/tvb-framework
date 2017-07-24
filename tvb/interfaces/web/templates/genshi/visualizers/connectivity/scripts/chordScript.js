/**
 * Created by vlad.farcas on 7/21/2017.
 */

/**
 *
 * Many thanks to Mike Bostock's bl.ock: https://gist.github.com/mbostock/4062006
 *
 */
//TODO: use encapsulation to avoid too many global vars
var region_labels = [""];
var weights = [];
var tract_lengths = [];
var data_counts = [];
var alpha = -0.5; //tract_length parameter
var beta = 10; //weight parameter

function set_region_labels(l){
    region_labels = l;
}

function set_weights(w){
    weights = w;
}
// TODO add select to change edges on user action
function set_tract_lenghts(t){
    tract_lengths = t;
}

function init_chord(){
    // todo use classic for(var i=0;....)
    for(var i in region_labels){
        var counts_line = [];
        for(var j in region_labels){
            var w = weights[parseInt(i) * parseInt(region_labels.length) + parseInt(j)] * beta;
            counts_line[j] = w;
        }
        data_counts[i] = counts_line;
    }
    var svg = d3.select(".diagram-svg"),
    width = +svg.attr("width"),
    height = +svg.attr("height"),
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
    //TODO can we use tvb color schemes ?
    var color = d3.scaleOrdinal()
        .domain(d3.range(4))
        .range(["#7aeac9", "#00c7ff", "#ffa4e2", "#8e60f2"]);
    var g = svg.append("g")
        .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")")
        .datum(chord(data_counts));

    var group = g.append("g")
        .attr("class", "groups")
        .selectAll("g")
        .data(function(chords) { return chords.groups; })
        .enter().append("g");


    group.append("path")
        .style("fill", function(d) { return color(d.index); })
        .style("stroke", function(d) { return d3.rgb(color(d.index)).darker(); })
        .attr("d", arc)
        .attr("id", function(d, i){return "group-" + i;});

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
        .text(function(d){i++; return region_labels[i];});

    g.append("g")
        .attr("class", "ribbons")
      .selectAll("path")
      .data(function(chords) { return chords; })
      .enter().append("path")
        .attr("d", ribbon)
        .style("fill", function(d) { return color(d.target.index); })
        .style("stroke", function(d) { return d3.rgb(color(d.target.index)).darker(); })

    // Returns an array of tick angles and values for a given group and step.
    function groupTicks(d, step) {
      var k = (d.endAngle - d.startAngle) / d.value;
      return d3.range(0, d.value, step).map(function(value) {
        return {value: value, angle: value * k + d.startAngle};
      });
    }

    function fade(opacity) {
        return function(d, i) {
        svg.selectAll("path.chord")
            .filter(function(d) { return d.source.index != i && d.target.index != i; })
            .transition()
            .style("stroke-opacity", opacity)
            .style("fill-opacity", opacity);
        };
    }
}


