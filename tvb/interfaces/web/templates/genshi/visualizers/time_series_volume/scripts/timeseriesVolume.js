var ctx = null
var currentQuadrant
var minimumValue, maximumValue, data
var entitiesOnX, entitiesOnY, entitiesOnZ, entityWidth, entityHeight
var selectedEntityX,selectedEntityY,selectedEntityZ
var quadrantHeight, quadrantWidth

function startVisualiser(dataUrls, minValue, maxValue) {
    var canvas = document.getElementById("volumetric-ts-canvas")
    if (!canvas.getContext) {
        displayMessage('You need a browser with canvas capabilities, to see this demo fully!', "errorMessage")
        return
    }
    canvas.height = $(canvas).parent().height() - 10
    canvas.width  = $(canvas).parent().width()
    quadrantHeight = canvas.height / 2
    quadrantWidth = canvas.width / 2
    ctx = canvas.getContext("2d")

    console.log(minValue + " " + maxValue)
    dataUrls = $.parseJSON(dataUrls)
    data = HLPR_readJSONfromFile(dataUrls[0])
    data = data[0]                                  // just the first slice for now

    minimumValue =  9999
    maximumValue = -9999
    for (var i = 0; i < data.length; ++i)
        for (var j = 0; j < data[0].length; ++j)
            for (var k = 0; k < data[0][0].length; ++k)
                if (data[i][j][k] > maximumValue)
                    maximumValue = data[i][j][k]
                else if (data[i][j][k] < minimumValue)
                    minimumValue = data[i][j][k]

    entitiesOnX = data.length
    entitiesOnY = data[0].length
    entitiesOnZ = data[0][0].length

    selectedEntityX = Math.floor(entitiesOnX / 2)
    selectedEntityY = Math.floor(entitiesOnY / 2)
    selectedEntityZ = Math.floor(entitiesOnZ / 2)

    drawScene()
}

function drawScene() {
    _setQuadrant(1, true)
    for (var i = 0; i < data.length; ++i)
        for (var j = 0; j < data[0].length; ++j)
            drawVoxel(i, j, data[i][j][selectedEntityZ])

    _setQuadrant(2, true)
    for (var j = 0; j < data[0].length; ++j)
        for (var k = 0; k < data[0][0].length; ++k)
            drawVoxel(j, k, data[selectedEntityX][j][k])

    _setQuadrant(3, true)
    for (var i = 0; i < data.length; ++i)
        for (var k = 0; k < data[0][0].length; ++k)
            drawVoxel(i, k, data[i][selectedEntityY][k])
    drawAxes()
}

function drawVoxel(line, col, value) {
    ctx.fillStyle = getGradientColorString(value, minimumValue, maximumValue)
    ctx.fillRect(col * entityWidth, line * entityHeight, entityWidth, entityHeight)
}

function drawAxes() {
    ctx.save()

    // horizontal line through quadrants 1 and 2
    _setQuadrant(2, true)
    ctx.beginPath()
    ctx.moveTo(0, selectedEntityY * entityHeight)
    ctx.lineTo(quadrantWidth * 2, selectedEntityY * entityHeight)   // * 2 to draw through both quadrants

    // vertical line through quadrants 2 and 3
    ctx.moveTo(selectedEntityZ * entityWidth, 0)
    ctx.lineTo(selectedEntityZ * entityWidth, quadrantHeight * 2)

    // horizontal line through quadrant 3
    _setQuadrant(3, true)
    ctx.moveTo(0, selectedEntityX * entityHeight)
    ctx.lineTo(quadrantWidth, selectedEntityX * entityHeight)

    // vertical line through quadrant 1
    _setQuadrant(1, true)
    ctx.moveTo(selectedEntityX * entityWidth, 0)
    ctx.lineTo(selectedEntityX * entityWidth, quadrantHeight)

    ctx.strokeStyle = "blue"
    ctx.stroke()
    ctx.restore()
}

function _setQuadrant(quadrantNo, updateContext) {
    currentQuadrant = quadrantNo
    switch (quadrantNo) {
        case 1:
            entityHeight = (quadrantHeight) / entitiesOnY
            entityWidth  = (quadrantWidth) / entitiesOnX
            break
        case 2:
            entityHeight = (quadrantHeight) / entitiesOnY
            entityWidth  = (quadrantWidth)  / entitiesOnZ
            break
        case 3:     
            ctx.translate(0, quadrantHeight)
            entityHeight = quadrantHeight / entitiesOnX
            entityWidth  = quadrantWidth  / entitiesOnZ
            break
        case 4:                                                     // quadrant 4 isn't used now, but just in case
            ctx.translate(quadrantWidth, quadrantHeight)
            // if quadrant 4 is used set entity height and width, depending on which axes you need on that quadrant
            break
        default:    ctx.translate(0, 0)
    }
    if (updateContext) {
        ctx.setTransform(1, 0, 0, 1, 0, 0)                          // reset the transformation
        switch (quadrantNo) {
            case 1:  ctx.translate(quadrantWidth, 0); break
            case 2:  ctx.translate(0, 0); break
            case 3:  ctx.translate(0, quadrantHeight); break
            case 4:  ctx.translate(quadrantWidth, quadrantHeight); break
        }
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
    if (e.offsetX >= quadrantWidth && e.offsetY >= quadrantHeight)    // 4th quadrant
        return
    if (e.offsetX > quadrantWidth) {                                // 1st quadrant
        _setQuadrant(1, false)
        selectedEntityX = Math.floor((e.offsetX - quadrantWidth) / entityWidth)
        selectedEntityY = Math.floor(e.offsetY / entityHeight)
    }
    else if (e.offsetY > quadrantHeight) {                          // 3rd quadrant
        _setQuadrant(3, false)
        selectedEntityX = Math.floor((e.offsetY - quadrantHeight) / entityHeight)
        selectedEntityZ = Math.floor(e.offsetX / entityWidth)
    }
    else {                                                           // 2nd quadrant
        _setQuadrant(2, false)
        selectedEntityY = Math.floor(e.offsetY / entityHeight)
        selectedEntityZ = Math.floor(e.offsetX / entityWidth)
    }

    drawScene()
}
