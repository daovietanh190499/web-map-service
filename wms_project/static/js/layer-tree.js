
function getListLayer() {
    let list_layer = null
    try {
        list_layer = JSON.parse(window.localStorage.getItem("layers"));
    } catch (e) {
        console.log(e)
    }
    if (!list_layer) {
        list_layer = {}
    }
    return list_layer
}

function clearListLayer() {
    window.localStorage.setItem("layers", "");
}

function removeLayer(layer_id) {
    let list_layer = getListLayer()
    delete list_layer[layer_id]
    window.localStorage.setItem("layers", JSON.stringify(list_layer))
}

function addLayer(layer_id, name, coords) {
    let list_layer = getListLayer()
    list_layer[layer_id] = {"name":name, "children": [], "coords": coords}
    window.localStorage.setItem("layers", JSON.stringify(list_layer))
}

function changeMenu(layer_id, name, coords) {
    let list_layer = getListLayer()
    if (layer_id in list_layer) {
        removeLayer(layer_id)
        document.getElementById(layer_id).classList.remove('fa-folder-minus')
        document.getElementById(layer_id).classList.add('fa-folder-plus')
    } else {
        addLayer(layer_id, name, coords)
        document.getElementById(layer_id).classList.remove('fa-folder-plus')
        document.getElementById(layer_id).classList.add('fa-folder-minus')
    }
    list_layer = getListLayer()
    updateLayerTree()
}

var theTreeControl

updateLayerTree()

function updateLayerTree() {
    if (theTreeControl) {
        theTreeControl.remove(map);
    }

    let list_layer = getListLayer()

    var layerBuilders = {
        OSM: function (layerSettings) {
            return L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                subdomains: ['a', 'b', 'c']
            });
        },
        SATELLITE: function (layerSettings) {
            return L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                attribution: 'Tiles © Esri'
            });
        }
    }

    for (let layer in list_layer) {
        layerBuilders[layer] = function (layerSettings) {
            return L.tileLayer(`api/images/${layer}/jp2/tiles/{z}/{x}/{y}.png/`, {
                maxZoom: 20,
                attribution: `${layer} JP2 Layer`
            });
        }
    }

    theTreeControl = new L.Control.LayerTreeControl({
        // layerTree: rootLayerSettings,
        openByDefault: true,
        layerBuilders: layerBuilders,
        featureBuilders: {
            WFS: {
                zoom: L.Control.LayerTreeControl.WFSZoomFeature
            }
        }
    }).addTo(map);

    var rootLayerId = theTreeControl.addLayerDynamically({
        code: "root",
        name: "All the Layers",
        active: true,
        selectedByDefault: false,
        openByDefault: true,
        childLayers: [],
        selectType: "NONE",
        serviceType: null,
        params: {}
    });

    var baseLayerId = theTreeControl.addLayerDynamically({
        code: "base",
        name: "Base layers",
        active: true,
        selectedByDefault: false,
        openByDefault: true,
        childLayers: [],
        selectType: "SINGLE",
        serviceType: null,
        params: {}
    }, rootLayerId);

    var overlaysLayerId = theTreeControl.addLayerDynamically({
        code: "overlays",
        name: "Overlays",
        active: true,
        selectedByDefault: false,
        openByDefault: true,
        childLayers: [],
        selectType: selectType,
        serviceType: null,
        params: {}
    }, rootLayerId);

    var osmLayerId = theTreeControl.addLayerDynamically({
        code: "osm",
        name: "OpenStreetMap",
        active: true,
        selectedByDefault: true,
        openByDefault: true,
        childLayers: [],
        selectType: "NONE",
        serviceType: "OSM",
        params: {}
    }, baseLayerId);

    var satelliteLayerId = theTreeControl.addLayerDynamically({
        code: "satellite",
        name: "Satellite",
        active: true,
        selectedByDefault: false,
        openByDefault: true,
        childLayers: [],
        selectType: "NONE",
        serviceType: "SATELLITE",
        params: {}
    }, baseLayerId);

    for (let layer in list_layer) {
        let coords = JSON.parse(list_layer[layer]['coords'])
        theTreeControl.addLayerDynamically({
            code: layer,
            name: list_layer[layer]['name'] ? list_layer[layer]['name'] : layer,
            active: true,
            selectedByDefault: false,
            openByDefault: true,
            childLayers: [],
            coord: [(coords[5] + coords[1])/2, (coords[0] + coords[4])/2],
            selectType: "NONE",
            serviceType: layer,
            params: {},
            callback: () => {
                (saveSideBar || (() => {}))();
            }
        }, overlaysLayerId);
    }
}

L.easyButton('fa-brush', function (btn, map) {
    clearListLayer()
    window.location.reload()
}, { position: "bottomleft" }).addTo(map);