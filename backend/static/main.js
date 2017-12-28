window.run = (mapboxgl, center_coords) => {
    mapboxgl.accessToken = 'pk.eyJ1IjoiZGFuaWVsc2FsYW1vbiIsImEiOiJjajlib3ZldWQxZmlsMzNvNzluZzRvdzlyIn0.t-mRniAFQ6HlDXUy2n888w';

    const map = new mapboxgl.Map({
        container: 'map',
        //style: 'mapbox://styles/mapbox/streets-v9',
        //style: 'mapbox://styles/danielsalamon/cjax404w44feb2qst82h601cm',
        style: 'mapbox://styles/danielsalamon/cjb3yv17s07qb2rnr5l7p34cg',
        center: center_coords,
        minZoom: 10,
        zoom: 11
    });

    let isDragging,
        isCursorOverPoint,
        canvas = map.getCanvasContainer(),
        cursor = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": center_coords
                }
            }]
        };


    const getPolygon = async (lat, lng, step) => (await fetch(`/api/get-geojson-${step}?lat=${lat}&lng=${lng}`)).json();

    const updatePolygon = (lat, lng) => {
        getPolygon(lat, lng, 15).then((mapData) => {
            map.getSource('api-15').setData({
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "properties": {},
                    "geometry": mapData
                }]
            });

            getPolygon(lat, lng, 30).then((mapData) =>
                map.getSource('api-30').setData({
                    "type": "FeatureCollection",
                    "features": [{
                        "type": "Feature",
                        "properties": {},
                        "geometry": mapData
                    }]
                })).catch((e) =>
                console.error(e)
            );
        }).catch((e) =>
            console.error(e)
        );
    };

    const mouseDown = () => {
        if (!isCursorOverPoint) return;

        isDragging = true;

        // Set a cursor indicator
        canvas.style.cursor = 'grab';

        // Mouse events
        map.on('mousemove', onMove);
        map.once('mouseup', onUp);
    };

    const onMove = (e) => {
        if (!isDragging) return;
        let coords = e.lngLat;
        canvas.style.cursor = 'grabbing';
        cursor.features[0].geometry.coordinates = [coords.lng, coords.lat];
        map.getSource('cursor').setData(cursor);
    };

    const onUp = (e) => {
        if (!isDragging) return;
        updatePolygon(e.lngLat.lat, e.lngLat.lng);
        canvas.style.cursor = '';
        isDragging = false;
        map.off('mousemove', onMove);
    };

    map.on('load', function () {

        // Add cursor to map
        (() => {
            map.addSource('cursor', {
                "type": "geojson",
                "data": cursor
            });

            map.addLayer({
                "id": "cursor",
                "type": "circle",
                "source": "cursor",
                "paint": {
                    "circle-radius": 10,
                    "circle-color": "#3887be"
                }
            });

            map.on('mouseenter', 'cursor', function () {
                map.setPaintProperty('cursor', 'circle-color', '#3bb2d0');
                canvas.style.cursor = 'move';
                isCursorOverPoint = true;
                map.dragPan.disable();
            });

            map.on('mouseleave', 'cursor', function () {
                map.setPaintProperty('cursor', 'circle-color', '#3887be');
                canvas.style.cursor = '';
                isCursorOverPoint = false;
                map.dragPan.enable();
            });

            map.on('mousedown', mouseDown);
        })();


        map.addSource('api-15', {type: 'geojson', data: {"type": "Point", "coordinates": [0, 0]}});
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
                'line-color': '#df0024',
                'line-width': 2
            }
        });
        map.addLayer({
            'id': 'fill-15',
            'type': 'fill',
            'source': 'api-15',
            'paint': {
                'fill-opacity': 0.2,
                'fill-color': '#df0024'
            }
        });


        map.addSource('api-30', {type: 'geojson', data: {"type": "Point", "coordinates": [0, 0]}});
        map.addLayer({
            'id': 'stroke-30',
            'type': 'line',
            'source': 'api-30',
            'layout': {
                'line-cap': 'round',
                'line-join': 'round',
                'line-round-limit': 1.1
            },
            'paint': {
                'line-opacity': 0.8,
                'line-color': '#00a9e5',
                'line-width': 2
            }
        });
        map.addLayer({
            'id': 'fill-30',
            'type': 'fill',
            'source': 'api-30',
            'paint': {
                'fill-opacity': 0.2,
                'fill-color': '#00a9e5'
            }
        });
    });
};