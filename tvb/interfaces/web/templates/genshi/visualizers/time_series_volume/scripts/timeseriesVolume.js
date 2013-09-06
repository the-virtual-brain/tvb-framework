function startVisualiser(dataUrls) {
    var canvas = document.getElementById("volumetric-ts-canvas")
    if (!canvas.getContext) {
        displayMessage('You need a browser with canvas capabilities, to see this demo fully!', "errorMessage")
        return
    }
    var ctx = canvas.getContext("2d")

    dataUrls = $.parseJSON(dataUrls)
    
}
