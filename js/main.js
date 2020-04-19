var scene = new THREE.Scene();
scene.background = new THREE.Color( 0xc0c0c0 );
var camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 1000 );
// var camera = new THREE.OrthographicCamera( width / - 2, width / 2, height / 2, height / - 2, near, far );
var renderer = new THREE.WebGLRenderer( {antialias: true} );
renderer.setSize( window.innerWidth/1.3, window.innerHeight/1.3 );
// TODO: set canvas size properly

const CUBIE_DIM = 1;
const STICKER_PADDING = 0.05;
const STICKER_THICKNESS = 0.02;  // max value: 1

const sticker_materials = [
    new THREE.MeshBasicMaterial( {color:"red"} ),             // +X face
    new THREE.MeshBasicMaterial( {color:0xff8c00} ),          // -X face
    new THREE.MeshBasicMaterial( {color:0xffff33} ),          // +Y face
    new THREE.MeshBasicMaterial( {color:"white"} ),           // -Y face
    new THREE.MeshBasicMaterial( {color:"blue"} ),            // +Z face
    new THREE.MeshBasicMaterial( {color:"green"} )            // -Z face
];

const black_material = new THREE.MeshBasicMaterial( { color: "black" } );

function makeCubie() {
    const cubie = new THREE.Object3D();
    const size = CUBIE_DIM - STICKER_PADDING*2;
    const sticker_geometry = new THREE.BoxGeometry(size, size, STICKER_THICKNESS);

    // add black background cubie
    const base_geometry = new THREE.BoxGeometry( 1, 1, 1 );
    const base_cubie = new THREE.Mesh(base_geometry, black_material);
    base_cubie.position.set( 0, 0, 0 );
    cubie.add(base_cubie);

    // add stickers
    [
        { position: [  1, 0, 0] },                            // +X face
        { position: [ -1, 0, 0] },                            // -X face
        { position: [ 0,  1, 0] },                            // +Y face
        { position: [ 0, -1, 0] },                            // -Y face
        { position: [ 0, 0,  1] },                            // +Z face
        { position: [ 0, 0, -1] },                            // -Z face
    ].forEach((settings, index) => {
        const sticker_material = sticker_materials[index];
        sticker_material.side = THREE.DoubleSide;
        const sticker = new THREE.Mesh(sticker_geometry, sticker_material);
        sticker.lookAt(...settings.position);
        sticker.position.set(...settings.position).multiplyScalar(CUBIE_DIM/2 + STICKER_THICKNESS/2);
        // sticker.position.set(...settings.position).multiplyScalar(CUBIE_DIM/2);
        cubie.add(sticker);
    });
    return cubie;
}

let cubies = [];

function addCubieToScene(position, quaternion = new THREE.Quaternion( 0, 0, 0, 1 )) {
    const cubie = makeCubie();
    cubie.position.set( position.x, position.y, position.z );
    cubie.setRotationFromQuaternion(quaternion);
    scene.add( cubie );
    cubies = cubies.concat(cubie);
}

camera.position.x = 3;
camera.position.y = 3;
camera.position.z = 3;
camera.lookAt( 0, 0, 0 );

function debug_vector(start_vec, end_vec) {
    var geometry = new THREE.Geometry();
    geometry.vertices.push( start_vec );
    geometry.vertices.push( end_vec );
    var material = new THREE.LineBasicMaterial( { color: "magenta" } );
    var line = new THREE.Line( geometry, material );
    scene.add( line );
}

function initCube() {
    for (var i = -1; i < 2; i++) {
        for (var j = -1; j < 2; j++) {
            for (var k = -1; k < 2; k++) {
                addCubieToScene( new THREE.Vector3( i, j, k ) );
            }
        }
    }
}

function updateCube(state) {
    for (let i=0; i<state.pieces.length; i++) {
        let piece = state.pieces[i],
            cubie = cubies[i];
        let piece_position = new THREE.Vector3(...piece.position);
        let piece_orientation = new THREE.Quaternion(...piece.orientation);
        cubie.position.set( piece_position.x, piece_position.y, piece_position.z );
        cubie.setRotationFromQuaternion( piece_orientation );
    }
}

function animate() {
    theta += 0.005;

    requestAnimationFrame( animate );
    var z = Math.cos(theta);
    var x = Math.sin(theta);

	camera.position.x = 5 * x;
    camera.position.y = 5 * z;
    camera.position.z = 5 * z;
    camera.lookAt( 2 * noise.perlin2( Math.cos(theta), Math.sin(theta) ),
                   2 * noise.perlin2( Math.cos(theta)+1, Math.sin(theta)+1 ),
                   2 * noise.perlin2( Math.cos(theta)+2, Math.sin(theta)+2 ));

    renderer.render( scene, camera );
}

function getstate() {
    $.get("/getstate", {user})
        .done(function (data) {
            updateCube(data);
        });
}

function maketurn(move) {
    $.post("/maketurn", JSON.stringify({user, move}))
            .done(function(data) {
                if (data.status === "ok")
                    updateCube(data);
                else
                    alert("invalid turn")
            });
}

var theta = 0;
let user;


$(document).ready(function() {
    user = prompt("Enter Username:");
    $("#username").text(user);

    $('body').prepend(renderer.domElement);  // add canvas to DOM

    initCube();
    getstate();

    setInterval(getstate, 500);

    for (let turn of "RUFLDBMESxyz") {
        Mousetrap.bind(turn.toLowerCase(), function() {maketurn(turn); });
        Mousetrap.bind(turn.toUpperCase(), function() {maketurn(turn + "'"); });
    }

    $("button.move-btn").click(function() {
        let basemove = $(this).data().move;
        let modifier = $("input[name=modifier]:checked").val();
        let move = basemove + modifier;
        maketurn(move);
    });

    renderer.render( scene, camera );
    animate();

});
