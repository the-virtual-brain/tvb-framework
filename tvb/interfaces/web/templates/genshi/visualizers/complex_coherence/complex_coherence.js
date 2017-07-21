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
 * Created by Dan Pop on 5/24/2017.
 */


function complex_coherence_init(canvasName, xAxisName, yAxisName, coh_spec_sd, coh_spec_av, x_min, x_max, y_min, y_max, vmin, vmax) {


    // TODO fix the Y scaling, fill contour, get data for logarithmic scale
    var cohSdDataY=$.parseJSON(coh_spec_sd);
    var cohSdDataX=[];
    var cohTopDataFunction=[];
    var cohBotDataFunction=[];
    var cohAvDataY=$.parseJSON(coh_spec_av);
    var cohAvDataX=[];
    var cohAvDataFunction=[];
    for(i=0;i<cohSdDataY.length;i++){
        cohSdDataX[i]=((x_max-x_min)*i)/(cohSdDataY.length-1);
        cohTopDataFunction[i]=[cohSdDataX[i],cohAvDataY[i]+cohSdDataY[i]];
        cohBotDataFunction[i]=[cohSdDataX[i],cohAvDataY[i]-cohSdDataY[i]];
        cohAvDataFunction[i]=[cohSdDataX[i],cohAvDataY[i]];
    }
    var margin = {top: 30, right: 20, bottom: 30, left: 50},
        width = 1000 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

// Set the ranges
    var xScale = d3.scale.linear().range([margin.left, width - margin.right]).domain([x_min, x_max]);
    var yScale = d3.scale.linear().range([height - margin.top, margin.bottom]).domain([y_min, y_max]);

// Define the axes
    var xAxis = d3.svg.axis()
            .scale(xScale),
        yAxis = d3.svg.axis()
            .scale(yScale)
            .orient("left");

    var vis = d3.select("#svg-container");

    vis.append("svg:g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + (height - margin.bottom) + ")")
        .call(xAxis);
    vis.append("svg:g")
        .attr("class", "y axis")
        .attr("transform", "translate(" + (margin.left) + ",0)")
        .call(yAxis);

    var lineGen = d3.svg.line()
        .x(function (d) {
            return xScale(d[0]);
        })
        .y(function (d) {
            return yScale(d[1]);
        })
        .interpolate("basis");

        vis.append('svg:path')
            .attr('d', lineGen(cohTopDataFunction))
            .attr('stroke', 'green')
            .attr('stroke-width', 2)
            .attr('fill', 'none');

        vis.append('svg:path')
            .attr('d', lineGen(cohAvDataFunction))
            .attr('stroke', 'blue')
            .attr('stroke-width', 2)
            .attr('fill', 'none');

        vis.append('svg:path')
            .attr('d', lineGen(cohBotDataFunction))
            .attr('stroke', 'green')
            .attr('stroke-width', 2)
            .attr('fill', 'none');
}

