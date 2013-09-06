var ctx = null
var currentQuadrant
var minimumValue, maximumValue, data
var entityWidth, entityHeight, voxelSize
var selectedEntity = [0, 0, 0]
var quadrantHeight, quadrantWidth
var axesOnQuadrant = [{x: 1, y: 0}, {x: 1, y: 2}, {x: 0, y: 2}]

function startVisualiser(dataUrls, minValue, maxValue, volumeOrigin, sizeOfVoxel, voxelUnit) {
    var canvas = document.getElementById("volumetric-ts-canvas")
    if (!canvas.getContext) {
        displayMessage('You need a browser with canvas capabilities, to see this demo fully!', "errorMessage")
        return
    }

    volumeOrigin = $.parseJSON(volumeOrigin)[0]
    voxelSize    = $.parseJSON(sizeOfVoxel)
    console.log(voxelSize)

    canvas.width  = $(canvas).parent().width()
    canvas.height = canvas.width / 3 + 100
    quadrantHeight = quadrantWidth = canvas.width / 3
    ctx = canvas.getContext("2d")

    console.log(minValue + " " + maxValue)
    dataUrls = $.parseJSON(dataUrls)
    data = HLPR_readJSONfromFile(dataUrls[0])
    data = data[0]                                  // just the first slice for now

    _rotateData()
    minimumValue =  9999
    maximumValue = -9999
    for (var i = 0; i < data.length; ++i)
        for (var j = 0; j < data[0].length; ++j)
            for (var k = 0; k < data[0][0].length; ++k)
                if (data[i][j][k] > maximumValue)
                    maximumValue = data[i][j][k]
                else if (data[i][j][k] < minimumValue)
                    minimumValue = data[i][j][k]

    selectedEntity[0] = Math.floor(data.length / 2)
    selectedEntity[1] = Math.floor(data[0].length / 2)
    selectedEntity[2] = Math.floor(data[0][0].length / 2)

    drawScene()
}

function getData(axis) {
    switch (axis) {
        case 0:     return data
        case 1:     return data[0]
        case 2:     return data[0][0]
    }
}

function drawScene() {
    _setQuadrant(0, true)
    ctx.fillStyle = getGradientColorString(minimumValue, minimumValue, maximumValue)
    ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height)
    for (var j = 0; j < data[0].length; ++j)
        for (var i = 0; i < data.length; ++i)
            drawVoxel(i, j, data[i][j][selectedEntity[2]])

    _setQuadrant(1, true)
    for (var k = 0; k < data[0][0].length; ++k)
        for (var j = 0; j < data[0].length; ++j)
            drawVoxel(k, j, data[selectedEntity[0]][j][k])

    _setQuadrant(2, true)
    for (var k = 0; k < data[0][0].length; ++k)
        for (var i = 0; i < data.length; ++i)
            drawVoxel(k, i, data[i][selectedEntity[1]][k])
    drawAxes()
}

function drawVoxel(line, col, value) {
    ctx.fillStyle = getGradientColorString(value, minimumValue, maximumValue)
    ctx.fillRect(col * entityWidth, line * entityHeight, entityWidth, entityHeight)
}

function drawAxes() {
    ctx.save()
    ctx.beginPath()

    for (var quadrant = 0; quadrant < 3; ++quadrant) {
        _setQuadrant(quadrant, true)
        drawCrossHair(selectedEntity[axesOnQuadrant[quadrant].x] * entityWidth + entityWidth / 2,
                      selectedEntity[axesOnQuadrant[quadrant].y] * entityHeight + entityHeight / 2)
    }

    ctx.strokeStyle = "blue"
    ctx.stroke()
    ctx.restore()
}

function drawCrossHair(x, y) {
    ctx.moveTo(Math.max(x - 20, 0), y)                              // the horizontal line
    ctx.lineTo(Math.min(x + 20, quadrantWidth), y)
    ctx.moveTo(x, Math.max(y - 20, 0))                              // the vertical line
    ctx.lineTo(x, Math.min(y + 20, quadrantHeight))
}

function _rotateData() {
    for (var i = 0; i < data.length; ++i)
        for (var j = 0; j < data[0].length; ++j)
            data[i][j].reverse()
}

function _setEntityDimensions(xAxis, yAxis) {
    var scaleOnHeight = quadrantHeight / (getData(yAxis).length * voxelSize[yAxis])
    var scaleOnWidth  = quadrantWidth  / (getData(xAxis).length * voxelSize[xAxis])
    var scale = Math.min(scaleOnHeight, scaleOnWidth)
    entityHeight = voxelSize[yAxis] * scale
    entityWidth  = voxelSize[xAxis] * scale
}

function _setQuadrant(quadrantNo, updateContext) {
    currentQuadrant = quadrantNo
    _setEntityDimensions(axesOnQuadrant[quadrantNo].x, axesOnQuadrant[quadrantNo].y)
    if (updateContext) {
        ctx.setTransform(1, 0, 0, 1, 0, 0)                          // reset the transformation
        ctx.translate(quadrantNo * quadrantWidth, 0)
    }
}

function customMouseDown() {
    this.mouseDown = true                                           // `this` is the canvas
}

function customMouseUp() {
    this.mouseDown = false
}

function customMouseMove(e) {
    if (!this.mouseDown)
        return
    if (e.offsetY >= quadrantHeight || e.offsetX >= 3 * quadrantWidth)              // outside any quadrant
        return
    var selectedOnX, selectedOnY
    if (e.offsetX < quadrantWidth) {                                // 1st quadrant
        _setQuadrant(0, false)
        selectedOnX = Math.floor(e.offsetX / entityWidth)
        selectedOnY = Math.floor(e.offsetY / entityHeight)
    }
    else if (e.offsetX < 2 * quadrantWidth) {                       // 2nd quadrant
        _setQuadrant(1, false)
        selectedOnX = Math.floor((e.offsetX - quadrantWidth) / entityWidth)
        selectedOnY = Math.floor(e.offsetY / entityHeight)
    }
    else {                                                          // 3rd quadrant
        _setQuadrant(2, false)
        selectedOnX = Math.floor((e.offsetX - 2 * quadrantWidth) / entityWidth)
        selectedOnY = Math.floor(e.offsetY / entityHeight)
    }

    selectedEntity[axesOnQuadrant[currentQuadrant].x] = selectedOnX
    selectedEntity[axesOnQuadrant[currentQuadrant].y] = selectedOnY
    drawScene()
}
