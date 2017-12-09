window.run = (mapboxgl, center_coords) => {
    mapboxgl.accessToken = 'pk.eyJ1IjoiZGFuaWVsc2FsYW1vbiIsImEiOiJjajlib3ZldWQxZmlsMzNvNzluZzRvdzlyIn0.t-mRniAFQ6HlDXUy2n888w';

    const map = new mapboxgl.Map({
        container: 'map',
        //style: 'mapbox://styles/mapbox/streets-v9',
        style: 'mapbox://styles/danielsalamon/cjax404w44feb2qst82h601cm',
        center: center_coords,
        zoom: 11
    });

    const url = '/api/get-geojson';
    map.on('load', function () {
        map.addSource('api-15', {type: 'geojson', data: url});
        map.addLayer({
            'id': 'stroke-15',
            'type': 'line',
            'source': 'api-15',
            'layout': {
                'line-cap': 'round',
                'line-join': 'round',
                'line-round-limit': 1.1
            },
            'paint': {
                'line-opacity': 0.8,
                'line-color': '#993333',
                'line-width': 2
            }
        });
        map.addLayer({
            'id': 'fill-15',
            'type': 'fill',
            'source': 'api-15',
            'paint': {
                'fill-opacity': 0.2,
                'fill-color': '#995555'
            }
        });
    });

    const getPolygon = async () => (await fetch('/api/get-geojson')).json();

    document.getElementById('refresh').addEventListener('click', async () => {

        const mapData = await getPolygon();
        console.log(mapData);


        map.getSource('api-15').setData({
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": {},
                "geometry": mapData
            }]
        });
    });
};